from rest_framework import serializers
from .models import User, Device, UserDeviceMapping

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'role']

class DeviceSerializer(serializers.ModelSerializer):
    owner_usernames = serializers.SerializerMethodField()
    
    class Meta:
        model = Device
        fields = ['id', 'name', 'description', 'max_consumption', 'price', 'created_at', 'owner_usernames']
        read_only_fields = ['id', 'created_at']
    
    def get_owner_usernames(self, obj):
        """Return list of all usernames who have this device assigned"""
        mappings = UserDeviceMapping.objects.filter(device=obj).select_related('user')
        return [mapping.user.username for mapping in mappings]

class DeviceCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200)
    description = serializers.CharField(required=False, allow_blank=True)
    max_consumption = serializers.DecimalField(max_digits=10, decimal_places=2)
    price = serializers.DecimalField(max_digits=10, decimal_places=2)

class UserDeviceMappingSerializer(serializers.ModelSerializer):
    device_name = serializers.CharField(source='device.name', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = UserDeviceMapping
        fields = ['id', 'user', 'device', 'device_name', 'user_username', 'assigned_at']
        read_only_fields = ['id', 'assigned_at']

class AssignDeviceSerializer(serializers.Serializer):
    device_id = serializers.UUIDField()
    user_id = serializers.UUIDField()

class UserCreateSerializer(serializers.Serializer):
    """For creating user from Auth service"""
    id = serializers.UUIDField()
    username = serializers.CharField(max_length=150)
    role = serializers.ChoiceField(choices=['admin', 'client'])