from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, ValidationError, NotAuthenticated
from django.db.models import Q
from .models import Post, PostAttachment, PostReaction, Comment, PostReport
from .serializers import (
    PostSerializer, PostCreateUpdateSerializer,
    CommentSerializer, PostAttachmentSerializer
)

class IsAuthorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user


def get_file_type(filename):
    ext = filename.split('.')[-1].lower() if '.' in filename else ''
    if ext in ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg']:
        return 'image'
    elif ext in ['mp4', 'webm', 'ogg', 'mov', 'avi', 'mkv']:
        return 'video'
    elif ext == 'pdf':
        return 'pdf'
    elif ext in ['doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt']:
        return 'document'
    return 'file'


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.select_related('user', 'user__profile', 'prison').prefetch_related(
        'attachments', 'reactions', 'comments', 'comments__user', 'comments__user__profile'
    )
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return PostCreateUpdateSerializer
        return PostSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Search filter
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(content__icontains=search)
            )

        # Category filter
        category = self.request.query_params.get('category', None)
        if category and category != 'all':
            queryset = queryset.filter(category=category)

        # Facility/Prison filter
        prison_id = self.request.query_params.get('prison', None)
        if prison_id:
            queryset = queryset.filter(prison_id=prison_id)

        # My posts filter
        my_posts = self.request.query_params.get('my_posts', None)
        if my_posts == 'true' or my_posts is True:
            if not self.request.user.is_authenticated:
                raise NotAuthenticated("You must be logged in to view your posts.")
            queryset = queryset.filter(user=self.request.user)

        return queryset

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Increment views count
        instance.views_count += 1
        instance.save(update_fields=['views_count'])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def perform_create(self, serializer):
        post = serializer.save()
        
        # Handle file attachments
        files = self.request.FILES.getlist('files')
        for file in files:
            file_type = get_file_type(file.name)
            PostAttachment.objects.create(post=post, file=file, file_type=file_type)

    def perform_update(self, serializer):
        post = serializer.save()

        # Handle removing files if specified
        remove_attachments = self.request.data.getlist('remove_attachments') or self.request.data.get('remove_attachments', [])
        if remove_attachments:
            if isinstance(remove_attachments, str):
                remove_attachments = [remove_attachments]
            PostAttachment.objects.filter(post=post, id__in=remove_attachments).delete()

        # Handle adding new files
        files = self.request.FILES.getlist('files')
        for file in files:
            file_type = get_file_type(file.name)
            PostAttachment.objects.create(post=post, file=file, file_type=file_type)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def react(self, request, pk=None):
        post = self.get_object()
        reaction_type = request.data.get('reaction_type')
        
        # Increment views count on reaction click
        post.views_count += 1
        post.save(update_fields=['views_count'])
        
        valid_reactions = ['like', 'helpful', 'warning', 'watching', 'important']
        if reaction_type not in valid_reactions:
            return Response(
                {"error": f"Invalid reaction_type. Must be one of {valid_reactions}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        existing_reaction = PostReaction.objects.filter(post=post, user=request.user).first()

        if existing_reaction:
            if existing_reaction.reaction_type == reaction_type:
                # Toggle off: delete if clicking the same reaction again
                existing_reaction.delete()
                return Response({"status": "removed", "reaction_type": reaction_type})
            else:
                # Update reaction to new type
                existing_reaction.reaction_type = reaction_type
                existing_reaction.save()
                return Response({"status": "updated", "reaction_type": reaction_type})
        else:
            # Create new reaction
            PostReaction.objects.create(post=post, user=request.user, reaction_type=reaction_type)
            return Response({"status": "added", "reaction_type": reaction_type})

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def report(self, request, pk=None):
        post = self.get_object()
        reason = request.data.get('reason', '').strip()

        if not reason:
            return Response({"error": "Reason is required to flag a post."}, status=status.HTTP_400_BAD_REQUEST)

        # Flag post and save report
        report, created = PostReport.objects.get_or_create(
            post=post, user=request.user,
            defaults={'reason': reason}
        )

        if not created:
            return Response({"message": "You have already flagged this post."}, status=status.HTTP_400_BAD_REQUEST)

        post.is_flagged = True
        post.save(update_fields=['is_flagged'])
        return Response({"message": "Post successfully reported."}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def comment(self, request, pk=None):
        post = self.get_object()
        content = request.data.get('content', '').strip()
        parent_id = request.data.get('parent_id', None)

        if not content:
            return Response({"error": "Comment content cannot be empty."}, status=status.HTTP_400_BAD_REQUEST)

        parent = None
        if parent_id:
            try:
                parent = Comment.objects.get(id=parent_id, post=post)
            except Comment.DoesNotExist:
                return Response({"error": "Parent comment does not exist."}, status=status.HTTP_400_BAD_REQUEST)

        comment = Comment.objects.create(
            post=post, user=request.user, content=content, parent=parent
        )
        serializer = CommentSerializer(comment, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def comments(self, request, pk=None):
        post = self.get_object()
        # Return only top level comments, replies will be nested inside them
        comments = post.comments.filter(parent=None).select_related('user', 'user__profile').prefetch_related('replies', 'replies__user', 'replies__user__profile')
        serializer = CommentSerializer(comments, many=True, context={'request': request})
        return Response(serializer.data)
