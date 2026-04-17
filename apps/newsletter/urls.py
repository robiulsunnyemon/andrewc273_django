from django.urls import path
from .views import SubscribeAPIView

urlpatterns = [
    path('newsletter/subscribe/', SubscribeAPIView.as_view(), name='subscribe'),
]