import React, { useEffect, useState } from 'react';
import type { Device, User, DeviceAssignment } from '../../types';
import { devicesApi, usersApi } from '../../api';
import MainLayout from '../../components/layout/MainLayout';

const AssignDevicePage: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [devices, setDevices] = useState<Device[]>([]);
  const [assignments, setAssignments] = useState<DeviceAssignment[]>([]);
  const [selectedUserId, setSelectedUserId] = useState('');
  const [selectedDeviceId, setSelectedDeviceId] = useState('');
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [usersData, devicesData, assignmentsData] = await Promise.all([
        usersApi.getAll(),
        devicesApi.getAll(),
        devicesApi.getAllAssignments(),
      ]);
      setUsers(usersData);
      setDevices(devicesData);
      setAssignments(assignmentsData);
    } catch (err: any) {
      setError('Failed to load data');
      console.error('Error fetching data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleAssign = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (!selectedUserId || !selectedDeviceId) {
      setError('Please select both a user and a device');
      return;
    }

    // Check if this specific user-device combination already exists
    const isAlreadyAssigned = assignments.some(
      a => a.device === selectedDeviceId && a.user === selectedUserId
    );
    if (isAlreadyAssigned) {
      setError('This device is already assigned to this user');
      return;
    }

    setSubmitting(true);

    try {
      const response = await devicesApi.assign({
        user_id: selectedUserId,
        device_id: selectedDeviceId,
      });
      setSuccess(response.message || 'Device assigned successfully!');
      setSelectedUserId('');
      setSelectedDeviceId('');
      // Refresh assignments
      const assignmentsData = await devicesApi.getAllAssignments();
      setAssignments(assignmentsData);
    } catch (err: any) {
      setError(err.response?.data?.error || err.response?.data?.detail || 'Failed to assign device');
    } finally {
      setSubmitting(false);
    }
  };

  const handleUnassign = async (deviceId: string, userId: string) => {
    if (!confirm('Are you sure you want to unassign this device from this user?')) {
      return;
    }

    try {
      await devicesApi.unassign(deviceId, userId);
      setSuccess('Device unassigned successfully!');
      // Refresh assignments
      const assignmentsData = await devicesApi.getAllAssignments();
      setAssignments(assignmentsData);
    } catch (err: any) {
      setError(err.response?.data?.error || err.response?.data?.detail || 'Failed to unassign device');
    }
  };

  const getUserName = (userId: string) => {
    const user = users.find(u => u.id === userId);
    return user ? user.username : userId;
  };

  const getDeviceName = (deviceId: string) => {
    const device = devices.find(d => d.id === deviceId);
    return device ? device.name : deviceId;
  };

  if (loading) {
    return (
      <MainLayout>
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
        </div>
      </MainLayout>
    );
  }

  // Removed unused variable - all devices are shown in dropdown

  return (
    <MainLayout>
      <div className="px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900">Assign Devices</h1>
            <p className="mt-2 text-sm text-gray-600">
              Assign energy monitoring devices to users.
            </p>
          </div>

          {error && (
            <div className="mb-4 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}

          {success && (
            <div className="mb-4 bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded">
              {success}
            </div>
          )}

          {/* Assignment Form */}
          <div className="bg-white shadow-lg rounded-lg p-6 mb-8">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">New Assignment</h2>
            <form onSubmit={handleAssign} className="space-y-4">
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <div>
                  <label htmlFor="user" className="block text-sm font-medium text-gray-700 mb-1">
                    Select User *
                  </label>
                  <select
                    id="user"
                    value={selectedUserId}
                    onChange={(e) => setSelectedUserId(e.target.value)}
                    className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm px-3 py-2 border"
                    required
                  >
                    <option value="">-- Choose a user --</option>
                    {users.map((user) => (
                      <option key={user.id} value={user.id}>
                        {user.username} ({user.role})
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label htmlFor="device" className="block text-sm font-medium text-gray-700 mb-1">
                    Select Device *
                  </label>
                  <select
                    id="device"
                    value={selectedDeviceId}
                    onChange={(e) => setSelectedDeviceId(e.target.value)}
                    className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm px-3 py-2 border"
                    required
                  >
                    <option value="">-- Choose a device --</option>
                    {devices.map((device) => (
                      <option key={device.id} value={device.id}>
                        {device.name}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="flex justify-end">
                <button
                  type="submit"
                  disabled={submitting}
                  className="inline-flex justify-center rounded-md border border-transparent bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:bg-indigo-400 disabled:cursor-not-allowed"
                >
                  {submitting ? 'Assigning...' : 'Assign Device'}
                </button>
              </div>
            </form>
          </div>

          {/* Current Assignments */}
          <div className="bg-white shadow-lg rounded-lg overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">Current Assignments</h2>
            </div>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      User
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Device
                    </th>
                    <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {assignments.length === 0 ? (
                    <tr>
                      <td colSpan={3} className="px-6 py-8 text-center text-sm text-gray-500">
                        No device assignments yet
                      </td>
                    </tr>
                  ) : (
                    assignments.map((assignment) => (
                      <tr key={assignment.id}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {getUserName(assignment.user)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {getDeviceName(assignment.device)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                          <button
                            onClick={() => handleUnassign(assignment.device, assignment.user)}
                            className="text-red-600 hover:text-red-900"
                          >
                            Unassign
                          </button>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </MainLayout>
  );
};

export default AssignDevicePage;