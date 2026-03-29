from django.db import models

# Create your models here.
import os
from django.db import models
from ckeditor_uploader.fields import RichTextUploadingField

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