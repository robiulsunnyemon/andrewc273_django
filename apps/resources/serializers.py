from rest_framework import serializers
from .models import LegalForm, FormFile,Prison

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






class PrisonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prison
        fields = [
            'id', 
            'code', 
            'name', 
            'name_title', 
            'name_display', 
            'type', 
            'security_level', 
            'region', 
            'latitude', 
            'longitude', 
            # 'url',             
            'time_zone', 
            'address', 
            'city',           
            'state',           
            'zip_code',       
            'contact_email', 
            'phone_number', 
            'gender', 
            'facl_type_description', 
            'has_camp', 
            'has_fsl', 
            'has_fdc', 
            'has_sff', 
            'has_ihp', 
            # 'image_normal', 
            # 'image_small'
        ]
        read_only_fields = ['id','url', 'image_normal', 'image_small']   