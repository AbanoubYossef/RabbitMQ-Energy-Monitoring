# Energy Management System - Microservices Architecture

A distributed energy management system built with microservices architecture, featuring real-time device monitoring, user management, and energy consumption analytics.

## Architecture Overview

This system consists of 6 microservices orchestrated with Docker Compose and Traefik as the API gateway:

```
┌─────────────┐
│   Traefik   │ (API Gateway & Load Balancer)
│   Port 80   │
└──────┬──────┘
       │
       ├──────────────┬──────────────┬──────────────┬──────────────┬──────────────┐
       │              │              │              │              │              │
┌──────▼──────┐ ┌────▼─────┐ ┌──────▼──────┐ ┌────▼─────┐ ┌──────▼──────┐ ┌────▼─────┐
│    Auth     │ │   User   │ │   Device    │ │Monitoring│ │  Frontend   │ │Simulator │
│  Service    │ │ Service  │ │  Service    │ │ Service  │ │   (React)   │ │          │
│  Port 8000  │ │Port 8001 │ │  Port 8002  │ │Port 8003 │ │   Port 80   │ │          │
└──────┬──────┘ └────┬─────┘ └──────┬──────┘ └────┬─────┘ └─────────────┘ └────┬─────┘
       │              │              │              │                             │
       └──────────────┴──────────────┴──────────────┴─────────────────────────────┘
                                     │
                      ┌──────────────┴──────────────┐
                      │                             │
               ┌──────▼──────┐             ┌────────▼────────┐
               │  PostgreSQL │             │    RabbitMQ     │
               │  Port 5432  │             │  Port 5672      │
               │             │             │  Management UI  │
               │  4 Databases│             │  Port 15672     │
               └─────────────┘             └─────────────────┘
```

## Microservices

### 1. Auth Service (Port 8000)
**Technology**: Django REST Framework + JWT

**Responsibilities**:
- User authentication and authorization
- JWT token generation and validation
- User registration with Saga pattern orchestration
- Role-based access control (Admin/Client)

**Key Features**:
- JWT-based authentication with 5-hour access tokens
- Saga pattern for distributed user creation across services
- Password hashing with Django's built-in security
- OpenAPI/Swagger documentation

**Database**: `auth_db` (PostgreSQL)
- Users table with credentials and roles

**API Endpoints**:
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get JWT tokens
- `GET /api/auth/validate` - Validate JWT token
- `GET /api/auth/users` - List all users (Admin only)
- `PUT /api/auth/users/{id}` - Update user (Admin only)
- `DELETE /api/auth/users/{id}` - Delete user (Admin only)

### 2. User Service (Port 8001)
**Technology**: Django REST Framework

**Responsibilities**:
- User profile management
- Extended user information (name, email, phone)
- User synchronization via RabbitMQ events

**Key Features**:
- JWT authentication middleware
- Role-based access control
- Event publishing for user lifecycle (created/updated/deleted)
- Saga compensation for rollback support

**Database**: `user_db` (PostgreSQL)
- Users table with profile information

**API Endpoints**:
- `POST /api/users` - Create user (internal Saga call)
- `GET /api/users` - List all users (Admin only)
- `GET /api/users/{id}` - Get user details
- `PUT /api/users/{id}` - Update user (Admin only)
- `DELETE /api/users/{id}` - Delete user (Admin only)
- `DELETE /api/users/{id}/rollback` - Rollback user creation (Saga)

### 3. Device Service (Port 8002)
**Technology**: Django REST Framework

**Responsibilities**:
- Device management (CRUD operations)
- User-device mapping (many-to-many relationships)
- Device assignment/unassignment
- User synchronization from Auth service

**Key Features**:
- Multiple users can share the same device
- Cascade deletion handling
- Event publishing for device lifecycle
- JWT authentication middleware

**Database**: `device_db` (PostgreSQL)
- Users table (synchronized)
- Devices table
- UserDeviceMapping table (many-to-many)

**API Endpoints**:
- `POST /api/devices` - Create device (Admin only)
- `GET /api/devices` - List devices (filtered by role)
- `GET /api/devices/{id}` - Get device details
- `PUT /api/devices/{id}` - Update device (Admin only)
- `DELETE /api/devices/{id}` - Delete device (Admin only)
- `POST /api/mappings/assign` - Assign device to user (Admin only)
- `DELETE /api/mappings/unassign/{device_id}` - Unassign device (Admin only)
- `GET /api/mappings/user/{user_id}/devices` - Get user's devices
- `GET /api/mappings` - List all mappings

### 4. Monitoring Service (Port 8003)
**Technology**: Django REST Framework

**Responsibilities**:
- Real-time device measurement ingestion
- Hourly energy consumption aggregation
- Historical data queries
- Data synchronization via RabbitMQ

**Key Features**:
- RabbitMQ consumer for device measurements
- Automatic hourly aggregation
- Role-based data access (Admin sees all, Client sees own devices)
- Time-series data management

**Database**: `monitoring_db` (PostgreSQL)
- Users table (synchronized)
- Devices table (synchronized)
- UserDeviceMapping table (synchronized)
- DeviceMeasurement table (raw 10-minute intervals)
- HourlyEnergyConsumption table (aggregated data)

**API Endpoints**:
- `GET /api/monitoring/measurements` - List measurements (filtered by role)
- `GET /api/monitoring/hourly/daily` - Get hourly data for a specific date
- `GET /api/monitoring/hourly/range` - Get data for a date range
- `GET /api/monitoring/devices` - List synchronized devices
- `GET /api/monitoring/users` - List synchronized users

**RabbitMQ Consumers**:
- `device_data_queue` - Ingests device measurements
- `sync_queue` - Synchronizes user/device/mapping data

### 5. Frontend (Port 80 via Traefik)
**Technology**: React 19 + TypeScript + Vite + TailwindCSS

**Features**:
- Modern responsive UI with TailwindCSS
- JWT-based authentication with context management
- Role-based routing and component rendering
- Real-time data visualization with Recharts

**Pages**:
- Login/Register
- Dashboard (role-specific)
- User Management (Admin only)
- Device Management (Admin only)
- Device Monitoring (hourly/daily charts)
- Device Assignment (Admin only)

**Key Libraries**:
- `axios` - HTTP client
- `react-router-dom` - Routing
- `recharts` - Data visualization
- `react-hook-form` - Form management
- `jwt-decode` - JWT token parsing
- `date-fns` - Date formatting

### 6. Device Simulator
**Technology**: Python + Pika (RabbitMQ client)

**Responsibilities**:
- Simulate smart meter readings
- Generate realistic energy consumption patterns
- Publish measurements to RabbitMQ

**Key Features**:
- Time-based consumption patterns (night/morning/day/evening/late)
- Configurable base load and intervals
- Time acceleration for testing (1 sec = X minutes simulated)
- Automatic reconnection to RabbitMQ

**Consumption Patterns**:
- Night (0-5h): 0.5x multiplier - Low consumption
- Morning (6-8h): 1.2x multiplier - Moderate-high consumption
- Day (9-16h): 0.8x multiplier - Moderate consumption
- Evening (17-21h): 1.5x multiplier - High consumption (peak)
- Late (22-23h): 0.7x multiplier - Moderate-low consumption

**Configuration**: `device_simulator/config.json`

## Infrastructure Components

### PostgreSQL (Port 5432)
- 4 separate databases for service isolation
- Automatic initialization via `init-databases.sh`
- Persistent volumes for data retention

**Databases**:
- `auth_db` - Authentication service
- `user_db` - User service
- `device_db` - Device service
- `monitoring_db` - Monitoring service

### RabbitMQ (Port 5672, Management UI: 15672)
- Message broker for asynchronous communication
- Event-driven architecture
- Persistent message queues

**Queues**:
- `device_data_queue` - Device measurements from simulator
- `sync_queue` - User/device/mapping synchronization events

**Event Types**:
- `user_created`, `user_updated`, `user_deleted`
- `device_created`, `device_updated`, `device_deleted`
- `device_assigned`, `device_unassigned`

### Traefik (Port 80, Dashboard: 8080)
- API Gateway and reverse proxy
- Automatic service discovery via Docker labels
- Load balancing and routing

**Routing Rules**:
- `/api/auth/*` → Auth Service
- `/api/users/*` → User Service
- `/api/devices/*`, `/api/mappings/*` → Device Service
- `/api/monitoring/*` → Monitoring Service
- `/*` → Frontend (lowest priority)

## Design Patterns

### 1. Saga Pattern
Used for distributed transactions across microservices:
- **User Registration**: Auth → User → Device services
- **User Update**: Auth → User → Device services
- **User Deletion**: Auth → User → Device services
- Automatic compensation (rollback) on failure

### 2. Event-Driven Architecture
- Services publish events to RabbitMQ
- Consumers react to events asynchronously
- Loose coupling between services

### 3. Database per Service
- Each microservice has its own database
- Data isolation and independence
- Synchronization via events

### 4. API Gateway Pattern
- Traefik as single entry point
- Centralized routing and load balancing
- Service discovery via Docker labels

## Getting Started

### Prerequisites
- Docker Desktop
- Docker Compose
- Git

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd <project-directory>
```

2. Configure environment variables:
```bash
# Edit .env file
JWT_SECRET_KEY=my-super-secret-key-change-in-production-123456
```

3. Start all services:
```bash
docker-compose up -d
```

4. Wait for services to be healthy:
```bash
docker-compose ps
```

5. Access the application:
- Frontend: http://localhost
- Traefik Dashboard: http://localhost:8080
- RabbitMQ Management: http://localhost:15672 (admin/admin123)

### Default Users

The system comes with pre-configured users:

**Admin User**:
- Username: `admin`
- Password: `admin123`
- Role: Admin (full access)

**Client Users**:
- Username: `alice` / Password: `alice123`
- Username: `bob` / Password: `bob123`
- Role: Client (limited access)

## API Documentation

Each service provides OpenAPI/Swagger documentation:

- Auth Service: http://localhost:8000/api/docs/
- User Service: http://localhost:8001/api/docs/
- Device Service: http://localhost:8002/api/docs/
- Monitoring Service: http://localhost:8003/api/docs/

## Development

### Rebuild All Services
```powershell
.\rebuild_all.ps1
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f auth-service
docker-compose logs -f device-simulator
```

### Stop Services
```bash
docker-compose down
```

### Reset Everything (including data)
```bash
docker-compose down -v
docker-compose up -d
```

## Testing

### Device Simulator Configuration

Edit `device_simulator/config.json` to customize:
- `device_id` - UUID of the device to simulate
- `interval_seconds` - Measurement interval (default: 1 second)
- `base_load_kwh` - Base energy consumption (default: 0.2 kWh)
- `time_acceleration` - Speed up time for testing

### Manual Testing Flow

1. Login as admin
2. Create a new device
3. Create a new user (or use existing client)
4. Assign device to user
5. Update simulator config with device ID
6. Restart simulator: `docker-compose restart device-simulator`
7. View measurements in monitoring dashboard

## Technology Stack

### Backend
- **Framework**: Django 5.0 + Django REST Framework 3.14
- **Authentication**: JWT (djangorestframework-simplejwt)
- **Database**: PostgreSQL 15
- **Message Broker**: RabbitMQ 3.13
- **API Gateway**: Traefik 3.2
- **Documentation**: drf-spectacular (OpenAPI 3.0)

### Frontend
- **Framework**: React 19
- **Language**: TypeScript 5.9
- **Build Tool**: Vite 7
- **Styling**: TailwindCSS 4
- **Charts**: Recharts 2
- **HTTP Client**: Axios
- **Routing**: React Router DOM 7

### DevOps
- **Containerization**: Docker
- **Orchestration**: Docker Compose
- **Web Server**: Nginx (for frontend)

## Security Features

- JWT-based authentication with secure token signing
- Password hashing with Django's PBKDF2 algorithm
- Role-based access control (RBAC)
- CORS configuration for frontend-backend communication
- Environment variable management for secrets
- Service isolation with separate databases

## Performance Considerations

- Database indexing on frequently queried fields
- Connection pooling for database connections
- Message queue for asynchronous processing
- Hourly aggregation to reduce query load
- Persistent RabbitMQ messages for reliability

## Monitoring & Observability

- RabbitMQ Management UI for queue monitoring
- Traefik Dashboard for routing visualization
- Docker logs for debugging
- Database query logging (DEBUG mode)

## Future Enhancements

- [ ] Add Redis for caching
- [ ] Implement rate limiting
- [ ] Add Prometheus + Grafana for metrics
- [ ] Implement WebSocket for real-time updates
- [ ] Add unit and integration tests
- [ ] Implement CI/CD pipeline
- [ ] Add API versioning
- [ ] Implement data backup strategy
- [ ] Add email notifications
- [ ] Implement audit logging

## License

[Specify your license here]

## Contributors

[Add contributors here]
