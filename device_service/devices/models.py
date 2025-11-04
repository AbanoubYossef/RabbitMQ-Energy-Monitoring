import uuid
from django.db import models

class User(models.Model):
    """
    Synchronized user table from Auth service
    """
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('client', 'Client'),
    ]
    
    id = models.UUIDField(primary_key=True, editable=False)
    username = models.CharField(max_length=150, unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='client')
    
    class Meta:
        db_table = 'users'
    
    def __str__(self):
        return self.username

class Device(models.Model):
    """
    Device model
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    max_consumption = models.DecimalField(max_digits=10, decimal_places=2)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'devices'
    
    def __str__(self):
        return self.name

class UserDeviceMapping(models.Model):
    """
    Many-to-many relationship: Multiple users can share the same device
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='device_assignments')
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='user_assignments')
    assigned_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'user_device_mapping'
        unique_together = ['user', 'device']  # Prevent duplicate assignments
    
    def __str__(self):
        return f"{self.device.name} -> {self.user.username}"