from django.shortcuts import get_object_or_404, render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Room, Message, UserStatus
from .serializers import RoomSerializer, MessageSerializer, RoomDetailSerializer, User
from django.db.models import Q
from rest_framework.permissions import IsAuthenticated


class RoomListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        
        rooms = Room.objects.filter(
            Q(user_1=request.user) | Q(user_2=request.user)
        ).order_by('-updated_at')
        serializer = RoomSerializer(rooms, many=True)
        return Response(serializer.data)

    def post(self, request):
        user_2_id = request.data.get("other_user_id") or request.data.get("user_2")
        
        if not user_2_id:
            return Response({"error": "Target user ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        user_1 = request.user
        user_2 = get_object_or_404(User, id=user_2_id)


        room = Room.objects.filter(
            (Q(user_1=user_1) & Q(user_2=user_2)) | 
            (Q(user_1=user_2) & Q(user_2=user_1))
        ).first()

        if room:
            serializer = RoomSerializer(room)
            return Response(serializer.data, status=status.HTTP_200_OK)

        ids = sorted([user_1.id, user_2.id])
        room = Room.objects.create(user_1_id=ids[0], user_2_id=ids[1])
        
        serializer = RoomSerializer(room)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
class RoomDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        room = get_object_or_404(Room, id=id)
        
        if request.user != room.user_1 and request.user != room.user_2:
            return Response({"detail": "You do not have permission to view this room."},
                            status=status.HTTP_403_FORBIDDEN)
        
        serializer = RoomDetailSerializer(room)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
