from django.db import models

# Create your models here.
import os
from django.db import models
from ckeditor_uploader.fields import RichTextUploadingField
from ckeditor.fields import RichTextField

class LegalForm(models.Model):
    title = models.CharField(max_length=255) 
    slug = models.SlugField(unique=True) 
    short_description = models.CharField(max_length=500, blank=True,null=True)
    content = RichTextUploadingField(config_name='default')
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class FormFile(models.Model):
    legal_form = models.ForeignKey(LegalForm, related_name='files', on_delete=models.CASCADE)
    file_name = models.CharField(max_length=255) # 
    pdf_file = models.FileField(upload_to='legal/pdfs/', blank=True, null=True) #

    @property
    def file_size(self):
        if self.pdf_file and os.path.exists(self.pdf_file.path):
            size = self.pdf_file.size
            return f"{round(size / (1024 * 1024), 2)} MB"
        return "0 MB"
    

class LegalLibrary(models.Model):
    title = models.CharField(max_length=255) 
    slug = models.SlugField(unique=True) 
    short_description = models.CharField(max_length=500, blank=True,null=True)
    summary = models.TextField(blank=True, null=True)
    full_text = RichTextField(config_name='default')
    uploade_file = models.FileField(upload_to='legal/library_files/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title



class Prison(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=255)
    name_title = models.CharField(max_length=255, null=True, blank=True)
    name_display = models.CharField(max_length=255, null=True, blank=True)

    type = models.CharField(max_length=50, null=True, blank=True)
    security_level = models.CharField(max_length=50, null=True, blank=True)
    region = models.CharField(max_length=100, null=True, blank=True)

    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    url = models.CharField(max_length=255, null=True, blank=True)




    
    time_zone = models.CharField(max_length=10, null=True, blank=True)

    address = models.TextField(null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=50, null=True, blank=True)
    zip_code = models.CharField(max_length=20, null=True, blank=True)

    phone_number = models.CharField(max_length=50, null=True, blank=True)
    contact_email = models.EmailField(null=True, blank=True)

    gender = models.CharField(max_length=20, null=True, blank=True)
    facl_type_description = models.CharField(max_length=255, null=True, blank=True)

    has_camp = models.BooleanField(default=False)
    has_fsl = models.BooleanField(default=False)
    has_fdc = models.BooleanField(default=False)
    has_sff = models.BooleanField(default=False)
    has_ihp = models.BooleanField(default=False)

    image_normal = models.CharField(max_length=255, null=True, blank=True)
    image_small = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.code})"