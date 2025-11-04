import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import ProtectedRoute from './components/common/ProtectedRoute';

// Auth Pages
import LoginPage from './pages/auth/LoginPage';
import RegisterPage from './pages/auth/RegisterPage';

// Dashboard
import DashboardPage from './pages/dashboard/DashboardPage';

// User Pages
import UsersListPage from './pages/users/UsersListPage';
import CreateEditUserPage from './pages/users/CreateEditUserPage';

// Device Pages
import DevicesListPage from './pages/devices/DevicesListPage';
import CreateDevicePage from './pages/devices/CreateDevicePage';
import EditDevicePage from './pages/devices/EditDevicePage';
import AssignDevicePage from './pages/devices/AssignDevicePage';

function App() {
  return (
    <Router>
      <AuthProvider>
        <Routes>
          {/* Public Routes */}
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />

          {/* Protected Routes */}
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <DashboardPage />
              </ProtectedRoute>
            }
          />

          {/* User Management Routes (Admin only) */}
          <Route
            path="/users"
            element={
              <ProtectedRoute requireAdmin>
                <UsersListPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/users/create"
            element={
              <ProtectedRoute requireAdmin>
                <CreateEditUserPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/users/:userId/edit"
            element={
              <ProtectedRoute requireAdmin>
                <CreateEditUserPage />
              </ProtectedRoute>
            }
          />

          {/* Device Management Routes */}
          <Route
            path="/devices"
            element={
              <ProtectedRoute>
                <DevicesListPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/devices/create"
            element={
              <ProtectedRoute requireAdmin>
                <CreateDevicePage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/devices/:deviceId/edit"
            element={
              <ProtectedRoute requireAdmin>
                <EditDevicePage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/devices/assign"
            element={
              <ProtectedRoute requireAdmin>
                <AssignDevicePage />
              </ProtectedRoute>
            }
          />

          {/* Default Route */}
          <Route path="/" element={<Navigate to="/dashboard" replace />} />

          {/* Catch all - redirect to dashboard */}
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </AuthProvider>
    </Router>
  );
}

export default App;