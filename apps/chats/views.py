from django.shortcuts import get_object_or_404, render

# Create your views here.
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Room, Message, UserStatus
from .serializers import RoomSerializer, MessageSerializer, RoomDetailSerializer, User,UserStatusSerializer
from django.db.models import Q
from rest_framework.permissions import IsAuthenticated



class RoomListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        rooms = Room.objects.filter(
            Q(user_1=request.user) | Q(user_2=request.user)
        )
        serializer = RoomSerializer(rooms, many=True)
        return Response(serializer.data)

    def post(self, request):
        user_2_id = request.data.get("user_2")

        if not user_2_id:
            return Response(
                {"error": "user_2 is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user_1 = request.user
        try:
            user_2 = User.objects.get(id=user_2_id)
        except User.DoesNotExist:
            return Response(
                {"error": "User does not exist."},
                status=status.HTTP_404_NOT_FOUND
            )

        room = Room.objects.filter(
            Q(user_1=user_1, user_2=user_2) |
            Q(user_1=user_2, user_2=user_1)
        ).first()

        if room:
            serializer = RoomSerializer(room)
            return Response(serializer.data, status=status.HTTP_200_OK)

        room = Room.objects.create(user_1=user_1, user_2=user_2)
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


class UserStatusView(APIView):
    permission_classes = [IsAuthenticated]

   
    

    def get(self, request, user_id=None):
        if user_id:
            
            status_obj = UserStatus.objects.filter(user_id=user_id).first()
            if not status_obj:
                return Response({"error": "User status has not been initialized yet."}, status=404)
        else:
            
            status_obj, created = UserStatus.objects.get_or_create(user=request.user)
        
        serializer = UserStatusSerializer(status_obj)
        return Response(serializer.data)

 
    def patch(self, request):
        
        status_obj, created = UserStatus.objects.get_or_create(user=request.user)
        
       
        serializer = UserStatusSerializer(status_obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)