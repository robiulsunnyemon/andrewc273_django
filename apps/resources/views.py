from os import stat

from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import LegalForm
from .serializers import LegalFormListSerializer, LegalFormDetailSerializer
from rest_framework import status


class LegalFormListView(APIView):
    def get(self, request):
       
        forms = LegalForm.objects.all().order_by('-id') 
        
        serializer = LegalFormListSerializer(forms, many=True, context={'request': request})
        
      
        return Response({
            "status": "success",
            "count": forms.count(),
            "data": serializer.data
        }, status=status.HTTP_200_OK)


class LegalFormDetailView(APIView):
    
    def get(self, request, pk):
      
        form = get_object_or_404(LegalForm, pk=pk)
        
        serializer = LegalFormDetailSerializer(form, context={'request': request})
        
        return Response({
            "status": "success",
            "data": serializer.data
        }, status=status.HTTP_200_OK)