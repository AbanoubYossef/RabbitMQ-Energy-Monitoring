import apiClient from './client';
import type { Device, CreateDeviceData, UpdateDeviceData, DeviceAssignment, AssignDeviceData, DeviceResponse, AssignmentResponse } from '../types';

export const devicesApi = {
  // Create device (admin only)
  create: async (data: CreateDeviceData): Promise<DeviceResponse> => {
    const response = await apiClient.post('/api/devices/create/', data);
    return response.data;
  },

  // Get all devices
  getAll: async (): Promise<Device[]> => {
    const response = await apiClient.get('/api/devices/');
    return response.data;
  },

  // Get device by ID
  getById: async (deviceId: string): Promise<Device> => {
    const response = await apiClient.get(`/api/devices/${deviceId}/`);
    return response.data;
  },

  // Update device (admin only)
  update: async (deviceId: string, data: UpdateDeviceData): Promise<DeviceResponse> => {
    const response = await apiClient.put(`/api/devices/${deviceId}/update/`, data);
    return response.data;
  },

  // Delete device (admin only)
  delete: async (deviceId: string): Promise<{ message: string }> => {
    const response = await apiClient.delete(`/api/devices/${deviceId}/delete/`);
    return response.data;
  },

  // Assign device to user (admin only)
  assign: async (data: AssignDeviceData): Promise<AssignmentResponse> => {
    const response = await apiClient.post('/api/devices/assign/', data);
    return response.data;
  },

  // Unassign device (admin only)
  unassign: async (deviceId: string, userId: string): Promise<{ message: string }> => {
    const response = await apiClient.delete(`/api/devices/${deviceId}/unassign/?user_id=${userId}`);
    return response.data;
  },

  // Get all device assignments (admin only)
  getAllAssignments: async (): Promise<DeviceAssignment[]> => {
    const response = await apiClient.get('/api/mappings/');
    return response.data;
  },
};