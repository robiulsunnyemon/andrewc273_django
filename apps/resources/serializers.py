from rest_framework import serializers
from .models import LegalForm, FormFile

class FormFileSerializer(serializers.ModelSerializer):
    size = serializers.ReadOnlyField(source='file_size')

    class Meta:
        model = FormFile
        fields = ['file_name', 'pdf_file', 'size']

class LegalFormListSerializer(serializers.ModelSerializer):
    class Meta:
        model = LegalForm
        fields = ['id', 'title', 'content', 'slug']


class LegalFormDetailSerializer(serializers.ModelSerializer):
    files = FormFileSerializer(many=True, read_only=True)

    class Meta:
        model = LegalForm
        fields = ['title', 'content', 'files', 'last_updated']