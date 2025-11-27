"""
RabbitMQ Publisher for User Service
Publishes user synchronization events to sync_queue
"""
import pika
import json
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


class UserSyncPublisher:
    """
    Publisher for user synchronization events.
    Publishes to sync_queue when users are created, updated, or deleted.
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
                routing_key='',
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
    
    def publish_user_updated(self, user_data):
        """
        Publish user update event to sync_queue
        
        Args:
            user_data: Dictionary containing updated user information
        """
        try:
            if not self.channel or self.connection.is_closed:
                self.connect()
            
            message = {
                "event_type": "user_updated",
                "data": {
                    "id": str(user_data['id']),
                    "username": user_data['username'],
                    "role": user_data['role']
                }
            }
            
            self.channel.basic_publish(
                exchange='sync_exchange',
                routing_key='',
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2,
                    content_type='application/json'
                )
            )
            
            logger.info(f"Published user_updated event for user {user_data['username']}")
            
        except Exception as e:
            logger.error(f"Failed to publish user_updated event: {e}")
    
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
                routing_key='',
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
    """Get or create global publisher instance with connection check"""
    global _publisher
    
    # Always try to ensure we have a valid connection
    if _publisher is None:
        _publisher = UserSyncPublisher()
    
    # Check if connection is valid, reconnect if needed
    try:
        if not _publisher.connection or _publisher.connection.is_closed:
            logger.info("Publisher connection is closed, reconnecting...")
            _publisher.connect()
    except Exception as e:
        logger.error(f"Failed to ensure RabbitMQ connection: {e}")
        # Try to create a fresh publisher
        try:
            _publisher = UserSyncPublisher()
            _publisher.connect()
        except Exception as e2:
            logger.error(f"Failed to create fresh publisher: {e2}")
    
    return _publisher


class RabbitMQConnection:
    """RabbitMQ connection manager for consumers"""
    
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
                credentials=credentials,
                heartbeat=600,
                blocked_connection_timeout=300
            )
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            logger.info("Consumer connected to RabbitMQ successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            return False
    
    def declare_queue(self, queue_name, durable=True):
        """Declare a queue"""
        if self.channel:
            self.channel.queue_declare(queue=queue_name, durable=durable)
            logger.info(f"Queue '{queue_name}' declared")
    
    def consume_messages(self, queue_name, callback):
        """Consume messages from a queue"""
        try:
            if not self.channel:
                if not self.connect():
                    logger.error("Failed to establish RabbitMQ connection")
                    return
            
            self.declare_queue(queue_name)
            self.channel.basic_qos(prefetch_count=1)
            self.channel.basic_consume(
                queue=queue_name,
                on_message_callback=callback,
                auto_ack=False
            )
            
            logger.info(f"Started consuming from {queue_name}")
            self.channel.start_consuming()
        except KeyboardInterrupt:
            logger.info("Stopping consumer...")
            self.stop()
        except Exception as e:
            logger.error(f"Error consuming messages: {e}")
            raise
    
    def stop(self):
        """Close connection"""
        try:
            if self.channel:
                self.channel.stop_consuming()
            if self.connection:
                self.connection.close()
            logger.info("RabbitMQ connection closed")
        except Exception as e:
            logger.error(f"Error closing connection: {e}")


def get_rabbitmq_connection():
    """Get a new RabbitMQ connection for consumers"""
    conn = RabbitMQConnection()
    conn.connect()
    return conn
