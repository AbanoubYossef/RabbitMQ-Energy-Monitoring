/**
 * Monitoring Service API Client
 * Handles energy consumption data queries
 */

import axios from 'axios';

const API_BASE_URL = '/api/monitoring';

export interface HourlyData {
  hour: number;
  total_consumption: number;
  measurement_count: number;
}

export interface DailyConsumptionResponse {
  device_id: string;
  date: string;
  hourly_data: HourlyData[];
  total_daily_consumption: number;
}

export interface DateRangeConsumptionResponse {
  device_id: string;
  start_date: string;
  end_date: string;
  data: Array<{
    id: string;
    device_id: string;
    date: string;
    hour: number;
    total_consumption: number;
    measurement_count: number;
  }>;
  total_consumption: number;
}

export interface Device {
  id: string;
  name: string;
  description: string;
  max_consumption: number;
  created_at: string;
}

/**
 * Get daily hourly consumption for a specific device and date
 */
export const getDailyConsumption = async (
  deviceId: string,
  date: string,
  token: string
): Promise<DailyConsumptionResponse> => {
  const response = await axios.get(
    `${API_BASE_URL}/hourly/daily/`,
    {
      params: { device_id: deviceId, date },
      headers: { Authorization: `Bearer ${token}` }
    }
  );
  return response.data;
};

/**
 * Get consumption data for a date range
 */
export const getDateRangeConsumption = async (
  deviceId: string,
  startDate: string,
  endDate: string,
  token: string
): Promise<DateRangeConsumptionResponse> => {
  const response = await axios.get(
    `${API_BASE_URL}/hourly/range/`,
    {
      params: {
        device_id: deviceId,
        start_date: startDate,
        end_date: endDate
      },
      headers: { Authorization: `Bearer ${token}` }
    }
  );
  return response.data;
};

/**
 * Get list of synchronized devices
 */
export const getMonitoringDevices = async (token: string): Promise<Device[]> => {
  const response = await axios.get(
    `${API_BASE_URL}/devices/`,
    {
      headers: { Authorization: `Bearer ${token}` }
    }
  );
  return response.data;
};
