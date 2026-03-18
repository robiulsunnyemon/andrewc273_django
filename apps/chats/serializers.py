from rest_framework import serializers
from .models import Room, Message, UserStatus
from django.contrib.auth import get_user_model

User = get_user_model()



class UserStatusSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)


    class Meta:
        model = UserStatus
        fields = ['id', 'email', 'manual_status','auto_status','last_seen','is_online']

class UserSerializer(serializers.ModelSerializer):
    name=serializers.CharField(source='profile.name', read_only=True)
    avatar=serializers.ImageField(source='profile.avatar', read_only=True)
    is_online = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'name', 'avatar', 'email','is_online']

    def get_is_online(self, obj):
        try:
            
            return obj.status.is_online 
        except:
           
            return False

class MessageSerializer(serializers.ModelSerializer):
    # sender_name = serializers.ReadOnlyField(source='sender.username')

    class Meta:
        model = Message
        fields = ['id', 'room', 'sender',  'content', 'file']
        read_only_fields = ['sender', 'created_at', 'is_read']
# class MessageSerializer(serializers.ModelSerializer):
#     receiver = serializers.SerializerMethodField()
#     sender_name = serializers.ReadOnlyField(source='sender.profile.name')

#     class Meta:
#         model = Message
#         fields = ['id', 'room', 'sender', 'sender_name', 'receiver', 'content', 'file', 'is_read', 'created_at']
#         read_only_fields = ['sender', 'created_at', 'is_read']

#     def get_receiver(self, obj):
        
#         room = obj.room
#         if obj.sender == room.user_1:
#             receiver = room.user_2
#         else:
#             receiver = room.user_1
    
#         return UserSerializer(receiver).data
    
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