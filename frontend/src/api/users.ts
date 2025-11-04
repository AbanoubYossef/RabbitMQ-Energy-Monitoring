import apiClient from './client';
import type { User } from '../types';

export const usersApi = {
  // Get all users (admin only) - from user service
  getAll: async (): Promise<User[]> => {
    const response = await apiClient.get('/api/users/');
    return response.data;
  },

  // Get user by ID - from user service
  getById: async (userId: string): Promise<User> => {
    const response = await apiClient.get(`/api/users/${userId}/`);
    return response.data;
  },

  // Update user (admin only) - from user service
  update: async (userId: string, data: Partial<User>): Promise<{ message: string; user: User }> => {
    const response = await apiClient.put(`/api/users/${userId}/update/`, data);
    return response.data;
  },

  // Delete user (admin only) - from user service
  delete: async (userId: string): Promise<{ message: string }> => {
    const response = await apiClient.delete(`/api/users/${userId}/delete/`);
    return response.data;
  },
};