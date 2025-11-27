"""
Django management command to start RabbitMQ sync consumer
Usage: python manage.py consume_sync
"""
from django.core.management.base import BaseCommand
from devices.consumers import UserSyncConsumer
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Start RabbitMQ consumer for user synchronization events'
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting user sync consumer...'))
        
        consumer = UserSyncConsumer()
        
        try:
            consumer.start_consuming()
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('\nConsumer stopped by user'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Consumer error: {e}'))
            raise
