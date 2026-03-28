from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import LegalForm, FormFile

# এই ক্লাসটি ব্যবহার করলে মেইন ফর্মের ভেতরেই ফাইল আপলোডের অপশন আসবে
class FormFileInline(admin.TabularInline):
    model = FormFile
    extra = 1  # ডিফল্টভাবে ১টি খালি ফাইল আপলোডের ঘর দেখাবে
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
            'fields': ('title', 'slug', 'content'),
        }),
        ('Detailed Content', {
            'description': "Use CKEditor to format the body text (Overview, Requirements, etc.)",
            'fields': ('content',),
        }),
    )


# admin.site.register(FormFile)