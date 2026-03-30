from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import ContactUs
from .serializers import ContactUsSerializer
from rest_framework.permissions import AllowAny

class ContactUsList(APIView):
    permission_classes = [AllowAny]
    # Ekhane queryset thakleo APIView nije theke eita use korbe na
    queryset = ContactUs.objects.all() 

    # def get(self, request, *args, **kwargs):
    #     contact_us_messages = ContactUs.objects.all()
    #     serializer = ContactUsSerializer(contact_us_messages, many=True)
    #     response_data = {
    #         "success": True,
    #         "status": status.HTTP_200_OK,
    #         "message": "Contact Us messages retrieved successfully",
    #         "data": serializer.data,
    #     }
    #     return Response(response_data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = ContactUsSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            response_data = {
                "success": True,
                "status": status.HTTP_201_CREATED,
                "message": "Contact Us message created successfully",
                "data": serializer.data,
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)