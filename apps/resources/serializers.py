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
        fields = ['name', 'latitude', 'longitude']






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

class ReviewSerializer(serializers.ModelSerializer):
    user = PublicProfileSerializer(source='user.profile', read_only=True)
    # এখানে source='category_ratings' দেওয়ার কারণে validated_data-তে এই নামেই ডাটা থাকবে
    categories = CategorySerializer(many=True, source='category_ratings')

    class Meta:
        model = Review
        fields = ['id', 'user', 'prison', 'comment', 'rating', 'created_at', 'categories']

    def create(self, validated_data):
        # 'categories' এর বদলে 'category_ratings' পপ করুন
        categories_data = validated_data.pop('category_ratings', []) 
        
        # রিভিউ তৈরি করুন
        review = Review.objects.create(**validated_data)

        # ক্যাটাগরি রেটিংগুলো সেভ করুন
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