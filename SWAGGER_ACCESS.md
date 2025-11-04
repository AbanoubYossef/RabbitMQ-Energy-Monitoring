# Swagger Documentation - Quick Access

## ✅ All Services Running Successfully!

Your Energy Management System is now running with Swagger/OpenAPI documentation enabled.

## 🌐 Access URLs

### Main Application
- **Frontend**: http://localhost
- **Traefik Dashboard**: http://localhost:8080

### Swagger/OpenAPI Documentation

#### Auth Service
- **Swagger UI**: http://localhost/api/docs/
- **OpenAPI Schema**: http://localhost/api/schema/
- **API Base**: http://localhost/api/auth/

#### User Service  
- **Swagger UI**: http://localhost:8001/api/docs/
- **OpenAPI Schema**: http://localhost:8001/api/schema/
- **API Base**: http://localhost:8001/api/

#### Device Service
- **Swagger UI**: http://localhost:8002/api/docs/
- **OpenAPI Schema**: http://localhost:8002/api/schema/
- **API Base**: http://localhost:8002/api/

## 🚀 Quick Start Guide

### 1. Open Swagger UI
Click on any of the Swagger UI links above to open the interactive documentation.

### 2. Test Public Endpoints
Try these endpoints without authentication:
- `POST /api/auth/register/` - Register a new user
- `POST /api/auth/login/` - Login and get JWT token

### 3. Authenticate for Protected Endpoints
1. Use the login endpoint to get an access token
2. Click the "Authorize" button (🔒) in Swagger UI
3. Enter: `Bearer YOUR_ACCESS_TOKEN`
4. Click "Authorize" then "Close"
5. Now you can test all protected endpoints!

### 4. Example Flow

```bash
# 1. Register (or use existing user)
POST /api/auth/login/
{
  "username": "admin",
  "password": "admin123"
}

# 2. Copy the "access" token from response

# 3. Click "Authorize" in Swagger UI and paste:
Bearer eyJ0eXAiOiJKV1QiLCJhbGc...

# 4. Test protected endpoints like:
GET /api/auth/users/
GET /api/devices/
POST /api/devices/create/
```

## 📋 Default Test Accounts

**Admin Account:**
- Username: `admin`
- Password: `admin123`

**Client Account:**
- Username: `alice`
- Password: `alice123`

## 🔧 Service Status

Check if all services are running:
```powershell
docker-compose ps
```

View logs:
```powershell
docker-compose logs -f auth-service
docker-compose logs -f user-service
docker-compose logs -f device-service
```

## 📖 Full Documentation

For complete Swagger usage guide, see: [SWAGGER_GUIDE.md](SWAGGER_GUIDE.md)

## 🛑 Stop Services

```powershell
docker-compose down
```

## 🔄 Restart Services

```powershell
docker-compose restart
```

---

**Happy API Testing! 🎉**
