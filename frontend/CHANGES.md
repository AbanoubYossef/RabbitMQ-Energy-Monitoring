# Frontend API Integration Changes

## Summary
Updated the frontend to properly integrate with the microservices backend APIs.

## Files Modified

### 1. `src/types/index.ts`
**Changes:**
- Updated `AuthResponse` to match backend structure with nested `tokens` object
- Updated `DecodedToken` to include all JWT payload fields (`user_id`, `iat`, `jti`, `token_type`)
- Updated `Device` interface to use `id` instead of `device_id`
- Changed `max_consumption` and `price` to `string` type (backend returns strings)
- Added `owner_username` field to Device
- Updated `DeviceAssignment` to match backend response structure
- Added `DeviceResponse` and `AssignmentResponse` types for API responses

### 2. `src/api/auth.ts`
**Changes:**
- Kept register and login endpoints (they work correctly)
- Updated response types to match backend structure
- Added user management endpoints from auth service:
  - `getAllUsers()` - GET /api/auth/users/
  - `getUserById()` - GET /api/auth/users/{id}/
  - `updateUser()` - PUT /api/auth/users/{id}/update/
  - `deleteUser()` - DELETE /api/auth/users/{id}/delete/

### 3. `src/api/users.ts`
**Changes:**
- Changed all endpoints to use `/api/users/` instead of `/api/auth/users/`
- Updated return types to match backend response structure
- Removed `getUserDevices()` (not available in user service)
- All methods now return proper response objects with `message` field

### 4. `src/api/devices.ts`
**Changes:**
- Updated all return types to match backend response structure
- `create()` and `update()` now return `DeviceResponse` with nested device object
- `assign()` returns `AssignmentResponse` with nested mapping object
- `delete()` and `unassign()` return objects with `message` field
- Removed `getUserDevices()` (endpoint routing issue with Traefik)

### 5. `src/api/client.ts`
**Changes:**
- Simplified response interceptor
- Removed token refresh logic (backend doesn't support refresh endpoint)
- On 401 error, clear tokens and redirect to login immediately

### 6. `src/pages/devices/DevicesListPage.tsx`
**Changes:**
- Changed `device.device_id` to `device.id` throughout
- Updated error handling to check for `error` field in response

### 7. `src/pages/devices/CreateDevicePage.tsx`
**Changes:**
- Updated to handle `DeviceResponse` structure
- Added console.log for success message
- Updated error handling to check for `error` field

## API Endpoint Changes

### Before:
- Users: `/api/auth/users/` (mixed with auth endpoints)
- Devices: Various response structures

### After:
- Auth: `/api/auth/` (register, login, validate, user management)
- Users: `/api/users/` (user service endpoints)
- Devices: `/api/devices/` and `/api/mappings/` (device service endpoints)

## Response Structure Changes

### Authentication Responses
**Before:**
```typescript
{
  access: string;
  refresh: string;
  user: User;
}
```

**After:**
```typescript
{
  message: string;
  tokens: {
    access: string;
    refresh: string;
    user: User;
  }
}
```

### Device Responses
**Before:**
```typescript
Device  // Direct device object
```

**After:**
```typescript
{
  message: string;
  device: Device;
}
```

### Assignment Responses
**Before:**
```typescript
DeviceAssignment  // Direct assignment object
```

**After:**
```typescript
{
  message: string;
  mapping: DeviceAssignment;
}
```

## Breaking Changes

1. **Device ID Field**: Changed from `device_id` to `id`
2. **Numeric Fields**: `max_consumption` and `price` are now strings
3. **Response Wrapping**: Most responses now include a `message` field and wrap data
4. **Token Refresh**: Removed automatic token refresh (not supported by backend)

## Testing Checklist

- [x] User registration works
- [x] User login works
- [x] Token validation works
- [x] List users (admin)
- [x] Get user by ID
- [x] Update user (admin)
- [x] Delete user (admin)
- [x] List devices
- [x] Create device (admin)
- [x] Update device (admin)
- [x] Delete device (admin)
- [x] Assign device (admin)
- [x] List device assignments

## Migration Guide for Developers

If you have existing code that uses the old API structure:

1. **Update Device References:**
   ```typescript
   // Old
   device.device_id
   
   // New
   device.id
   ```

2. **Handle Wrapped Responses:**
   ```typescript
   // Old
   const device = await devicesApi.create(data);
   
   // New
   const response = await devicesApi.create(data);
   const device = response.device;
   ```

3. **Update Numeric Parsing:**
   ```typescript
   // Old
   device.price  // number
   
   // New
   parseFloat(device.price)  // string to number
   ```

4. **Update Error Handling:**
   ```typescript
   // Old
   err.response?.data?.detail
   
   // New
   err.response?.data?.error || err.response?.data?.detail
   ```

## Documentation

See `API_INTEGRATION.md` for complete API documentation including:
- All available endpoints
- Request/response formats
- Authentication flow
- Role-based access control
- Error handling
- Testing instructions
