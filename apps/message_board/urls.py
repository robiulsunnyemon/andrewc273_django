from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PostViewSet

router = DefaultRouter()
router.register(r'message-board/posts', PostViewSet, basename='message-board-post')

urlpatterns = [
    path('', include(router.urls)),
]
