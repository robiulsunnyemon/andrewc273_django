from rest_framework import serializers
from .models import Room, Message, UserStatus
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email']

class MessageSerializer(serializers.ModelSerializer):
    # sender_name = serializers.ReadOnlyField(source='sender.username')

    class Meta:
        model = Message
        fields = ['id', 'room', 'sender',  'content', 'file']
        read_only_fields = ['sender', 'created_at', 'is_read']

class RoomSerializer(serializers.ModelSerializer):
    user_1 = UserSerializer()
    user_2 = UserSerializer()

    class Meta:
        model = Room
        fields = ['id', 'user_1', 'user_2', 'last_message', 'updated_at']

class RoomDetailSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Room
        fields = ['id', 'user_1', 'user_2', 'messages','last_message', 'updated_at']