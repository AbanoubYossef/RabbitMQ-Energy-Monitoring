from django.db import models
import uuid


class ChatSession(models.Model):
    """Chat session between user and support"""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('closed', 'Closed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.UUIDField(db_index=True)
    username = models.CharField(max_length=150)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'chat_sessions'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Session {self.id} - {self.username} ({self.status})"


class ChatMessage(models.Model):
    """Individual chat messages"""
    SENDER_CHOICES = [
        ('user', 'User'),
        ('bot', 'Bot'),
        ('admin', 'Admin'),
    ]
    
    RESPONSE_TYPE_CHOICES = [
        ('rule_based', 'Rule Based'),
        ('ai_generated', 'AI Generated'),
        ('admin_reply', 'Admin Reply'),
        ('user_message', 'User Message'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    sender = models.CharField(max_length=20, choices=SENDER_CHOICES)
    message = models.TextField()
    response_type = models.CharField(max_length=20, choices=RESPONSE_TYPE_CHOICES, null=True, blank=True)
    rule_id = models.IntegerField(null=True, blank=True, help_text="Matched rule ID if rule-based")
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'chat_messages'
        ordering = ['timestamp']
    
    def __str__(self):
        return f"{self.sender}: {self.message[:50]}..."
