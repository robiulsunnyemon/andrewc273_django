from rest_framework import serializers
from .models import ContactUs

class ContactUsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactUs
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'subject', 'message', 'is_read', 'created_at', 'updated_at']
        read_only_fields = ['is_read', 'created_at', 'updated_at']