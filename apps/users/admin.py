from django.contrib import admin
from .models import User, Profile
from unfold.admin import ModelAdmin
# Register your models here.

@admin.register(User)
class CustomAdminClass(ModelAdmin):
        list_display = ('id','email', 'is_staff', 'is_active', 'date_joined')
        search_fields = ('email',)
        
        list_filter = ('is_staff', 'is_active')
    # pass



@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'has_podcast_story', 'total_posts', 'total_letters']
    list_editable = ['has_podcast_story'] # Make has_podcast_story editable in the list view
    search_fields = ['user__email', 'name']