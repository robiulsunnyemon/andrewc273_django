from django.urls import path
from .views import *

urlpatterns = [
    # example endpoint
    path("rooms/", RoomListCreateView.as_view(), name="rooms"),
    path("rooms/<int:id>/", RoomDetailView.as_view(), name="room-detail"),
]