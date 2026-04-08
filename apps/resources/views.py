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
    
    

from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import filters

from django_filters.rest_framework import DjangoFilterBackend

from .models import Prison
from .serializers import PrisonSerializer
from .utils import PrisonPagination


class PrisonListView(GenericAPIView):
    queryset = Prison.objects.all().order_by("id")
    serializer_class = PrisonSerializer
    pagination_class = PrisonPagination

    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter,
        DjangoFilterBackend,
    ]

    search_fields = [
        "name",
        "city",
        "state",
        "code",
        "region",
    ]

    filterset_fields = [
        "state",
        "city",
        "gender",
        "security_level",
        "type",
    ]

    ordering_fields = ["name", "city", "state", "id"]

    def get(self, request, *args, **kwargs):
        # first, we filter the queryset based on the search, filter, and ordering parameters
        queryset = self.filter_queryset(self.get_queryset())

        # then we paginate the filtered queryset
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            # return paginated response with metadata (like total count, next/previous links, etc.)
            return self.get_paginated_response(serializer.data)

        # if no pagination is applied (for displaying all data at once)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    



class PrisonDetailView(GenericAPIView):
    queryset = Prison.objects.all()
    serializer_class = PrisonSerializer

    def get(self, request, pk):
        prison = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = self.get_serializer(prison)
        return Response(serializer.data)