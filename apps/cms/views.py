from django.shortcuts import render


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import LegalDocument
from .serializers import LegalDocumentSerializer
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
