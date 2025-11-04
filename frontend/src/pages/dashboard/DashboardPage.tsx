import React, { useEffect, useState } from 'react';
import type { Device } from '../../types';
import { useAuth } from '../../contexts/AuthContext';
import { devicesApi, usersApi } from '../../api';
import MainLayout from '../../components/layout/MainLayout';

const DashboardPage: React.FC = () => {
  const { user, isAdmin } = useAuth();
  const [myDevices, setMyDevices] = useState<Device[]>([]);
  const [stats, setStats] = useState({
    totalUsers: 0,
    totalDevices: 0,
    totalAssignments: 0,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        if (isAdmin) {
          // Fetch admin statistics
          const [users, devices, assignments] = await Promise.all([
            usersApi.getAll(),
            devicesApi.getAll(),
            devicesApi.getAllAssignments(),
          ]);
          setStats({
            totalUsers: users.length,
            totalDevices: devices.length,
            totalAssignments: assignments.length,
          });
        } else {
          // Fetch client's devices - the API already filters by user
          const devices = await devicesApi.getAll();
          setMyDevices(devices);
        }
      } catch (err: any) {
        setError('Failed to load dashboard data');
        console.error('Dashboard error:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, [user, isAdmin]);

  if (loading) {
    return (
      <MainLayout>
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      <div className="px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="mt-2 text-sm text-gray-600">
            Welcome back, {user?.username}!
          </p>
        </div>

        {error && (
          <div className="mb-4 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        )}

        {isAdmin ? (
          // Admin Dashboard
          <div>
            <h2 className="text-xl font-semibold text-gray-800 mb-4">System Overview</h2>
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
              <div className="bg-white overflow-hidden shadow-lg rounded-lg">
                <div className="p-6">
                  <div className="flex items-center">
                    <div className="flex-shrink-0 bg-indigo-500 rounded-md p-3">
                      <svg className="h-6 w-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                      </svg>
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">Total Users</dt>
                        <dd className="flex items-baseline">
                          <div className="text-2xl font-semibold text-gray-900">{stats.totalUsers}</div>
                        </dd>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-white overflow-hidden shadow-lg rounded-lg">
                <div className="p-6">
                  <div className="flex items-center">
                    <div className="flex-shrink-0 bg-green-500 rounded-md p-3">
                      <svg className="h-6 w-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
                      </svg>
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">Total Devices</dt>
                        <dd className="flex items-baseline">
                          <div className="text-2xl font-semibold text-gray-900">{stats.totalDevices}</div>
                        </dd>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-white overflow-hidden shadow-lg rounded-lg">
                <div className="p-6">
                  <div className="flex items-center">
                    <div className="flex-shrink-0 bg-yellow-500 rounded-md p-3">
                      <svg className="h-6 w-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                      </svg>
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">Active Assignments</dt>
                        <dd className="flex items-baseline">
                          <div className="text-2xl font-semibold text-gray-900">{stats.totalAssignments}</div>
                        </dd>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div className="mt-8 bg-white shadow-lg rounded-lg p-6">
              <h3 className="text-lg font-semibold text-gray-800 mb-4">Quick Actions</h3>
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
                <a
                  href="/users"
                  className="block p-4 border border-gray-300 rounded-lg hover:border-indigo-500 hover:shadow-md transition"
                >
                  <h4 className="font-medium text-gray-900">Manage Users</h4>
                  <p className="mt-1 text-sm text-gray-500">View and manage all users</p>
                </a>
                <a
                  href="/devices"
                  className="block p-4 border border-gray-300 rounded-lg hover:border-indigo-500 hover:shadow-md transition"
                >
                  <h4 className="font-medium text-gray-900">Manage Devices</h4>
                  <p className="mt-1 text-sm text-gray-500">View and manage all devices</p>
                </a>
                <a
                  href="/devices/assign"
                  className="block p-4 border border-gray-300 rounded-lg hover:border-indigo-500 hover:shadow-md transition"
                >
                  <h4 className="font-medium text-gray-900">Assign Devices</h4>
                  <p className="mt-1 text-sm text-gray-500">Assign devices to users</p>
                </a>
              </div>
            </div>
          </div>
        ) : (
          // Client Dashboard
          <div>
            <h2 className="text-xl font-semibold text-gray-800 mb-4">My Assigned Devices</h2>
            {myDevices.length === 0 ? (
              <div className="bg-white shadow-lg rounded-lg p-8 text-center">
                <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
                </svg>
                <h3 className="mt-2 text-sm font-medium text-gray-900">No devices assigned</h3>
                <p className="mt-1 text-sm text-gray-500">
                  You don't have any devices assigned to you yet. Please contact an administrator.
                </p>
              </div>
            ) : (
              <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
                {myDevices.map((device) => (
                  <div key={device.id} className="bg-white shadow-lg rounded-lg overflow-hidden hover:shadow-xl transition">
                    <div className="p-6">
                      <div className="flex items-start justify-between">
                        <div>
                          <h3 className="text-lg font-semibold text-gray-900">{device.name}</h3>
                          <p className="mt-1 text-sm text-gray-600">{device.description}</p>
                        </div>
                      </div>
                      <div className="mt-4 space-y-3 border-t pt-4">
                        <div className="flex justify-between">
                          <span className="text-sm text-gray-500">Max Consumption:</span>
                          <span className="text-sm font-semibold text-gray-900">{device.max_consumption} W</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-sm text-gray-500">Price:</span>
                          <span className="text-sm font-semibold text-gray-900">${parseFloat(device.price.toString()).toFixed(2)}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-sm text-gray-500">Created on:</span>
                          <span className="text-sm font-semibold text-gray-900">
                            {new Date(device.created_at).toLocaleDateString()}
                          </span>
                        </div>
                      </div>
                      <div className="mt-4 pt-4 border-t">
                        <div className="inline-block px-3 py-1 bg-green-100 text-green-800 rounded-full text-xs font-semibold">
                          ✓ Active
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </MainLayout>
  );
};

export default DashboardPage;