# Design Document - Assignment 2 Completion

## Overview

This design document outlines the technical approach for implementing the remaining 30% of Assignment 2. The implementation focuses on event-driven synchronization, realistic data simulation, user-friendly visualization, and comprehensive documentation.

## Architecture

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (React)                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ Device       │  │ Date Picker  │  │ Energy       │         │
│  │ Selector     │  │ Calendar     │  │ Charts       │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP/REST
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Traefik (Reverse Proxy)                       │
└──────┬──────────────┬──────────────┬──────────────┬────────────┘
       │              │              │              │
       ▼              ▼              ▼              ▼
┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐
│   Auth     │ │   User     │ │  Device    │ │ Monitoring │
│  Service   │ │  Service   │ │  Service   │ │  Service   │
│            │ │            │ │            │ │            │
│ +RabbitMQ  │ │            │ │ +RabbitMQ  │ │ +RabbitMQ  │
│ Publisher  │ │            │ │ Publisher  │ │ Consumers  │
└─────┬──────┘ └────────────┘ └─────┬──────┘ └─────┬──────┘
      │                              │              │
      │         Publish Events       │              │
      └──────────────┬───────────────┘              │
                     ▼                               │
              ┌─────────────┐                       │
              │  RabbitMQ   │                       │
              │             │                       │
              │ sync_queue  │◄──────────────────────┘
              │ device_data │◄──────────────────────┐
              │ _queue      │                       │
              └─────────────┘                       │
                     ▲                               │
                     │                               │
              ┌──────┴──────┐                       │
              │  Simulator  │                       │
              │  (Python)   │                       │
              │             │                       │
              │ Generates   │                       │
              │ Realistic   │                       │
              │ Patterns    │                       │
              └─────────────┘                       │
                                                     │
┌────────────────────────────────────────────────────┘
│                  PostgreSQL
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
│  │ auth_db  │  │ user_db  │  │device_db │  │monitoring│
│  │          │  │          │  │          │  │   _db    │
│  │ +users   │  │          │  │ +users   │  │ +users   │
│  │          │  │          │  │          │  │ +devices │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘
```

## Components and Interfaces

### 1. User Synchronization Component

#### Auth Service Publisher

**File:** `auth_service/authentication/rabbitmq.py`

```python
class RabbitMQPublisher:
    def __init__(self):
        self.connection = None
        self.channel = None
    
    def connect(self):
        """Establish connection to RabbitMQ"""
        credentials = pika.PlainCredentials(
            settings.RABBITMQ_USER,
            settings.RABBITMQ_PASS
        )
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=settings.RABBITMQ_HOST,
                port=settings.RABBITMQ_PORT,
                credentials=credentials
            )
        )
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='sync_queue', durable=True)
    
    def publish_user_created(self, user_data):
        """Publish user creation event"""
        message = {
            "event_type": "user_created",
            "data": {
                "id": str(user_data['id']),
                "username": user_data['username'],
                "role": user_data['role']
            }
        }
        self.channel.basic_publish(
            exchange='',
            routing_key='sync_queue',
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=2)
        )
    
    def publish_user_deleted(self, user_id):
        """Publish user deletion event"""
        message = {
            "event_type": "user_deleted",
            "data": {"id": str(user_id)}
        }
        self.channel.basic_publish(
            exchange='',
            routing_key='sync_queue',
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=2)
        )
    
    def close(self):
        """Close connection"""
        if self.connection:
            self.connection.close()
```

**Integration Point:** Call `publish_user_created()` after successful user creation in `views.py`

#### Device Service Consumer

**File:** `device_service/devices/consumers.py`

```python
class UserSyncConsumer:
    def __init__(self):
        self.connection = None
        self.channel = None
    
    def callback(self, ch, method, properties, body):
        """Process sync messages"""
        try:
            message = json.loads(body)
            event_type = message.get('event_type')
            data = message.get('data')
            
            if event_type == 'user_created':
                self.handle_user_created(data)
            elif event_type == 'user_deleted':
                self.handle_user_deleted(data)
            
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            logger.error(f"Error processing sync message: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
    
    def handle_user_created(self, data):
        """Create user in local database"""
        User.objects.get_or_create(
            id=data['id'],
            defaults={
                'username': data['username'],
                'role': data['role']
            }
        )
    
    def handle_user_deleted(self, data):
        """Delete user from local database"""
        User.objects.filter(id=data['id']).delete()
    
    def start_consuming(self):
        """Start consuming messages"""
        self.connection = get_rabbitmq_connection()
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='sync_queue', durable=True)
        self.channel.basic_consume(
            queue='sync_queue',
            on_message_callback=self.callback
        )
        self.channel.start_consuming()
```

### 2. Device Synchronization Component

#### Device Service Publisher

**File:** `device_service/devices/rabbitmq.py`

```python
class DeviceSyncPublisher:
    def publish_device_created(self, device_data):
        """Publish device creation event"""
        message = {
            "event_type": "device_created",
            "data": {
                "id": str(device_data['id']),
                "name": device_data['name'],
                "description": device_data.get('description', ''),
                "max_consumption": device_data['max_consumption']
            }
        }
        # Publish to sync_queue
    
    def publish_device_updated(self, device_data):
        """Publish device update event"""
        message = {
            "event_type": "device_updated",
            "data": {
                "id": str(device_data['id']),
                "name": device_data['name'],
                "description": device_data.get('description', ''),
                "max_consumption": device_data['max_consumption']
            }
        }
        # Publish to sync_queue
    
    def publish_device_deleted(self, device_id):
        """Publish device deletion event"""
        message = {
            "event_type": "device_deleted",
            "data": {"id": str(device_id)}
        }
        # Publish to sync_queue
```

**Integration Point:** Call after device CRUD operations in `views.py`

### 3. Device Data Simulator

#### Project Structure

```
device_simulator/
├── simulator.py          # Main application
├── config.json          # Configuration file
├── requirements.txt     # Dependencies
└── README.md           # Usage instructions
```

#### Configuration Schema

**File:** `device_simulator/config.json`

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
    "night": {"hours": [0, 1, 2, 3, 4, 5], "multiplier": 0.5},
    "morning": {"hours": [6, 7, 8], "multiplier": 1.2},
    "day": {"hours": [9, 10, 11, 12, 13, 14, 15, 16], "multiplier": 0.8},
    "evening": {"hours": [17, 18, 19, 20, 21], "multiplier": 1.5},
    "late": {"hours": [22, 23], "multiplier": 0.7}
  }
}
```

#### Simulator Algorithm

```python
class EnergyPatternGenerator:
    def generate_measurement(self, hour, base_load):
        """Generate realistic measurement based on time of day"""
        
        # Determine pattern multiplier
        if 0 <= hour < 6:
            multiplier = 0.5  # Night: low consumption
        elif 6 <= hour < 9:
            multiplier = 1.2  # Morning: moderate-high
        elif 9 <= hour < 17:
            multiplier = 0.8  # Day: moderate
        elif 17 <= hour < 22:
            multiplier = 1.5  # Evening: high consumption
        else:
            multiplier = 0.7  # Late night: moderate-low
        
        # Add random fluctuation (±10%)
        fluctuation = random.uniform(0.9, 1.1)
        
        # Calculate final value
        value = base_load * multiplier * fluctuation
        
        return round(value, 3)
```

### 4. Frontend Energy Visualization

#### Component Structure

```
frontend/src/
├── pages/
│   └── EnergyDashboard.tsx      # Main dashboard page
├── components/
│   ├── DeviceSelector.tsx       # Device dropdown
│   ├── DatePicker.tsx           # Date selection
│   ├── EnergyBarChart.tsx       # Bar chart component
│   ├── EnergyLineChart.tsx      # Line chart component
│   └── SummaryCards.tsx         # Statistics cards
└── services/
    └── monitoringApi.ts         # API client
```

#### API Client

**File:** `frontend/src/services/monitoringApi.ts`

```typescript
export const monitoringApi = {
  async getDailyConsumption(deviceId: string, date: string, token: string) {
    const response = await fetch(
      `/api/monitoring/hourly/daily/?device_id=${deviceId}&date=${date}`,
      {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      }
    );
    
    if (!response.ok) {
      throw new Error('Failed to fetch consumption data');
    }
    
    return response.json();
  }
};
```

#### Chart Component

**File:** `frontend/src/components/EnergyBarChart.tsx`

```typescript
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';

interface EnergyBarChartProps {
  data: Array<{hour: number, total_consumption: number}>;
}

export const EnergyBarChart: React.FC<EnergyBarChartProps> = ({ data }) => {
  return (
    <BarChart width={800} height={400} data={data}>
      <CartesianGrid strokeDasharray="3 3" />
      <XAxis 
        dataKey="hour" 
        label={{ value: 'Hour of Day', position: 'insideBottom', offset: -5 }}
      />
      <YAxis 
        label={{ value: 'Energy (kWh)', angle: -90, position: 'insideLeft' }}
      />
      <Tooltip />
      <Legend />
      <Bar dataKey="total_consumption" fill="#8884d8" name="Consumption (kWh)" />
    </BarChart>
  );
};
```

## Data Models

### Sync Message Format

```typescript
// User Created Event
{
  "event_type": "user_created",
  "data": {
    "id": "uuid",
    "username": "string",
    "role": "string"
  }
}

// Device Created Event
{
  "event_type": "device_created",
  "data": {
    "id": "uuid",
    "name": "string",
    "description": "string",
    "max_consumption": number
  }
}

// Device Measurement
{
  "timestamp": "ISO8601",
  "device_id": "uuid",
  "measurement_value": number
}
```

## Error Handling

### RabbitMQ Connection Errors

1. **Connection Failure:** Retry with exponential backoff (1s, 2s, 4s, 8s, max 30s)
2. **Message Processing Error:** Log error, nack message with requeue=True
3. **Invalid Message Format:** Log error, ack message (don't requeue)

### API Errors

1. **Authentication Failure:** Redirect to login page
2. **No Data Available:** Display friendly message "No data available for selected date"
3. **Network Error:** Display retry button with error message

### Simulator Errors

1. **Configuration Error:** Exit with clear error message
2. **RabbitMQ Connection Error:** Retry connection every 5 seconds
3. **Invalid Device ID:** Exit with error message

## Testing Strategy

### Unit Tests

1. **RabbitMQ Publishers:** Test message format and publishing
2. **Consumers:** Test message processing logic
3. **Simulator:** Test pattern generation algorithm
4. **Frontend Components:** Test rendering and user interactions

### Integration Tests

1. **End-to-End Sync:** Create user → Verify in all services
2. **Device Data Flow:** Simulator → RabbitMQ → Monitoring → API
3. **Frontend Integration:** API calls → Chart rendering

### Manual Testing

1. **User Sync:** Create/delete users, verify synchronization
2. **Device Sync:** Create/delete devices, verify synchronization
3. **Simulator:** Run for 1 hour, verify data accuracy
4. **Charts:** Test with various date ranges and devices

## Performance Considerations

1. **Message Processing:** Process messages asynchronously to avoid blocking
2. **Database Queries:** Use indexes on device_id and timestamp fields
3. **Chart Rendering:** Limit data points to 24 hours maximum
4. **API Response Time:** Cache frequently accessed data

## Security Considerations

1. **JWT Validation:** All API endpoints require valid JWT token
2. **User Authorization:** Users can only view their own devices
3. **RabbitMQ Credentials:** Store in environment variables
4. **Input Validation:** Validate all user inputs and message data
