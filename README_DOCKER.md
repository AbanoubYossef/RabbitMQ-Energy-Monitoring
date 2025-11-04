# Energy Management System - Docker Deployment

Complete microservices-based energy management system running entirely in Docker.

## 🚀 Quick Start

### Start the Application

```powershell
.\start.ps1
```

Or manually:

```bash
docker-compose up -d
```

### Access the Application

Open your browser: **http://localhost**

### Stop the Application

```powershell
.\stop.ps1
```

Or manually:

```bash
docker-compose down
```

## 📦 What's Included

All services run in Docker containers:

- ✅ **Frontend** - React + TypeScript + Vite (Nginx)
- ✅ **Auth Service** - Django REST API (Authentication)
- ✅ **User Service** - Django REST API (User Management)
- ✅ **Device Service** - Django REST API (Device Management)
- ✅ **PostgreSQL** - Database (3 separate databases)
- ✅ **Traefik** - API Gateway & Load Balancer

## 🔑 Default Credentials

| Role | Username | Password |
|------|----------|----------|
| Admin | `admin` | `admin123` |
| Client | `alice` | `alice123` |

## 🌐 Service URLs

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost | Main application |
| **API** | http://localhost/api | Backend APIs |
| **Traefik Dashboard** | http://localhost:8080 | Monitoring |

## 📋 Requirements

- Docker Desktop
- 4GB RAM minimum
- Ports 80 and 8080 available

## 🛠️ Common Commands

```bash
# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f frontend
docker-compose logs -f auth-service

# Restart services
docker-compose restart

# Rebuild after code changes
docker-compose build
docker-compose up -d

# Clean slate (removes all data)
docker-compose down -v
docker-compose up -d
```

## 📚 Documentation

- **[DOCKER_SETUP.md](DOCKER_SETUP.md)** - Complete Docker setup guide
- **[RUNNING_GUIDE.md](RUNNING_GUIDE.md)** - Original running guide
- **[API_INTEGRATION.md](frontend/API_INTEGRATION.md)** - API documentation

## 🎯 Features

### Admin Features
- User management (CRUD)
- Device management (CRUD)
- Device assignment to users
- View all assignments
- System statistics

### Client Features
- View assigned devices
- View device details
- Personal dashboard

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Browser (Port 80)                     │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│                  Traefik (API Gateway)                   │
│  Routes: /api/* → Backend, /* → Frontend                │
└──────┬──────────────────────────────────────────┬───────┘
       │                                          │
       ▼                                          ▼
┌──────────────┐                          ┌──────────────┐
│   Frontend   │                          │   Backend    │
│  (Nginx)     │                          │  Services    │
│              │                          │              │
│ React + TS   │                          │ Auth Service │
│ Tailwind CSS │                          │ User Service │
└──────────────┘                          │Device Service│
                                          └──────┬───────┘
                                                 │
                                                 ▼
                                          ┌──────────────┐
                                          │  PostgreSQL  │
                                          │              │
                                          │  auth_db     │
                                          │  user_db     │
                                          │  device_db   │
                                          └──────────────┘
```

## 🔧 Development

### Making Changes

**Backend:**
1. Edit files in `auth_service/`, `user_service/`, or `device_service/`
2. Rebuild: `docker-compose build <service-name>`
3. Restart: `docker-compose up -d <service-name>`

**Frontend:**
1. Edit files in `frontend/src/`
2. Rebuild: `docker-compose build frontend`
3. Restart: `docker-compose up -d frontend`

### Database Access

```bash
docker exec -it postgres psql -U postgres
```

## 🐛 Troubleshooting

### Services won't start
```bash
docker-compose down -v
docker-compose up -d --build
```

### Port conflicts
Edit `docker-compose.yml` to change ports

### View detailed logs
```bash
docker-compose logs -f <service-name>
```

## 📊 Monitoring

- **Traefik Dashboard**: http://localhost:8080
- **Container Stats**: `docker stats`
- **Service Status**: `docker-compose ps`

## 🔒 Security Notes

⚠️ **For Development Only**

Before production deployment:
1. Change all default passwords
2. Generate secure JWT secret key
3. Enable HTTPS
4. Set `DEBUG=False`
5. Use production database
6. Implement proper backup strategy

## 📝 Test Data

Generate 15 random users and devices:

```powershell
.\generate_test_data.ps1
```

## ✅ Verification

After starting, verify everything works:

1. Open http://localhost
2. Login with admin credentials
3. Navigate to Users page
4. Navigate to Devices page
5. Try assigning a device to a user

## 🆘 Support

If you encounter issues:

1. Check logs: `docker-compose logs -f`
2. Verify Docker is running: `docker info`
3. Check service status: `docker-compose ps`
4. Review [DOCKER_SETUP.md](DOCKER_SETUP.md)

## 📄 License

[Your License Here]

## 👥 Contributors

[Your Name/Team]

---

**Built with Docker 🐳 | Powered by Traefik 🚀**
