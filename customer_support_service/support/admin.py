from django.contrib import admin
from .models import ChatSession, ChatMessage


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ['id', 'username', 'status', 'created_at', 'updated_at']
    list_filter = ['status', 'created_at']
    search_fields = ['username', 'user_id']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'session', 'sender', 'message_preview', 'response_type', 'timestamp']
    list_filter = ['sender', 'response_type', 'timestamp']
    search_fields = ['message']
    readonly_fields = ['id', 'timestamp']
    
    def message_preview(self, obj):
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
    message_preview.short_description = 'Message'
