from django.urls import path
from .views import (
CaseSubmissionListCreateAPIView, CaseDetailAPIView, AIEnhanceTextView, AIAnalyzeLinkView, DownloadDocumentAPIView
)
urlpatterns = [
    path('cases/', CaseSubmissionListCreateAPIView.as_view(), name='case-list-create'),
    path('cases/<int:pk>/', CaseDetailAPIView.as_view(), name='case-detail'),
    path('cases/enhance-text/', AIEnhanceTextView.as_view(), name='ai-enhance'),
    path('cases/analyze-link/', AIAnalyzeLinkView.as_view(), name='ai-analyze-link'),
    path('documents/download/<int:document_id>/', DownloadDocumentAPIView.as_view(), name='document-download'),
]
