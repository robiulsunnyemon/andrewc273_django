
import os

from django.utils import timezone

from ckeditor.fields import RichTextField
from django.db import models
# Create your models here.

class CaseSubmission(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    )
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='cases', null=True, blank=True)
    case_title = models.CharField(max_length=255)
    case_number = models.CharField(max_length=100, unique=True)
    author = models.CharField(max_length=255, blank=True, null=True)
    press_release = models.TextField(blank=True, null=True,)
    press_release_enhanced = models.TextField(blank=True, null=True, help_text="Polished version by AI")
    #key_legal_arguments = RichTextField(blank=True, null=True, help_text="Key legal arguments extracted by AI")
    state = models.CharField(max_length=100)
    federal_district = models.CharField(max_length=255, blank=True, null=True)
    court_type = models.CharField(max_length=100, blank=True, null=True)
    case_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    accepted_at = models.DateTimeField(null=True, blank=True, help_text="Timestamp when the case was accepted")
    #link analysis
    external_link = models.URLField(max_length=500, blank=True, null=True, help_text="User pastes doc link here")
    ai_analysis_summary = models.TextField(blank=True, null=True, help_text="Summary generated from the link/file")

    is_anonymous = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.case_title
    
    def save(self, *args, **kwargs):
        
        if self.case_status == 'accepted' and not self.accepted_at:
            self.accepted_at = timezone.now()

        elif self.case_status != 'accepted':
            self.accepted_at = None
            
        super().save(*args, **kwargs)


class CaseDocument(models.Model):
    case = models.ForeignKey(CaseSubmission, related_name='documents', on_delete=models.CASCADE)
    file = models.FileField(upload_to='cases/documents/')
    title = models.CharField(max_length=255, blank=True, null=True)
    document_type = models.CharField(max_length=10, blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.file:
            file_name, file_extension = os.path.splitext(self.file.name)
            if not self.title:
                self.title = file_name
            self.document_type = file_extension.lower().replace('.', '')
            
        super(CaseDocument, self).save(*args, **kwargs)

    


    def __str__(self):
        return f"{self.title} ({self.document_type})"

class LegalArgument(models.Model):
    case = models.ForeignKey(CaseSubmission, related_name='legal_arguments', on_delete=models.CASCADE)
    title = models.CharField(max_length=255, blank=True, null=True)
    content = models.TextField(blank=True, null=True)              

    def __str__(self):
        return f"{self.title} - {self.case.case_title}"