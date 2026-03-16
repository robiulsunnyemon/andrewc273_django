from django.db import models

# Create your models here.

class CaseSubmission(models.Model):
    case_title = models.CharField(max_length=255)
    case_number = models.CharField(max_length=100, unique=True)
    author = models.CharField(max_length=255, blank=True, null=True)
    press_release = models.TextField()
    press_release_enhanced = models.TextField(blank=True, null=True, help_text="Polished version by AI")
    state = models.CharField(max_length=100)
    federal_district = models.CharField(max_length=255, blank=True, null=True)
    court_type = models.CharField(max_length=100, blank=True, null=True)
    #link analysis
    external_link = models.URLField(max_length=500, blank=True, null=True, help_text="User pastes doc link here")
    ai_analysis_summary = models.TextField(blank=True, null=True, help_text="Summary generated from the link/file")

    is_anonymous = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.case_title


class CaseDocument(models.Model):
    case = models.ForeignKey(CaseSubmission, related_name='documents', on_delete=models.CASCADE)
    file = models.FileField(upload_to='cases/documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)