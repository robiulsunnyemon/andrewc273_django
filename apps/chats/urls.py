from django.urls import path
from .views import *

urlpatterns = [
    # example endpoint
    path("rooms/", RoomListCreateView.as_view(), name="rooms"),
    path("rooms/<int:id>/", RoomDetailView.as_view(), name="room-detail"),

    path('status/', UserStatusView.as_view(), name='my-status'),
    path('status/<int:user_id>/', UserStatusView.as_view(), name='user-status'),
]