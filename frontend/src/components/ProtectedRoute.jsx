import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Loader2 } from 'lucide-react';

export default function ProtectedRoute({ children, allowedRoles }) {
  const { user, loading, isAuthenticated } = useAuth();
  const location = useLocation();

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center text-white">
        <div className="flex items-center gap-3 bg-slate-800 px-6 py-4 rounded-2xl border border-slate-700 shadow-2xl">
          <Loader2 className="w-5 h-5 animate-spin text-emerald-400" />
          <span className="text-sm font-medium">Verifying Session...</span>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (allowedRoles && !allowedRoles.includes(user?.role)) {
    return (
      <div className="p-8 text-center bg-red-50 text-red-700 rounded-2xl border border-red-200 m-6">
        <h3 className="text-lg font-bold">Access Restricted</h3>
        <p className="text-sm mt-1">Your role ({user?.role}) does not have permission to view this page.</p>
      </div>
    );
  }

  return children;
}
