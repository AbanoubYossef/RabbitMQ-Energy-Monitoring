# How to Login and Use Swagger UI

## 🚀 Quick Start Guide

### Step 1: Open Swagger UI

Open your browser and go to:
```
http://127.0.0.1/api/docs/
```

You'll see the Swagger UI interface with all available API endpoints.

---

## 🔐 Step 2: Login to Get Access Token

### Method A: Using Swagger UI

1. **Find the Login Endpoint**
   - Scroll down to find `POST /api/auth/login/`
   - Click on it to expand

2. **Click "Try it out"** button (top right of the endpoint)

3. **Fill in the Request Body**
   ```json
   {
     "username": "admin",
     "password": "admin123"
   }
   ```

4. **Click "Execute"** button

5. **Copy the Access Token**
   - Look at the response below
   - Find the `access` token in the response
   - Copy the entire token (it's a long string starting with `eyJ...`)

   Example response:
   ```json
   {
     "message": "Login successful",
     "tokens": {
       "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",  ← COPY THIS
       "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
       "user": {
         "id": "uuid-here",
         "username": "admin",
         "role": "admin"
       }
     }
   }
   ```

---

## 🔓 Step 3: Authorize in Swagger

1. **Click the "Authorize" button**
   - It's at the top right of the page
   - Has a lock icon 🔒

2. **Enter the Token**
   - In the popup window, you'll see a field labeled "Value"
   - Type: `Bearer ` (with a space after it)
   - Paste your access token after "Bearer "
   - Should look like: `Bearer eyJ0eXAiOiJKV1QiLCJhbGc...`

3. **Click "Authorize"** button

4. **Click "Close"** button

✅ You're now authenticated! All API requests will include your token.

---

## 🎯 Step 4: Test Protected Endpoints

Now you can test any endpoint! Try these:

### Get All Users (Admin only)
1. Find `GET /api/auth/users/`
2. Click "Try it out"
3. Click "Execute"
4. See the list of all users

### Get All Devices
1. Find `GET /api/devices/`
2. Click "Try it out"
3. Click "Execute"
4. See all devices

### Create a New Device (Admin only)
1. Find `POST /api/devices/create/`
2. Click "Try it out"
3. Fill in the request body:
   ```json
   {
     "name": "Smart Meter",
     "description": "Energy monitoring device",
     "max_consumption": 5000,
     "price": 299.99
   }
   ```
4. Click "Execute"
5. See the newly created device

---

## 👥 Available Test Accounts

### Admin Account (Full Access)
```
Username: admin
Password: admin123
```
- Can create/update/delete users
- Can create/update/delete devices
- Can assign devices to users
- Can view everything

### Client Account (Read Only)
```
Username: alice
Password: alice123
```
- Can view own dashboard
- Can view assigned devices
- Cannot modify anything

---

## 📝 Common Tasks

### 1. Register a New User
```
POST /api/auth/register/

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

### 2. Create a Device (Admin only)
```
POST /api/devices/create/

{
  "name": "Solar Panel Monitor",
  "description": "Tracks solar panel output",
  "max_consumption": 3000,
  "price": 499.99
}
```

### 3. Assign Device to User (Admin only)
```
POST /api/devices/assign/

{
  "user_id": "user-uuid-here",
  "device_id": "device-uuid-here"
}
```

### 4. Get User's Devices
```
GET /api/users/{user_id}/devices/
```

---

## 🔄 If Token Expires

JWT tokens expire after 5 hours. If you get authentication errors:

1. Go back to `POST /api/auth/login/`
2. Login again to get a new token
3. Click "Authorize" and enter the new token

---

## 🌐 All Swagger URLs

### Auth Service (Main)
**http://127.0.0.1/api/docs/**
- User registration
- Login/authentication
- User management

### User Service
**http://127.0.0.1:8001/api/docs/**
- User profile operations
- Internal user service endpoints

### Device Service
**http://127.0.0.1:8002/api/docs/**
- Device management
- Device assignments
- User-device mappings

---

## 💡 Tips

1. **Always use "Try it out"** before you can edit the request
2. **Check the response** to see if the request was successful
3. **Copy UUIDs** from responses to use in other requests
4. **Use the "Authorize" button** once, and all requests will be authenticated
5. **Scroll down** to see all available endpoints
6. **Expand sections** by clicking on them
7. **Look for green (200)** responses = success
8. **Red (400/401/403/500)** responses = error

---

## 🐛 Troubleshooting

### "Unauthorized" Error
- Make sure you clicked "Authorize" and entered the token
- Check that you used `Bearer ` before the token
- Token might be expired - login again

### "Forbidden" Error
- You don't have permission (e.g., client trying to delete users)
- Login as admin for full access

### "Not Found" Error
- Check the UUID is correct
- The resource might have been deleted

### Can't See Swagger UI
- Use `http://127.0.0.1/api/docs/` instead of `localhost`
- Clear browser cache
- Try incognito mode

---

## 📖 Example Complete Flow

```
1. Open: http://127.0.0.1/api/docs/

2. Login:
   POST /api/auth/login/
   {
     "username": "admin",
     "password": "admin123"
   }

3. Copy access token from response

4. Click "Authorize" button
   Enter: Bearer eyJ0eXAiOiJKV1Qi...
   Click "Authorize"
   Click "Close"

5. Test endpoints:
   GET /api/auth/users/          ← See all users
   GET /api/devices/              ← See all devices
   POST /api/devices/create/      ← Create new device
   POST /api/devices/assign/      ← Assign device to user

6. Done! 🎉
```

---

**Need help? Check SWAGGER_GUIDE.md for more detailed information!**
