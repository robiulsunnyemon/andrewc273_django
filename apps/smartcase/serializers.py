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
        fields = ['id', 'case_title', 'case_number', 'author', 'press_release', 'state', 'federal_district', 'court_type', 'is_anonymous', 'press_release_enhanced', 'ai_analysis_summary', 'documents', 'created_at']
    
        read_only_fields = ['press_release_enhanced', 'ai_analysis_summary', 'created_at']

class CaseCardSerializer(serializers.ModelSerializer):
    # summary snippet toiri korar jonno
    content_snippet = serializers.SerializerMethodField()
    name=serializers.CharField(source='profile.name', read_only=True)
    avatar=serializers.ImageField(source='profile.avatar', read_only=True)

    class Meta:
        model = CaseSubmission
        fields = ['id', 'case_title', 'author','name','avatar', 'federal_district', 'created_at', 'content_snippet']

    def get_content_snippet(self, obj):
        return obj.press_release[:150] + "..." if obj.press_release else ""