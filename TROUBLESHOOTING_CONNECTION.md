# Connection Troubleshooting Guide

## ✅ Good News: Your Services Are Running!

I've verified that all services are running correctly and responding on port 80. The issue is likely with your browser configuration.

## 🔍 Verified Working:
- ✅ Port 80 is listening (Docker process)
- ✅ http://localhost/ returns HTTP 200
- ✅ http://127.0.0.1/ returns HTTP 200  
- ✅ http://localhost/api/docs/ returns HTTP 200
- ✅ All Docker containers are up and healthy

## 🛠️ Solutions to Try:

### Solution 1: Try Different URL Formats
Instead of `http://localhost`, try:
- **http://127.0.0.1/** 
- **http://127.0.0.1/api/docs/**
- **http://localhost:80/**

### Solution 2: Clear Browser Cache
1. Press `Ctrl + Shift + Delete`
2. Clear cached images and files
3. Restart your browser
4. Try again

### Solution 3: Try a Different Browser
- If using Chrome, try Edge or Firefox
- If using Edge, try Chrome
- Try an Incognito/Private window

### Solution 4: Check Browser Proxy Settings
1. Open browser settings
2. Search for "proxy"
3. Ensure "No proxy" or "Direct connection" is selected
4. Disable any VPN or proxy extensions

### Solution 5: Flush DNS Cache
Open PowerShell as Administrator and run:
```powershell
ipconfig /flushdns
```

### Solution 6: Check Windows Hosts File
1. Open Notepad as Administrator
2. Open: `C:\Windows\System32\drivers\etc\hosts`
3. Make sure there's no conflicting entry for localhost
4. Should have: `127.0.0.1 localhost`

### Solution 7: Restart Docker Desktop
1. Right-click Docker Desktop icon in system tray
2. Click "Restart"
3. Wait for Docker to fully restart
4. Try accessing again

### Solution 8: Use PowerShell to Open Browser
Run this command to open the URL directly:
```powershell
Start-Process "http://127.0.0.1/"
```

For Swagger:
```powershell
Start-Process "http://127.0.0.1/api/docs/"
```

## 🧪 Test from Command Line

You can verify the services are working with PowerShell:

```powershell
# Test main page
Invoke-WebRequest -Uri "http://localhost/" -UseBasicParsing

# Test Swagger
Invoke-WebRequest -Uri "http://localhost/api/docs/" -UseBasicParsing

# Test API endpoint
Invoke-WebRequest -Uri "http://localhost/api/auth/login/" -Method POST -ContentType "application/json" -Body '{"username":"admin","password":"admin123"}' -UseBasicParsing
```

## 📊 Check Service Status

```powershell
# View all containers
docker-compose ps

# Check if port 80 is listening
netstat -ano | Select-String ":80 "

# View logs
docker-compose logs -f
```

## 🔄 If Nothing Works: Full Restart

```powershell
# Stop everything
docker-compose down

# Remove volumes (optional - will delete data)
docker-compose down -v

# Start fresh
docker-compose up --build -d

# Wait 30 seconds for services to start
timeout /t 30

# Try accessing again
Start-Process "http://127.0.0.1/"
```

## 📱 Alternative: Access via IP Address

Find your machine's IP address:
```powershell
ipconfig | Select-String "IPv4"
```

Then try accessing via that IP (e.g., http://192.168.1.100/)

## 🆘 Still Not Working?

If none of these work, the issue might be:
1. **Firewall blocking**: Check Windows Firewall settings
2. **Antivirus blocking**: Temporarily disable antivirus
3. **Corporate network**: Check with IT if on company network
4. **Port conflict**: Another service might be using port 80

### Check for Port Conflicts:
```powershell
# See what's using port 80
Get-Process -Id (Get-NetTCPConnection -LocalPort 80).OwningProcess | Select-Object ProcessName, Id
```

## ✅ Quick Verification Script

Save this as `test-connection.ps1` and run it:

```powershell
Write-Host "Testing Energy Management System..." -ForegroundColor Cyan

# Test localhost
try {
    $response = Invoke-WebRequest -Uri "http://localhost/" -UseBasicParsing -TimeoutSec 5
    Write-Host "✅ localhost: OK (Status: $($response.StatusCode))" -ForegroundColor Green
} catch {
    Write-Host "❌ localhost: FAILED" -ForegroundColor Red
}

# Test 127.0.0.1
try {
    $response = Invoke-WebRequest -Uri "http://127.0.0.1/" -UseBasicParsing -TimeoutSec 5
    Write-Host "✅ 127.0.0.1: OK (Status: $($response.StatusCode))" -ForegroundColor Green
} catch {
    Write-Host "❌ 127.0.0.1: FAILED" -ForegroundColor Red
}

# Test Swagger
try {
    $response = Invoke-WebRequest -Uri "http://localhost/api/docs/" -UseBasicParsing -TimeoutSec 5
    Write-Host "✅ Swagger: OK (Status: $($response.StatusCode))" -ForegroundColor Green
} catch {
    Write-Host "❌ Swagger: FAILED" -ForegroundColor Red
}

# Check Docker
Write-Host "`nDocker Status:" -ForegroundColor Cyan
docker-compose ps

Write-Host "`nIf all tests pass but browser fails, try:" -ForegroundColor Yellow
Write-Host "1. Use http://127.0.0.1/ instead of http://localhost/" -ForegroundColor Yellow
Write-Host "2. Clear browser cache" -ForegroundColor Yellow
Write-Host "3. Try a different browser" -ForegroundColor Yellow
```

---

**The services are confirmed working - this is a browser/network configuration issue, not a Docker/application issue!**
