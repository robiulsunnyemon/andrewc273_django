from django.urls import path
from .views import LegalFormListView, LegalFormDetailView, LegalLibraryDetailView, LegalLibraryListView, LocationListView, PrisonListView, PrisonDetailView

urlpatterns = [
    
    path('legal-forms/', LegalFormListView.as_view(), name='form-list'),
    path('legal-forms/<int:pk>/', LegalFormDetailView.as_view(), name='form-detail'),

    path("prisons/", PrisonListView.as_view()),
    path("prisons/<int:pk>/", PrisonDetailView.as_view()),

    path('legal-library/', LegalLibraryListView.as_view(), name='library-list'),
    path('legal-library/<int:pk>/', LegalLibraryDetailView.as_view(), name='library-detail'),
    path('api/locations/', LocationListView.as_view(), name='location-list'),
]