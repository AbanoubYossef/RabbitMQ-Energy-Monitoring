# Running the Application

## 🚀 Quick Start

### Backend (Already Running)
```bash
# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Restart services
docker-compose restart
```

### Frontend (Currently Running)
```bash
cd frontend
npm run dev
```

## 📍 Service URLs

### Backend Services
- **API Gateway**: http://localhost
- **Auth Service**: http://localhost/api/auth/
- **User Service**: http://localhost/api/users/
- **Device Service**: http://localhost/api/devices/
- **Traefik Dashboard**: http://localhost:8080

### Frontend
- **React Application**: http://localhost:5174

## 👤 Test Accounts

### Admin Account
- **Username**: `admin`
- **Password**: `admin123`
- **Permissions**: Full access to all features

### Client Account
- **Username**: `alice`
- **Password**: `alice123`
- **Permissions**: View own profile, view devices

## ✅ Testing Checklist

### Authentication
- [ ] Login with admin account
- [ ] Login with client account
- [ ] Logout functionality
- [ ] Token persistence (refresh page)

### User Management (Admin Only)
- [ ] View all users
- [ ] View user details
- [ ] Update user information
- [ ] Delete user

### Device Management
- [ ] View all devices (both roles)
- [ ] Create device (admin only)
- [ ] Update device (admin only)
- [ ] Delete device (admin only)
- [ ] Assign device to user (admin only)
- [ ] View device assignments

### Client Features
- [ ] View own profile
- [ ] View devices list
- [ ] Cannot access admin features

## 🔧 Troubleshooting

### Backend Issues

**Services not starting:**
```bash
docker-compose down
docker-compose up --build
```

**Database issues:**
```bash
docker-compose down -v  # Remove volumes
docker-compose up
```

**View service logs:**
```bash
docker-compose logs auth-service
docker-compose logs user-service
docker-compose logs device-service
```

### Frontend Issues

**Port already in use:**
- Frontend will automatically use next available port (5174, 5175, etc.)

**API connection errors:**
- Check backend is running: `docker-compose ps`
- Verify Traefik is accessible: http://localhost
- Check browser console for CORS errors

**Module not found:**
```bash
cd frontend
npm install
npm run dev
```

**Clear cache and rebuild:**
```bash
cd frontend
rm -rf node_modules
npm install
npm run dev
```

## 📊 Monitoring

### Check Service Health
```bash
# All services status
docker-compose ps

# Service logs (real-time)
docker-compose logs -f

# Specific service logs
docker-compose logs -f auth-service
docker-compose logs -f user-service
docker-compose logs -f device-service
```

### Database Access
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
```

## 🛑 Stopping Services

### Stop Frontend
- Press `Ctrl+C` in the terminal running `npm run dev`
- Or close the terminal

### Stop Backend
```bash
# Stop all services
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v
```

## 🔄 Restarting Services

### Restart All Backend Services
```bash
docker-compose restart
```

### Restart Specific Service
```bash
docker-compose restart auth-service
docker-compose restart user-service
docker-compose restart device-service
```

### Rebuild and Restart
```bash
docker-compose up --build -d
```

## 📝 Development Workflow

1. **Make backend changes**:
   ```bash
   # Edit files in auth_service/, user_service/, or device_service/
   docker-compose restart <service-name>
   # Or rebuild if dependencies changed
   docker-compose up <service-name> --build -d
   ```

2. **Make frontend changes**:
   - Files auto-reload with Vite hot module replacement
   - No restart needed for most changes

3. **Test changes**:
   - Open http://localhost:5174
   - Check browser console for errors
   - Check backend logs: `docker-compose logs -f`

## 🎯 API Testing

### Using Browser
- Open http://localhost:5174
- Use the UI to test features

### Using PowerShell
```powershell
# Test login
$body = @{
    username = "admin"
    password = "admin123"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost/api/auth/login/" -Method POST -Body $body -ContentType "application/json"
```

### Using Postman/Insomnia
- Import endpoints from `frontend/API_INTEGRATION.md`
- Base URL: `http://localhost`

## 📚 Additional Resources

- **API Documentation**: `frontend/API_INTEGRATION.md`
- **Change Log**: `frontend/CHANGES.md`
- **Backend Testing**: `test_all_apis.ps1`

## 🆘 Getting Help

If you encounter issues:
1. Check service logs: `docker-compose logs -f`
2. Verify all services are running: `docker-compose ps`
3. Check browser console for frontend errors
4. Review API documentation: `frontend/API_INTEGRATION.md`
