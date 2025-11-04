// User types
export interface User {
  id: string;
  username: string;
  role: 'admin' | 'client';
  fname?: string;
  lname?: string;
  email?: string;
  phone?: string;
  created_at?: string;
  updated_at?: string;
}

// Auth types
export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterData {
  username: string;
  password: string;
  role?: 'admin' | 'client';
  fname?: string;
  lname?: string;
  email?: string;
  phone?: string;
}

export interface AuthResponse {
  message: string;
  tokens: {
    access: string;
    refresh: string;
    user: User;
  };
}

export interface DecodedToken {
  user_id: string;
  username: string;
  role: 'admin' | 'client';
  exp: number;
  iat: number;
  jti: string;
  token_type: string;
}

// Device types
export interface Device {
  id: string;
  name: string;
  description: string;
  max_consumption: string;  // Backend returns as string
  price: string;            // Backend returns as string
  created_at: string;
  owner_username?: string | null;
}

export interface CreateDeviceData {
  name: string;
  description: string;
  max_consumption: number;
  price: number;
}

export interface UpdateDeviceData {
  name?: string;
  description?: string;
  max_consumption?: number;
  price?: number;
}

export interface DeviceResponse {
  message: string;
  device: Device;
}

// Device assignment types
export interface DeviceAssignment {
  id: string;
  user: string;  // UUID
  device: string;  // UUID
  device_name: string;
  user_username: string;
  assigned_at: string;
}

export interface AssignDeviceData {
  user_id: string;
  device_id: string;
}

export interface AssignmentResponse {
  message: string;
  mapping: DeviceAssignment;
}

// API Error type
export interface ApiError {
  message: string;
  status?: number;
  detail?: string;
}