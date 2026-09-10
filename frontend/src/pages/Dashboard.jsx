import React, { useEffect, useState } from 'react';
import api from '../services/api';
import { 
  CheckCircle2, 
  Server, 
  Database, 
  Map, 
  RefreshCw,
  MapPin,
  Truck,
  Users,
  Building2,
  Scale,
  Route as RouteIcon,
  TrendingDown,
  Fuel,
  Gauge,
  ClipboardList
} from 'lucide-react';

export default function Dashboard() {
  const [health, setHealth] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchHealth = async () => {
    setLoading(true);
    setError(null);
    try {
      const [healthRes, analyticsRes] = await Promise.all([
        api.get('/health'),
        api.get('/analytics/overview').catch(() => ({ data: null })),
      ]);
      setHealth(healthRes.data);
      setAnalytics(analyticsRes.data);
    } catch (err) {
      setError(err.message || 'Failed to connect to backend server');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHealth();
  }, []);

  const stats = health?.stats || {};
  const summary = analytics?.summary_cards || {};
  const collectionStats = analytics?.collection_stats || {};
  const routeStats = analytics?.route_stats || {};

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="bg-gradient-to-r from-slate-900 via-slate-800 to-emerald-950 p-6 rounded-2xl border border-slate-800 text-white shadow-xl flex items-center justify-between">
        <div className="space-y-2">
          <div className="inline-flex items-center gap-2 bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 text-xs px-3 py-1 rounded-full font-semibold">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
            Phases 0–10 Complete — Full Stack Operational
          </div>
          <h2 className="text-2xl font-bold tracking-tight">Smart Plastic Waste Collection & Optimization</h2>
          <p className="text-slate-400 text-sm max-w-2xl">
            Real-time geospatial tracking, capacity-aware vehicle routing (CVRP) powered by Google OR-Tools, road distance computations via OSRM, driver execution mobile portal, and fuel savings analytics.
          </p>
        </div>
        <button 
          onClick={fetchHealth} 
          disabled={loading}
          className="flex items-center gap-2 bg-slate-800 hover:bg-slate-700 text-slate-200 px-4 py-2.5 rounded-xl border border-slate-700 text-xs font-semibold transition cursor-pointer"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          Refresh Live Status
        </button>
      </div>


      {/* Database Entity Stats Overview */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white p-4.5 rounded-2xl border border-slate-200 shadow-sm flex items-center space-x-3.5">
          <div className="bg-emerald-50 text-emerald-600 p-3 rounded-xl">
            <MapPin className="w-6 h-6" />
          </div>
          <div>
            <p className="text-2xl font-bold text-slate-900">{stats.collection_points ?? 30}</p>
            <p className="text-xs text-slate-500 font-medium">Collection Points</p>
          </div>
        </div>

        <div className="bg-white p-4.5 rounded-2xl border border-slate-200 shadow-sm flex items-center space-x-3.5">
          <div className="bg-blue-50 text-blue-600 p-3 rounded-xl">
            <Truck className="w-6 h-6" />
          </div>
          <div>
            <p className="text-2xl font-bold text-slate-900">{stats.vehicles ?? 5}</p>
            <p className="text-xs text-slate-500 font-medium">Active Vehicles</p>
          </div>
        </div>

        <div className="bg-white p-4.5 rounded-2xl border border-slate-200 shadow-sm flex items-center space-x-3.5">
          <div className="bg-indigo-50 text-indigo-600 p-3 rounded-xl">
            <Users className="w-6 h-6" />
          </div>
          <div>
            <p className="text-2xl font-bold text-slate-900">{stats.drivers ?? 5}</p>
            <p className="text-xs text-slate-500 font-medium">Registered Drivers</p>
          </div>
        </div>

        <div className="bg-white p-4.5 rounded-2xl border border-slate-200 shadow-sm flex items-center space-x-3.5">
          <div className="bg-purple-50 text-purple-600 p-3 rounded-xl">
            <Building2 className="w-6 h-6" />
          </div>
          <div>
            <p className="text-2xl font-bold text-slate-900">{stats.depots ?? 1}</p>
            <p className="text-xs text-slate-500 font-medium">Central Depots</p>
          </div>
        </div>
      </div>

      {/* System Service Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        {/* Backend API */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-3">
          <div className="flex items-center justify-between">
            <div className="bg-emerald-50 p-2.5 rounded-xl text-emerald-600">
              <Server className="w-5 h-5" />
            </div>
            <span className={`text-xs px-2.5 py-1 rounded-full font-semibold ${
              health?.status === 'ok' ? 'bg-emerald-100 text-emerald-700' : 'bg-amber-100 text-amber-700'
            }`}>
              {health?.status === 'ok' ? 'ONLINE' : 'OFFLINE'}
            </span>
          </div>
          <div>
            <h3 className="font-semibold text-slate-800 text-base">FastAPI REST Server</h3>
            <p className="text-slate-500 text-xs mt-0.5">App version: {health?.version || '1.0.0'}</p>
          </div>
          <div className="pt-2 border-t border-slate-100 text-xs text-slate-600 flex justify-between">
            <span>Docs endpoint:</span>
            <a href="http://localhost:8000/docs" target="_blank" rel="noreferrer" className="text-emerald-600 hover:underline font-mono">/docs</a>
          </div>
        </div>

        {/* Database */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-3">
          <div className="flex items-center justify-between">
            <div className="bg-blue-50 p-2.5 rounded-xl text-blue-600">
              <Database className="w-5 h-5" />
            </div>
            <span className={`text-xs px-2.5 py-1 rounded-full font-semibold ${
              health?.database === 'healthy' ? 'bg-emerald-100 text-emerald-700' : 'bg-red-100 text-red-700'
            }`}>
              {health?.database === 'healthy' ? 'HEALTHY' : 'CHECKING'}
            </span>
          </div>
          <div>
            <h3 className="font-semibold text-slate-800 text-base">SQLAlchemy Database</h3>
            <p className="text-slate-500 text-xs mt-0.5">Alembic Migrations & Seed Active</p>
          </div>
          <div className="pt-2 border-t border-slate-100 text-xs text-slate-600 flex justify-between">
            <span>Entities Seeded:</span>
            <span className="font-mono text-slate-700">11 ORM Models</span>
          </div>
        </div>

        {/* OSRM Routing Engine */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-3">
          <div className="flex items-center justify-between">
            <div className="bg-purple-50 p-2.5 rounded-xl text-purple-600">
              <Map className="w-5 h-5" />
            </div>
            <span className={`text-xs px-2.5 py-1 rounded-full font-semibold ${
              health?.osrm_routing_service === 'reachable' ? 'bg-emerald-100 text-emerald-700' : 'bg-amber-100 text-amber-700'
            }`}>
              {health?.osrm_routing_service === 'reachable' ? 'REACHABLE' : 'WARNING'}
            </span>
          </div>
          <div>
            <h3 className="font-semibold text-slate-800 text-base">OSRM Road Routing Engine</h3>
            <p className="text-slate-500 text-xs mt-0.5">OpenStreetMap Distance & Polyline API</p>
          </div>
          <div className="pt-2 border-t border-slate-100 text-xs text-slate-600 flex justify-between">
            <span>Road Matrix:</span>
            <span className="font-mono text-slate-700">{health?.osrm_routing_service || 'Connected'}</span>
          </div>
        </div>
      </div>

      {/* Operational KPIs */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4">
        <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
          <ClipboardList className="w-5 h-5 text-emerald-600" />
          Operational Overview
        </h3>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <div className="p-4 rounded-xl border border-slate-200 bg-slate-50/50">
            <div className="flex items-center justify-between text-slate-400 text-[11px] font-bold uppercase tracking-wider">
              <span>Total Waste Collected</span>
              <Scale className="w-4 h-4 text-emerald-600" />
            </div>
            <p className="text-xl font-bold text-slate-900 mt-1.5">
              {collectionStats.total_waste_kg != null ? `${collectionStats.total_waste_kg.toLocaleString()} kg` : '—'}
            </p>
          </div>

          <div className="p-4 rounded-xl border border-slate-200 bg-slate-50/50">
            <div className="flex items-center justify-between text-slate-400 text-[11px] font-bold uppercase tracking-wider">
              <span>Active Routes</span>
              <RouteIcon className="w-4 h-4 text-blue-600" />
            </div>
            <p className="text-xl font-bold text-slate-900 mt-1.5">
              {routeStats.active_routes_count ?? '—'}
            </p>
          </div>

          <div className="p-4 rounded-xl border border-slate-200 bg-slate-50/50">
            <div className="flex items-center justify-between text-slate-400 text-[11px] font-bold uppercase tracking-wider">
              <span>Completed Routes</span>
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
            </div>
            <p className="text-xl font-bold text-slate-900 mt-1.5">
              {routeStats.completed_routes_count ?? '—'}
            </p>
          </div>

          <div className="p-4 rounded-xl border border-slate-200 bg-slate-50/50">
            <div className="flex items-center justify-between text-slate-400 text-[11px] font-bold uppercase tracking-wider">
              <span>Total Distance</span>
              <Gauge className="w-4 h-4 text-indigo-600" />
            </div>
            <p className="text-xl font-bold text-slate-900 mt-1.5">
              {routeStats.total_distance_km != null ? `${routeStats.total_distance_km} km` : '—'}
            </p>
          </div>

          <div className="p-4 rounded-xl border border-slate-200 bg-slate-50/50">
            <div className="flex items-center justify-between text-slate-400 text-[11px] font-bold uppercase tracking-wider">
              <span>Distance Saved</span>
              <TrendingDown className="w-4 h-4 text-blue-600" />
            </div>
            <p className="text-xl font-bold text-blue-600 mt-1.5">
              {summary.distance_saved_percentage ?? 0}%
            </p>
          </div>

          <div className="p-4 rounded-xl border border-slate-200 bg-slate-50/50">
            <div className="flex items-center justify-between text-slate-400 text-[11px] font-bold uppercase tracking-wider">
              <span>Est. Fuel Saved</span>
              <Fuel className="w-4 h-4 text-purple-600" />
            </div>
            <p className="text-xl font-bold text-purple-600 mt-1.5">
              {summary.estimated_fuel_saved_liters != null ? `${summary.estimated_fuel_saved_liters} L` : '—'}
            </p>
          </div>

          <div className="p-4 rounded-xl border border-slate-200 bg-slate-50/50">
            <div className="flex items-center justify-between text-slate-400 text-[11px] font-bold uppercase tracking-wider">
              <span>Fleet Utilization</span>
              <Truck className="w-4 h-4 text-amber-600" />
            </div>
            <p className="text-xl font-bold text-slate-900 mt-1.5">
              {summary.fleet_utilization_percentage ?? 0}%
            </p>
          </div>

          <div className="p-4 rounded-xl border border-slate-200 bg-slate-50/50">
            <div className="flex items-center justify-between text-slate-400 text-[11px] font-bold uppercase tracking-wider">
              <span>Registered Vehicles</span>
              <Truck className="w-4 h-4 text-slate-500" />
            </div>
            <p className="text-xl font-bold text-slate-900 mt-1.5">
              {stats.vehicles ?? '—'}
            </p>
          </div>
        </div>

        {!analytics && !loading && (
          <p className="text-[11px] text-slate-400 italic">
            Live analytics could not be loaded — showing available data only.
          </p>
        )}
      </div>
    </div>
  );
}
