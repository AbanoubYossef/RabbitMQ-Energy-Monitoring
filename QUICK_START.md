# ⚡ Quick Start - 3 Minutes to API Testing

## 🎯 Goal
Login and test your APIs using Swagger UI in 3 simple steps!

---

## Step 1️⃣: Open Swagger (10 seconds)

Open your browser and go to:
```
http://127.0.0.1/api/docs/
```

---

## Step 2️⃣: Login & Get Token (30 seconds)

1. Find **`POST /api/auth/login/`** endpoint
2. Click **"Try it out"**
3. Enter credentials:
   ```json
   {
     "username": "admin",
     "password": "admin123"
   }
   ```
4. Click **"Execute"**
5. **Copy** the `access` token from the response

---

## Step 3️⃣: Authorize (20 seconds)

1. Click the **"Authorize" 🔒** button (top right)
2. Type: **`Bearer `** (with space)
3. **Paste** your token after "Bearer "
4. Click **"Authorize"**
5. Click **"Close"**

---

## ✅ Done! Now Test Any Endpoint

Try these:

### See All Users
- `GET /api/auth/users/` → Click "Try it out" → "Execute"

### See All Devices  
- `GET /api/devices/` → Click "Try it out" → "Execute"

### Create a Device
- `POST /api/devices/create/` → Click "Try it out"
- Enter:
  ```json
  {
    "name": "Test Device",
    "description": "My first device",
    "max_consumption": 1000,
    "price": 99.99
  }
  ```
- Click "Execute"

---

## 🔑 Login Credentials

**Admin (Full Access):**
- Username: `admin`
- Password: `admin123`

**Client (View Only):**
- Username: `alice`  
- Password: `alice123`

---

## 📍 All Swagger URLs

| Service | URL |
|---------|-----|
| **Auth Service** | http://127.0.0.1/api/docs/ |
| **User Service** | http://127.0.0.1:8001/api/docs/ |
| **Device Service** | http://127.0.0.1:8002/api/docs/ |

---

## 🆘 Problems?

**Can't access Swagger?**
- Use `http://127.0.0.1/api/docs/` (not localhost)
- Clear browser cache (Ctrl+Shift+Delete)
- Try incognito mode (Ctrl+Shift+N)

**Getting "Unauthorized"?**
- Did you click "Authorize"?
- Did you type `Bearer ` before the token?
- Token format: `Bearer eyJ0eXAiOiJKV1Qi...`

**Need more help?**
- See: `HOW_TO_LOGIN_SWAGGER.md` (detailed guide)
- See: `SWAGGER_GUIDE.md` (complete documentation)

---

## 🎉 That's It!

You're now ready to test all your APIs interactively!

**Happy Testing! 🚀**
