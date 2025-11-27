#!/usr/bin/env python3
"""
Load Balancer Service for Energy Management System
Distributes device data across multiple monitoring service replicas
"""
import pika
import json
import time
import os
import sys
from dotenv import load_dotenv
from consistent_hash import ConsistentHash

load_dotenv()


class LoadBalancer:
    """Load balancer for distributing device measurements"""
    
    def __init__(self):
        self.rabbitmq_host = os.getenv('RABBITMQ_HOST', 'localhost')
        self.rabbitmq_port = int(os.getenv('RABBITMQ_PORT', 5672))
        self.rabbitmq_user = os.getenv('RABBITMQ_USER', 'admin')
        self.rabbitmq_pass = os.getenv('RABBITMQ_PASS', 'admin123')
        self.device_data_queue = os.getenv('DEVICE_DATA_QUEUE', 'device_data_queue')
        self.num_replicas = int(os.getenv('NUM_REPLICAS', 3))
        self.virtual_nodes = int(os.getenv('VIRTUAL_NODES', 150))
        
        self.connection = None
        self.channel = None
        self.consistent_hash = ConsistentHash(self.num_replicas, self.virtual_nodes)
        
        # Statistics
        self.total_messages = 0
        self.distribution_stats = {i: 0 for i in range(1, self.num_replicas + 1)}
    
    def connect(self):
        """Connect to RabbitMQ with retry logic"""
        max_retries = 5
        retry_delay = 2
        
        for attempt in range(1, max_retries + 1):
            try:
                credentials = pika.PlainCredentials(self.rabbitmq_user, self.rabbitmq_pass)
                parameters = pika.ConnectionParameters(
                    host=self.rabbitmq_host,
                    port=self.rabbitmq_port,
                    credentials=credentials,
                    heartbeat=600,
                    blocked_connection_timeout=300
                )
                
                self.connection = pika.BlockingConnection(parameters)
                self.channel = self.connection.createChannel()
                
                # Declare main device data queue
                self.channel.queue_declare(queue=self.device_data_queue, durable=True)
                
                # Declare ingest queues for each replica
                for replica_id in range(1, self.num_replicas + 1):
                    queue_name = f"ingest_queue_{replica_id}"
                    self.channel.queue_declare(queue=queue_name, durable=True)
                    print(f"✅ Declared queue: {queue_name}")
                
                print(f"✅ Connected to RabbitMQ at {self.rabbitmq_host}:{self.rabbitmq_port}")
                return True
                
            except Exception as e:
                print(f"❌ Connection attempt {attempt}/{max_retries} failed: {e}")
                if attempt < max_retries:
                    print(f"⏳ Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    print("❌ Failed to connect to RabbitMQ after all retries")
                    return False
    
    def callback(self, ch, method, properties, body):
        """Process incoming device measurement"""
        try:
            data = json.loads(body)
            device_id = data.get('device_id')
            
            if not device_id:
                print("⚠️  Message missing device_id, skipping")
                ch.basic_ack(delivery_tag=method.delivery_tag)
                return
            
            # Get replica using consistent hashing
            replica_id = self.consistent_hash.get_replica(device_id)
            ingest_queue = f"ingest_queue_{replica_id}"
            
            # Forward to replica's ingest queue
            ch.basic_publish(
                exchange='',
                routing_key=ingest_queue,
                body=body,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Persistent
                    content_type='application/json'
                )
            )
            
            # Update statistics
            self.total_messages += 1
            self.distribution_stats[replica_id] += 1
            
            # Log every 10 messages
            if self.total_messages % 10 == 0:
                self.print_stats()
            
            # Acknowledge original message
            ch.basic_ack(delivery_tag=method.delivery_tag)
            
        except Exception as e:
            print(f"❌ Error processing message: {e}")
            # Reject and requeue
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
    
    def print_stats(self):
        """Print distribution statistics"""
        print(f"\n📊 Load Balancer Statistics:")
        print(f"   Total messages processed: {self.total_messages}")
        print(f"   Distribution across replicas:")
        for replica_id in range(1, self.num_replicas + 1):
            count = self.distribution_stats[replica_id]
            percentage = (count / self.total_messages * 100) if self.total_messages > 0 else 0
            print(f"      Replica {replica_id}: {count} messages ({percentage:.1f}%)")
        print()
    
    def start(self):
        """Start consuming and distributing messages"""
        print("=" * 70)
        print("  LOAD BALANCER SERVICE - Energy Management System")
        print("=" * 70)
        print(f"Configuration:")
        print(f"  RabbitMQ Host:    {self.rabbitmq_host}:{self.rabbitmq_port}")
        print(f"  Source Queue:     {self.device_data_queue}")
        print(f"  Num Replicas:     {self.num_replicas}")
        print(f"  Virtual Nodes:    {self.virtual_nodes}")
        print("=" * 70)
        
        if not self.connect():
            print("❌ Failed to connect. Exiting.")
            sys.exit(1)
        
        print(f"\n✅ Load balancer started. Consuming from {self.device_data_queue}")
        print("   Press Ctrl+C to stop\n")
        
        try:
            # Start consuming
            self.channel.basic_qos(prefetch_count=1)
            self.channel.basic_consume(
                queue=self.device_data_queue,
                on_message_callback=self.callback
            )
            
            self.channel.start_consuming()
            
        except KeyboardInterrupt:
            print("\n\n✅ Load balancer stopped by user")
            self.print_stats()
        except Exception as e:
            print(f"\n❌ Load balancer error: {e}")
        finally:
            self.stop()
    
    def stop(self):
        """Stop load balancer and cleanup"""
        try:
            if self.channel:
                self.channel.stop_consuming()
            if self.connection and not self.connection.is_closed:
                self.connection.close()
            print("✅ RabbitMQ connection closed")
        except Exception as e:
            print(f"❌ Error closing connection: {e}")
        
        print("=" * 70)


def main():
    """Main entry point"""
    load_balancer = LoadBalancer()
    load_balancer.start()


if __name__ == "__main__":
    main()
