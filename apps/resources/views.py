from os import stat

from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import LegalForm,LegalLibrary, Prison
from .serializers import LegalFormListSerializer, LegalFormDetailSerializer, LegalLibraryListSerializer, LegalLibrarySerializer, PrisonSerializer
from rest_framework import status
from rest_framework import filters
from rest_framework.generics import GenericAPIView
from django_filters.rest_framework import DjangoFilterBackend
from .utils import PrisonPagination

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
    
    
#prison list and detail view

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
    

#prison detail view

class PrisonDetailView(GenericAPIView):
    queryset = Prison.objects.all()
    serializer_class = PrisonSerializer

    def get(self, request, pk):
        prison = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = self.get_serializer(prison)
        return Response(serializer.data)
    





#legal library list and detail view
class LegalLibraryListView(GenericAPIView):
    queryset = LegalLibrary.objects.all().order_by("-created_at")
    serializer_class = LegalLibraryListSerializer
    pagination_class = PrisonPagination

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "short_description"]

    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            # context={'request': request} is important for generating absolute URLs for file fields
            serializer = self.get_serializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)
    
# legal library detail view

class LegalLibraryDetailView(GenericAPIView):
    queryset = LegalLibrary.objects.all()
    serializer_class = LegalLibrarySerializer

    def get(self, request, pk): 
        library = get_object_or_404(LegalLibrary, pk=pk)
        serializer = self.get_serializer(library, context={'request': request})
        return Response(serializer.data)

    # def get(self, request, slug):
    #     library = get_object_or_404(LegalLibrary, slug=slug)
    #     serializer = self.get_serializer(library, context={'request': request})
    #     return Response(serializer.data)
    
