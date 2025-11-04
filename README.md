# Energy Management System

A complete microservices-based energy management system for monitoring and managing energy consumption devices. Built with Django REST Framework backend and React TypeScript frontend.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [API Documentation](#api-documentation)
- [User Roles](#user-roles)
- [Development](#development)
- [Testing](#testing)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)

## 🎯 Overview

The Energy Management System is a full-stack application that allows administrators to manage users and energy monitoring devices, assign devices to users, and enables clients to view their assigned devices and monitor energy consumption.

### Key Capabilities

- **User Management**: Create, update, and delete users with role-based access control
- **Device Management**: Manage energy monitoring devices with specifications
- **Device Assignment**: Assign devices to users (many-to-many relationship)
- **Real-time Monitoring**: Track device assignments and energy consumption
- **Secure Authentication**: JWT-based authentication with role-based permissions

## ✨ Features

### Admin Features
- ✅ Full user management (CRUD operations)
- ✅ Full device management (CRUD operations)
- ✅ Assign/unassign devices to users
- ✅ View all device assignments
- ✅ System statistics dashboard
- ✅ Multiple users can share the same device

### Client Features
- ✅ View personal dashboard
- ✅ View assigned devices
- ✅ View device specifications (consumption, price)
- ✅ Read-only access to device information

## 🏗️ Architecture

### Microservices Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Browser (Port 80)                     │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│              Traefik (API Gateway & Router)              │
│  • Routes /api/auth → Auth Service                      │
│  • Routes /api/users → User Service                     │
│  • Routes /api/devices → Device Service                 │
│  • Routes / → Frontend                                  │
└──────┬──────────────────────────────────────────┬───────┘
       │                                          │
       ▼                                          ▼
┌──────────────┐                          ┌──────────────┐
│   Frontend   │                          │   Backend    │
│              │                          │  Services    │
│ React 19     │                          │              │
│ TypeScript   │                          │ Auth Service │
│ Vite         │                          │ (Port 8000)  │
│ Tailwind CSS │                          │              │
│ React Router │                          │ User Service │
│ Axios        │                          │ (Port 8001)  │
│              │                          │              │
│ Served by    │                          │Device Service│
│ Nginx        │                          │ (Port 8002)  │
└──────────────┘                          └──────┬───────┘
                                                 │
                                                 ▼
                                          ┌──────────────┐
                                          │  PostgreSQL  │
                                          │  (Port 5432) │
                                          │              │
                                          │  auth_db     │
                                          │  user_db     │
                                          │  device_db   │
                                          └──────────────┘
```

### Service Communication

1. **Auth Service**: Handles authentication, JWT token generation, and user CRUD operations
2. **User Service**: Manages user profile data (name, email, phone)
3. **Device Service**: Manages devices and user-device assignments
4. **Saga Pattern**: Ensures data consistency across services during user creation/deletion

### Database Design

Each service has its own PostgreSQL database:

**auth_db:**
- `users` table: id, username, password, role, created_at

**user_db:**
- `users` table: id, username, role, fname, lname, email, phone, created_at

**device_db:**
- `users` table: id, username, role (synchronized)
- `devices` table: id, name, description, max_consumption, price, created_at
- `user_device_mapping` table: id, user_id, device_id, assigned_at

## 🛠️ Technology Stack

### Backend
- **Framework**: Django 5.0 + Django REST Framework
- **Authentication**: JWT (djangorestframework-simplejwt)
- **Database**: PostgreSQL 15
- **API Gateway**: Traefik v3.2
- **Containerization**: Docker + Docker Compose

### Frontend
- **Framework**: React 19
- **Language**: TypeScript 5.9
- **Build Tool**: Vite 7
- **Styling**: Tailwind CSS 4
- **Routing**: React Router 7
- **HTTP Client**: Axios
- **Form Handling**: React Hook Form
- **Web Server**: Nginx (production)

### DevOps
- **Containerization**: Docker
- **Orchestration**: Docker Compose
- **Reverse Proxy**: Traefik
- **Database**: PostgreSQL (containerized)

## 🚀 Quick Start

### Prerequisites

- Docker Desktop installed and running
- 4GB RAM minimum
- Ports 80 and 8080 available

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Microservices-Energy-Management-System-main
   ```

2. **Start all services**
   ```powershell
   .\start.ps1
   ```
   
   Or manually:
   ```bash
   docker-compose up -d
   ```

3. **Access the application**
   
   Open your browser: **http://localhost**

4. **Login with default credentials**
   
   **Admin:**
   - Username: `admin`
   - Password: `admin123`
   
   **Client:**
   - Username: `alice`
   - Password: `alice123`

### Generate Test Data

To populate the system with 15 users and 15 devices:

```powershell
.\generate_test_data.ps1
```

This creates:
- 15 users (13 clients, 2 admins)
- 15 energy monitoring devices
- Random device assignments

## 📁 Project Structure

```
.
├── auth_service/              # Authentication microservice
│   ├── authentication/        # Django app
│   │   ├── models.py         # User model
│   │   ├── views.py          # API endpoints
│   │   ├── serializers.py    # Data serialization
│   │   └── saga.py           # Saga pattern implementation
│   ├── Dockerfile
│   └── requirements.txt
│
├── user_service/              # User management microservice
│   ├── users/                # Django app
│   │   ├── models.py         # User profile model
│   │   ├── views.py          # API endpoints
│   │   └── middleware.py     # JWT authentication
│   ├── Dockerfile
│   └── requirements.txt
│
├── device_service/            # Device management microservice
│   ├── devices/              # Django app
│   │   ├── models.py         # Device & mapping models
│   │   ├── views.py          # API endpoints
│   │   └── serializers.py    # Data serialization
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/                  # React frontend
│   ├── src/
│   │   ├── api/              # API client functions
│   │   ├── components/       # React components
│   │   ├── contexts/         # React contexts (Auth)
│   │   ├── pages/            # Page components
│   │   ├── types/            # TypeScript types
│   │   └── utils/            # Utility functions
│   ├── Dockerfile
│   ├── nginx.conf            # Nginx configuration
│   └── package.json
│
├── docker-compose.yml         # Docker orchestration
├── .env                       # Environment variables
├── init-databases.sh          # Database initialization
│
├── README.md                  # This file
├── README_DOCKER.md           # Docker quick reference
├── DOCKER_SETUP.md            # Detailed Docker guide
├── RUNNING_GUIDE.md           # Original running guide
│
├── start.ps1                  # Start script
├── stop.ps1                   # Stop script
├── generate_test_data.ps1     # Test data generator
└── test_all_apis.ps1          # API testing script
```

## 📚 API Documentation

### Authentication Endpoints

**Register User**
```http
POST /api/auth/register/
Content-Type: application/json

{
  "username": "john",
  "password": "password123",
  "role": "client",
  "fname": "John",
  "lname": "Doe",
  "email": "john@example.com",
  "phone": "+1234567890"
}
```

**Login**
```http
POST /api/auth/login/
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}

Response:
{
  "message": "Login successful",
  "tokens": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "user": {
      "id": "uuid",
      "username": "admin",
      "role": "admin"
    }
  }
}
```

### User Management Endpoints

**List All Users** (Admin only)
```http
GET /api/users/
Authorization: Bearer <token>
```

**Get User by ID**
```http
GET /api/users/{user_id}/
Authorization: Bearer <token>
```

**Update User** (Admin only)
```http
PUT /api/users/{user_id}/update/
Authorization: Bearer <token>
Content-Type: application/json

{
  "fname": "John",
  "lname": "Smith",
  "email": "john.smith@example.com",
  "phone": "+1234567890"
}
```

**Delete User** (Admin only)
```http
DELETE /api/users/{user_id}/delete/
Authorization: Bearer <token>
```

### Device Management Endpoints

**List All Devices**
```http
GET /api/devices/
Authorization: Bearer <token>
```

**Create Device** (Admin only)
```http
POST /api/devices/create/
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Smart Thermostat",
  "description": "WiFi-enabled temperature control",
  "max_consumption": 150,
  "price": 249.99
}
```

**Update Device** (Admin only)
```http
PUT /api/devices/{device_id}/update/
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Smart Thermostat Pro",
  "max_consumption": 120
}
```

**Delete Device** (Admin only)
```http
DELETE /api/devices/{device_id}/delete/
Authorization: Bearer <token>
```

**Assign Device to User** (Admin only)
```http
POST /api/devices/assign/
Authorization: Bearer <token>
Content-Type: application/json

{
  "user_id": "uuid",
  "device_id": "uuid"
}
```

**Unassign Device** (Admin only)
```http
DELETE /api/devices/{device_id}/unassign/?user_id={user_id}
Authorization: Bearer <token>
```

**List All Assignments** (Admin only)
```http
GET /api/mappings/
Authorization: Bearer <token>
```

For complete API documentation, see [frontend/API_INTEGRATION.md](frontend/API_INTEGRATION.md)

## 👥 User Roles

### Admin Role
- Full access to all features
- Can create, update, and delete users
- Can create, update, and delete devices
- Can assign/unassign devices to users
- Can view all system data

### Client Role
- View personal dashboard
- View assigned devices
- Read-only access to device information
- Cannot modify any data

## 💻 Development

### Running Locally (Without Docker)

**Backend Services:**

1. Install Python dependencies:
   ```bash
   cd auth_service
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py runserver 8000
   ```

2. Repeat for user_service (port 8001) and device_service (port 8002)

**Frontend:**

```bash
cd frontend
npm install
npm run dev
```

Access at http://localhost:5173

### Making Changes

**Backend:**
1. Edit files in service directories
2. Rebuild Docker image: `docker-compose build <service-name>`
3. Restart: `docker-compose up -d <service-name>`

**Frontend:**
1. Edit files in `frontend/src/`
2. Rebuild: `docker-compose build frontend`
3. Restart: `docker-compose up -d frontend`

### Code Style

**Backend:**
- Follow PEP 8 style guide
- Use Django best practices
- Document complex functions

**Frontend:**
- Use TypeScript strict mode
- Follow React best practices
- Use functional components with hooks

## 🧪 Testing

### Test All APIs

```powershell
.\test_all_apis.ps1
```

This script tests:
- User registration and login
- User CRUD operations
- Device CRUD operations
- Device assignments

### Manual Testing

1. Login as admin
2. Create a new user
3. Create a new device
4. Assign device to user
5. Login as client
6. Verify device appears in client dashboard

## 🚢 Deployment

### Docker Deployment (Recommended)

```bash
docker-compose up -d
```

All services run in containers with automatic networking and health checks.

### Production Considerations

1. **Security:**
   - Change default passwords
   - Generate secure JWT secret key
   - Enable HTTPS
   - Set `DEBUG=False`

2. **Database:**
   - Use managed PostgreSQL service
   - Enable automated backups
   - Set up replication

3. **Monitoring:**
   - Enable Traefik access logs
   - Set up application monitoring
   - Configure alerts

4. **Scaling:**
   - Use Docker Swarm or Kubernetes
   - Scale services horizontally
   - Add load balancing

## 🐛 Troubleshooting

### Common Issues

**Port Conflicts:**
```bash
# Check what's using port 80
netstat -ano | findstr :80

# Change ports in docker-compose.yml if needed
```

**Database Connection Errors:**
```bash
# Reset database
docker-compose down -v
docker-compose up -d
```

**Frontend Not Loading:**
```bash
# Check logs
docker-compose logs frontend

# Rebuild
docker-compose build frontend
docker-compose up -d frontend
```

**API Errors:**
```bash
# Check backend logs
docker-compose logs auth-service
docker-compose logs user-service
docker-compose logs device-service
```

### Viewing Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f <service-name>

# Last 100 lines
docker-compose logs --tail=100 <service-name>
```

### Database Access

```bash
# Connect to PostgreSQL
docker exec -it postgres psql -U postgres

# List databases
\l

# Connect to database
\c auth_db

# List tables
\dt

# Query data
SELECT * FROM users;
```

## 📊 Monitoring

### Traefik Dashboard

Access at http://localhost:8080

Shows:
- Active routes
- Service health
- Request metrics
- Error rates

### Container Stats

```bash
docker stats
```

Shows real-time resource usage for all containers.

## 🔒 Security

### Authentication
- JWT tokens with 5-hour expiration
- Secure password hashing (Django's PBKDF2)
- Role-based access control

### API Security
- CORS configured for allowed origins
- CSRF protection enabled
- SQL injection prevention (Django ORM)

### Production Security Checklist
- [ ] Change all default passwords
- [ ] Generate secure JWT secret (256-bit)
- [ ] Enable HTTPS/TLS
- [ ] Set DEBUG=False
- [ ] Configure firewall rules
- [ ] Enable rate limiting
- [ ] Set up monitoring and alerts
- [ ] Regular security updates

## 📝 Environment Variables

Create `.env` file in project root:

```env
# JWT Secret (MUST be same across all services)
JWT_SECRET_KEY=your-super-secret-key-change-in-production

# PostgreSQL
POSTGRES_USER=postgres
POSTGRES_PASSWORD=secure-password

# Optional: Override service ports
# AUTH_PORT=8000
# USER_PORT=8001
# DEVICE_PORT=8002
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

[Your License Here]

## 👨‍💻 Authors

[Your Name/Team]

## 🙏 Acknowledgments

- Django REST Framework
- React Team
- Traefik Team
- PostgreSQL Community

## 📞 Support

For issues or questions:
1. Check documentation in this README
2. Review [DOCKER_SETUP.md](DOCKER_SETUP.md)
3. Check logs: `docker-compose logs -f`
4. Open an issue on GitHub

## 🗺️ Roadmap

Future enhancements:
- [ ] Real-time energy consumption monitoring
- [ ] Data visualization and charts
- [ ] Email notifications
- [ ] Mobile app
- [ ] Advanced analytics
- [ ] Export reports (PDF/CSV)
- [ ] Multi-language support
- [ ] Dark mode

---

**Built with ❤️ using Django, React, and Docker**
