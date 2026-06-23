from os import stat

from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from apps.smartcase.permissions import IsOwnerOrReadOnly
from .models import LegalForm,LegalLibrary, Prison,Review,CategoryRating

from .serializers import LegalFormListSerializer, LegalFormDetailSerializer,ReviewSerializer,CategorySerializer,LegalLibraryListSerializer, LegalLibrarySerializer, PrisonSerializer,LocationSerializer
from rest_framework import status
from rest_framework import filters
from rest_framework.generics import GenericAPIView
from django_filters.rest_framework import DjangoFilterBackend
from .utils import PrisonPagination
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from django.db.models import Avg




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

# class PrisonListView(GenericAPIView):
#     queryset = Prison.objects.all().order_by("id")
#     serializer_class = PrisonSerializer
#     pagination_class = PrisonPagination

#     filter_backends = [
#         filters.SearchFilter,
#         filters.OrderingFilter,
#         DjangoFilterBackend,
#     ]

#     search_fields = [
#         "name",
#         "city",
#         "state",
#         "code",
#         "region",
#     ]

#     filterset_fields = [
#         "state",
#         "city",
#         "gender",
#         "security_level",
#         "type",
#     ]

#     ordering_fields = ["name", "city", "state", "id"]

#     def get(self, request, *args, **kwargs):

#         queryset = self.filter_queryset(self.get_queryset())
#         page = self.paginate_queryset(queryset)
#         if page is not None:
#             serializer = self.get_serializer(page, many=True)
#             return self.get_paginated_response(serializer.data)
#         serializer = self.get_serializer(queryset, many=True)
#         return Response(serializer.data)




class PrisonListView(ListAPIView): 
    serializer_class = PrisonSerializer
    pagination_class = PrisonPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    
    filterset_fields = ["state", "city", "gender", "security_level", "type"]
    ordering_fields = ["name", "city", "state", "id"]

    def get_queryset(self):
        queryset = Prison.objects.all().order_by("id")
        search_query = self.request.query_params.get('search', None)
        category = self.request.query_params.get('category', None)

        if category == 'halfway_house':
            queryset = queryset.filter(type='HALFWAY_HOUSE')
        elif category == 'prison':
            queryset = queryset.exclude(type='HALFWAY_HOUSE')
        
        if search_query:
            queryset = queryset.filter(name_display__istartswith=search_query)
            
        return queryset

# class PrisonDetailView(RetrieveAPIView):
#     queryset = Prison.objects.all()
#     serializer_class = PrisonSerializer

# from django.db.models import Q
# from rest_framework.generics import ListAPIView, RetrieveAPIView
# from rest_framework import filters
# from django_filters.rest_framework import DjangoFilterBackend
# from django.shortcuts import get_object_or_404
# from rest_framework.response import Response
# from .models import Prison
# from .serializers import PrisonSerializer
# from .utils import PrisonPagination

# class PrisonListView(ListAPIView):
#     serializer_class = PrisonSerializer
#     pagination_class = PrisonPagination
#     filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    
#     filterset_fields = ["state", "city", "gender", "security_level", "type"]
#     ordering_fields = ["name", "city", "state", "id"]

#     def get_queryset(self):
#         queryset = Prison.objects.all().order_by("id")
#         search_query = self.request.query_params.get('search', None)
        
#         if search_query:
#             val = search_query.lower().strip()

#             # 
#             state_mapping = {
#                 "alabama": "AL", "alaska": "AK", "arizona": "AZ", "arkansas": "AR",
#                 "california": "CA", "colorado": "CO", "connecticut": "CT", "delaware": "DE",
#                 "florida": "FL", "georgia": "GA", "hawaii": "HI", "idaho": "ID",
#                 "illinois": "IL", "indiana": "IN", "iowa": "IA", "kansas": "KS",
#                 "kentucky": "KY", "louisiana": "LA", "maine": "ME", "maryland": "MD",
#                 "massachusetts": "MA", "michigan": "MI", "minnesota": "MN", "mississippi": "MS",
#                 "missouri": "MO", "montana": "MT", "nebraska": "NE", "nevada": "NV",
#                 "new hampshire": "NH", "new jersey": "NJ", "new mexico": "NM", "new york": "NY",
#                 "north carolina": "NC", "north dakota": "ND", "ohio": "OH", "oklahoma": "OK",
#                 "oregon": "OR", "pennsylvania": "PA", "rhode island": "RI", "south carolina": "SC",
#                 "south dakota": "SD", "tennessee": "TN", "texas": "TX", "utah": "UT",
#                 "vermont": "VT", "virginia": "VA", "washington": "WA", "west virginia": "WV",
#                 "wisconsin": "WI", "wyoming": "WY"
#             }

            
#             mapped_state_code = state_mapping.get(val)

#             if mapped_state_code:
                
#                 queryset = queryset.filter(state__iexact=mapped_state_code)
#             else:
                
#                 queryset = queryset.filter(
#                     Q(state__iexact=search_query) | 
#                     Q(name_display__istartswith=search_query)
#                 )
            
#         return queryset

# class PrisonDetailView(RetrieveAPIView):
#     queryset = Prison.objects.all()
#     serializer_class = PrisonSerializer
#     lookup_field = "pk"
# #prison detail view

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
    #     return Response(serializer.data)  ````
    


class LocationListView(APIView):
    def get(self, request):
        category = request.query_params.get('category', None)
        queryset = Prison.objects.all()
        if category == 'halfway_house':
            queryset = queryset.filter(type='HALFWAY_HOUSE')
        elif category == 'prison':
            queryset = queryset.exclude(type='HALFWAY_HOUSE')
            
        serializer = LocationSerializer(queryset, many=True)
        return Response(serializer.data)
    





class PrisonRetingDetailView(APIView):
    def get(self, request, pk):
        prison = Prison.objects.get(pk=pk)

        reviews = Review.objects.filter(prison=prison)
        review_data = ReviewSerializer(reviews, many=True).data

        avg_rating = reviews.aggregate(avg=Avg('rating'))['avg']

        category_avg = CategoryRating.objects.filter(review__prison=prison) \
            .values('category') \
            .annotate(avg=Avg('score'))

        return Response({
            "prison": {
                "id": prison.id,
                "name": prison.name,
                "location": prison.address,
                "latitude": prison.latitude,
                "longitude": prison.longitude
            },
            "average_rating": avg_rating,
            "category_breakdown": list(category_avg),
            "reviews": review_data
        })


class CreateReviewView(APIView):
    permission_classes = [IsOwnerOrReadOnly]


    def get(self, request):
       
        prison_id = request.query_params.get('prison_id')
        
        if prison_id:
            
            reviews = Review.objects.filter(prison_id=prison_id).order_by('-created_at')
        else:
           
            reviews = Review.objects.all().order_by('-created_at')

        serializer = ReviewSerializer(reviews, many=True, context={'request': request})
        
        return Response({
            "success": True,
            "message": "Reviews retrieved successfully.",
            "data": {
                "reviews": serializer.data
            }
        }, status=status.HTTP_200_OK)
    
    def post(self, request):
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)