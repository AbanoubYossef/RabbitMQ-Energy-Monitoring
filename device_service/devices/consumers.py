"""
RabbitMQ Consumers for Device Service
Consumes synchronization events from sync_queue
"""
import pika
import json
import logging
from django.conf import settings
from .models import User

logger = logging.getLogger(__name__)


def get_rabbitmq_connection():
    """Create RabbitMQ connection"""
    credentials = pika.PlainCredentials(
        settings.RABBITMQ_USER,
        settings.RABBITMQ_PASS
    )
    
    parameters = pika.ConnectionParameters(
        host=settings.RABBITMQ_HOST,
        port=settings.RABBITMQ_PORT,
        virtual_host='/',
        credentials=credentials,
        heartbeat=600,
        blocked_connection_timeout=300
    )
    
    return pika.BlockingConnection(parameters)


class UserSyncConsumer:
    """
    Consumer for user synchronization events.
    Listens to sync_queue for user_created and user_deleted events.
    """
    
    def __init__(self):
        self.connection = None
        self.channel = None
    
    def callback(self, ch, method, properties, body):
        """
        Process sync messages from queue
        
        Args:
            ch: Channel
            method: Delivery method
            properties: Message properties
            body: Message body (JSON)
        """
        try:
            message = json.loads(body)
            event_type = message.get('event_type')
            data = message.get('data')
            
            logger.info(f"Received sync event: {event_type}")
            
            if event_type == 'user_created':
                self.handle_user_created(data)
            elif event_type == 'user_deleted':
                self.handle_user_deleted(data)
            else:
                logger.warning(f"Unknown event type: {event_type}")
            
            # Acknowledge message
            ch.basic_ack(delivery_tag=method.delivery_tag)
            logger.info(f"Successfully processed {event_type} event")
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in message: {e}")
            # Acknowledge bad message to remove it from queue
            ch.basic_ack(delivery_tag=method.delivery_tag)
            
        except Exception as e:
            logger.error(f"Error processing sync message: {e}")
            # Requeue message for retry
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
    
    def handle_user_created(self, data):
        """
        Handle user_created event
        Creates or updates user in local database
        
        Args:
            data: User data dictionary with id, username, role
        """
        try:
            user, created = User.objects.get_or_create(
                id=data['id'],
                defaults={
                    'username': data['username'],
                    'role': data['role']
                }
            )
            
            if created:
                logger.info(f"Created user: {user.username} ({user.id})")
            else:
                # Update existing user
                user.username = data['username']
                user.role = data['role']
                user.save()
                logger.info(f"Updated user: {user.username} ({user.id})")
                
        except Exception as e:
            logger.error(f"Failed to create/update user: {e}")
            raise
    
    def handle_user_deleted(self, data):
        """
        Handle user_deleted event
        Deletes user from local database
        
        Args:
            data: Dictionary with user id
        """
        try:
            user_id = data['id']
            deleted_count, _ = User.objects.filter(id=user_id).delete()
            
            if deleted_count > 0:
                logger.info(f"Deleted user: {user_id}")
            else:
                logger.warning(f"User not found for deletion: {user_id}")
                
        except Exception as e:
            logger.error(f"Failed to delete user: {e}")
            raise
    
    def start_consuming(self):
        """
        Start consuming messages from device_service_sync_queue
        This is a blocking operation
        """
        try:
            logger.info("Connecting to RabbitMQ...")
            self.connection = get_rabbitmq_connection()
            self.channel = self.connection.channel()
            
            # Declare fanout exchange
            self.channel.exchange_declare(
                exchange='sync_exchange',
                exchange_type='fanout',
                durable=True
            )
            
            # Declare exclusive queue for device service
            result = self.channel.queue_declare(queue='device_service_sync_queue', durable=True)
            queue_name = result.method.queue
            
            # Bind queue to exchange
            self.channel.queue_bind(
                exchange='sync_exchange',
                queue=queue_name
            )
            
            # Set QoS - process one message at a time
            self.channel.basic_qos(prefetch_count=1)
            
            # Start consuming
            self.channel.basic_consume(
                queue=queue_name,
                on_message_callback=self.callback
            )
            
            logger.info(f"User sync consumer started on {queue_name}. Waiting for messages...")
            self.channel.start_consuming()
            
        except KeyboardInterrupt:
            logger.info("Consumer stopped by user")
            self.stop_consuming()
            
        except Exception as e:
            logger.error(f"Consumer error: {e}")
            raise
    
    def stop_consuming(self):
        """Stop consuming and close connection"""
        try:
            if self.channel:
                self.channel.stop_consuming()
            if self.connection:
                self.connection.close()
            logger.info("Consumer stopped and connection closed")
        except Exception as e:
            logger.error(f"Error stopping consumer: {e}")
