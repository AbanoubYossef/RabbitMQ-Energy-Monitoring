import pika
import json
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


class RabbitMQConnection:
    """RabbitMQ connection manager"""
    
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
            logger.info("Connected to RabbitMQ successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            return False
    
    def declare_queue(self, queue_name, durable=True):
        """Declare a queue"""
        if self.channel:
            self.channel.queue_declare(queue=queue_name, durable=durable)
            logger.info(f"Queue '{queue_name}' declared")
    
    def publish_message(self, queue_name, message):
        """Publish a message to a queue"""
        try:
            if not self.channel:
                self.connect()
            
            self.channel.basic_publish(
                exchange='',
                routing_key=queue_name,
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Make message persistent
                )
            )
            logger.info(f"Published message to {queue_name}: {message}")
            return True
        except Exception as e:
            logger.error(f"Failed to publish message: {e}")
            return False
    
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
    """Get a new RabbitMQ connection"""
    conn = RabbitMQConnection()
    conn.connect()
    return conn
