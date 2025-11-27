"""
Django management command to start RabbitMQ consumer
"""
from django.core.management.base import BaseCommand
from users.message_consumer import start_consumer


class Command(BaseCommand):
    help = 'Start RabbitMQ consumer for user service'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting User Service RabbitMQ consumer...'))
        start_consumer()
