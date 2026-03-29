from django.urls import path
from .views import FAQListView, LegalDocumentDetailView

urlpatterns = [
    path('legal/<str:slug>/', LegalDocumentDetailView.as_view()),
    path('faqs/', FAQListView.as_view()),

    #path('policy/', PolicyDetailView.as_view()),
]