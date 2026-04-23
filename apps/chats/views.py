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
from django.utils import timezone
from rest_framework.pagination import PageNumberPagination


class RoomListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    # def get(self, request):
    #     rooms = Room.objects.filter(
    #         Q(user_1=request.user) | Q(user_2=request.user)
    #     )
    #     serializer = RoomSerializer(rooms, many=True)
    #     return Response(serializer.data)
    def get(self, request):
        search_query = request.query_params.get("search", "").strip()

        rooms = Room.objects.filter(
            Q(user_1=request.user) | Q(user_2=request.user)
        )
        # rooms = Room.objects.all()

        if search_query:
            rooms = rooms.filter(
                Q(user_1__profile__name__icontains=search_query) |
                Q(user_2__profile__name__icontains=search_query) |
                Q(user_1__email__icontains=search_query) |
                Q(user_2__email__icontains=search_query)
            )

        # Pagination
        # paginator = PageNumberPagination()
        # paginator.page_size = 2  

        # paginated_rooms = paginator.paginate_queryset(rooms, request)
        # serializer = RoomSerializer(paginated_rooms, many=True)

        # return paginator.get_paginated_response(serializer.data)
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
    
    def delete(self, request):
        
        room_id = request.data.get("room_id") 
        if not room_id:
            return Response({"error": "room_id is required to delete."}, status=status.HTTP_400_BAD_REQUEST)
        room = get_object_or_404(Room, id=room_id)
        if room.user_1 == request.user or room.user_2 == request.user:
            room.delete()
            return Response({"message": "Room deleted successfully."}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "You do not have permission to delete this room."}, status=status.HTTP_403_FORBIDDEN)
    
class RoomDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        room = get_object_or_404(Room, id=id)
        
        if request.user != room.user_1 and request.user != room.user_2:
            return Response({"detail": "You do not have permission to view this room."},
                            status=status.HTTP_403_FORBIDDEN)
        messages_queryset = room.messages.all().order_by('-created_at')

        # 3. Setup Pagination
        paginator = PageNumberPagination()
        paginator.page_size = 10  # As per your original request
        
        paginated_messages = paginator.paginate_queryset(messages_queryset, request)
        
        # 4. Serialize
        # Serialize the room info (without the 'messages' field to avoid double loading)
        room_data = RoomSerializer(room).data
        # Serialize only the current page of messages
        message_serializer = MessageSerializer(paginated_messages, many=True)

        # 5. Build Custom Paginated Response
        # This keeps the room info at the top and adds pagination links for the messages
        return paginator.get_paginated_response({
            'room': room_data,
            'messages': message_serializer.data
        })
        
        # serializer = RoomDetailSerializer(room)
        # return Response(serializer.data, status=status.HTTP_200_OK)





class UserStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id=None):
        """
        Get the status of a user.
        If user_id is provided, fetch that user's status.
        Otherwise, return current user's status.
        """
        if user_id:
            status_obj = UserStatus.objects.filter(user_id=user_id).first()
            if not status_obj:
                return Response({"error": "User status has not been initialized yet."}, status=404)
        else:
            status_obj, created = UserStatus.objects.get_or_create(user=request.user)

        serializer = UserStatusSerializer(status_obj)
        return Response(serializer.data)

    def patch(self, request):
        """
        Manual toggle for current user.
        Only manual_status can be updated via this endpoint.
        """
        status_obj, created = UserStatus.objects.get_or_create(user=request.user)

        # Toggle manual_status if not provided
        manual_status = request.data.get("manual_status", None)
        if manual_status is None:
            # invert current manual_status
            status_obj.manual_status = not status_obj.manual_status
        else:
            # set to value sent in request
            status_obj.manual_status = bool(manual_status)

        # Optional: update last_seen to now if going online manually
        if status_obj.manual_status:
            status_obj.last_seen = timezone.now()

        status_obj.save()

        serializer = UserStatusSerializer(status_obj)
        return Response(serializer.data, status=status.HTTP_200_OK)

# class UserStatusView(APIView):
#     permission_classes = [IsAuthenticated]

   
    

#     def get(self, request, user_id=None):
#         if user_id:
            
#             status_obj = UserStatus.objects.filter(user_id=user_id).first()
#             if not status_obj:
#                 return Response({"error": "User status has not been initialized yet."}, status=404)
#         else:
            
#             status_obj, created = UserStatus.objects.get_or_create(user=request.user)
        
#         serializer = UserStatusSerializer(status_obj)
#         return Response(serializer.data)

 
#     def patch(self, request):
        
#         status_obj, created = UserStatus.objects.get_or_create(user=request.user)
        
       
#         serializer = UserStatusSerializer(status_obj, data=request.data, partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)