from django.db import models
from ckeditor.fields import RichTextField

class LegalDocument(models.Model):
    DOCUMENT_TYPES = (
        ('privacy_policy', 'Privacy Policy'),
        ('terms_conditions', 'Terms and Conditions'),
    )
    

    title = models.CharField(max_length=255) 
    
    
    slug = models.CharField(max_length=50, choices=DOCUMENT_TYPES, unique=True)
    
    content = RichTextField(config_name='default')
    version = models.CharField(max_length=10, default="1.0.0")
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

