import json
from pydantic import ValidationError
from rest_framework import serializers
from .models import CaseSubmission, CaseDocument, LegalArgument, PodcastStory,Story, StoryFile
from django.db import transaction
from apps.users.models import Profile

class PublicProfileSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    social_links = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ['name', 'avatar', 'status', 'social_links']

    def get_status(self, obj):
        p = obj
        user = obj.user
        # SocialLink connect
        s = getattr(user, 'social_link', None)
        
        top_badge = "Legion"
        if p.total_letters >= 500000 or p.total_posts >= 150:
            top_badge = "Omega"
        elif p.total_letters >= 250000 or p.total_posts >= 75:
            top_badge = "Phi"

        # verified link must 2 link
        connected_count = 0
        if s:
            # how many link
            links = [s.facebook, s.x, s.instagram, s.youtube, s.truth]
            connected_count = len([link for link in links if link])

        return {
            "top_badge": top_badge,
            "is_verified": connected_count >= 2,
            "is_large_contributor": p.total_posts > 200,
            "has_star": p.has_podcast_story
        }

    def get_social_links(self, obj):
        
        s = getattr(obj.user, 'social_link', None)
        if s:
            return {
                "facebook": s.facebook,
                "x": s.x,
                "instagram": s.instagram,
                "youtube": s.youtube,
                "truth": s.truth
            }
        return {}

class CaseDocumentSerializer(serializers.ModelSerializer):
    download_url = serializers.SerializerMethodField()
    file_size = serializers.SerializerMethodField()
    # is_video = serializers.SerializerMethodField()
    class Meta:
        model = CaseDocument
        fields = ['id', 'case','title', 'file','download_url','document_type', 'file_size',  'uploaded_at']
        read_only_fields = ['uploaded_at', 'file_size', 'document_type']

    # def get_download_url(self, obj):
    #     request = self.context.get('request')
    #     if request:
    #         # Full path: 
    #         return request.build_absolute_uri(f"/api/documents/download/{obj.id}/")
        
    #     return f"/api/documents/download/{obj.id}/"
    def get_download_url(self, obj):
        request = self.context.get('request')
        
        if request:
            return request.build_absolute_uri(obj.file.url)
        
        return obj.file.url
    
    

    def get_file_size(self, obj):
        try:
            size = obj.file.size
            if size < 1024: return f"{size} B"
            elif size < 1048576: return f"{round(size / 1024, 1)} KB"
            else: return f"{round(size / 1048576, 1)} MB"
        except: return "Unknown"

    # def get_is_video(self, obj):
    #     try:
    #         return obj.file.name.endswith(('.mp4', '.avi', '.mov'))
    #     except: return False

class LegalArgumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = LegalArgument
        fields = ['title', 'content']

class CaseSubmissionSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()

    documents = CaseDocumentSerializer(many=True, read_only=True)
    # legal_arguments = LegalArgumentSerializer(many=True)
    
    legal_arguments = LegalArgumentSerializer(many=True, required=False)
    


    class Meta:
        model = CaseSubmission
        fields = ['id', 'user', 'case_title', 'case_number', 'author', 'name', 'avatar', 'press_release', 'state', 'federal_district','case_status','status','court_type','legal_arguments','accepted_at', 'is_anonymous', 'press_release_enhanced', 'ai_analysis_summary', 'documents', 'created_at']
    
        read_only_fields = ['press_release_enhanced', 'ai_analysis_summary', 'created_at', 'accepted_at']

    # def to_internal_value(self, data):
    #     legal_arguments = data.get('legal_arguments')

    #     if isinstance(legal_arguments, str):
    #         if legal_arguments.strip() == "":
    #             data['legal_arguments'] = []
    #         else:
    #             try:
    #                 data['legal_arguments'] = json.loads(legal_arguments)
    #             except ValueError:
    #                 raise serializers.ValidationError({
    #                 "legal_arguments": "Invalid JSON format"
    #             })

    #     return super().to_internal_value(data)
    # def to_internal_value(self, data):
    #     print("RAW legal_arguments:", data.get('legal_arguments'))

    #     legal_arguments = data.get('legal_arguments')

    #     if isinstance(legal_arguments, str):
    #         print("STRING DETECTED:", legal_arguments)
            
    #         if legal_arguments.strip() == "":
    #             data['legal_arguments'] = []
    #         else:
    #             import json
    #             data['legal_arguments'] = json.loads(legal_arguments)

    #     print("FINAL DATA:", data.get('legal_arguments'))

    #     return super().to_internal_value(data)

    def validate(self, attrs):
        legal_arguments = self.initial_data.get('legal_arguments')

        if isinstance(legal_arguments, str):
            import json
            legal_arguments = json.loads(legal_arguments)

        attrs['legal_arguments'] = legal_arguments or []
        return attrs

    

    def get_name(self, obj):
        # User -> Profile -> Name sequence check
        try:
            if obj.user and hasattr(obj.user, 'profile'):
                return obj.user.profile.name or "No Name Provided"
        except Exception:
            return "Unknown Author"
        return "Unknown Author"
    
    def get_avatar(self, obj):
        # user-er profile ebong avatar ache kina check kora
        if hasattr(obj.user, 'profile') and obj.user.profile.avatar:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.user.profile.avatar.url)
            return obj.user.profile.avatar.url
        return None
        # status field to show if case is pending, accepted or rejected

    def get_status(self, obj):
        user = obj.user
        if not user or not hasattr(user, 'profile'):
            return None
        p = user.profile
        s = getattr(user, 'social_link', None)
        top_badge = "Legion"
        if p.total_letters >= 500000 or p.total_posts >= 150:
            top_badge = "Omega"
        elif p.total_letters >= 250000 or p.total_posts >= 75:
            top_badge = "Phi"
        # elif p.total_letters >= 50 or p.total_posts >= 2:
        #     top_badge = "Sigma"

        is_verified = s.connected_count >= 2 if s else False
        is_large_contributor = p.total_posts > 200
        has_star = p.has_podcast_story
        return {
            "top_badge": top_badge,
            "is_verified": is_verified,
            "is_large_contributor": is_large_contributor,
            "has_star": has_star
        }
    
    #new add 
    def create(self, validated_data):
        
        arguments_data = validated_data.pop('legal_arguments', [])

        # print("DEBUG arguments_data:", arguments_data)

        with transaction.atomic():
            case = CaseSubmission.objects.create(**validated_data)
            for argument in arguments_data:
                LegalArgument.objects.create(case=case, **argument)
            
        return case
    

     # new add 
    def update(self, instance, validated_data):
        # legal arguments data ke alada kore niye asha
        arguments_data = validated_data.pop('legal_arguments', None)
        
        #  normal field gulo update kora
        instance = super().update(instance, validated_data)

        # legal arguments update kora
        if arguments_data is not None:
            # existing arguments gulo delete kore deya, tarpor notun gulo create kora
            instance.legal_arguments.all().delete()
            for argument in arguments_data:
                LegalArgument.objects.create(case=instance, **argument)
                
        return instance

        

    

class CaseCardSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    # summary snippet toiri korar jonno
    content_snippet = serializers.SerializerMethodField()
    #name = serializers.CharField(source='profile.name', read_only=True)
    name = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = CaseSubmission
        fields = ['id', 'case_title','user', 'author','name','avatar', 'federal_district','is_anonymous', 'created_at', 'content_snippet','accepted_at', 'status', 'case_status','state']

    def get_name(self, obj):
        # User -> Profile -> Name sequence check
        try:
            if obj.user and hasattr(obj.user, 'profile'):
                return obj.user.profile.name or "No Name Provided"
        except Exception:
            return "Unknown Author"
        return "Unknown Author"

    def get_content_snippet(self, obj):
        return obj.press_release[:150] + "..." if obj.press_release else ""
    
    
    def get_avatar(self, obj):
        # user-er profile ebong avatar ache kina check kora
        if hasattr(obj.user, 'profile') and obj.user.profile.avatar:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.user.profile.avatar.url)
            return obj.user.profile.avatar.url
        return None
    
    def get_status(self, obj):
        user = obj.user
        if not user or not hasattr(user, 'profile'):
            return None
        p = user.profile
        s = getattr(user, 'social_link', None)
        top_badge = "Legion"
        if p.total_letters >= 500000 or p.total_posts >= 150:
            top_badge = "Omega"
        elif p.total_letters >= 250000 or p.total_posts >= 75:
            top_badge = "Phi"
        # elif p.total_letters >= 50 or p.total_posts >= 2:
        #     top_badge = "Sigma"

        is_verified = s.connected_count >= 2 if s else False
        is_large_contributor = p.total_posts > 200
        has_star = p.has_podcast_story
        return {
            "top_badge": top_badge,
            "is_verified": is_verified,
            "is_large_contributor": is_large_contributor,
            "has_star": has_star
        }
    
#media serializer for card view

class CaseCardMediaSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    # summary snippet toiri korar jonno
    # content_snippet = serializers.SerializerMethodField()
    #name = serializers.CharField(source='profile.name', read_only=True)
    documents = CaseDocumentSerializer(many=True, read_only=True)
    # documents = serializers.SerializerMethodField()
    # download_url = serializers.SerializerMethodField()
    # file_size = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()


    class Meta:
        model = CaseSubmission
        fields = ['id', 'case_title', 'author','name','avatar', 'federal_district', 'created_at', 'status','accepted_at', 'documents', 'case_status']
    


    def get_name(self, obj):
        # User -> Profile -> Name sequence check
        try:
            if obj.user and hasattr(obj.user, 'profile'):
                return obj.user.profile.name or "No Name Provided"
        except Exception:
            return "Unknown Author"
        return "Unknown Author"

    # def get_content_snippet(self, obj):
    #     return obj.press_release[:150] + "..." if obj.press_release else ""
    
    
    def get_avatar(self, obj):
        # user-er profile ebong avatar ache kina check kora
        if hasattr(obj.user, 'profile') and obj.user.profile.avatar:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.user.profile.avatar.url)
            return obj.user.profile.avatar.url
        return None
    
    def get_status(self, obj):
        user = obj.user
        if not user or not hasattr(user, 'profile'):
            return None
        p = user.profile
        s = getattr(user, 'social_link', None)
        top_badge = "Legion"
        if p.total_letters >= 500000 or p.total_posts >= 150:
            top_badge = "Omega"
        elif p.total_letters >= 250000 or p.total_posts >= 75:
            top_badge = "Phi"
        elif p.total_letters >= 50 or p.total_posts >= 2:
            top_badge = "Sigma"

        is_verified = s.connected_count >= 2 if s else False
        is_large_contributor = p.total_posts > 200
        has_star = p.has_podcast_story
        return {
            "top_badge": top_badge,
            "is_verified": is_verified,
            "is_large_contributor": is_large_contributor,
            "has_star": has_star
        }






class StoryFileSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()
    class Meta:
        model = StoryFile
        fields = ['id', 'file','file_url','story_file_type', 'uploaded_at']


    


    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return None
    

    def get_file_size(self, obj):
        try:
            size = obj.file.size
            if size < 1024: return f"{size} B"
            elif size < 1048576: return f"{round(size / 1024, 1)} KB"
            else: return f"{round(size / 1048576, 1)} MB"
        except: return "Unknown Size"


class StorySerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()
    files = StoryFileSerializer(many=True, read_only=True)
    uploaded_files = serializers.ListField(child=serializers.FileField(),write_only=True,required=False)

    class Meta:
        model = Story
        fields = [
            'id', 'user', 'title','description', 'name', 'avatar', 'status', 'is_featured','files', 'uploaded_files', 'created_at'
        ]
        
        read_only_fields = ['is_featured','user', 'created_at']

    def get_name(self, obj):
        # User -> Profile -> Name sequence check
        try:
            if obj.user and hasattr(obj.user, 'profile'):
                return obj.user.profile.name or "No Name Provided"
        except Exception:
            return "Unknown Author"
        return "Unknown Author"
    
    def get_avatar(self, obj):
        # user-er profile ebong avatar ache kina check kora
        if hasattr(obj.user, 'profile') and obj.user.profile.avatar:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.user.profile.avatar.url)
            return obj.user.profile.avatar.url
        return None
        # status field to show if case is pending, accepted or rejected

    def get_status(self, obj):
        user = obj.user
        if not user or not hasattr(user, 'profile'):
            return None
        p = user.profile
        s = getattr(user, 'social_link', None)
        top_badge = "Legion"
        if p.total_letters >= 500000 or p.total_posts >= 150:
            top_badge = "Omega"
        elif p.total_letters >= 250000 or p.total_posts >= 75:
            top_badge = "Phi"
        # elif p.total_letters >= 50 or p.total_posts >= 2:
        #     top_badge = "Sigma"

        is_verified = s.connected_count >= 2 if s else False
        is_large_contributor = p.total_posts > 200
        # has_star = p.has_podcast_story
        return {
            "top_badge": top_badge,
            "is_verified": is_verified,
            "is_large_contributor": is_large_contributor,
            # "has_star": has_star
        }

    def validate_uploaded_files(self, value):
        """
       validate_uploaded_files method ta StorySerializer er moddhe add kora hoyeche, jeta uploaded_files field er jonno custom validation provide kore. Ei method ta ensure kore je user video file upload korte parbe na, karon video file gulo accept kora hobe na.
        """
        forbidden_video_extensions = [
            '.mp4', '.mkv', '.wmv', '.3gp', '.avi', '.mov', '.flv', '.webm'
        ]
        
        for file in value:
            file_name = file.name.lower()
            
           
            if any(file_name.endswith(ext) for ext in forbidden_video_extensions):
                raise ValidationError(f"Can not upload video files: {file.name}")
            
           
           
            content_type = getattr(file, 'content_type', None)
            if content_type and content_type.startswith('video/'):
                raise ValidationError(f"Can not upload video files: {file.name}")
                
        return value
    

    # def create(self, validated_data):
        
    #     files_data = validated_data.pop('uploaded_files', [])
       
    #     story = Story.objects.create(**validated_data)
        
    #     for file_data in files_data:
    #         StoryFile.objects.create(story=story, file=file_data)
            
    #     return story
    
    def create(self, validated_data):
        files_data = validated_data.pop('uploaded_files', [])

        story = Story.objects.create(**validated_data)

        for file_data in files_data:
            StoryFile.objects.create(
            story=story,
            file=file_data
        )
        return story
    
class PodcastStorySerializer(serializers.ModelSerializer):
   
    file_download_url = serializers.SerializerMethodField()

    class Meta:
        model = PodcastStory
        
        fields = ['id', 'title', 'files','descriptions', 'created_at', 'file_download_url']

    def get_file_download_url(self, obj):
        request = self.context.get('request')
        if obj.files:
            
            if request:
                return request.build_absolute_uri(obj.files.url)
            return obj.files.url
        return None