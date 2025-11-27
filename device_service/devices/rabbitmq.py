"""
RabbitMQ Publisher for Device Service
Publishes device synchronization events to sync_queue
"""
import pika
import json
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


class DeviceSyncPublisher:
    """
    Publisher for device synchronization events.
    Publishes to sync_queue when devices are created, updated, or deleted.
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
            
            logger.info("Connected to RabbitMQ successfully and declared sync_exchange")
            
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            raise
    
    def publish_device_created(self, device_data):
        """
        Publish device creation event to sync_queue
        
        Args:
            device_data: Dictionary containing device information
                - id: Device UUID
                - name: Device name
                - description: Device description
                - max_consumption: Maximum consumption
        """
        try:
            logger.info(f"Attempting to publish device_created event for {device_data.get('name', 'unknown')}")
            
            if not self.channel or self.connection.is_closed:
                logger.info("Reconnecting to RabbitMQ...")
                self.connect()
            
            message = {
                "event_type": "device_created",
                "data": {
                    "id": str(device_data['id']),
                    "name": device_data['name'],
                    "description": device_data.get('description', ''),
                    "max_consumption": float(device_data['max_consumption'])
                }
            }
            
            logger.info(f"Publishing message: {json.dumps(message)}")
            
            self.channel.basic_publish(
                exchange='sync_exchange',
                routing_key='',  # Fanout exchange ignores routing key
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Make message persistent
                    content_type='application/json'
                )
            )
            
            logger.info(f"Successfully published device_created event for device {device_data['name']}")
            
        except Exception as e:
            logger.error(f"Failed to publish device_created event: {e}", exc_info=True)
            # Don't raise - we don't want to fail device creation if sync fails
    
    def publish_device_updated(self, device_data):
        """
        Publish device update event to sync_queue
        
        Args:
            device_data: Dictionary containing updated device information
        """
        try:
            logger.info(f"Attempting to publish device_updated event for {device_data.get('name', 'unknown')}")
            
            if not self.channel or self.connection.is_closed:
                logger.info("Reconnecting to RabbitMQ...")
                self.connect()
            
            message = {
                "event_type": "device_updated",
                "data": {
                    "id": str(device_data['id']),
                    "name": device_data['name'],
                    "description": device_data.get('description', ''),
                    "max_consumption": float(device_data['max_consumption'])
                }
            }
            
            logger.info(f"Publishing message: {json.dumps(message)}")
            
            self.channel.basic_publish(
                exchange='sync_exchange',
                routing_key='',  # Fanout exchange ignores routing key
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2,
                    content_type='application/json'
                )
            )
            
            logger.info(f"Successfully published device_updated event for device {device_data['name']}")
            
        except Exception as e:
            logger.error(f"Failed to publish device_updated event: {e}", exc_info=True)
    
    def publish_device_deleted(self, device_id):
        """
        Publish device deletion event to sync_queue
        
        Args:
            device_id: UUID of the deleted device
        """
        try:
            print(f"[RABBITMQ] Attempting to publish device_deleted event for device {device_id}")
            logger.info(f"Attempting to publish device_deleted event for device {device_id}")
            
            if not self.channel or self.connection.is_closed:
                print(f"[RABBITMQ] Reconnecting to RabbitMQ...")
                logger.info("Reconnecting to RabbitMQ...")
                self.connect()
            
            message = {
                "event_type": "device_deleted",
                "data": {
                    "id": str(device_id)
                }
            }
            
            print(f"[RABBITMQ] Publishing message: {json.dumps(message)}")
            logger.info(f"Publishing message: {json.dumps(message)}")
            
            self.channel.basic_publish(
                exchange='sync_exchange',
                routing_key='',  # Fanout exchange ignores routing key
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2,
                    content_type='application/json'
                )
            )
            
            print(f"[RABBITMQ] Successfully published device_deleted event for device {device_id}")
            logger.info(f"Successfully published device_deleted event for device {device_id}")
            
        except Exception as e:
            print(f"[RABBITMQ] Failed to publish device_deleted event: {e}")
            logger.error(f"Failed to publish device_deleted event: {e}", exc_info=True)
    
    def publish_device_assigned(self, user_id, device_id):
        """
        Publish device assignment event to sync_queue
        
        Args:
            user_id: UUID of the user
            device_id: UUID of the device
        """
        try:
            logger.info(f"Attempting to publish device_assigned event for device {device_id} to user {user_id}")
            
            if not self.channel or self.connection.is_closed:
                logger.info("Reconnecting to RabbitMQ...")
                self.connect()
            
            message = {
                "event_type": "device_assigned",
                "data": {
                    "user_id": str(user_id),
                    "device_id": str(device_id)
                }
            }
            
            logger.info(f"Publishing message: {json.dumps(message)}")
            
            self.channel.basic_publish(
                exchange='sync_exchange',
                routing_key='',  # Fanout exchange ignores routing key
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2,
                    content_type='application/json'
                )
            )
            
            logger.info(f"Successfully published device_assigned event: device {device_id} to user {user_id}")
            
        except Exception as e:
            logger.error(f"Failed to publish device_assigned event: {e}", exc_info=True)
    
    def publish_device_unassigned(self, user_id, device_id):
        """
        Publish device unassignment event to sync_queue
        
        Args:
            user_id: UUID of the user
            device_id: UUID of the device
        """
        try:
            print(f"[RABBITMQ] Attempting to publish device_unassigned event for device {device_id} from user {user_id}")
            logger.info(f"Attempting to publish device_unassigned event for device {device_id} from user {user_id}")
            
            if not self.channel or self.connection.is_closed:
                print("[RABBITMQ] Reconnecting to RabbitMQ...")
                logger.info("Reconnecting to RabbitMQ...")
                self.connect()
            
            message = {
                "event_type": "device_unassigned",
                "data": {
                    "user_id": str(user_id),
                    "device_id": str(device_id)
                }
            }
            
            print(f"[RABBITMQ] Publishing message: {json.dumps(message)}")
            logger.info(f"Publishing message: {json.dumps(message)}")
            
            self.channel.basic_publish(
                exchange='sync_exchange',
                routing_key='',  # Fanout exchange ignores routing key
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2,
                    content_type='application/json'
                )
            )
            
            print(f"[RABBITMQ] Successfully published device_unassigned event: device {device_id} from user {user_id}")
            logger.info(f"Successfully published device_unassigned event: device {device_id} from user {user_id}")
            
        except Exception as e:
            print(f"[RABBITMQ ERROR] Failed to publish device_unassigned event: {e}")
            logger.error(f"Failed to publish device_unassigned event: {e}", exc_info=True)
    
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
        _publisher = DeviceSyncPublisher()
    
    # Check if connection is valid, reconnect if needed
    try:
        if not _publisher.connection or _publisher.connection.is_closed:
            logger.info("Publisher connection is closed, reconnecting...")
            _publisher.connect()
    except Exception as e:
        logger.error(f"Failed to ensure RabbitMQ connection: {e}")
        # Try to create a fresh publisher
        try:
            _publisher = DeviceSyncPublisher()
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
                self.connect()
            
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
