import pika
import json
import logging
from django.conf import settings

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
        credentials=credentials,
        heartbeat=600,
        blocked_connection_timeout=300
    )
    return pika.BlockingConnection(parameters)


def publish_chat_message(message_data):
    """
    Publish chat message to RabbitMQ for WebSocket delivery
    
    Args:
        message_data: Dictionary with message details
    """
    try:
        connection = get_rabbitmq_connection()
        channel = connection.channel()
        
        # Declare queue
        channel.queue_declare(queue=settings.CHAT_MESSAGES_QUEUE, durable=True)
        
        # Publish message
        channel.basic_publish(
            exchange='',
            routing_key=settings.CHAT_MESSAGES_QUEUE,
            body=json.dumps(message_data),
            properties=pika.BasicProperties(
                delivery_mode=2,  # Persistent
                content_type='application/json'
            )
        )
        
        logger.info(f"✅ Published chat message to {settings.CHAT_MESSAGES_QUEUE}")
        
        connection.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to publish chat message: {e}")
        return False
