from django.urls import path
from .views import CaseSubmissionListCreateAPIView, CaseDetailAPIView

urlpatterns = [
    path('cases/', CaseSubmissionListCreateAPIView.as_view(), name='case-list-create'),
    path('cases/<int:pk>/', CaseDetailAPIView.as_view(), name='case-detail'),
]