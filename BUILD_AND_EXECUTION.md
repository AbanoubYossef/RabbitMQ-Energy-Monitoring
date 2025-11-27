# Build and Execution Guide

## Energy Management System - Microservices Architecture

This document provides comprehensive instructions for building, deploying, and executing the Energy Management System.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [System Requirements](#system-requirements)
3. [Installation Steps](#installation-steps)
4. [Build Process](#build-process)
5. [Execution Instructions](#execution-instructions)
6. [Configuration](#configuration)
7. [Verification & Testing](#verification--testing)
8. [Troubleshooting](#troubleshooting)
9. [Development Workflow](#development-workflow)
10. [Production Deployment](#production-deployment)

---

## Prerequisites

### Required Software

#### 1. Docker Desktop
- **Version**: 20.10 or higher
- **Download**: https://www.docker.com/products/docker-desktop

**Installation Verification**:
```bash
docker --version
# Expected: Docker version 20.10.x or higher

docker-compose --version
# Expected: Docker Compose version 2.x.x or higher
```

#### 2. Git
- **Version**: 2.x or higher
- **Download**: https://git-scm.com/downloads

**Installation Verification**:
```bash
git --version
# Expected: git version 2.x.x
```

#### 3. Text Editor (Optional)
- Visual Studio Code (recommended)
- Sublime Text
- Notepad++
- Any text editor for configuration files

---

## System Requirements

### Minimum Requirements
- **CPU**: 2 cores
- **RAM**: 4 GB
- **Disk Space**: 20 GB free
- **OS**: Windows 10/11, macOS 10.15+, Linux (Ubuntu 20.04+)
- **Network**: Internet connection for initial image downloads

### Recommended Requirements
- **CPU**: 4+ cores
- **RAM**: 8+ GB
- **Disk Space**: 50+ GB free
- **OS**: Latest stable version
- **Network**: Broadband connection

---

## Installation Steps

### Step 1: Clone the Repository

```bash
# Clone the repository
git clone <repository-url>

# Navigate to project directory
cd <project-directory>
```

### Step 2: Verify Project Structure

```bash
# List directory contents
dir  # Windows
ls   # Linux/macOS
```

**Expected Structure**:
```
├── auth_service/
├── user_service/
├── device_service/
├── monitoring_service/
├── frontend/
├── device_simulator/
├── traefik/
├── docker-compose.yml
├── .env
├── init-databases.sh
└── README.md
```

### Step 3: Configure Environment Variables


#### Edit the `.env` file in the root directory:

```bash
# Open .env file
notepad .env  # Windows
nano .env     # Linux/macOS
```

**Required Configuration**:
```env
# JWT Secret Key (CHANGE THIS IN PRODUCTION!)
JWT_SECRET_KEY=my-super-secret-key-change-in-production-123456
```

**Security Note**: Generate a strong secret key for production:
```bash
# Python method
python -c "import secrets; print(secrets.token_urlsafe(32))"

# OpenSSL method
openssl rand -base64 32
```

---

## Build Process

### Option 1: Build All Services (Recommended for First Time)

```bash
# Build all Docker images
docker-compose build

# Expected output:
# Building auth-service...
# Building user-service...
# Building device-service...
# Building monitoring-service...
# Building frontend...
# Building device-simulator...
# Successfully built [image-ids]
```

**Build Time**: 5-15 minutes (depending on internet speed and system performance)

### Option 2: Build Individual Services

```bash
# Build specific service
docker-compose build auth-service
docker-compose build user-service
docker-compose build device-service
docker-compose build monitoring-service
docker-compose build frontend
docker-compose build device-simulator
```

### Option 3: Build with No Cache (Clean Build)

```bash
# Force rebuild without using cache
docker-compose build --no-cache

# Use when:
# - Dependencies have changed
# - Experiencing build issues
# - Need fresh build
```

### Build Verification

```bash
# List built images
docker images

# Expected output should include:
# - <project>-auth-service
# - <project>-user-service
# - <project>-device-service
# - <project>-monitoring-service
# - <project>-frontend
# - <project>-device-simulator
# - traefik:v3.2
# - postgres:15-alpine
# - rabbitmq:3.13-management-alpine
```

---

## Execution Instructions

### Starting the System

#### Method 1: Start All Services (Detached Mode)

```bash
# Start all services in background
docker-compose up -d

# Expected output:
# Creating network "microservices-network"
# Creating volume "postgres_data"
# Creating volume "rabbitmq_data"
# Creating postgres...
# Creating rabbitmq...
# Creating traefik...
# Creating auth-service...
# Creating user-service...
# Creating device-service...
# Creating monitoring-service...
# Creating frontend...
# Creating device-simulator...
```

**Startup Time**: 30-60 seconds for all services to be healthy

#### Method 2: Start with Logs (Foreground Mode)

```bash
# Start and view logs in real-time
docker-compose up

# Press Ctrl+C to stop
```

#### Method 3: Start Specific Services

```bash
# Start only required services
docker-compose up -d postgres rabbitmq
docker-compose up -d auth-service user-service
```

### Checking Service Status

```bash
# View running containers
docker-compose ps

# Expected output:
# NAME                STATUS              PORTS
# traefik            Up                  0.0.0.0:80->80/tcp, 0.0.0.0:8080->8080/tcp
# postgres           Up (healthy)        0.0.0.0:5432->5432/tcp
# rabbitmq           Up (healthy)        0.0.0.0:5672->5672/tcp, 0.0.0.0:15672->15672/tcp
# auth-service       Up                  0.0.0.0:8000->8000/tcp
# user-service       Up                  0.0.0.0:8001->8001/tcp
# device-service     Up                  0.0.0.0:8002->8002/tcp
# monitoring-service Up                  0.0.0.0:8003->8003/tcp
# frontend           Up                  80/tcp
# device-simulator   Up                  
```

### Viewing Logs

```bash
# View logs for all services
docker-compose logs

# View logs for specific service
docker-compose logs auth-service
docker-compose logs device-simulator

# Follow logs in real-time
docker-compose logs -f

# View last 100 lines
docker-compose logs --tail=100

# View logs with timestamps
docker-compose logs -t
```

### Stopping the System

```bash
# Stop all services (preserves data)
docker-compose stop

# Stop specific service
docker-compose stop auth-service

# Stop and remove containers (preserves volumes)
docker-compose down

# Stop and remove everything including volumes (CAUTION: DATA LOSS)
docker-compose down -v
```

### Restarting Services

```bash
# Restart all services
docker-compose restart

# Restart specific service
docker-compose restart auth-service
docker-compose restart device-simulator
```

---

## Configuration

### Service-Specific Configuration

#### 1. Auth Service Configuration

**File**: `auth_service/.env`

```env
SECRET_KEY=secret
DEBUG=True
DB_NAME=auth_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=postgres
DB_PORT=5432
JWT_SECRET_KEY=secret
RABBITMQ_HOST=rabbitmq
RABBITMQ_PORT=5672
RABBITMQ_USER=admin
RABBITMQ_PASS=admin123
```

#### 2. Frontend Configuration

**File**: `frontend/.env`

```env
VITE_API_BASE_URL=http://localhost
```

**For Production**:
```env
VITE_API_BASE_URL=https://your-domain.com
```

#### 3. Device Simulator Configuration

**File**: `device_simulator/config.json`

```json
{
  "device_id": "550e8400-e29b-41d4-a716-446655440000",
  "interval_seconds": 1,
  "base_load_kwh": 0.2,
  "time_acceleration": 600
}
```

**Parameters**:
- `device_id`: UUID of device to simulate (must exist in system)
- `interval_seconds`: Measurement interval (1 second = real-time)
- `base_load_kwh`: Base energy consumption per measurement
- `time_acceleration`: Simulated minutes per real second (600 = 10 hours/minute)

### Database Configuration

**Automatic Initialization**: Databases are created automatically on first startup via `init-databases.sh`

**Manual Database Access**:
```bash
# Connect to PostgreSQL
docker exec -it postgres psql -U postgres

# List databases
\l

# Connect to specific database
\c auth_db

# List tables
\dt

# Exit
\q
```

### RabbitMQ Configuration

**Default Credentials**:
- Username: `admin`
- Password: `admin123`

**Change Credentials** (in `docker-compose.yml`):
```yaml
rabbitmq:
  environment:
    RABBITMQ_DEFAULT_USER: your_username
    RABBITMQ_DEFAULT_PASS: your_secure_password
```

**Note**: Update all service configurations if you change RabbitMQ credentials.

---

## Verification & Testing

### Step 1: Verify Service Health

```bash
# Check all services are running
docker-compose ps

# All services should show "Up" or "Up (healthy)"
```

### Step 2: Access Web Interfaces

#### Frontend Application
- **URL**: http://localhost
- **Expected**: Login page should load
- **Test**: Try logging in with default credentials

#### Traefik Dashboard
- **URL**: http://localhost:8080
- **Expected**: Dashboard showing all services
- **Check**: All routers should be green/active

#### RabbitMQ Management
- **URL**: http://localhost:15672
- **Credentials**: admin / admin123
- **Expected**: Management interface
- **Check**: Queues `device_data_queue` and `sync_queue` should exist

### Step 3: API Health Checks

```bash
# Test Auth Service
curl http://localhost:8000/api/auth/users/

# Test User Service
curl http://localhost:8001/api/users/

# Test Device Service
curl http://localhost:8002/api/devices/

# Test Monitoring Service
curl http://localhost:8003/api/monitoring/devices/
```

### Step 4: Test User Registration

```bash
# Register new user via API
curl -X POST http://localhost/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpass123",
    "email": "test@example.com",
    "name": "Test User",
    "role": "client"
  }'

# Expected: 201 Created with user data
```

### Step 5: Test Login

```bash
# Login
curl -X POST http://localhost/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'

# Expected: 200 OK with access and refresh tokens
```

### Step 6: Verify Device Simulator

```bash
# Check simulator logs
docker-compose logs device-simulator

# Expected output:
# "Connected to RabbitMQ"
# "Publishing measurement for device..."
# "Timestamp: ..., Energy: ... kWh"
```

### Step 7: Verify Data Flow

```bash
# Check monitoring service for measurements
curl http://localhost:8003/api/monitoring/measurements/

# Expected: List of device measurements
```

---

## Troubleshooting

### Common Issues and Solutions

#### Issue 1: Port Already in Use

**Error**: `Bind for 0.0.0.0:80 failed: port is already allocated`

**Solution**:
```bash
# Windows - Find process using port
netstat -ano | findstr :80

# Kill process (replace PID)
taskkill /PID <PID> /F

# Or change port in docker-compose.yml
ports:
  - "8080:80"  # Use port 8080 instead
```

#### Issue 2: Services Not Starting

**Error**: Container exits immediately

**Solution**:
```bash
# Check logs for specific service
docker-compose logs auth-service

# Common causes:
# - Database not ready (wait for health check)
# - Environment variables missing
# - Port conflicts
# - Build errors

# Rebuild service
docker-compose build --no-cache auth-service
docker-compose up -d auth-service
```

#### Issue 3: Database Connection Failed

**Error**: `could not connect to server: Connection refused`

**Solution**:
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check PostgreSQL logs
docker-compose logs postgres

# Restart PostgreSQL
docker-compose restart postgres

# Wait for health check
docker-compose ps postgres
# Should show "Up (healthy)"
```

#### Issue 4: RabbitMQ Connection Failed

**Error**: `Connection refused - RabbitMQ`

**Solution**:
```bash
# Check RabbitMQ status
docker-compose ps rabbitmq

# Check RabbitMQ logs
docker-compose logs rabbitmq

# Restart RabbitMQ
docker-compose restart rabbitmq

# Verify queues exist
# Access http://localhost:15672
```

#### Issue 5: Frontend Not Loading

**Error**: Blank page or 404

**Solution**:
```bash
# Check frontend logs
docker-compose logs frontend

# Rebuild frontend
docker-compose build --no-cache frontend
docker-compose up -d frontend

# Check Traefik routing
# Access http://localhost:8080
# Verify frontend router exists
```

#### Issue 6: Device Simulator Not Publishing

**Error**: No measurements in monitoring service

**Solution**:
```bash
# Check simulator logs
docker-compose logs device-simulator

# Verify device_id exists in system
# 1. Login as admin
# 2. Create device
# 3. Copy device UUID
# 4. Update device_simulator/config.json
# 5. Restart simulator

docker-compose restart device-simulator
```

#### Issue 7: JWT Token Invalid

**Error**: `401 Unauthorized` or `Token is invalid`

**Solution**:
```bash
# Ensure JWT_SECRET_KEY is same across all services
# Check .env file
# Check service-specific .env files

# Restart all services after changing
docker-compose restart
```

### Debug Mode

#### Enable Detailed Logging

**Edit service .env files**:
```env
DEBUG=True
LOG_LEVEL=DEBUG
```

**Restart services**:
```bash
docker-compose restart
```

#### Access Container Shell

```bash
# Access running container
docker exec -it auth-service /bin/bash

# Check environment variables
env | grep DB

# Check network connectivity
ping postgres
ping rabbitmq

# Exit
exit
```

### Performance Issues

#### High CPU Usage

```bash
# Check resource usage
docker stats

# Limit resources in docker-compose.yml
services:
  auth-service:
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
```

#### Slow Startup

```bash
# Check health checks
docker-compose ps

# Increase health check intervals
healthcheck:
  interval: 30s
  timeout: 10s
  retries: 10
```

---

## Development Workflow

### Making Code Changes

#### Backend Services (Django)

```bash
# 1. Make changes to Python files
# 2. Rebuild service
docker-compose build auth-service

# 3. Restart service
docker-compose up -d auth-service

# 4. View logs
docker-compose logs -f auth-service
```

#### Frontend (React)

```bash
# 1. Make changes to React files
# 2. Rebuild frontend
docker-compose build frontend

# 3. Restart frontend
docker-compose up -d frontend

# 4. Clear browser cache
# 5. Refresh page
```

### Database Migrations

```bash
# Create migrations
docker exec -it auth-service python manage.py makemigrations

# Apply migrations
docker exec -it auth-service python manage.py migrate

# For all services
docker exec -it user-service python manage.py migrate
docker exec -it device-service python manage.py migrate
docker exec -it monitoring-service python manage.py migrate
```

### Adding New Dependencies

#### Python Dependencies

```bash
# 1. Add to requirements.txt
echo "new-package==1.0.0" >> auth_service/requirements.txt

# 2. Rebuild service
docker-compose build --no-cache auth-service

# 3. Restart service
docker-compose up -d auth-service
```

#### Frontend Dependencies

```bash
# 1. Access frontend container
docker exec -it frontend sh

# 2. Install package
npm install new-package

# 3. Exit and rebuild
exit
docker-compose build frontend
docker-compose up -d frontend
```

### Running Tests

```bash
# Django tests
docker exec -it auth-service python manage.py test

# Frontend tests (if configured)
docker exec -it frontend npm test
```

---

## Production Deployment

### Pre-Deployment Checklist

- [ ] Change all default passwords
- [ ] Generate strong JWT secret key
- [ ] Set DEBUG=False in all services
- [ ] Configure proper CORS origins
- [ ] Set up SSL/TLS certificates
- [ ] Configure firewall rules
- [ ] Set up backup strategy
- [ ] Configure monitoring and alerting
- [ ] Review security settings
- [ ] Test disaster recovery procedures

### Production Environment Variables

```env
# .env (Production)
JWT_SECRET_KEY=<strong-random-key-64-characters>
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
CORS_ALLOWED_ORIGINS=https://your-domain.com
```

### SSL/TLS Configuration

**Update docker-compose.yml for Traefik**:
```yaml
traefik:
  command:
    - "--entrypoints.web.address=:80"
    - "--entrypoints.websecure.address=:443"
    - "--certificatesresolvers.myresolver.acme.email=your@email.com"
    - "--certificatesresolvers.myresolver.acme.storage=/letsencrypt/acme.json"
    - "--certificatesresolvers.myresolver.acme.httpchallenge.entrypoint=web"
  volumes:
    - ./letsencrypt:/letsencrypt
```

### Database Backup Strategy

```bash
# Automated backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
docker exec postgres pg_dumpall -U postgres > backup_$DATE.sql
# Upload to S3 or backup server
```

### Monitoring Setup

**Recommended Tools**:
- Prometheus for metrics
- Grafana for visualization
- ELK Stack for log aggregation
- Sentry for error tracking

### Scaling for Production

```bash
# Scale services horizontally
docker-compose up -d --scale auth-service=3 --scale device-service=2

# Use Docker Swarm or Kubernetes for orchestration
```

---

## Quick Reference Commands

### Essential Commands

```bash
# Start system
docker-compose up -d

# Stop system
docker-compose down

# View logs
docker-compose logs -f

# Restart service
docker-compose restart <service-name>

# Rebuild service
docker-compose build <service-name>

# Check status
docker-compose ps

# Access container
docker exec -it <container-name> /bin/bash

# View resource usage
docker stats
```

### Maintenance Commands

```bash
# Clean up unused images
docker image prune -a

# Clean up unused volumes
docker volume prune

# Clean up everything
docker system prune -a --volumes

# Backup database
docker exec postgres pg_dump -U postgres <db-name> > backup.sql

# Restore database
docker exec -i postgres psql -U postgres <db-name> < backup.sql
```

---

## Support and Resources

### Documentation
- Docker: https://docs.docker.com
- Django: https://docs.djangoproject.com
- React: https://react.dev
- Traefik: https://doc.traefik.io/traefik/

### API Documentation
- Auth Service: http://localhost:8000/api/docs/
- User Service: http://localhost:8001/api/docs/
- Device Service: http://localhost:8002/api/docs/
- Monitoring Service: http://localhost:8003/api/docs/

### Getting Help
1. Check logs: `docker-compose logs <service>`
2. Review this documentation
3. Check GitHub issues
4. Contact development team

---

**Last Updated**: November 2025
**Version**: 1.0.0
