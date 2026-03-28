from django.urls import path
from .views import LegalFormListView, LegalFormDetailView

urlpatterns = [
    # লিস্ট API: /api/v1/legal-forms/
    path('legal-forms/', LegalFormListView.as_view(), name='form-list'),
    
    # আইডি ভিত্তিক ডিটেইল API: /api/v1/legal-forms/1/ (এখানে ১ হলো আইডি)
    path('legal-forms/<int:pk>/', LegalFormDetailView.as_view(), name='form-detail'),
]