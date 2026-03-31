from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import LegalForm, FormFile

# 
class FormFileInline(admin.TabularInline):
    model = FormFile
    extra = 2 # ডিফল্টভাবে ১টি খালি ফাইল আপলোডের ঘর দেখাবে
    fields = ('file_name', 'pdf_file') # কোন ফিল্ডগুলো দেখাবে

@admin.register(LegalForm)
class LegalFormAdmin(admin.ModelAdmin):
    
    list_display = ('id', 'title', 'slug', 'last_updated')

    prepopulated_fields = {'slug': ('title',)} 
    inlines = [FormFileInline]
    
    search_fields = ('title', 'content')
    
    
    inlines = [FormFileInline]

    # CKEditor 
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug'),
        }),
        ('Detailed Content', {
            'description': "Use CKEditor to format the body text (Overview, Requirements, etc.)",
            'fields': ('content',),
        }),
    )


# admin.site.register(FormFile)