from django.urls import path
from .views import LegalFormListView, LegalFormDetailView

urlpatterns = [
    
    path('legal-forms/', LegalFormListView.as_view(), name='form-list'),
    
    path('legal-forms/<int:pk>/', LegalFormDetailView.as_view(), name='form-detail'),
]