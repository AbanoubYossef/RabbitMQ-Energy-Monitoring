# Docker Setup Guide - Complete Deployment

This guide explains how to run the entire Energy Management System using Docker.

## Prerequisites

- Docker Desktop installed and running
- Docker Compose v2.x or higher
- At least 4GB of available RAM

## Architecture

The application consists of 6 Docker containers:

1. **Traefik** (API Gateway) - Routes all traffic on port 80
2. **PostgreSQL** - Database with 3 separate databases
3. **Auth Service** - Django REST API for authentication
4. **User Service** - Django REST API for user management
5. **Device Service** - Django REST API for device management
6. **Frontend** - React SPA served by Nginx

## Quick Start

### 1. Start All Services

```bash
docker-compose up -d
```

This will:
- Build all Docker images (first time only)
- Start all containers in detached mode
- Create the database and run migrations
- Set up networking between services

### 2. Check Service Status

```bash
docker-compose ps
```

All services should show "Up" status.

### 3. Access the Application

Open your browser and navigate to:
```
http://localhost
```

The frontend will be served through Traefik on port 80.

## Service URLs

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost | React application |
| API Gateway | http://localhost/api | All backend APIs |
| Auth API | http://localhost/api/auth | Authentication endpoints |
| User API | http://localhost/api/users | User management |
| Device API | http://localhost/api/devices | Device management |
| Traefik Dashboard | http://localhost:8080 | Traefik admin panel |

## Default Credentials

### Admin Account
- Username: `admin`
- Password: `admin123`

### Client Account
- Username: `alice`
- Password: `alice123`

## Common Commands

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f frontend
docker-compose logs -f auth-service
docker-compose logs -f user-service
docker-compose logs -f device-service
```

### Restart Services

```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart frontend
docker-compose restart auth-service
```

### Stop Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v
```

### Rebuild Services

```bash
# Rebuild all
docker-compose build

# Rebuild specific service
docker-compose build frontend
docker-compose build auth-service

# Rebuild and restart
docker-compose up -d --build
```

## Database Access

```bash
# Connect to PostgreSQL
docker exec -it postgres psql -U postgres

# List databases
\l

# Connect to specific database
\c auth_db
\c user_db
\c device_db

# List tables
\dt

# Exit
\q
```

## Troubleshooting

### Port Conflicts

If port 80 or 8080 is already in use:

1. Stop the conflicting service
2. Or modify `docker-compose.yml` to use different ports:

```yaml
traefik:
  ports:
    - "8000:80"  # Change 80 to 8000
    - "8081:8080"  # Change 8080 to 8081
```

### Container Won't Start

```bash
# Check logs
docker-compose logs <service-name>

# Remove and recreate
docker-compose down
docker-compose up -d --force-recreate
```

### Database Issues

```bash
# Reset database
docker-compose down -v
docker-compose up -d

# This will delete all data and recreate databases
```

### Frontend Not Loading

```bash
# Check if frontend container is running
docker-compose ps frontend

# Check frontend logs
docker-compose logs frontend

# Rebuild frontend
docker-compose build frontend
docker-compose up -d frontend
```

### API Errors

```bash
# Check backend service logs
docker-compose logs auth-service
docker-compose logs user-service
docker-compose logs device-service

# Restart backend services
docker-compose restart auth-service user-service device-service
```

## Development Workflow

### Making Backend Changes

1. Edit files in `auth_service/`, `user_service/`, or `device_service/`
2. Rebuild the service:
   ```bash
   docker-compose build <service-name>
   docker-compose up -d <service-name>
   ```

### Making Frontend Changes

1. Edit files in `frontend/src/`
2. Rebuild the frontend:
   ```bash
   docker-compose build frontend
   docker-compose up -d frontend
   ```

### Hot Reload (Development Mode)

For faster development, you can run services locally:

**Backend:**
```bash
# Stop Docker backend services
docker-compose stop auth-service user-service device-service

# Run locally (in separate terminals)
cd auth_service && python manage.py runserver 8000
cd user_service && python manage.py runserver 8001
cd device_service && python manage.py runserver 8002
```

**Frontend:**
```bash
# Stop Docker frontend
docker-compose stop frontend

# Run locally
cd frontend && npm run dev
```

## Production Deployment

For production deployment:

1. Update `.env` file with secure values:
   ```
   JWT_SECRET_KEY=<generate-secure-random-key>
   POSTGRES_PASSWORD=<secure-password>
   ```

2. Set `DEBUG=False` in service environment variables

3. Use production-grade database (not Docker PostgreSQL)

4. Enable HTTPS in Traefik

5. Set up proper backup strategy

## Monitoring

### Health Checks

```bash
# Check if all services are healthy
docker-compose ps

# Test API endpoints
curl http://localhost/api/auth/login/
curl http://localhost/api/devices/
```

### Resource Usage

```bash
# View container resource usage
docker stats
```

## Backup and Restore

### Backup Database

```bash
# Backup all databases
docker exec postgres pg_dumpall -U postgres > backup.sql

# Backup specific database
docker exec postgres pg_dump -U postgres auth_db > auth_backup.sql
```

### Restore Database

```bash
# Restore all databases
docker exec -i postgres psql -U postgres < backup.sql

# Restore specific database
docker exec -i postgres psql -U postgres auth_db < auth_backup.sql
```

## Scaling

To run multiple instances of a service:

```bash
docker-compose up -d --scale user-service=3
```

Traefik will automatically load balance between instances.

## Clean Up

### Remove Everything

```bash
# Stop and remove containers, networks, volumes
docker-compose down -v

# Remove images
docker-compose down --rmi all -v

# Remove all unused Docker resources
docker system prune -a --volumes
```

## Support

For issues or questions:
1. Check logs: `docker-compose logs -f`
2. Review this guide
3. Check Docker and Docker Compose versions
4. Ensure sufficient system resources

## Next Steps

After starting the application:
1. Login with admin credentials
2. Create users and devices
3. Assign devices to users
4. Test the API endpoints
5. Explore the Traefik dashboard at http://localhost:8080
