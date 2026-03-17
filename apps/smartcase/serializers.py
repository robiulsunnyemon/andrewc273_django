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

