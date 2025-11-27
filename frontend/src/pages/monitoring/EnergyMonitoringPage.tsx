import React, { useEffect, useState } from 'react';
import { format } from 'date-fns';
import MainLayout from '../../components/layout/MainLayout';
import EnergyChart from '../../components/monitoring/EnergyChart';
import { getAccessToken } from '../../utils/auth';
import {
  getDailyConsumption,
  getMonitoringDevices,
  type Device,
  type DailyConsumptionResponse,
} from '../../api/monitoringApi';

const EnergyMonitoringPage: React.FC = () => {
  const token = getAccessToken();
  const [devices, setDevices] = useState<Device[]>([]);
  const [selectedDevice, setSelectedDevice] = useState<string>('');
  const [selectedDate, setSelectedDate] = useState<string>(
    format(new Date(), 'yyyy-MM-dd')
  );
  const [chartType, setChartType] = useState<'bar' | 'line'>('bar');
  const [consumptionData, setConsumptionData] = useState<DailyConsumptionResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Fetch devices on mount
  useEffect(() => {
    const fetchDevices = async () => {
      if (!token) return;
      try {
        const devicesData = await getMonitoringDevices(token);
        setDevices(devicesData);
        if (devicesData.length > 0) {
          setSelectedDevice(devicesData[0].id);
        }
      } catch (err: any) {
        console.error('Failed to fetch devices:', err);
        setError('Failed to load devices. Please try again.');
      }
    };
    fetchDevices();
  }, [token]);

  // Fetch consumption data when device or date changes
  useEffect(() => {
    const fetchConsumption = async () => {
      if (!token || !selectedDevice) return;

      setLoading(true);
      setError('');
      try {
        const data = await getDailyConsumption(selectedDevice, selectedDate, token);
        setConsumptionData(data);
      } catch (err: any) {
        console.error('Failed to fetch consumption data:', err);
        setError('Failed to load consumption data. Please try again.');
        setConsumptionData(null);
      } finally {
        setLoading(false);
      }
    };

    fetchConsumption();
  }, [token, selectedDevice, selectedDate]);

  const handleDeviceChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedDevice(e.target.value);
  };

  const handleDateChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSelectedDate(e.target.value);
  };

  const handleChartTypeChange = (type: 'bar' | 'line') => {
    setChartType(type);
  };

  return (
    <MainLayout>
      <div className="px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Energy Monitoring</h1>
          <p className="mt-2 text-sm text-gray-600">
            View historical energy consumption data for your devices
          </p>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-lg">
            {error}
          </div>
        )}

        {/* Filters */}
        <div className="bg-white p-6 rounded-lg shadow-lg mb-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Device Selector */}
            <div>
              <label htmlFor="device" className="block text-sm font-medium text-gray-700 mb-2">
                Select Device
              </label>
              <select
                id="device"
                value={selectedDevice}
                onChange={handleDeviceChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                disabled={devices.length === 0}
              >
                {devices.length === 0 ? (
                  <option>No devices available</option>
                ) : (
                  devices.map((device) => (
                    <option key={device.id} value={device.id}>
                      {device.name}
                    </option>
                  ))
                )}
              </select>
            </div>

            {/* Date Picker */}
            <div>
              <label htmlFor="date" className="block text-sm font-medium text-gray-700 mb-2">
                Select Date
              </label>
              <input
                type="date"
                id="date"
                value={selectedDate}
                onChange={handleDateChange}
                max={format(new Date(), 'yyyy-MM-dd')}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>

            {/* Chart Type Selector */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Chart Type
              </label>
              <div className="flex space-x-2">
                <button
                  onClick={() => handleChartTypeChange('bar')}
                  className={`flex-1 px-4 py-2 rounded-lg font-medium transition ${
                    chartType === 'bar'
                      ? 'bg-indigo-600 text-white'
                      : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                  }`}
                >
                  Bar Chart
                </button>
                <button
                  onClick={() => handleChartTypeChange('line')}
                  className={`flex-1 px-4 py-2 rounded-lg font-medium transition ${
                    chartType === 'line'
                      ? 'bg-indigo-600 text-white'
                      : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                  }`}
                >
                  Line Chart
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Loading State */}
        {loading && (
          <div className="flex justify-center items-center h-96">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
          </div>
        )}

        {/* Chart and Stats */}
        {!loading && consumptionData && (
          <>
            {/* Summary Stats */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
              <div className="bg-white p-6 rounded-lg shadow-lg">
                <div className="flex items-center">
                  <div className="flex-shrink-0 bg-indigo-500 rounded-md p-3">
                    <svg className="h-6 w-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-500">Total Daily Consumption</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {consumptionData.total_daily_consumption.toFixed(3)} kWh
                    </p>
                  </div>
                </div>
              </div>

              <div className="bg-white p-6 rounded-lg shadow-lg">
                <div className="flex items-center">
                  <div className="flex-shrink-0 bg-green-500 rounded-md p-3">
                    <svg className="h-6 w-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-500">Active Hours</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {consumptionData.hourly_data.filter(h => h.total_consumption > 0).length} / 24
                    </p>
                  </div>
                </div>
              </div>

              <div className="bg-white p-6 rounded-lg shadow-lg">
                <div className="flex items-center">
                  <div className="flex-shrink-0 bg-yellow-500 rounded-md p-3">
                    <svg className="h-6 w-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-500">Peak Hour</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {consumptionData.hourly_data.reduce((max, h) => 
                        h.total_consumption > max.total_consumption ? h : max
                      ).hour}:00
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Chart */}
            {consumptionData.hourly_data.length > 0 ? (
              <EnergyChart
                data={consumptionData.hourly_data}
                chartType={chartType}
                title={`Hourly Energy Consumption - ${format(new Date(selectedDate), 'MMMM dd, yyyy')}`}
              />
            ) : (
              <div className="bg-white p-12 rounded-lg shadow-lg text-center">
                <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
                <h3 className="mt-4 text-lg font-medium text-gray-900">No data available</h3>
                <p className="mt-2 text-sm text-gray-500">
                  No energy consumption data found for this device on the selected date.
                </p>
              </div>
            )}
          </>
        )}

        {/* No Device Selected */}
        {!loading && !consumptionData && devices.length === 0 && (
          <div className="bg-white p-12 rounded-lg shadow-lg text-center">
            <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
            </svg>
            <h3 className="mt-4 text-lg font-medium text-gray-900">No devices available</h3>
            <p className="mt-2 text-sm text-gray-500">
              No devices have been synchronized to the monitoring service yet.
            </p>
          </div>
        )}
      </div>
    </MainLayout>
  );
};

export default EnergyMonitoringPage;
