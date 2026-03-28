# from django.contrib import admin

# from django.contrib import admin
# from .models import Page, PageSection
# from apps.cms.models import  Page,PageSection

# Register your models here.

from unfold.admin import ModelAdmin
from django.contrib import admin
from .models import LegalDocument

@admin.register(LegalDocument)
class LegalDocumentAdmin(ModelAdmin):
   
    list_display = ('title', 'slug', 'version', 'last_updated')
    
    
    search_fields = ('title', 'slug')
    
    list_filter = ('slug', 'version')

   
# @admin.register(Page)
# class PageAdmin(ModelAdmin):
#     list_display = ('title', 'type', 'version', 'status')
#     list_filter = ('type', 'status')
#     # inlines = [PageSectionInline]

# @admin.register(PageSection)
# class PageSectionAdmin(ModelAdmin):
#     list_display = ('page', 'order', 'title', 'description')