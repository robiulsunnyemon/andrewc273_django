from django.db import models

# Create your models here.
from django.contrib.auth import get_user_model

from apps.users.models import User


class UserStatus(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='status')
    is_online = models.BooleanField(default=False)
    last_seen = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} - {'Online' if self.is_online else 'Offline'}"

class Room(models.Model):
 
    user_1=models.ForeignKey(User, related_name='chat_user_1', on_delete=models.CASCADE)
    user_2=models.ForeignKey(User, related_name='chat_user_2', on_delete=models.CASCADE)

    last_message = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user_1', 'user_2')

    def __str__(self):
        return f"Chat between {self.user_1.email} and {self.user_2.email}"

    
class Message(models.Model):
    room = models.ForeignKey(Room, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    content = models.TextField(blank=True, null=True)
    file=models.FileField(upload_to='chat_files/', blank=True, null=True)
    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"From {self.sender.email} in Room {self.room.id}"