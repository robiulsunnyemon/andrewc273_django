from rest_framework import serializers
from .models import CaseSubmission, CaseDocument

class CaseDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CaseDocument
        fields = ['id', 'case', 'file', 'uploaded_at']
        read_only_fields = ['uploaded_at']

class CaseSubmissionSerializer(serializers.ModelSerializer):
    documents = CaseDocumentSerializer(many=True, read_only=True)
    class Meta:
        model = CaseSubmission
        fields = ['id', 'user', 'case_title', 'case_number', 'author', 'press_release', 'state', 'federal_district', 'court_type', 'is_anonymous', 'press_release_enhanced', 'ai_analysis_summary', 'documents', 'created_at']
    
        read_only_fields = ['press_release_enhanced', 'ai_analysis_summary', 'created_at']

class CaseCardSerializer(serializers.ModelSerializer):
    # summary snippet toiri korar jonno
    content_snippet = serializers.SerializerMethodField()
    #name = serializers.CharField(source='profile.name', read_only=True)
    name = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = CaseSubmission
        fields = ['id', 'case_title', 'author','name','avatar', 'federal_district', 'created_at', 'content_snippet']

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