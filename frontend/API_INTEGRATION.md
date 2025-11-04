# Frontend API Integration Guide

## Overview
This document describes how the frontend integrates with the microservices backend APIs.

## Backend Architecture
The backend consists of three microservices:
- **Auth Service** (port 8000): Authentication, JWT tokens, user management
- **User Service** (port 8001): User profile data
- **Device Service** (port 8002): Device management and assignments
- **Traefik** (port 80): API Gateway/Reverse Proxy

All requests go through Traefik at `http://localhost`.

## API Endpoints

### Authentication Service (`/api/auth/`)

#### Register User
```typescript
POST /api/auth/register/
Body: {
  username: string;
  password: string;
  role?: 'admin' | 'client';
  fname?: string;
  lname?: string;
  email?: string;
  phone?: string;
}
Response: {
  message: string;
  tokens: {
    access: string;
    refresh: string;
    user: User;
  }
}
```

#### Login
```typescript
POST /api/auth/login/
Body: {
  username: string;
  password: string;
}
Response: {
  message: string;
  tokens: {
    access: string;
    refresh: string;
    user: User;
  }
}
```

#### Validate Token
```typescript
GET /api/auth/validate/
Headers: Authorization: Bearer <token>
Response: {
  valid: boolean;
  user: User;
}
```

### User Service (`/api/users/`)

#### List All Users (Admin Only)
```typescript
GET /api/users/
Headers: Authorization: Bearer <token>
Response: User[]
```

#### Get User by ID
```typescript
GET /api/users/{user_id}/
Headers: Authorization: Bearer <token>
Response: User
```

#### Update User (Admin Only)
```typescript
PUT /api/users/{user_id}/update/
Headers: Authorization: Bearer <token>
Body: {
  fname?: string;
  lname?: string;
  email?: string;
  phone?: string;
}
Response: {
  message: string;
  user: User;
}
```

#### Delete User (Admin Only)
```typescript
DELETE /api/users/{user_id}/delete/
Headers: Authorization: Bearer <token>
Response: {
  message: string;
}
```

### Device Service (`/api/devices/`)

#### List All Devices
```typescript
GET /api/devices/
Headers: Authorization: Bearer <token>
Response: Device[]
```

#### Get Device by ID
```typescript
GET /api/devices/{device_id}/
Headers: Authorization: Bearer <token>
Response: Device
```

#### Create Device (Admin Only)
```typescript
POST /api/devices/create/
Headers: Authorization: Bearer <token>
Body: {
  name: string;
  description: string;
  max_consumption: number;
  price: number;
}
Response: {
  message: string;
  device: Device;
}
```

#### Update Device (Admin Only)
```typescript
PUT /api/devices/{device_id}/update/
Headers: Authorization: Bearer <token>
Body: {
  name?: string;
  description?: string;
  max_consumption?: number;
  price?: number;
}
Response: {
  message: string;
  device: Device;
}
```

#### Delete Device (Admin Only)
```typescript
DELETE /api/devices/{device_id}/delete/
Headers: Authorization: Bearer <token>
Response: {
  message: string;
}
```

#### Assign Device to User (Admin Only)
```typescript
POST /api/devices/assign/
Headers: Authorization: Bearer <token>
Body: {
  user_id: string;
  device_id: string;
}
Response: {
  message: string;
  mapping: DeviceAssignment;
}
```

#### Unassign Device (Admin Only)
```typescript
DELETE /api/devices/{device_id}/unassign/
Headers: Authorization: Bearer <token>
Response: {
  message: string;
}
```

#### List All Device Assignments (Admin Only)
```typescript
GET /api/mappings/
Headers: Authorization: Bearer <token>
Response: DeviceAssignment[]
```

## Data Types

### User
```typescript
interface User {
  id: string;
  username: string;
  role: 'admin' | 'client';
  fname?: string;
  lname?: string;
  email?: string;
  phone?: string;
  created_at?: string;
}
```

### Device
```typescript
interface Device {
  id: string;
  name: string;
  description: string;
  max_consumption: string;  // Backend returns as string
  price: string;            // Backend returns as string
  created_at: string;
  owner_username?: string | null;
}
```

### DeviceAssignment
```typescript
interface DeviceAssignment {
  id: string;
  user: string;  // UUID
  device: string;  // UUID
  device_name: string;
  user_username: string;
  assigned_at: string;
}
```

## Authentication Flow

1. **Login/Register**: User submits credentials
2. **Receive Tokens**: Backend returns access and refresh tokens
3. **Store Tokens**: Frontend stores tokens in localStorage
4. **Attach Token**: All subsequent requests include `Authorization: Bearer <access_token>` header
5. **Handle 401**: If token expires, redirect to login

## API Client Configuration

The API client (`src/api/client.ts`) is configured with:
- Base URL: `http://localhost` (Traefik gateway)
- Request interceptor: Automatically adds JWT token to headers
- Response interceptor: Handles 401 errors by redirecting to login

## Role-Based Access Control

### Admin Users Can:
- View all users
- Create, update, delete users
- Create, update, delete devices
- Assign/unassign devices to users
- View all device assignments

### Client Users Can:
- View their own profile
- View devices (read-only)
- View their assigned devices

## Error Handling

All API errors follow this structure:
```typescript
{
  error?: string;
  detail?: string;
  message?: string;
}
```

Frontend should check for these fields when handling errors.

## Testing the APIs

You can test the APIs using the PowerShell script:
```powershell
.\test_all_apis.ps1
```

Or manually with curl/Postman using the endpoints documented above.

## Environment Variables

Create a `.env` file in the frontend directory:
```
VITE_API_URL=http://localhost
```

## Notes

- All timestamps are in ISO 8601 format
- UUIDs are used for all entity IDs
- Numeric values (max_consumption, price) are returned as strings from backend
- Token expiration is 5 hours for access tokens
- Refresh tokens are valid for 1 day
