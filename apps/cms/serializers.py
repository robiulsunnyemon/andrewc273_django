from rest_framework import serializers
# from .models import Page, PageSection



from .models import FAQ, LegalDocument

class LegalDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = LegalDocument
        fields = ['title', 'slug', 'content', 'version', 'last_updated']


class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = ['question', 'answer', 'order']


# class PageSectionSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = PageSection
#         fields = ['id', 'order', 'title', 'description']

# class PageSerializer(serializers.ModelSerializer):
#     sections = PageSectionSerializer(many=True, read_only=True)

#     class Meta:
#         model = Page
#         fields = ['id', 'title',  'version', 'sections']