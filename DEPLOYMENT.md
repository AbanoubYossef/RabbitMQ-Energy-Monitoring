# Energy Management System - Deployment Documentation

## UML Deployment Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              Deployment Environment                                  │
│                                                                                      │
│  ┌────────────────────────────────────────────────────────────────────────────┐    │
│  │                          Docker Host (Physical/VM)                          │    │
│  │                                                                              │    │
│  │  ┌──────────────────────────────────────────────────────────────────────┐  │    │
│  │  │                    Docker Network: microservices-network              │  │    │
│  │  │                                                                        │  │    │
│  │  │  ┌─────────────────────────────────────────────────────────────┐     │  │    │
│  │  │  │  <<Container>>                                               │     │  │    │
│  │  │  │  Traefik API Gateway                                         │     │  │    │
│  │  │  │  ┌────────────────────────────────────────────────┐         │     │  │    │
│  │  │  │  │ <<Artifact>>                                    │         │     │  │    │
│  │  │  │  │ traefik:v3.2                                    │         │     │  │    │
│  │  │  │  │ - HTTP Router                                   │         │     │  │    │
│  │  │  │  │ - Load Balancer                                 │         │     │  │    │
│  │  │  │  │ - Service Discovery                             │         │     │  │    │
│  │  │  │  └────────────────────────────────────────────────┘         │     │  │    │
│  │  │  │  Ports: 80 (HTTP), 8080 (Dashboard)                         │     │  │    │
│  │  │  └──────────────────┬──────────────────────────────────────────┘     │  │    │
│  │  │                     │                                                 │  │    │
│  │  │  ┌──────────────────┼─────────────────────────────────────────┐     │  │    │
│  │  │  │                  │  Application Layer                       │     │  │    │
│  │  │  │                  │                                          │     │  │    │
│  │  │  │  ┌───────────────▼──────────┐  ┌──────────────────────┐   │     │  │    │
│  │  │  │  │ <<Container>>             │  │ <<Container>>         │   │     │  │    │
│  │  │  │  │ Auth Service              │  │ User Service          │   │     │  │    │
│  │  │  │  │ ┌──────────────────────┐ │  │ ┌─────────────────┐  │   │     │  │    │
│  │  │  │  │ │ <<Artifact>>          │ │  │ │ <<Artifact>>     │  │   │     │  │    │
│  │  │  │  │ │ Django 5.0            │ │  │ │ Django 5.0       │  │   │     │  │    │
│  │  │  │  │ │ DRF 3.14              │ │  │ │ DRF 3.14         │  │   │     │  │    │
│  │  │  │  │ │ JWT Auth              │ │  │ │ Profile Mgmt     │  │   │     │  │    │
│  │  │  │  │ │ Saga Orchestrator     │ │  │ │ Event Consumer   │  │   │     │  │    │
│  │  │  │  │ └──────────────────────┘ │  │ └─────────────────┘  │   │     │  │    │
│  │  │  │  │ Port: 8000                │  │ Port: 8001           │   │     │  │    │
│  │  │  │  └───────────┬───────────────┘  └──────────┬───────────┘   │     │  │    │
│  │  │  │              │                              │               │     │  │    │
│  │  │  │  ┌───────────▼──────────┐  ┌───────────────▼──────────┐   │     │  │    │
│  │  │  │  │ <<Container>>         │  │ <<Container>>             │   │     │  │    │
│  │  │  │  │ Device Service        │  │ Monitoring Service        │   │     │  │    │
│  │  │  │  │ ┌──────────────────┐ │  │ ┌──────────────────────┐  │   │     │  │    │
│  │  │  │  │ │ <<Artifact>>      │ │  │ │ <<Artifact>>          │  │   │     │  │    │
│  │  │  │  │ │ Django 5.0        │ │  │ │ Django 5.0            │  │   │     │  │    │
│  │  │  │  │ │ DRF 3.14          │ │  │ │ DRF 3.14              │  │   │     │  │    │
│  │  │  │  │ │ Device CRUD       │ │  │ │ Time-series Data      │  │   │     │  │    │
│  │  │  │  │ │ Mapping Mgmt      │ │  │ │ Aggregation Engine    │  │   │     │  │    │
│  │  │  │  │ │ Event Consumer    │ │  │ │ RabbitMQ Consumer     │  │   │     │  │    │
│  │  │  │  │ └──────────────────┘ │  │ └──────────────────────┘  │   │     │  │    │
│  │  │  │  │ Port: 8002            │  │ Port: 8003                │   │     │  │    │
│  │  │  │  └───────────┬───────────┘  └──────────┬────────────────┘   │     │  │    │
│  │  │  │              │                         │                    │     │  │    │
│  │  │  │  ┌───────────▼─────────────────────────▼──────────────┐    │     │  │    │
│  │  │  │  │ <<Container>>                                       │    │     │  │    │
│  │  │  │  │ Frontend                                            │    │     │  │    │
│  │  │  │  │ ┌────────────────────────────────────────────────┐ │    │     │  │    │
│  │  │  │  │ │ <<Artifact>>                                    │ │    │     │  │    │
│  │  │  │  │ │ React 19 + TypeScript                           │ │    │     │  │    │
│  │  │  │  │ │ Vite 7 Build                                    │ │    │     │  │    │
│  │  │  │  │ │ TailwindCSS 4                                   │ │    │     │  │    │
│  │  │  │  │ │ Nginx Web Server                                │ │    │     │  │    │
│  │  │  │  │ └────────────────────────────────────────────────┘ │    │     │  │    │
│  │  │  │  │ Port: 80                                            │    │     │  │    │
│  │  │  │  └─────────────────────────────────────────────────────┘    │     │  │    │
│  │  │  │                                                              │     │  │    │
│  │  │  └──────────────────────────────────────────────────────────────┘     │  │    │
│  │  │                                                                        │  │    │
│  │  │  ┌──────────────────────────────────────────────────────────────┐    │  │    │
│  │  │  │                    Data & Messaging Layer                     │    │  │    │
│  │  │  │                                                               │    │  │    │
│  │  │  │  ┌────────────────────────────┐  ┌──────────────────────┐   │    │  │    │
│  │  │  │  │ <<Container>>               │  │ <<Container>>         │   │    │  │    │
│  │  │  │  │ PostgreSQL                  │  │ RabbitMQ              │   │    │  │    │
│  │  │  │  │ ┌────────────────────────┐ │  │ ┌─────────────────┐  │   │    │  │    │
│  │  │  │  │ │ <<Artifact>>            │ │  │ │ <<Artifact>>     │  │   │    │  │    │
│  │  │  │  │ │ postgres:15-alpine      │ │  │ │ rabbitmq:3.13    │  │   │    │  │    │
│  │  │  │  │ │                         │ │  │ │ -management      │  │   │    │  │    │
│  │  │  │  │ │ Databases:              │ │  │ │                  │  │   │    │  │    │
│  │  │  │  │ │ - auth_db               │ │  │ │ Queues:          │  │   │    │  │    │
│  │  │  │  │ │ - user_db               │ │  │ │ - device_data    │  │   │    │  │    │
│  │  │  │  │ │ - device_db             │ │  │ │ - sync_queue     │  │   │    │  │    │
│  │  │  │  │ │ - monitoring_db         │ │  │ │                  │  │   │    │  │    │
│  │  │  │  │ └────────────────────────┘ │  │ └─────────────────┘  │   │    │  │    │
│  │  │  │  │ Port: 5432                  │  │ Ports: 5672, 15672   │   │    │  │    │
│  │  │  │  │ Volume: postgres_data       │  │ Volume: rabbitmq_data│   │    │  │    │
│  │  │  │  └────────────────────────────┘  └──────────────────────┘   │    │  │    │
│  │  │  │                                                               │    │  │    │
│  │  │  └───────────────────────────────────────────────────────────────┘    │  │    │
│  │  │                                                                        │  │    │
│  │  │  ┌──────────────────────────────────────────────────────────────┐    │  │    │
│  │  │  │                    Simulation Layer                           │    │  │    │
│  │  │  │                                                               │    │  │    │
│  │  │  │  ┌────────────────────────────────────────────────────────┐  │    │  │    │
│  │  │  │  │ <<Container>>                                           │  │    │  │    │
│  │  │  │  │ Device Simulator                                        │  │    │  │    │
│  │  │  │  │ ┌────────────────────────────────────────────────────┐ │  │    │  │    │
│  │  │  │  │ │ <<Artifact>>                                        │ │  │    │  │    │
│  │  │  │  │ │ Python 3.11                                         │ │  │    │  │    │
│  │  │  │  │ │ Pika (RabbitMQ Client)                              │ │  │    │  │    │
│  │  │  │  │ │ - Simulates smart meter readings                    │ │  │    │  │    │
│  │  │  │  │ │ - Time-based consumption patterns                   │ │  │    │  │    │
│  │  │  │  │ │ - Publishes to device_data_queue                    │ │  │    │  │    │
│  │  │  │  │ └────────────────────────────────────────────────────┘ │  │    │  │    │
│  │  │  │  │ No exposed ports                                        │  │    │  │    │
│  │  │  │  └────────────────────────────────────────────────────────┘  │    │  │    │
│  │  │  │                                                               │    │  │    │
│  │  │  └───────────────────────────────────────────────────────────────┘    │  │    │
│  │  │                                                                        │  │    │
│  │  └────────────────────────────────────────────────────────────────────────┘  │    │
│  │                                                                              │    │
│  └──────────────────────────────────────────────────────────────────────────────┘    │
│                                                                                      │
└─────────────────────────────────────────────────────────────────────────────────────┘

                                    ┌──────────────┐
                                    │   Client     │
                                    │   Browser    │
                                    └──────┬───────┘
                                           │
                                           │ HTTP/HTTPS
                                           │
                                           ▼
                                    Port 80 (Traefik)
```

## Component Communication Flow

```
┌──────────┐                    ┌──────────┐                    ┌──────────┐
│  Client  │───── HTTP ────────▶│ Traefik  │───── HTTP ────────▶│ Services │
│ Browser  │◀──── Response ─────│ Gateway  │◀──── Response ─────│ (Django) │
└──────────┘                    └──────────┘                    └────┬─────┘
                                                                     │
                                                                     │ SQL
                                                                     ▼
                                                              ┌──────────────┐
                                                              │  PostgreSQL  │
                                                              │  (4 DBs)     │
                                                              └──────────────┘

┌──────────────┐                ┌──────────┐                 ┌──────────────┐
│   Device     │─── Publish ───▶│ RabbitMQ │─── Consume ────▶│ Monitoring   │
│  Simulator   │                │  Broker  │                 │   Service    │
└──────────────┘                └────┬─────┘                 └──────────────┘
                                     │
                                     │ Publish/Subscribe
                                     ▼
                              ┌──────────────┐
                              │ Auth/User/   │
                              │ Device       │
                              │ Services     │
                              └──────────────┘
```

## Deployment Architecture Details

### Node: Docker Host
- **Type**: Physical server, Virtual Machine, or Cloud Instance
- **OS**: Linux (recommended), Windows, or macOS
- **Requirements**: 
  - Docker Engine 20.10+
  - Docker Compose 2.0+
  - Minimum 4GB RAM
  - Minimum 20GB disk space

### Network: microservices-network
- **Type**: Bridge network
- **Purpose**: Internal communication between containers
- **Isolation**: Services communicate only within this network
- **DNS**: Automatic service discovery by container name

### Execution Environment: Docker Containers

#### Container 1: Traefik (API Gateway)
- **Image**: traefik:v3.2
- **Purpose**: Reverse proxy, load balancer, API gateway
- **Exposed Ports**: 
  - 80 → HTTP traffic
  - 8080 → Dashboard UI
- **Configuration**: Dynamic via Docker labels
- **Dependencies**: None (entry point)

#### Container 2: Auth Service
- **Base Image**: python:3.11-slim
- **Runtime**: Django 5.0 + Gunicorn
- **Exposed Port**: 8000
- **Dependencies**: PostgreSQL, RabbitMQ
- **Database**: auth_db
- **Environment Variables**: JWT_SECRET_KEY, DB credentials

#### Container 3: User Service
- **Base Image**: python:3.11-slim
- **Runtime**: Django 5.0 + Gunicorn
- **Exposed Port**: 8001
- **Dependencies**: PostgreSQL, RabbitMQ
- **Database**: user_db
- **Event Consumers**: user_created, user_updated, user_deleted

#### Container 4: Device Service
- **Base Image**: python:3.11-slim
- **Runtime**: Django 5.0 + Gunicorn
- **Exposed Port**: 8002
- **Dependencies**: PostgreSQL, RabbitMQ
- **Database**: device_db
- **Event Consumers**: user/device lifecycle events

#### Container 5: Monitoring Service
- **Base Image**: python:3.11-slim
- **Runtime**: Django 5.0 + Gunicorn
- **Exposed Port**: 8003
- **Dependencies**: PostgreSQL, RabbitMQ
- **Database**: monitoring_db
- **Event Consumers**: device_data_queue, sync_queue

#### Container 6: Frontend
- **Base Image**: node:20-alpine (build), nginx:alpine (runtime)
- **Build**: Vite production build
- **Runtime**: Nginx web server
- **Exposed Port**: 80 (internal)
- **Static Assets**: Optimized React bundle

#### Container 7: PostgreSQL
- **Image**: postgres:15-alpine
- **Exposed Port**: 5432
- **Persistent Volume**: postgres_data
- **Databases**: 4 isolated databases
- **Initialization**: init-databases.sh script

#### Container 8: RabbitMQ
- **Image**: rabbitmq:3.13-management-alpine
- **Exposed Ports**: 
  - 5672 → AMQP protocol
  - 15672 → Management UI
- **Persistent Volume**: rabbitmq_data
- **Queues**: device_data_queue, sync_queue

#### Container 9: Device Simulator
- **Base Image**: python:3.11-slim
- **Runtime**: Python script with Pika
- **No Exposed Ports**: Internal only
- **Dependencies**: RabbitMQ
- **Configuration**: config.json

## Deployment Patterns

### 1. Database per Service Pattern
Each microservice has its own isolated database:
- **auth_db**: User credentials, roles
- **user_db**: User profiles
- **device_db**: Devices, mappings
- **monitoring_db**: Measurements, aggregations

### 2. API Gateway Pattern
Traefik acts as single entry point:
- Routes requests based on path prefixes
- Provides load balancing
- Enables service discovery
- Centralizes SSL termination (if configured)

### 3. Event-Driven Communication
Services communicate asynchronously via RabbitMQ:
- Loose coupling between services
- Eventual consistency
- Resilience to service failures
- Scalability

### 4. Saga Pattern for Distributed Transactions
Auth service orchestrates multi-service operations:
- User registration spans Auth → User → Device services
- Automatic rollback on failure
- Maintains data consistency

## Scalability Considerations

### Horizontal Scaling
Each service can be scaled independently:
```yaml
docker-compose up -d --scale auth-service=3 --scale device-service=2
```

### Load Balancing
Traefik automatically load balances across service instances.

### Database Scaling
- Read replicas for PostgreSQL
- Connection pooling
- Query optimization with indexes

### Message Queue Scaling
- RabbitMQ clustering for high availability
- Multiple consumers per queue
- Message persistence

## High Availability

### Service Health Checks
```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U postgres"]
  interval: 10s
  timeout: 5s
  retries: 5
```

### Automatic Restart
```yaml
restart: unless-stopped
```

### Data Persistence
- PostgreSQL: postgres_data volume
- RabbitMQ: rabbitmq_data volume
- Survives container restarts

## Security Architecture

### Network Isolation
- Services communicate only within Docker network
- No direct external access to databases
- Traefik as controlled entry point

### Authentication & Authorization
- JWT tokens with expiration
- Role-based access control (Admin/Client)
- Password hashing (PBKDF2)

### Environment Variables
- Secrets stored in .env files
- Not committed to version control
- Injected at runtime

### CORS Configuration
- Restricted origins
- Credential support
- Method whitelisting

## Monitoring & Logging

### Container Logs
```bash
docker-compose logs -f [service-name]
```

### RabbitMQ Management UI
- Queue monitoring
- Message rates
- Consumer status
- URL: http://localhost:15672

### Traefik Dashboard
- Service health
- Request routing
- Traffic metrics
- URL: http://localhost:8080

### Database Monitoring
- Connection pooling stats
- Query performance (DEBUG mode)
- Disk usage monitoring

## Backup & Recovery

### Database Backup
```bash
docker exec postgres pg_dump -U postgres auth_db > auth_db_backup.sql
docker exec postgres pg_dump -U postgres user_db > user_db_backup.sql
docker exec postgres pg_dump -U postgres device_db > device_db_backup.sql
docker exec postgres pg_dump -U postgres monitoring_db > monitoring_db_backup.sql
```

### Database Restore
```bash
docker exec -i postgres psql -U postgres auth_db < auth_db_backup.sql
```

### Volume Backup
```bash
docker run --rm -v postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_backup.tar.gz /data
```

## Disaster Recovery

### Complete System Reset
```bash
docker-compose down -v
docker-compose up -d
```

### Service Recovery
```bash
docker-compose restart [service-name]
```

### Data Recovery
1. Stop services
2. Restore volume from backup
3. Restart services

## Performance Optimization

### Database Indexing
- Primary keys on all tables
- Foreign key indexes
- Composite indexes for common queries

### Caching Strategy
- Django query caching
- Static file caching in Nginx
- Browser caching headers

### Connection Pooling
- PostgreSQL connection pooling
- RabbitMQ connection reuse
- HTTP keep-alive

### Asynchronous Processing
- RabbitMQ for background tasks
- Non-blocking I/O
- Event-driven architecture

## Deployment Checklist

- [ ] Docker and Docker Compose installed
- [ ] Environment variables configured (.env file)
- [ ] JWT secret key set (production-grade)
- [ ] Database credentials secured
- [ ] RabbitMQ credentials changed from defaults
- [ ] Firewall rules configured
- [ ] SSL certificates obtained (for production)
- [ ] Backup strategy implemented
- [ ] Monitoring tools configured
- [ ] Log aggregation setup
- [ ] Health check endpoints verified
- [ ] Load testing performed
- [ ] Security audit completed
- [ ] Documentation updated
- [ ] Team training completed

