from django.urls import path
from . import consumers  

websocket_urlpatterns = [
    # URL: ws://127.0.0.1:8000/ws/chat/ROOM_ID/
    
    path('ws/chat/<int:room_id>/', consumers.ChatConsumer.as_asgi()),
]