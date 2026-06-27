from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.users.models import Profile
from apps.resources.models import Prison
from .models import Post, PostAttachment, PostReaction, Comment, PostReport

User = get_user_model()

class UserMiniSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'avatar']

    def get_name(self, obj):
        try:
            profile = obj.profile
            if profile.name:
                return profile.name
            if profile.first_name or profile.last_name:
                return f"{profile.first_name} {profile.last_name}".strip()
        except AttributeError:
            pass
        return obj.email.split('@')[0]

    def get_avatar(self, obj):
        try:
            profile = obj.profile
            if profile.avatar:
                request = self.context.get('request')
                if request:
                    return request.build_absolute_uri(profile.avatar.url)
                return profile.avatar.url
        except AttributeError:
            pass
        return None


class PostAttachmentSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = PostAttachment
        fields = ['id', 'file', 'file_url', 'file_type', 'uploaded_at']

    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file:
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None


class CommentSerializer(serializers.ModelSerializer):
    user = UserMiniSerializer(read_only=True)
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'post', 'user', 'content', 'parent', 'created_at', 'updated_at', 'replies']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def get_replies(self, obj):
        # Only return children when resolving parent comment to avoid deep recursion
        if obj.parent_id is None:
            replies = obj.replies.all()
            return CommentSerializer(replies, many=True, context=self.context).data
        return []


class PostSerializer(serializers.ModelSerializer):
    user = UserMiniSerializer(read_only=True)
    attachments = PostAttachmentSerializer(many=True, read_only=True)
    prison_name = serializers.CharField(source='prison.name', read_only=True)
    prison_code = serializers.CharField(source='prison.code', read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    comments_count = serializers.SerializerMethodField()
    reactions_count = serializers.SerializerMethodField()
    user_reaction = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id', 'user', 'title', 'content', 'category', 'category_display',
            'prison', 'prison_name', 'prison_code', 'is_pinned', 'is_flagged',
            'views_count', 'created_at', 'updated_at', 'attachments',
            'comments_count', 'reactions_count', 'user_reaction'
        ]
        read_only_fields = ['id', 'user', 'views_count', 'is_pinned', 'is_flagged', 'created_at', 'updated_at']

    def get_comments_count(self, obj):
        return obj.comments.count()

    def get_reactions_count(self, obj):
        counts = {
            'like': 0,
            'helpful': 0,
            'warning': 0,
            'watching': 0,
            'important': 0
        }
        for reaction in obj.reactions.all():
            if reaction.reaction_type in counts:
                counts[reaction.reaction_type] += 1
        return counts

    def get_user_reaction(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            reaction = obj.reactions.filter(user=request.user).first()
            if reaction:
                return reaction.reaction_type
        return None


class PostCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'category', 'prison']

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['user'] = request.user
        post = super().create(validated_data)
        return post
