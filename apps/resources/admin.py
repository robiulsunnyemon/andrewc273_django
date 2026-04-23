from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import LegalForm, FormFile, LegalLibrary,Prison
from unfold.admin import ModelAdmin
# 
class FormFileInline(admin.TabularInline):
    model = FormFile
    extra = 2 # default 
    fields = ('file_name', 'pdf_file') # displayed fields in the inline form

@admin.register(LegalForm)
class LegalFormAdmin(ModelAdmin):
    
    list_display = ('id', 'title', 'slug','short_description', 'last_updated')

    prepopulated_fields = {'slug': ('title',)} 
    inlines = [FormFileInline]
    
    search_fields = ('title', 'content')
    
    
    inlines = [FormFileInline]

    # CKEditor 
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug','short_description'),
        }),
        ('Detailed Content', {
            'description': "Use CKEditor to format the body text (Overview, Requirements, etc.)",
            'fields': ('content',),
        }),
    )


# admin.site.register(FormFile)

#prison

@admin.register(Prison)
class PrisonAdmin(ModelAdmin):
    list_display = ('code', 'name', 'city', 'state', 'security_level')
    search_fields = ('name', 'city', 'state')


#legal library

@admin.register(LegalLibrary)
class LegalLibraryAdmin(ModelAdmin):
    list_display = ('title', 'slug', 'created_at')
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title',)