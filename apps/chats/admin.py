

from django.contrib import admin

from apps.chats.models import Room, UserStatus,Message

# Register your models here.
# admin.site.register(Room)
# admin.site.register(Message)
# admin.site.register(UserStatus)

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_1', 'user_2', 'last_message', 'updated_at')
    search_fields = ('user_1__email', 'user_2__email')
    ordering = ('-updated_at',)

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'room', 'sender', 'content', 'created_at')
    search_fields = ('sender__email', 'content')
    ordering = ('-created_at',)

@admin.register(UserStatus)
class UserStatusAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'manual_status', 'auto_status', 'last_seen')
    search_fields = ('user__email',)
    ordering = ('-last_seen',)