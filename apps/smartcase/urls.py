from django.urls import path
from .views import (
AcceptedCaseDetailAPIView, AuthorProfileView, CaseMediaSubmissionListAPIView, PodcastStoryView, StoryDetailView, StoryView,CaseSubmissionListCreateAPIView, CaseDetailAPIView, AIEnhanceTextView, AIAnalyzeLinkView, DownloadDocumentAPIView,UserCaseStatsView,AcceptedCaseListView,PublicStatsView
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
    # urls.py
    path('author-profile/<int:user_id>/', AuthorProfileView.as_view(), name='author-profile'),
    path('public-stats/', PublicStatsView.as_view(), name='public-stats'),
    path('stories/', StoryView.as_view(), name='stories'),
    path('stories/<int:pk>/', StoryDetailView.as_view(), name='story-detail'),
    path('podcast-stories/', PodcastStoryView.as_view(), name='podcast-stories'),

]
