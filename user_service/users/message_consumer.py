"""
RabbitMQ Consumer for User Service
Handles user management operations via message queue
"""
import json
import logging
from django.core.management.base import BaseCommand
from users.models import User
from users.rabbitmq import get_rabbitmq_connection

logger = logging.getLogger(__name__)


class UserServiceConsumer:
    """Consumer for user service operations"""
    
    def __init__(self):
        self.connection = None
        self.queue_name = 'user_service_queue'
        try:
            self.connection = get_rabbitmq_connection()
            if not self.connection or not self.connection.channel:
                logger.error("Failed to establish RabbitMQ connection")
        except Exception as e:
            logger.error(f"Error initializing consumer: {e}")
    
    def callback(self, ch, method, properties, body):
        """Process incoming messages"""
        try:
            message = json.loads(body)
            action = message.get('action')
            data = message.get('data', {})
            
            logger.info(f"Received action: {action} with data: {data}")
            
            if action == 'create_user':
                self.create_user(data)
            elif action == 'update_user':
                self.update_user(data)
            elif action == 'delete_user':
                self.delete_user(data)
            else:
                logger.warning(f"Unknown action: {action}")
            
            # Acknowledge message
            ch.basic_ack(delivery_tag=method.delivery_tag)
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            # Reject and requeue on error
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    
    def create_user(self, data):
        """Create user in database"""
        try:
            user, created = User.objects.get_or_create(
                id=data['id'],
                defaults={
                    'username': data['username'],
                    'role': data['role'],
                    'fname': data.get('fname', ''),
                    'lname': data.get('lname', ''),
                    'email': data.get('email', ''),
                    'phone': data.get('phone', '')
                }
            )
            if created:
                logger.info(f"User created: {user.id}")
            else:
                logger.info(f"User already exists: {user.id}")
        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            raise
    
    def update_user(self, data):
        """Update user in database"""
        try:
            user = User.objects.get(id=data['id'])
            for key, value in data.items():
                if key != 'id' and hasattr(user, key):
                    setattr(user, key, value)
            user.save()
            logger.info(f"User updated: {user.id}")
        except User.DoesNotExist:
            logger.error(f"User not found: {data['id']}")
        except Exception as e:
            logger.error(f"Failed to update user: {e}")
            raise
    
    def delete_user(self, data):
        """Delete user from database"""
        try:
            User.objects.filter(id=data['id']).delete()
            logger.info(f"User deleted: {data['id']}")
        except Exception as e:
            logger.error(f"Failed to delete user: {e}")
            raise
    
    def start(self):
        """Start consuming messages"""
        if not self.connection or not self.connection.channel:
            logger.error("Cannot start consumer: No valid RabbitMQ connection")
            return
        
        try:
            self.connection.declare_queue(self.queue_name)
            logger.info(f"Starting consumer for {self.queue_name}")
            self.connection.consume_messages(self.queue_name, self.callback)
        except KeyboardInterrupt:
            logger.info("Consumer stopped by user")
        except Exception as e:
            logger.error(f"Consumer error: {e}")
            raise


def start_consumer():
    """Start the consumer"""
    consumer = UserServiceConsumer()
    consumer.start()
