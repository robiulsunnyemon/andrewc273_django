from django.contrib import admin

from apps.smartcase.models import CaseDocument, CaseSubmission, LegalArgument, PodcastStory,Story, StoryFile
from unfold.admin import ModelAdmin, TabularInline
from django.utils.html import format_html
# Register your models here.

class LegalArgumentInline(TabularInline):
    model = LegalArgument
    extra = 1
    fields = ('title', 'content')

# 
class CaseDocumentInline(TabularInline):
    model = CaseDocument
    extra = 1
@admin.register(CaseSubmission)
class CaseSubmissionAdmin(ModelAdmin):
    list_display = ('id', 'user', 'case_title', 'case_number', 'case_status', 'author', 'state','press_release_enhanced','ai_analysis_summary','created_at')
    search_fields = ('case_title', 'case_number', 'author', 'state','case_status')
    readonly_fields = ('accepted_at',)
    inlines = [LegalArgumentInline, CaseDocumentInline]

@admin.register(CaseDocument)
class CaseDocumentAdmin(ModelAdmin):
    list_display = ('case', 'file', 'uploaded_at')
    search_fields = ('case__case_title', 'file')








class StoryFileReadOnlyInline(admin.TabularInline):
    model = StoryFile
    extra = 0 
    readonly_fields = ('file', 'uploaded_at', 'download_link')
    can_delete = False

    def download_link(self, obj):
        if obj.file:
            return format_html(
                '<a href="{}" download>Download</a>',
                obj.file.url
            )
        return "-"

    download_link.short_description = "Download"

@admin.register(Story)
class StoryAdmin(ModelAdmin):
    
    list_display = ('id', 'title', 'is_featured',  'created_at')
    
    list_editable = ('is_featured', )
    
    list_filter = ('is_featured', 'created_at')
    search_fields = ('title', 'author_name')
    inlines = [StoryFileReadOnlyInline]

    def has_add_permission(self, request, obj=None):
    
        return True

@admin.register(PodcastStory)
class PodcastStoryAdmin(ModelAdmin):
    list_display = ('id', 'title','created_at')
    search_fields = ('title',)
    list_filter = ('created_at',)
