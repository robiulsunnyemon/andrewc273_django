from django.urls import path
from .views import LegalDocumentDetailView

urlpatterns = [
    path('legal/<str:slug>/', LegalDocumentDetailView.as_view()),

    #path('policy/', PolicyDetailView.as_view()),
]