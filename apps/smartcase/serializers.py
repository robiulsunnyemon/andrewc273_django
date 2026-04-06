from rest_framework import serializers
from .models import CaseSubmission, CaseDocument

class CaseDocumentSerializer(serializers.ModelSerializer):
    download_url = serializers.SerializerMethodField()
    file_size = serializers.SerializerMethodField()
    # is_video = serializers.SerializerMethodField()
    class Meta:
        model = CaseDocument
        fields = ['id', 'case','title', 'file','download_url', 'file_size',  'uploaded_at']
        read_only_fields = ['uploaded_at']

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

class CaseSubmissionSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()

    documents = CaseDocumentSerializer(many=True, read_only=True)
    class Meta:
        model = CaseSubmission
        fields = ['id', 'user', 'case_title', 'case_number', 'author', 'press_release', 'state', 'federal_district','case_status','status','court_type','key_legal_arguments', 'is_anonymous', 'press_release_enhanced', 'ai_analysis_summary', 'documents', 'created_at']
    
        read_only_fields = ['press_release_enhanced', 'ai_analysis_summary', 'created_at']
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

        

    

class CaseCardSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    # summary snippet toiri korar jonno
    content_snippet = serializers.SerializerMethodField()
    #name = serializers.CharField(source='profile.name', read_only=True)
    name = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = CaseSubmission
        fields = ['id', 'case_title', 'author','name','avatar', 'federal_district', 'created_at', 'content_snippet', 'status', 'case_status']

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
    # download_url = serializers.SerializerMethodField()
    # file_size = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()


    class Meta:
        model = CaseSubmission
        fields = ['id', 'case_title', 'author','name','avatar', 'federal_district', 'created_at', 'status', 'documents', 'case_status']


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
