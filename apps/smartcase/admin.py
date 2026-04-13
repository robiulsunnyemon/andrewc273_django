from django.contrib import admin

from apps.smartcase.models import CaseDocument, CaseSubmission, LegalArgument
from unfold.admin import ModelAdmin, TabularInline
# Register your models here.

class LegalArgumentInline(TabularInline):
    model = LegalArgument
    extra = 1
    fields = ('title', 'description')

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