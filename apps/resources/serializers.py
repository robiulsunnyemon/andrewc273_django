from rest_framework import serializers
from .models import LegalForm, FormFile

class FormFileSerializer(serializers.ModelSerializer):
    size = serializers.ReadOnlyField(source='file_size')
    download_url = serializers.FileField(source='pdf_file', read_only=True)

    class Meta:
        model = FormFile
        fields = ['file_name', 'pdf_file', 'size', 'download_url']

class LegalFormListSerializer(serializers.ModelSerializer):
    class Meta:
        model = LegalForm
        fields = ['id', 'title', 'short_description', 'slug']


class LegalFormDetailSerializer(serializers.ModelSerializer):
    files = FormFileSerializer(many=True, read_only=True)

    class Meta:
        model = LegalForm
        fields = [ 'id', 'title', 'short_description', 'content', 'files', 'last_updated']