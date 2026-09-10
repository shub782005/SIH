import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import Login from './pages/Login';
import CollectionPoints from './pages/CollectionPoints';
import Vehicles from './pages/Vehicles';
import Drivers from './pages/Drivers';
import Optimization from './pages/Optimization';
import RoutesView from './pages/RoutesView';
import DriverPortal from './pages/DriverPortal';
import Analytics from './pages/Analytics';
import PlaceholderPage from './pages/PlaceholderPage';
import ProtectedRoute from './components/ProtectedRoute';
import { AuthProvider } from './context/AuthContext';
import api from './services/api';

function MainLayout({ children, systemStatus }) {
  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans">
      <Navbar systemStatus={systemStatus} />

      <div className="flex flex-1">
        <Sidebar />
        <main className="flex-1 p-6 overflow-y-auto">
          {children}
        </main>
      </div>
    </div>
  );
}

export default function App() {
  const [systemStatus, setSystemStatus] = useState(null);

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const res = await api.get('/health');
        setSystemStatus(res.data);
      } catch (err) {
        setSystemStatus({ status: 'error' });
      }
    };
    checkHealth();
  }, []);

  return (
    <AuthProvider>
      <Router>
        <Routes>
          {/* Public Login Route */}
          <Route path="/login" element={<Login />} />

          {/* Protected Application Routes */}
          <Route 
            path="/" 
            element={
              <ProtectedRoute>
                <MainLayout systemStatus={systemStatus}>
                  <Dashboard />
                </MainLayout>
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/collection-points" 
            element={
              <ProtectedRoute allowedRoles={['ADMIN', 'MANAGER']}>
                <MainLayout systemStatus={systemStatus}>
                  <CollectionPoints />
                </MainLayout>
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/vehicles" 
            element={
              <ProtectedRoute allowedRoles={['ADMIN', 'MANAGER']}>
                <MainLayout systemStatus={systemStatus}>
                  <Vehicles />
                </MainLayout>
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/drivers" 
            element={
              <ProtectedRoute allowedRoles={['ADMIN', 'MANAGER']}>
                <MainLayout systemStatus={systemStatus}>
                  <Drivers />
                </MainLayout>
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/optimization" 
            element={
              <ProtectedRoute allowedRoles={['ADMIN', 'MANAGER']}>
                <MainLayout systemStatus={systemStatus}>
                  <Optimization />
                </MainLayout>
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/routes" 
            element={
              <ProtectedRoute allowedRoles={['ADMIN', 'MANAGER']}>
                <MainLayout systemStatus={systemStatus}>
                  <RoutesView />
                </MainLayout>
              </ProtectedRoute>
            } 
          />

          <Route 
            path="/analytics" 
            element={
              <ProtectedRoute allowedRoles={['ADMIN', 'MANAGER']}>
                <MainLayout systemStatus={systemStatus}>
                  <Analytics />
                </MainLayout>
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/driver" 
            element={
              <ProtectedRoute allowedRoles={['ADMIN', 'DRIVER']}>
                <MainLayout systemStatus={systemStatus}>
                  <DriverPortal />
                </MainLayout>
              </ProtectedRoute>
            } 
          />

          <Route 
            path="/settings" 
            element={
              <ProtectedRoute allowedRoles={['ADMIN']}>
                <MainLayout systemStatus={systemStatus}>
                  <PlaceholderPage title="System Configuration & Depot Setup" description="Configure single/multi-depot locations, priority calculation weights, and OSRM engine endpoints." />
                </MainLayout>
              </ProtectedRoute>
            } 
          />
        </Routes>
      </Router>
    </AuthProvider>
  );
}
