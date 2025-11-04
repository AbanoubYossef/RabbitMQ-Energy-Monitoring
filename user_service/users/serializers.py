
from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'role', 'fname', 'lname', 'email', 'phone', 'created_at']
        read_only_fields = ['id', 'created_at']

class UserCreateSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    username = serializers.CharField(max_length=150)
    role = serializers.ChoiceField(choices=['admin', 'client'])
    fname = serializers.CharField(max_length=100)
    lname = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)

class UserUpdateSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150, required=False)
    role = serializers.ChoiceField(choices=['admin', 'client'], required=False)
    fname = serializers.CharField(max_length=100, required=False)
    lname = serializers.CharField(max_length=100, required=False)
    email = serializers.EmailField(required=False)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)