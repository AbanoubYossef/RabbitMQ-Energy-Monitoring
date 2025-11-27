import json
import logging
from datetime import datetime
from django.utils import timezone
from django.db import transaction
from .models import User, Device, DeviceMeasurement, HourlyEnergyConsumption, UserDeviceMapping
from .rabbitmq import get_rabbitmq_connection
from django.conf import settings

logger = logging.getLogger(__name__)


class DeviceDataConsumer:
    """Consumes device measurement data from smart meters"""
    
    def __init__(self):
        self.connection = get_rabbitmq_connection()
    
    def callback(self, ch, method, properties, body):
        """Process incoming device measurement"""
        try:
            data = json.loads(body)
            logger.info(f"Received device data: {data}")
            
            # Expected format: {"timestamp": "ISO8601", "device_id": "uuid", "measurement_value": float}
            device_id = data.get('device_id')
            timestamp_str = data.get('timestamp')
            measurement_value = float(data.get('measurement_value'))
            
            # Parse timestamp
            timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            if timezone.is_naive(timestamp):
                timestamp = timezone.make_aware(timestamp)
            
            # Store raw measurement
            measurement = DeviceMeasurement.objects.create(
                device_id=device_id,
                timestamp=timestamp,
                measurement_value=measurement_value
            )
            logger.info(f"Stored measurement: {measurement}")
            
            # Aggregate into hourly consumption
            self.aggregate_hourly(device_id, timestamp, measurement_value)
            
            # Acknowledge message
            ch.basic_ack(delivery_tag=method.delivery_tag)
            
        except Exception as e:
            logger.error(f"Error processing device data: {e}")
            # Reject and requeue message
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
    
    def aggregate_hourly(self, device_id, timestamp, measurement_value):
        """Aggregate measurement into hourly total"""
        try:
            date = timestamp.date()
            hour = timestamp.hour
            
            # Get or create hourly record
            hourly, created = HourlyEnergyConsumption.objects.get_or_create(
                device_id=device_id,
                date=date,
                hour=hour,
                defaults={
                    'total_consumption': 0.0,
                    'measurement_count': 0
                }
            )
            
            # Update totals
            hourly.total_consumption += measurement_value
            hourly.measurement_count += 1
            hourly.save()
            
            logger.info(f"Updated hourly consumption: {hourly}")
            
        except Exception as e:
            logger.error(f"Error aggregating hourly data: {e}")
    
    def start(self):
        """Start consuming messages"""
        logger.info("Starting Device Data Consumer...")
        self.connection.consume_messages(settings.DEVICE_DATA_QUEUE, self.callback)


class SyncConsumer:
    """Consumes synchronization events for users and devices"""
    
    def __init__(self):
        self.connection = get_rabbitmq_connection()
    
    def callback(self, ch, method, properties, body):
        """Process synchronization event with transaction boundary"""
        try:
            data = json.loads(body)
            logger.info(f"Received sync event: {data}")
            
            event_type = data.get('event_type')
            
            # Use transaction for atomicity
            with transaction.atomic():
                if event_type == 'user_created':
                    self.handle_user_created(data)
                elif event_type == 'user_updated':
                    self.handle_user_updated(data)
                elif event_type == 'user_deleted':
                    self.handle_user_deleted(data)
                elif event_type == 'device_created':
                    self.handle_device_created(data)
                elif event_type == 'device_updated':
                    self.handle_device_updated(data)
                elif event_type == 'device_deleted':
                    self.handle_device_deleted(data)
                elif event_type == 'device_assigned':
                    self.handle_device_assigned(data)
                elif event_type == 'device_unassigned':
                    self.handle_device_unassigned(data)
                else:
                    logger.warning(f"Unknown event type: {event_type}")
            
            # Only ACK after successful processing
            ch.basic_ack(delivery_tag=method.delivery_tag)
            
        except Exception as e:
            logger.error(f"Error processing sync event: {e}")
            # Requeue for retry
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
    
    def handle_user_created(self, data):
        """Handle user creation event"""
        try:
            user_data = data.get('data', {})
            user, created = User.objects.update_or_create(
                id=user_data['id'],
                defaults={
                    'username': user_data['username'],
                    'role': user_data['role']
                }
            )
            action = "Created" if created else "Updated"
            logger.info(f"{action} user: {user}")
        except Exception as e:
            logger.error(f"Error handling user_created: {e}")
    
    def handle_user_updated(self, data):
        """Handle user update event"""
        try:
            user_data = data.get('data', {})
            user, created = User.objects.update_or_create(
                id=user_data['id'],
                defaults={
                    'username': user_data['username'],
                    'role': user_data['role']
                }
            )
            logger.info(f"Updated user: {user}")
        except Exception as e:
            logger.error(f"Error handling user_updated: {e}")
    
    def handle_user_deleted(self, data):
        """Handle user deletion event (idempotent)"""
        try:
            user_id = data.get('data', {}).get('id')
            deleted_count, _ = User.objects.filter(id=user_id).delete()
            
            if deleted_count > 0:
                logger.info(f"Deleted user: {user_id}")
            else:
                logger.warning(f"User {user_id} not found - already deleted (idempotent operation OK)")
        except Exception as e:
            logger.error(f"Error handling user_deleted: {e}")
            raise
    
    def handle_device_created(self, data):
        """Handle device creation event"""
        try:
            device_data = data.get('data', {})
            device, created = Device.objects.update_or_create(
                id=device_data['id'],
                defaults={
                    'name': device_data['name'],
                    'description': device_data.get('description', ''),
                    'max_consumption': device_data['max_consumption']
                }
            )
            action = "Created" if created else "Updated"
            logger.info(f"{action} device: {device}")
        except Exception as e:
            logger.error(f"Error handling device_created: {e}")
    
    def handle_device_updated(self, data):
        """Handle device update event"""
        try:
            device_data = data.get('data', {})
            device, created = Device.objects.update_or_create(
                id=device_data['id'],
                defaults={
                    'name': device_data['name'],
                    'description': device_data.get('description', ''),
                    'max_consumption': device_data['max_consumption']
                }
            )
            logger.info(f"Updated device: {device}")
        except Exception as e:
            logger.error(f"Error handling device_updated: {e}")
    
    def handle_device_deleted(self, data):
        """Handle device deletion event with orphaned mapping cleanup"""
        try:
            device_id = data.get('data', {}).get('id')
            
            # Check for orphaned mappings
            remaining_mappings = UserDeviceMapping.objects.filter(device_id=device_id).count()
            if remaining_mappings > 0:
                logger.warning(
                    f"Device {device_id} still has {remaining_mappings} mappings! "
                    f"Unassignment events may be missing. Cleaning up..."
                )
                # Clean up orphaned mappings
                UserDeviceMapping.objects.filter(device_id=device_id).delete()
            
            # Delete the device (idempotent)
            deleted_count, _ = Device.objects.filter(id=device_id).delete()
            
            if deleted_count > 0:
                logger.info(f"Deleted device: {device_id}")
            else:
                logger.warning(f"Device {device_id} not found - already deleted (idempotent operation OK)")
        except Exception as e:
            logger.error(f"Error handling device_deleted: {e}")
            raise
    
    def handle_device_assigned(self, data):
        """Handle device assignment to user with better race condition handling"""
        try:
            mapping_data = data.get('data', {})
            user_id = mapping_data.get('user_id')
            device_id = mapping_data.get('device_id')
            
            # Get or create user (handle out-of-order events)
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                logger.warning(f"User {user_id} not found - events out of order, creating placeholder")
                user = User.objects.create(
                    id=user_id,
                    username=f'user_{str(user_id)[:8]}',
                    role='client'
                )
            
            # Get or create device (handle out-of-order events)
            try:
                device = Device.objects.get(id=device_id)
            except Device.DoesNotExist:
                logger.warning(f"Device {device_id} not found - events out of order, creating placeholder")
                device = Device.objects.create(
                    id=device_id,
                    name=f'Device_{str(device_id)[:8]}',
                    description='Placeholder - will be updated when device_created arrives',
                    max_consumption=0.0
                )
            
            # Use get_or_create for idempotency
            mapping, created = UserDeviceMapping.objects.get_or_create(
                user=user,
                device=device
            )
            
            action = "Created" if created else "Already exists"
            logger.info(f"{action} assignment: {device.name} -> {user.username}")
        except Exception as e:
            logger.error(f"Error handling device_assigned: {e}")
            raise
    
    def handle_device_unassigned(self, data):
        """Handle device unassignment from user (idempotent)"""
        try:
            mapping_data = data.get('data', {})
            user_id = mapping_data.get('user_id')
            device_id = mapping_data.get('device_id')
            
            # Use filter().delete() for idempotency
            deleted_count, _ = UserDeviceMapping.objects.filter(
                user_id=user_id,
                device_id=device_id
            ).delete()
            
            if deleted_count > 0:
                logger.info(f"Deleted assignment: device {device_id} from user {user_id}")
            else:
                logger.warning(f"Assignment already deleted - idempotent operation OK")
        except Exception as e:
            logger.error(f"Error handling device_unassigned: {e}")
            raise
    
    def start(self):
        """Start consuming messages"""
        logger.info("Starting Sync Consumer...")
        
        # Declare fanout exchange
        if not self.connection.channel:
            self.connection.connect()
        
        self.connection.channel.exchange_declare(
            exchange='sync_exchange',
            exchange_type='fanout',
            durable=True
        )
        
        # Declare exclusive queue for monitoring service
        result = self.connection.channel.queue_declare(queue='monitoring_service_sync_queue', durable=True)
        queue_name = result.method.queue
        
        # Bind queue to exchange
        self.connection.channel.queue_bind(
            exchange='sync_exchange',
            queue=queue_name
        )
        
        logger.info(f"Monitoring sync consumer bound to {queue_name}")
        self.connection.consume_messages(queue_name, self.callback)
