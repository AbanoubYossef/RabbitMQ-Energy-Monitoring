from django.core.management.base import BaseCommand
import threading
import logging
from monitoring.consumers import DeviceDataConsumer, SyncConsumer

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Start RabbitMQ message consumers'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting RabbitMQ consumers...'))
        
        # Start Device Data Consumer in a separate thread
        device_consumer = DeviceDataConsumer()
        device_thread = threading.Thread(target=device_consumer.start, daemon=True)
        device_thread.start()
        self.stdout.write(self.style.SUCCESS('Device Data Consumer started'))
        
        # Start Sync Consumer in a separate thread
        sync_consumer = SyncConsumer()
        sync_thread = threading.Thread(target=sync_consumer.start, daemon=True)
        sync_thread.start()
        self.stdout.write(self.style.SUCCESS('Sync Consumer started'))
        
        # Keep the main thread alive
        try:
            device_thread.join()
            sync_thread.join()
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('Stopping consumers...'))
