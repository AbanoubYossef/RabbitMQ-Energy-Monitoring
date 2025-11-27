"""
Management command to sync existing devices to monitoring service
"""
from django.core.management.base import BaseCommand
from devices.models import Device
from devices.rabbitmq import DeviceSyncPublisher


class Command(BaseCommand):
    help = 'Sync all existing devices to monitoring service via RabbitMQ'

    def handle(self, *args, **options):
        devices = Device.objects.all()
        
        if not devices.exists():
            self.stdout.write(self.style.WARNING('No devices found to sync'))
            return
        
        publisher = DeviceSyncPublisher()
        publisher.connect()
        
        synced_count = 0
        for device in devices:
            try:
                device_data = {
                    'id': device.id,
                    'name': device.name,
                    'description': device.description,
                    'max_consumption': device.max_consumption,
                }
                publisher.publish_device_created(device_data)
                synced_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Synced device: {device.name} ({device.id})')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Failed to sync device {device.name}: {str(e)}')
                )
        
        if publisher.connection and not publisher.connection.is_closed:
            publisher.connection.close()
        
        self.stdout.write(
            self.style.SUCCESS(f'\nSuccessfully synced {synced_count} devices')
        )
