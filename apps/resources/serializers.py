from rest_framework import serializers

from .models import CategoryRating, LegalForm, FormFile,Prison,LegalLibrary,Review

from apps.smartcase.serializers import PublicProfileSerializer

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
            #  'url',             
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
            #  'image_normal', 
            #   'image_small'
        ]
        read_only_fields = ['id','url', 'image_normal', 'image_small']   
   
   


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prison
        fields = ['id', 'name', 'latitude', 'longitude', 'type']






class LegalLibrarySerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()
    file_size = serializers.SerializerMethodField()

    class Meta:
        model = LegalLibrary
        fields = [
            'id', 
            'title', 
            'slug', 
            'short_description', 
            'summary', 
            'full_text', 
            'uploade_file', 
            'file_url',     
            'file_size',    
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def get_file_url(self, obj):
        if obj.uploade_file:
            request = self.context.get('request')
            if request is not None:
                return request.build_absolute_uri(obj.uploade_file.url)
            return obj.uploade_file.url
        return None

    def get_file_size(self, obj):
        if obj.uploade_file:
            try:
                size = obj.uploade_file.size
                return f"{round(size / (1024 * 1024), 2)} MB"
            except:
                return "0 MB"
        return "0 MB"

class LegalLibraryListSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = LegalLibrary
        fields = [
            'id', 
            'title', 
            'slug',
            'short_description', 
            'file_url', 
            'created_at'
        ]

    def get_file_url(self, obj):
        if obj.uploade_file:
            request = self.context.get('request')
            if request is not None:
                return request.build_absolute_uri(obj.uploade_file.url)
            return obj.uploade_file.url
        return None
    

from rest_framework import serializers

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryRating
        fields = ['category', 'score']


# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ['id', 'first_name', 'last_name']

import json
import cloudinary.uploader

class ReviewSerializer(serializers.ModelSerializer):
    user = PublicProfileSerializer(source='user.profile', read_only=True)
    categories = CategorySerializer(many=True, source='category_ratings')
    file = serializers.FileField(write_only=True, required=False, allow_null=True)
    review_file = serializers.URLField(read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'user', 'prison', 'comment', 'rating', 'created_at', 'categories', 'file', 'review_file']

    def to_internal_value(self, data):
        # multipart/form-data হলে categories ডাটা স্ট্রিং আকারে আসতে পারে, তা JSON এ কনভার্ট করা হচ্ছে
        if 'categories' in data and isinstance(data['categories'], str):
            try:
                mutable_data = data.copy() if hasattr(data, 'copy') else data.dict()
                mutable_data['categories'] = json.loads(data['categories'])
                data = mutable_data
            except json.JSONDecodeError:
                pass
        return super().to_internal_value(data)

    def create(self, validated_data):
        file = validated_data.pop('file', None)
        categories_data = validated_data.pop('category_ratings', []) 
        
        review_file_url = None
        if file:
            # Cloudinary-তে ফাইল আপলোড (এটি ইমেজ এবং পিডিএফ দুটোই রিসিভ করবে)
            upload_result = cloudinary.uploader.upload(
                file,
                resource_type="auto",  # auto দিলে ইমেজ এবং পিডিএফ উভয় ফাইলই হ্যান্ডেল করতে পারে
                folder="reviews/"
            )
            review_file_url = upload_result.get('secure_url')
            
        review = Review.objects.create(review_file=review_file_url, **validated_data)

        for cat in categories_data:
            CategoryRating.objects.create(review=review, **cat)

        return review

    
# class ReviewSerializer(serializers.ModelSerializer):
#     # user = PublicProfileSerializer(read_only=True)
#     user = PublicProfileSerializer(source='user.profile', read_only=True)
#     categories = CategorySerializer(many=True, source='category_ratings')
#     # categories = CategorySerializer(many=True)

#     class Meta:
#         model = Review
#         fields = ['id', 'user','prison', 'comment', 'rating', 'created_at', 'categories']

#     def create(self, validated_data):
#         categories_data = validated_data.pop('categories')
#         review = Review.objects.create(**validated_data)

#         for cat in categories_data:
#             CategoryRating.objects.create(review=review, **cat)

#         return review