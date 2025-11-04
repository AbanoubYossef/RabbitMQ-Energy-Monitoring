
import uuid
from django.db import models
from django.contrib.auth.hashers import make_password, check_password

class User(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('client', 'Client'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=255)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='client')
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Required for Django's custom user model
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []
    
    class Meta:
        db_table = 'users'
    
    def __str__(self):
        return self.username
    
    @property
    def is_anonymous(self):
        return False
    
    @property
    def is_authenticated(self):
        return True
    
    @property
    def is_active(self):
        """All users are active by default"""
        return True
    
    @property
    def is_staff(self):
        """Admin users are staff"""
        return self.role == 'admin'
    
    @property
    def is_superuser(self):
        """Admin users are superusers"""
        return self.role == 'admin'
    
    def has_perm(self, perm, obj=None):
        """Admin users have all permissions"""
        return self.role == 'admin'
    
    def has_module_perms(self, app_label):
        """Admin users have all module permissions"""
        return self.role == 'admin'
    
    def set_password(self, raw_password):
        """Hash and set the password"""
        self.password = make_password(raw_password)
    
    def check_password(self, raw_password):
        """Verify password"""
        return check_password(raw_password, self.password)