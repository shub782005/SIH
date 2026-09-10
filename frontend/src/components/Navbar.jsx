import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Leaf, Activity, LogOut, LogIn, User } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function Navbar({ systemStatus }) {
  const { user, isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const getRoleBadgeStyle = (role) => {
    switch (role) {
      case 'ADMIN':
        return 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30';
      case 'MANAGER':
        return 'bg-blue-500/20 text-blue-300 border-blue-500/30';
      case 'DRIVER':
        return 'bg-amber-500/20 text-amber-300 border-amber-500/30';
      default:
        return 'bg-slate-700 text-slate-300 border-slate-600';
    }
  };

  return (
    <header className="bg-slate-900 text-white border-b border-slate-800 px-6 py-3.5 flex items-center justify-between sticky top-0 z-50 shadow-md">
      {/* Brand / Logo */}
      <Link to="/" className="flex items-center space-x-3 group">
        <div className="bg-emerald-500/20 p-2 rounded-xl border border-emerald-500/30 text-emerald-400 group-hover:scale-105 transition">
          <Leaf className="w-6 h-6 animate-pulse" />
        </div>
        <div>
          <h1 className="text-lg font-bold tracking-tight text-white flex items-center gap-2">
            EcoRoute <span className="text-xs bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 px-2 py-0.5 rounded-full font-mono">CVRP v1.0</span>
          </h1>
          <p className="text-xs text-slate-400">Plastic Collection Optimization Platform</p>
        </div>
      </Link>

      {/* Live System Health & User Session */}
      <div className="flex items-center space-x-4">
        <div className="hidden sm:flex items-center space-x-2 bg-slate-800/80 px-3.5 py-1.5 rounded-lg border border-slate-700 text-xs">
          <Activity className="w-4 h-4 text-emerald-400" />
          <span className="text-slate-300">Backend API:</span>
          <span className={`font-semibold ${systemStatus?.status === 'ok' ? 'text-emerald-400' : 'text-amber-400'}`}>
            {systemStatus?.status === 'ok' ? 'ONLINE' : 'CONNECTING...'}
          </span>
        </div>

        {/* User Session Badge */}
        {isAuthenticated ? (
          <div className="flex items-center space-x-3">
            <div className="flex items-center space-x-2.5 bg-slate-800 px-3 py-1.5 rounded-xl border border-slate-700">
              <div className="w-7 h-7 rounded-lg bg-gradient-to-tr from-emerald-500 to-teal-500 text-slate-950 flex items-center justify-center font-bold text-xs">
                {user?.name?.[0]?.toUpperCase() || 'U'}
              </div>
              <div className="text-left text-xs">
                <p className="font-semibold text-slate-200">{user?.name}</p>
                <span className={`text-[9px] px-1.5 py-0.2 rounded border font-mono font-bold uppercase tracking-wider ${getRoleBadgeStyle(user?.role)}`}>
                  {user?.role}
                </span>
              </div>
            </div>

            <button 
              onClick={handleLogout}
              title="Sign Out"
              className="p-2 bg-slate-800 hover:bg-red-500/20 hover:text-red-400 text-slate-400 rounded-xl border border-slate-700 transition cursor-pointer"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        ) : (
          <Link
            to="/login"
            className="flex items-center gap-2 bg-emerald-500 hover:bg-emerald-400 text-slate-950 px-4 py-2 rounded-xl font-bold text-xs transition shadow-md shadow-emerald-500/20"
          >
            <LogIn className="w-4 h-4" />
            Sign In
          </Link>
        )}
      </div>
    </header>
  );
}
