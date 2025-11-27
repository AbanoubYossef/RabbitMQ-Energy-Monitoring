#!/usr/bin/env python3
"""
Device Data Simulator for Energy Management System
Simulates smart meter readings with realistic consumption patterns
"""

import pika
import json
import time
import random
import argparse
import sys
import os
from datetime import datetime
from pathlib import Path


class EnergyPatternGenerator:
    """
    Generates realistic energy consumption patterns based on time of day
    """
    
    def __init__(self, base_load, patterns):
        """
        Initialize pattern generator
        
        Args:
            base_load: Base energy consumption in kWh
            patterns: Dictionary of time-based patterns
        """
        self.base_load = base_load
        self.patterns = patterns
        
        # Build hour-to-multiplier mapping
        self.hour_multipliers = {}
        for pattern_name, pattern_data in patterns.items():
            multiplier = pattern_data['multiplier']
            for hour in pattern_data['hours']:
                self.hour_multipliers[hour] = multiplier
    
    def generate_measurement(self, current_time=None):
        """
        Generate realistic measurement based on time of day
        
        Args:
            current_time: datetime object (defaults to now)
            
        Returns:
            float: Energy consumption value in kWh
        """
        if current_time is None:
            current_time = datetime.now()
        
        hour = current_time.hour
        
        # Get multiplier for current hour
        multiplier = self.hour_multipliers.get(hour, 1.0)
        
        # Add random fluctuation (±10%)
        fluctuation = random.uniform(0.9, 1.1)
        
        # Calculate final value
        value = self.base_load * multiplier * fluctuation
        
        return round(value, 3)
    
    def get_pattern_info(self, hour):
        """Get pattern information for a specific hour"""
        for pattern_name, pattern_data in self.patterns.items():
            if hour in pattern_data['hours']:
                return pattern_name, pattern_data
        return "unknown", {"multiplier": 1.0, "description": "Unknown pattern"}


class SimulatorPublisher:
    """
    RabbitMQ publisher for simulator
    """
    
    def __init__(self, config):
        """
        Initialize publisher with RabbitMQ configuration
        
        Args:
            config: Dictionary with RabbitMQ connection details
        """
        self.config = config
        self.connection = None
        self.channel = None
        self.queue_name = config['queue']
    
    def connect(self):
        """Establish connection to RabbitMQ with retry logic"""
        max_retries = 5
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                credentials = pika.PlainCredentials(
                    self.config['user'],
                    self.config['password']
                )
                
                parameters = pika.ConnectionParameters(
                    host=self.config['host'],
                    port=self.config['port'],
                    virtual_host='/',
                    credentials=credentials,
                    heartbeat=600,
                    blocked_connection_timeout=300
                )
                
                self.connection = pika.BlockingConnection(parameters)
                self.channel = self.connection.channel()
                
                # Declare queue (idempotent)
                self.channel.queue_declare(queue=self.queue_name, durable=True)
                
                print(f"✓ Connected to RabbitMQ at {self.config['host']}:{self.config['port']}")
                return True
                
            except Exception as e:
                print(f"✗ Connection attempt {attempt + 1}/{max_retries} failed: {e}")
                if attempt < max_retries - 1:
                    print(f"  Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    print("✗ Failed to connect to RabbitMQ after all retries")
                    return False
    
    def send_measurement(self, device_id, measurement_value):
        """
        Send measurement to RabbitMQ
        
        Args:
            device_id: UUID of the device
            measurement_value: Energy consumption value in kWh
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Check connection
            if not self.channel or self.connection.is_closed:
                if not self.connect():
                    return False
            
            # Create message
            message = {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "device_id": device_id,
                "measurement_value": measurement_value
            }
            
            # Publish message
            self.channel.basic_publish(
                exchange='',
                routing_key=self.queue_name,
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Make message persistent
                    content_type='application/json'
                )
            )
            
            return True
            
        except Exception as e:
            print(f"✗ Error sending measurement: {e}")
            return False
    
    def close(self):
        """Close RabbitMQ connection"""
        try:
            if self.connection and not self.connection.is_closed:
                self.connection.close()
                print("✓ RabbitMQ connection closed")
        except Exception as e:
            print(f"✗ Error closing connection: {e}")


class DeviceSimulator:
    """
    Main simulator class
    """
    
    def __init__(self, config_path='config.json', **overrides):
        """
        Initialize simulator
        
        Args:
            config_path: Path to configuration file
            **overrides: Command-line overrides for configuration
        """
        self.config = self.load_config(config_path)
        
        # Apply command-line overrides
        if overrides.get('device_id'):
            self.config['device_id'] = overrides['device_id']
        if overrides.get('interval'):
            self.config['interval_seconds'] = overrides['interval']
        if overrides.get('base_load'):
            self.config['base_load_kwh'] = overrides['base_load']
        if overrides.get('duration'):
            self.config['duration_seconds'] = overrides['duration']
        else:
            self.config['duration_seconds'] = None  # Run indefinitely
        
        # Time acceleration: 1 second real = 10 minutes simulated
        self.time_acceleration = overrides.get('time_acceleration', 1)
        
        # Initialize components
        self.pattern_generator = EnergyPatternGenerator(
            self.config['base_load_kwh'],
            self.config['patterns']
        )
        self.publisher = SimulatorPublisher(self.config['rabbitmq'])
        
        self.running = False
        self.message_count = 0
        self.simulated_time_offset = 0  # Minutes offset from current time
    
    def load_config(self, config_path):
        """Load configuration from JSON file"""
        try:
            config_file = Path(config_path)
            if not config_file.exists():
                print(f"✗ Configuration file not found: {config_path}")
                sys.exit(1)
            
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            # Override RabbitMQ settings from environment variables if present
            if 'RABBITMQ_HOST' in os.environ:
                config['rabbitmq']['host'] = os.environ['RABBITMQ_HOST']
            if 'RABBITMQ_PORT' in os.environ:
                config['rabbitmq']['port'] = int(os.environ['RABBITMQ_PORT'])
            if 'RABBITMQ_USER' in os.environ:
                config['rabbitmq']['user'] = os.environ['RABBITMQ_USER']
            if 'RABBITMQ_PASS' in os.environ:
                config['rabbitmq']['password'] = os.environ['RABBITMQ_PASS']
            
            # Validate required fields
            required_fields = ['device_id', 'interval_seconds', 'base_load_kwh', 'rabbitmq']
            for field in required_fields:
                if field not in config:
                    print(f"✗ Missing required field in config: {field}")
                    sys.exit(1)
            
            return config
            
        except json.JSONDecodeError as e:
            print(f"✗ Invalid JSON in configuration file: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"✗ Error loading configuration: {e}")
            sys.exit(1)
    
    def print_header(self):
        """Print simulator header"""
        print("=" * 70)
        print("  DEVICE DATA SIMULATOR - Energy Management System")
        print("=" * 70)
        print(f"\nConfiguration:")
        print(f"  Device ID:        {self.config['device_id']}")
        print(f"  Interval:         {self.config['interval_seconds']} seconds")
        print(f"  Base Load:        {self.config['base_load_kwh']} kWh")
        if self.time_acceleration > 1:
            print(f"  Time Acceleration: 1 sec = {self.time_acceleration} minutes simulated")
        if self.config.get('duration_seconds'):
            duration = self.config['duration_seconds']
            sim_duration = duration * self.time_acceleration
            print(f"  Duration:         {duration} seconds ({sim_duration} minutes simulated)")
        print(f"  RabbitMQ Host:    {self.config['rabbitmq']['host']}:{self.config['rabbitmq']['port']}")
        print(f"  Queue:            {self.config['rabbitmq']['queue']}")
        print("\nConsumption Patterns:")
        for pattern_name, pattern_data in self.config['patterns'].items():
            hours_str = f"{pattern_data['hours'][0]}-{pattern_data['hours'][-1]}"
            print(f"  {pattern_name.capitalize():10} ({hours_str:5}): {pattern_data['multiplier']}x - {pattern_data['description']}")
        print("\n" + "=" * 70)
    
    def run(self):
        """Main simulator loop"""
        self.print_header()
        
        # Connect to RabbitMQ
        print("\nConnecting to RabbitMQ...")
        if not self.publisher.connect():
            print("✗ Failed to connect. Exiting.")
            sys.exit(1)
        
        duration_msg = f" for {self.config['duration_seconds']} seconds" if self.config.get('duration_seconds') else ""
        print(f"\n✓ Simulator started. Sending measurements every {self.config['interval_seconds']} seconds{duration_msg}")
        print("  Press Ctrl+C to stop\n")
        
        self.running = True
        start_time = time.time()
        
        try:
            while self.running:
                # Calculate simulated time
                elapsed_seconds = time.time() - start_time
                
                # Apply time acceleration: add simulated minutes to current time
                simulated_minutes_offset = int(elapsed_seconds * self.time_acceleration)
                current_time = datetime.now()
                
                # Calculate simulated hour by adding offset
                total_minutes = current_time.hour * 60 + current_time.minute + simulated_minutes_offset
                simulated_hour = (total_minutes // 60) % 24
                simulated_minute = total_minutes % 60
                
                # Create simulated datetime for pattern calculation
                simulated_time = current_time.replace(hour=simulated_hour, minute=simulated_minute)
                
                # Generate measurement based on simulated time
                measurement_value = self.pattern_generator.generate_measurement(simulated_time)
                
                # Get pattern info
                pattern_name, pattern_data = self.pattern_generator.get_pattern_info(simulated_hour)
                
                # Send to RabbitMQ
                success = self.publisher.send_measurement(
                    self.config['device_id'],
                    measurement_value
                )
                
                if success:
                    self.message_count += 1
                    real_time_str = current_time.strftime("%H:%M:%S")
                    sim_time_str = f"{simulated_hour:02d}:{simulated_minute:02d}"
                    print(f"[{self.message_count:4d}] Real: {real_time_str} | Sim: {sim_time_str} | {pattern_name:8} | {measurement_value:.3f} kWh | ✓ Sent")
                else:
                    print(f"[{self.message_count:4d}] {current_time.strftime('%Y-%m-%d %H:%M:%S')} | Failed to send")
                
                # Check if duration limit reached
                if self.config.get('duration_seconds') and elapsed_seconds >= self.config['duration_seconds']:
                    print(f"\n✓ Simulation duration completed ({self.config['duration_seconds']} seconds)")
                    break
                
                # Wait for next interval
                time.sleep(self.config['interval_seconds'])
                
        except KeyboardInterrupt:
            print("\n\n✓ Simulator stopped by user")
        except Exception as e:
            print(f"\n✗ Simulator error: {e}")
        finally:
            self.stop()
    
    def stop(self):
        """Stop simulator and cleanup"""
        self.running = False
        self.publisher.close()
        print(f"\n✓ Total messages sent: {self.message_count}")
        print("=" * 70)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Device Data Simulator for Energy Management System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with default config.json
  python simulator.py
  
  # Override device ID
  python simulator.py --device-id 123e4567-e89b-12d3-a456-426614174000
  
  # Override interval (in seconds)
  python simulator.py --interval 60
  
  # Override base load
  python simulator.py --base-load 0.3
  
  # Use custom config file
  python simulator.py --config my_config.json
        """
    )
    
    parser.add_argument(
        '--config',
        default='config.json',
        help='Path to configuration file (default: config.json)'
    )
    parser.add_argument(
        '--device-id',
        help='Override device ID from config'
    )
    parser.add_argument(
        '--interval',
        type=int,
        help='Override interval in seconds'
    )
    parser.add_argument(
        '--base-load',
        type=float,
        help='Override base load in kWh'
    )
    parser.add_argument(
        '--duration',
        type=int,
        help='Duration to run simulation in seconds (default: run indefinitely)'
    )
    parser.add_argument(
        '--time-acceleration',
        type=int,
        default=1,
        help='Time acceleration factor: 1 second real = X minutes simulated (default: 1)'
    )
    
    args = parser.parse_args()
    
    # Create and run simulator
    simulator = DeviceSimulator(
        config_path=args.config,
        device_id=args.device_id,
        interval=args.interval,
        base_load=args.base_load,
        duration=args.duration,
        time_acceleration=args.time_acceleration
    )
    
    simulator.run()


if __name__ == "__main__":
    main()
