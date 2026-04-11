from django.contrib import admin

from apps.smartcase.models import CaseDocument, CaseSubmission
from unfold.admin import ModelAdmin
# Register your models here.
@admin.register(CaseSubmission)
class CaseSubmissionAdmin(ModelAdmin):
    list_display = ('id', 'user', 'case_title', 'case_number', 'case_status', 'author', 'state','press_release_enhanced','ai_analysis_summary','created_at')
    search_fields = ('case_title', 'case_number', 'author', 'state','case_status')
    readonly_fields = ('accepted_at',)

@admin.register(CaseDocument)
class CaseDocumentAdmin(ModelAdmin):
    list_display = ('case', 'file', 'uploaded_at')
    search_fields = ('case__case_title', 'file')