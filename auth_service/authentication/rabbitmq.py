"""
RabbitMQ Publisher for Auth Service
Publishes user synchronization events to sync_queue
"""
import pika
import json
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


class RabbitMQPublisher:
    """
    Publisher for user synchronization events.
    Publishes to sync_queue when users are created or deleted.
    """
    
    def __init__(self):
        self.connection = None
        self.channel = None
    
    def connect(self):
        """Establish connection to RabbitMQ"""
        try:
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
            
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            
            # Declare fanout exchange for broadcasting sync events
            self.channel.exchange_declare(
                exchange='sync_exchange',
                exchange_type='fanout',
                durable=True
            )
            
            logger.info("Connected to RabbitMQ successfully")
            
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            raise
    
    def publish_to_queue(self, queue_name, message):
        """
        Publish message to a specific queue
        
        Args:
            queue_name: Name of the queue
            message: Dictionary containing the message
        """
        try:
            if not self.channel or self.connection.is_closed:
                self.connect()
            
            # Declare queue
            self.channel.queue_declare(queue=queue_name, durable=True)
            
            self.channel.basic_publish(
                exchange='',
                routing_key=queue_name,
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Make message persistent
                    content_type='application/json'
                )
            )
            
            logger.info(f"Published message to {queue_name}: {message.get('action')}")
            
        except Exception as e:
            logger.error(f"Failed to publish to {queue_name}: {e}")
            raise
    
    def publish_user_created(self, user_data):
        """
        Publish user creation event to sync_queue
        
        Args:
            user_data: Dictionary containing user information
                - id: User UUID
                - username: Username
                - role: User role
        """
        try:
            if not self.channel or self.connection.is_closed:
                self.connect()
            
            message = {
                "event_type": "user_created",
                "data": {
                    "id": str(user_data['id']),
                    "username": user_data['username'],
                    "role": user_data['role']
                }
            }
            
            self.channel.basic_publish(
                exchange='sync_exchange',
                routing_key='',  # Fanout exchange ignores routing key
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Make message persistent
                    content_type='application/json'
                )
            )
            
            logger.info(f"Published user_created event for user {user_data['username']}")
            
        except Exception as e:
            logger.error(f"Failed to publish user_created event: {e}")
            # Don't raise - we don't want to fail user creation if sync fails
    
    def publish_user_deleted(self, user_id):
        """
        Publish user deletion event to sync_queue
        
        Args:
            user_id: UUID of the deleted user
        """
        try:
            if not self.channel or self.connection.is_closed:
                self.connect()
            
            message = {
                "event_type": "user_deleted",
                "data": {
                    "id": str(user_id)
                }
            }
            
            self.channel.basic_publish(
                exchange='sync_exchange',
                routing_key='',  # Fanout exchange ignores routing key
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2,
                    content_type='application/json'
                )
            )
            
            logger.info(f"Published user_deleted event for user {user_id}")
            
        except Exception as e:
            logger.error(f"Failed to publish user_deleted event: {e}")
    
    def close(self):
        """Close RabbitMQ connection"""
        try:
            if self.connection and not self.connection.is_closed:
                self.connection.close()
                logger.info("RabbitMQ connection closed")
        except Exception as e:
            logger.error(f"Error closing RabbitMQ connection: {e}")


# Global publisher instance
_publisher = None


def get_publisher():
    """Get or create global publisher instance"""
    global _publisher
    if _publisher is None:
        _publisher = RabbitMQPublisher()
        try:
            _publisher.connect()
        except Exception as e:
            logger.error(f"Failed to initialize RabbitMQ publisher: {e}")
    return _publisher
