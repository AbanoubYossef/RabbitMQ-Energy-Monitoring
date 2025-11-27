# Device Data Simulator

A standalone Python application that simulates smart meter readings for the Energy Management System. Generates realistic energy consumption patterns and sends measurements to RabbitMQ every 10 minutes (configurable).

## Features

- ✅ **Realistic Consumption Patterns**: Simulates different consumption levels based on time of day
- ✅ **Configurable Device ID**: Easy configuration via JSON file or command-line arguments
- ✅ **RabbitMQ Integration**: Sends measurements to `device_data_queue`
- ✅ **Automatic Reconnection**: Handles RabbitMQ connection failures with exponential backoff
- ✅ **Real-time Logging**: Displays sent measurements with timestamps and patterns

## Installation

### Prerequisites

- Python 3.7 or higher
- RabbitMQ server running (default: localhost:5672)

### Install Dependencies

```bash
cd device_simulator
pip install -r requirements.txt
```

## Configuration

### Configuration File (`config.json`)

```json
{
  "device_id": "4c189959-e674-4eaa-8ebb-98fd953657c5",
  "interval_seconds": 600,
  "base_load_kwh": 0.2,
  "rabbitmq": {
    "host": "localhost",
    "port": 5672,
    "user": "admin",
    "password": "admin123",
    "queue": "device_data_queue"
  },
  "patterns": {
    "night": {
      "hours": [0, 1, 2, 3, 4, 5],
      "multiplier": 0.5,
      "description": "Low consumption during night"
    },
    "morning": {
      "hours": [6, 7, 8],
      "multiplier": 1.2,
      "description": "Moderate-high consumption in morning"
    },
    "day": {
      "hours": [9, 10, 11, 12, 13, 14, 15, 16],
      "multiplier": 0.8,
      "description": "Moderate consumption during day"
    },
    "evening": {
      "hours": [17, 18, 19, 20, 21],
      "multiplier": 1.5,
      "description": "High consumption in evening"
    },
    "late": {
      "hours": [22, 23],
      "multiplier": 0.7,
      "description": "Moderate-low consumption late night"
    }
  }
}
```

### Configuration Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `device_id` | UUID of the device to simulate | Required |
| `interval_seconds` | Time between measurements (seconds) | 600 (10 minutes) |
| `base_load_kwh` | Base energy consumption (kWh) | 0.2 |
| `rabbitmq.host` | RabbitMQ server hostname | localhost |
| `rabbitmq.port` | RabbitMQ server port | 5672 |
| `rabbitmq.user` | RabbitMQ username | admin |
| `rabbitmq.password` | RabbitMQ password | admin123 |
| `rabbitmq.queue` | Queue name for measurements | device_data_queue |

## Usage

### Basic Usage

Run with default configuration:

```bash
python simulator.py
```

### Command-Line Options

Override configuration values:

```bash
# Use specific device ID
python simulator.py --device-id 123e4567-e89b-12d3-a456-426614174000

# Change interval to 60 seconds (1 minute)
python simulator.py --interval 60

# Change base load to 0.3 kWh
python simulator.py --base-load 0.3

# Use custom configuration file
python simulator.py --config my_config.json

# Combine multiple options
python simulator.py --device-id abc123 --interval 300 --base-load 0.25
```

### Get Help

```bash
python simulator.py --help
```

## How It Works

### Consumption Patterns

The simulator generates realistic energy consumption based on time of day:

| Time Period | Hours | Multiplier | Description |
|-------------|-------|------------|-------------|
| **Night** | 0-5 | 0.5x | Low consumption (sleeping) |
| **Morning** | 6-8 | 1.2x | Moderate-high (getting ready) |
| **Day** | 9-16 | 0.8x | Moderate (away/working) |
| **Evening** | 17-21 | 1.5x | High consumption (home activities) |
| **Late Night** | 22-23 | 0.7x | Moderate-low (winding down) |

### Calculation Formula

```
measurement_value = base_load × time_multiplier × random_fluctuation
```

Where:
- `base_load`: Configured base consumption (e.g., 0.2 kWh)
- `time_multiplier`: Pattern multiplier based on hour (0.5x to 1.5x)
- `random_fluctuation`: Random value between 0.9 and 1.1 (±10%)

### Example Output

```
======================================================================
  DEVICE DATA SIMULATOR - Energy Management System
======================================================================

Configuration:
  Device ID:        4c189959-e674-4eaa-8ebb-98fd953657c5
  Interval:         600 seconds (10.0 minutes)
  Base Load:        0.2 kWh
  RabbitMQ Host:    localhost:5672
  Queue:            device_data_queue

Consumption Patterns:
  Night      (0-5  ): 0.5x - Low consumption during night
  Morning    (6-8  ): 1.2x - Moderate-high consumption in morning
  Day        (9-16 ): 0.8x - Moderate consumption during day
  Evening    (17-21): 1.5x - High consumption in evening
  Late       (22-23): 0.7x - Moderate-low consumption late night

======================================================================

Connecting to RabbitMQ...
✓ Connected to RabbitMQ at localhost:5672

✓ Simulator started. Sending measurements every 600 seconds
  Press Ctrl+C to stop

[   1] 2025-11-09 21:45:00 | evening  | 0.294 kWh | ✓ Sent
[   2] 2025-11-09 21:55:00 | evening  | 0.312 kWh | ✓ Sent
[   3] 2025-11-09 22:05:00 | late     | 0.142 kWh | ✓ Sent
```

## Message Format

Messages sent to RabbitMQ have the following JSON format:

```json
{
  "timestamp": "2025-11-09T21:45:00.123456Z",
  "device_id": "4c189959-e674-4eaa-8ebb-98fd953657c5",
  "measurement_value": 0.294
}
```

## Troubleshooting

### Connection Refused

**Problem:** `Connection refused` error when starting simulator

**Solution:**
1. Verify RabbitMQ is running:
   ```bash
   docker ps | grep rabbitmq
   ```
2. Check RabbitMQ is accessible:
   ```bash
   curl http://localhost:15672
   ```
3. Verify credentials in `config.json`

### Invalid Device ID

**Problem:** Device ID not found in system

**Solution:**
1. Get valid device IDs from the API:
   ```bash
   curl http://localhost/api/devices/ -H "Authorization: Bearer YOUR_TOKEN"
   ```
2. Update `device_id` in `config.json` or use `--device-id` argument

### Module Not Found

**Problem:** `ModuleNotFoundError: No module named 'pika'`

**Solution:**
```bash
pip install -r requirements.txt
```

### Permission Denied

**Problem:** `Permission denied` when running simulator

**Solution:**
```bash
chmod +x simulator.py
```

## Testing

### Quick Test (1-minute intervals)

For testing purposes, use a shorter interval:

```bash
python simulator.py --interval 60
```

This will send measurements every minute instead of every 10 minutes.

### Verify Data Flow

1. **Start simulator:**
   ```bash
   python simulator.py
   ```

2. **Check RabbitMQ queue:**
   - Open http://localhost:15672
   - Login with admin/admin123
   - Go to "Queues" tab
   - Check `device_data_queue` for messages

3. **Verify in database:**
   ```bash
   docker exec -it postgres psql -U postgres -d monitoring_db
   SELECT COUNT(*) FROM device_measurements;
   SELECT * FROM device_measurements ORDER BY created_at DESC LIMIT 5;
   ```

4. **Check via API:**
   ```bash
   curl http://localhost/api/monitoring/measurements/ \
     -H "Authorization: Bearer YOUR_TOKEN"
   ```

## Integration with Energy Management System

The simulator integrates with the complete system:

```
Simulator → RabbitMQ → Monitoring Service → PostgreSQL → API → Frontend
```

1. **Simulator** generates measurements every 10 minutes
2. **RabbitMQ** queues messages in `device_data_queue`
3. **Monitoring Service** consumes messages and:
   - Stores raw measurements in `device_measurements` table
   - Aggregates into hourly totals in `hourly_energy_consumption` table
4. **API** provides endpoints to query consumption data
5. **Frontend** displays charts and statistics

## Advanced Usage

### Multiple Devices

Run multiple simulators for different devices:

```bash
# Terminal 1 - Device 1
python simulator.py --device-id device-1-uuid --interval 600

# Terminal 2 - Device 2
python simulator.py --device-id device-2-uuid --interval 600

# Terminal 3 - Device 3
python simulator.py --device-id device-3-uuid --interval 600
```

### Custom Patterns

Create a custom configuration file with different patterns:

```json
{
  "device_id": "your-device-id",
  "interval_seconds": 300,
  "base_load_kwh": 0.5,
  "patterns": {
    "always_high": {
      "hours": [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23],
      "multiplier": 2.0,
      "description": "Always high consumption"
    }
  }
}
```

Then run:
```bash
python simulator.py --config custom_config.json
```

## Requirements

- Python 3.7+
- pika 1.3.2
- python-dateutil 2.8.2

## License

Part of the Energy Management System - Assignment 2

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Verify RabbitMQ is running and accessible
3. Check the monitoring service logs: `docker-compose logs monitoring-service`
4. Verify device ID exists in the system
