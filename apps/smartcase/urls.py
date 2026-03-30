from django.urls import path
from .views import (
AcceptedCaseDetailAPIView, CaseMediaSubmissionListAPIView, CaseSubmissionListCreateAPIView, CaseDetailAPIView, AIEnhanceTextView, AIAnalyzeLinkView, DownloadDocumentAPIView,UserCaseStatsView,AcceptedCaseListView
)
urlpatterns = [
    path('cases/', CaseSubmissionListCreateAPIView.as_view(), name='case-list-create'),
    path('cases/<int:pk>/', CaseDetailAPIView.as_view(), name='case-detail'),
    path('cases/enhance-text/', AIEnhanceTextView.as_view(), name='ai-enhance'),
    path('cases/analyze-link/', AIAnalyzeLinkView.as_view(), name='ai-analyze-link'),
    path('documents/download/<int:document_id>/', DownloadDocumentAPIView.as_view(), name='document-download'),
    path('cases/media/', CaseMediaSubmissionListAPIView.as_view(), name='case-media-list'),
    path('cases/stats/', UserCaseStatsView.as_view(), name='user-case-stats'),
    path('cases/accepted/', AcceptedCaseListView.as_view(), name='accepted-case-list'),
    path('cases/accepted/<int:pk>/', AcceptedCaseDetailAPIView.as_view(), name='accepted-case-detail'),

]
