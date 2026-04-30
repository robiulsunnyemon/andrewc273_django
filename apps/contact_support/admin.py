from django.contrib import admin
from unfold.admin import ModelAdmin
# Register your models here.
from .models import ContactUs
@admin.register(ContactUs)
class ContactUsAdmin(ModelAdmin):
    list_display = ('first_name', 'last_name', 'email','phone_number', 'subject',  'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('first_name', 'last_name', 'email', 'phone_number')