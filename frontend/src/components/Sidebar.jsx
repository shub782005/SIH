import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, 
  MapPin, 
  Truck, 
  Users, 
  Route, 
  Cpu, 
  BarChart3, 
  Settings,
  Navigation
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

// Nav items are gated by role so a DRIVER (or MANAGER) account never sees, or
// can navigate to, admin-only operations screens from the sidebar. `roles:
// null` means visible to every authenticated role.
const NAV_ITEMS = [
  { name: 'Dashboard', path: '/', icon: LayoutDashboard, roles: null },
  { name: 'Collection Points', path: '/collection-points', icon: MapPin, roles: ['ADMIN', 'MANAGER'] },
  { name: 'Vehicles Fleet', path: '/vehicles', icon: Truck, roles: ['ADMIN', 'MANAGER'] },
  { name: 'Drivers', path: '/drivers', icon: Users, roles: ['ADMIN', 'MANAGER'] },
  { name: 'Route Optimization', path: '/optimization', icon: Cpu, roles: ['ADMIN', 'MANAGER'] },
  { name: 'Active Routes', path: '/routes', icon: Route, roles: ['ADMIN', 'MANAGER'] },
  { name: 'Operational Analytics', path: '/analytics', icon: BarChart3, roles: ['ADMIN', 'MANAGER'] },
  { name: 'Driver Interface', path: '/driver', icon: Navigation, roles: ['DRIVER', 'ADMIN'] },
  { name: 'Settings', path: '/settings', icon: Settings, roles: ['ADMIN'] },
];

export default function Sidebar() {
  const { user } = useAuth();
  const navItems = NAV_ITEMS.filter((item) => !item.roles || item.roles.includes(user?.role));

  return (
    <aside className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col justify-between p-4 min-h-[calc(100vh-61px)]">
      <nav className="space-y-1">
        <div className="px-3 py-2 text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
          Operations Management
        </div>
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center space-x-3 px-3.5 py-2.5 rounded-lg text-sm font-medium transition-all ${
                  isActive
                    ? 'bg-emerald-600 text-white shadow-md shadow-emerald-900/20'
                    : 'text-slate-400 hover:bg-slate-800 hover:text-slate-200'
                }`
              }
            >
              <Icon className="w-4 h-4" />
              <span>{item.name}</span>
            </NavLink>
          );
        })}
      </nav>

      {/* Footer Info */}
      <div className="bg-slate-800/60 border border-slate-800 rounded-xl p-3.5 text-xs text-slate-400">
        <p className="font-semibold text-slate-300">{user?.name || 'Signed in'}</p>
        <p className="text-[11px] mt-1 text-slate-400">Role: {user?.role || '—'}</p>
      </div>
    </aside>
  );
}
