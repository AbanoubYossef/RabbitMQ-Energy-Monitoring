from rest_framework import serializers
from .models import DeviceMeasurement, HourlyEnergyConsumption, Device, User, UserDeviceMapping


class DeviceMeasurementSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceMeasurement
        fields = ['id', 'device_id', 'timestamp', 'measurement_value', 'created_at']
        read_only_fields = ['id', 'created_at']


class HourlyEnergyConsumptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = HourlyEnergyConsumption
        fields = ['id', 'device_id', 'date', 'hour', 'total_consumption', 'measurement_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class DeviceSerializer(serializers.ModelSerializer):
    user_id = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    
    class Meta:
        model = Device
        fields = ['id', 'name', 'description', 'max_consumption', 'created_at', 'user_id', 'status']
        read_only_fields = ['id', 'created_at', 'user_id', 'status']
    
    def get_user_id(self, obj):
        """Get the user_id from the latest mapping"""
        mapping = obj.user_assignments.first()
        return str(mapping.user.id) if mapping else None
    
    def get_status(self, obj):
        """Get device status based on assignment"""
        return 'assigned' if obj.user_assignments.exists() else 'unassigned'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'role', 'created_at']
        read_only_fields = ['id', 'created_at']


class UserDeviceMappingSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDeviceMapping
        fields = ['id', 'user', 'device', 'assigned_at']
        read_only_fields = ['id', 'assigned_at']
