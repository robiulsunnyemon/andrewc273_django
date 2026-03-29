from django.shortcuts import render


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import FAQ, LegalDocument
from .serializers import FAQSerializer, LegalDocumentSerializer
from django.shortcuts import get_object_or_404

class LegalDocumentDetailView(APIView):
    """
    slug (privacy_policy বা terms_conditions) 
    
    """
    
    def get(self, request, slug, format=None):
       
        document = get_object_or_404(LegalDocument, slug=slug)
        
        
        serializer = LegalDocumentSerializer(document)
        
       
        return Response(
            {
                "status": "success",
                "data": serializer.data
            }, 
            status=status.HTTP_200_OK
        )

class FAQListView(APIView):
    def get(self, request, format=None):
        faqs = FAQ.objects.filter(is_active=True).order_by('order')
        serializer = FAQSerializer(faqs, many=True)
        return Response({
            "status": "success",
            "count": faqs.count(),
            "data": serializer.data
        }, status=status.HTTP_200_OK)