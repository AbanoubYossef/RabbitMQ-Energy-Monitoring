from django.db import models
import uuid


class User(models.Model):
    """Synchronized user data from Auth Service"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=150, unique=True)
    role = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'users'

    def __str__(self):
        return self.username


class Device(models.Model):
    """Synchronized device data from Device Service"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    max_consumption = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'devices'

    def __str__(self):
        return self.name


class UserDeviceMapping(models.Model):
    """Synchronized user-device mapping from Device Service"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='device_assignments')
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='user_assignments')
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_device_mapping'
        unique_together = ['user', 'device']

    def __str__(self):
        return f"{self.device.name} -> {self.user.username}"


class DeviceMeasurement(models.Model):
    """Raw 10-minute interval measurements from smart meters"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    device_id = models.UUIDField(db_index=True)
    timestamp = models.DateTimeField(db_index=True)
    measurement_value = models.FloatField(help_text="Energy consumed in 10-minute interval (kWh)")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'device_measurements'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['device_id', 'timestamp']),
        ]

    def __str__(self):
        return f"Device {self.device_id} - {self.timestamp} - {self.measurement_value} kWh"


class HourlyEnergyConsumption(models.Model):
    """Aggregated hourly energy consumption"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    device_id = models.UUIDField(db_index=True)
    date = models.DateField(db_index=True)
    hour = models.IntegerField(help_text="Hour of day (0-23)")
    total_consumption = models.FloatField(help_text="Total energy consumed in hour (kWh)")
    measurement_count = models.IntegerField(default=0, help_text="Number of measurements aggregated")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'hourly_energy_consumption'
        ordering = ['-date', '-hour']
        unique_together = ['device_id', 'date', 'hour']
        indexes = [
            models.Index(fields=['device_id', 'date', 'hour']),
        ]

    def __str__(self):
        return f"Device {self.device_id} - {self.date} {self.hour}:00 - {self.total_consumption} kWh"
