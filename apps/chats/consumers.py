import json
import base64
import uuid
from django.core.files.base import ContentFile
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Room, Message

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_text = data.get('message', '')
        file_data = data.get('file', None) # Base64 encoded file data
        file_name = data.get('file_name', 'file.jpg') # Default file name if not provided
        sender = self.scope['user']

        # database save 
        saved_msg = await self.save_message(sender, message_text, file_data, file_name)

        # group send
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message_text,
                'file_url': saved_msg.file.url if saved_msg.file else None,
                'sender_id': sender.id
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def save_message(self, sender, content, file_data=None, file_name=None):
        room = Room.objects.get(id=self.room_id)
        file_obj = None

        # convert base64 file data to Django file object
        if file_data:
            format, imgstr = file_data.split(';base64,') 
            ext = format.split('/')[-1] 
            file_obj = ContentFile(base64.b64decode(imgstr), name=f"{uuid.uuid4()}.{ext}")

        # create message
        msg = Message.objects.create(
            room=room, 
            sender=sender, 
            content=content, 
            file=file_obj
        )
        
        # update last message in room
        room.last_message = content if content else "Sent a file"
        room.save()
        return msg