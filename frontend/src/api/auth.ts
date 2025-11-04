import apiClient from './client';
import type { LoginCredentials, RegisterData, AuthResponse, User } from '../types';

export const authApi = {
  // Register new user
  register: async (data: RegisterData): Promise<AuthResponse> => {
    const response = await apiClient.post('/api/auth/register/', data);
    return response.data;
  },

  // Login user
  login: async (credentials: LoginCredentials): Promise<AuthResponse> => {
    const response = await apiClient.post('/api/auth/login/', credentials);
    return response.data;
  },

  // Validate token
  validateToken: async (): Promise<{ valid: boolean; user: User }> => {
    const response = await apiClient.get('/api/auth/validate/');
    return response.data;
  },

  // Get all users (admin only) - from auth service
  getAllUsers: async (): Promise<User[]> => {
    const response = await apiClient.get('/api/auth/users/');
    return response.data;
  },

  // Get user by ID - from auth service
  getUserById: async (userId: string): Promise<User> => {
    const response = await apiClient.get(`/api/auth/users/${userId}/`);
    return response.data;
  },

  // Update user - from auth service
  updateUser: async (userId: string, data: Partial<User>): Promise<{ message: string; user: User }> => {
    const response = await apiClient.put(`/api/auth/users/${userId}/update/`, data);
    return response.data;
  },

  // Delete user - from auth service
  deleteUser: async (userId: string): Promise<{ message: string }> => {
    const response = await apiClient.delete(`/api/auth/users/${userId}/delete/`);
    return response.data;
  },
};