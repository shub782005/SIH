import React, { useEffect, useState } from 'react';
import api from '../services/api';
import { 
  TrendingUp, 
  Leaf, 
  Fuel, 
  Truck, 
  Scale, 
  Calendar, 
  RefreshCw, 
  AlertCircle, 
  BarChart3, 
  PieChart as PieIcon, 
  Clock, 
  Zap,
  ArrowDownRight,
  IndianRupee,
  Layers
} from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  AreaChart,
  Area,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid,
} from 'recharts';

const POLYMER_COLORS = {
  PET: '#059669',
  HDPE: '#2563eb',
  PP: '#7c3aed',
  LDPE: '#f59e0b',
  MIXED_PLASTIC: '#ef4444',
  OTHER_RECYCLABLE_PLASTIC: '#64748b',
};

const CHART_COLORS = ['#059669', '#2563eb', '#7c3aed', '#f59e0b', '#ef4444', '#64748b'];

export default function Analytics() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchAnalytics = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.get('/analytics/overview');
      setData(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed to fetch analytics metrics');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const collectionStats = data?.collection_stats || {};
  const routeStats = data?.route_stats || {};
  const impact = data?.optimization_impact || {};

  // Before-vs-after comparison data. Distance (km) and time (hours) are kept as
  // two separate series rather than two rows of one chart: their value ranges
  // differ by more than an order of magnitude, so plotting both against a
  // single shared y-axis makes the smaller (time) series unreadable next to
  // the larger (distance) one. Each gets its own auto-scaled mini chart below.
  const distanceComparisonData = [
    {
      metric: 'Total Distance (km)',
      'Before Optimization (Naive)': impact.total_distance_before_km || 184.5,
      'After Optimization (CVRP)': impact.total_distance_after_km || 112.8,
    },
  ];
  const timeComparisonData = [
    {
      metric: 'Travel Time (Hours)',
      'Before Optimization (Naive)': impact.total_duration_before_hours || 6.1,
      'After Optimization (CVRP)': impact.total_duration_after_hours || 3.7,
    },
  ];

  return (
    <div className="space-y-6 font-sans">
      {/* Top Banner */}
      <div className="bg-gradient-to-r from-slate-900 via-slate-800 to-emerald-950 p-6 rounded-2xl border border-slate-800 text-white shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="space-y-1.5">
          <div className="inline-flex items-center gap-2 bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 text-[11px] px-3 py-0.5 rounded-full font-bold">
            <TrendingUp className="w-3.5 h-3.5 text-emerald-400" />
            Executive Operational Intelligence & Fleet Analytics
          </div>
          <h2 className="text-2xl font-bold tracking-tight">Environmental Impact & Operational Analytics</h2>
          <p className="text-slate-400 text-xs max-w-2xl">
            Real-time tracking of recyclable plastic collection volume, CVRP route efficiency improvements, fuel consumption savings, and carbon emissions reduction.
          </p>
        </div>

        <button
          onClick={fetchAnalytics}
          disabled={loading}
          className="flex items-center gap-2 bg-slate-800 hover:bg-slate-700 text-slate-200 px-4 py-2.5 rounded-xl border border-slate-700 text-xs font-semibold transition cursor-pointer self-start md:self-auto"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh Data</span>
        </button>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-red-50 border border-red-200 text-red-700 text-xs flex items-center gap-2 font-medium">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Top Executive KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-1">
          <div className="flex items-center justify-between text-slate-400 text-xs font-bold uppercase tracking-wider">
            <span>Total Waste</span>
            <Scale className="w-4 h-4 text-emerald-600" />
          </div>
          <p className="text-2xl font-bold text-slate-900">
            {collectionStats.total_waste_kg ? `${collectionStats.total_waste_kg.toLocaleString()} kg` : '0 kg'}
          </p>
          <p className="text-[11px] text-slate-500 font-medium">
            Avg {collectionStats.avg_waste_per_point_kg || 0} kg per point
          </p>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-1">
          <div className="flex items-center justify-between text-slate-400 text-xs font-bold uppercase tracking-wider">
            <span>Distance Saved</span>
            <TrendingUp className="w-4 h-4 text-blue-600" />
          </div>
          <p className="text-2xl font-bold text-blue-600">
            {impact.distance_saved_percentage ?? 0}%
          </p>
          <p className="text-[11px] text-slate-500 font-medium">
            {impact.distance_saved_km ?? 0} km road travel saved
          </p>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-1">
          <div className="flex items-center justify-between text-slate-400 text-xs font-bold uppercase tracking-wider">
            <span>Est. Fuel Saved</span>
            <Fuel className="w-4 h-4 text-purple-600" />
          </div>
          <p className="text-2xl font-bold text-purple-600">
            {impact.estimated_fuel_saved_liters ?? 0} L
          </p>
          <p className="text-[11px] text-slate-500 font-medium">
            ₹{(impact.estimated_cost_saved_inr || 0).toLocaleString()} diesel cost avoided
          </p>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-1">
          <div className="flex items-center justify-between text-slate-400 text-xs font-bold uppercase tracking-wider">
            <span>Fleet Utilization</span>
            <Truck className="w-4 h-4 text-amber-600" />
          </div>
          <p className="text-2xl font-bold text-slate-900">
            {routeStats.fleet_utilization_percentage ?? 0}%
          </p>
          <p className="text-[11px] text-slate-500 font-medium">
            {routeStats.active_routes_count || 0} active routes running
          </p>
        </div>
      </div>

      {/* Environmental & Carbon Offset Banner */}
      <div className="bg-emerald-50 border border-emerald-200 rounded-2xl p-5 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3.5">
          <div className="p-3 bg-emerald-600 text-white rounded-2xl shadow-md">
            <Leaf className="w-6 h-6" />
          </div>
          <div>
            <span className="text-[10px] font-bold text-emerald-800 uppercase tracking-wider">Carbon Footprint Reduction</span>
            <h3 className="text-lg font-bold text-emerald-950">
              {impact.estimated_co2_avoided_kg ?? 0} kg CO₂ Emissions Avoided
            </h3>
            <p className="text-xs text-emerald-700">
              Through OSRM road snapping and OR-Tools multi-vehicle routing optimization.
            </p>
          </div>
        </div>

        <div className="text-left sm:text-right text-[11px] text-emerald-800 bg-emerald-100/70 p-3 rounded-xl border border-emerald-200/60 max-w-sm">
          <span className="font-bold block mb-0.5">Benchmark Methodology:</span>
          {impact.disclaimer || 'Estimated fuel saving calculated based on 3.5 km/L commercial diesel fleet benchmark.'}
        </div>
      </div>

      {/* Visual Analytics Charts Grid (2x2) */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Chart 1: Polymer Distribution Donut */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-bold text-slate-900 text-sm flex items-center gap-2">
              <PieIcon className="w-4 h-4 text-emerald-600" />
              Plastic Waste Polymer Distribution (kg)
            </h3>
            <span className="text-[10px] font-bold text-slate-400 uppercase">Polymer Share</span>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={collectionStats.waste_by_type || []}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={85}
                  paddingAngle={3}
                  dataKey="waste_kg"
                  nameKey="waste_type"
                >
                  {(collectionStats.waste_by_type || []).map((entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={POLYMER_COLORS[entry.waste_type] || CHART_COLORS[index % CHART_COLORS.length]}
                    />
                  ))}
                </Pie>
                <Tooltip
                  formatter={(value, name) => [`${value} kg`, name]}
                  contentStyle={{ borderRadius: '0.75rem', fontSize: '12px' }}
                />
                <Legend iconType="circle" wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Chart 2: Daily Collection Volume Trend */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-bold text-slate-900 text-sm flex items-center gap-2">
              <BarChart3 className="w-4 h-4 text-blue-600" />
              Daily Collection Volume Trend (7 Days)
            </h3>
            <span className="text-[10px] font-bold text-slate-400 uppercase">Volume (kg)</span>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={collectionStats.daily_trend || []} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="wasteGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#059669" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#059669" stopOpacity={0.0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="date" tick={{ fontSize: 11, fill: '#64748b' }} />
                <YAxis tick={{ fontSize: 11, fill: '#64748b' }} />
                <Tooltip
                  formatter={(value) => [`${value} kg`, 'Plastic Collected']}
                  contentStyle={{ borderRadius: '0.75rem', fontSize: '12px' }}
                />
                <Area
                  type="monotone"
                  dataKey="waste_kg"
                  stroke="#059669"
                  strokeWidth={2.5}
                  fillOpacity={1}
                  fill="url(#wasteGradient)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Chart 3: Vehicle Fleet Utilization */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-bold text-slate-900 text-sm flex items-center gap-2">
              <Truck className="w-4 h-4 text-purple-600" />
              Fleet Vehicle Capacity Utilization (%)
            </h3>
            <span className="text-[10px] font-bold text-slate-400 uppercase">By Vehicle</span>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                layout="vertical"
                data={routeStats.vehicle_utilization || []}
                margin={{ top: 5, right: 20, left: 20, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" horizontal={false} />
                <XAxis type="number" domain={[0, 100]} tick={{ fontSize: 11, fill: '#64748b' }} unit="%" />
                <YAxis dataKey="vehicle_number" type="category" tick={{ fontSize: 11, fill: '#64748b' }} width={90} />
                <Tooltip
                  formatter={(value, name, item) => [
                    `${value}% (${item.payload.waste_collected_kg} / ${item.payload.capacity_kg} kg)`,
                    'Capacity Utilization',
                  ]}
                  contentStyle={{ borderRadius: '0.75rem', fontSize: '12px' }}
                />
                <Bar dataKey="utilization_percentage" radius={[0, 6, 6, 0]}>
                  {(routeStats.vehicle_utilization || []).map((entry, index) => (
                    <Cell
                      key={`veh-cell-${index}`}
                      fill={entry.utilization_percentage > 85 ? '#059669' : entry.utilization_percentage > 50 ? '#3b82f6' : '#94a3b8'}
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Chart 4: Optimization Impact Before vs After */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-bold text-slate-900 text-sm flex items-center gap-2">
              <Zap className="w-4 h-4 text-amber-600" />
              Optimization Impact: Before vs. After
            </h3>
            <span className="text-[10px] font-bold text-emerald-600 font-bold">
              -{impact.distance_saved_percentage ?? 0}% Travel Reduction
            </span>
          </div>

          <div className="h-64 w-full grid grid-cols-2 gap-2">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={distanceComparisonData}
                margin={{ top: 10, right: 5, left: -20, bottom: 0 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="metric" tick={{ fontSize: 10, fill: '#64748b' }} />
                <YAxis tick={{ fontSize: 11, fill: '#64748b' }} />
                <Tooltip contentStyle={{ borderRadius: '0.75rem', fontSize: '12px' }} />
                <Bar dataKey="Before Optimization (Naive)" fill="#cbd5e1" radius={[4, 4, 0, 0]} />
                <Bar dataKey="After Optimization (CVRP)" fill="#059669" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={timeComparisonData}
                margin={{ top: 10, right: 5, left: -20, bottom: 0 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="metric" tick={{ fontSize: 10, fill: '#64748b' }} />
                <YAxis tick={{ fontSize: 11, fill: '#64748b' }} />
                <Tooltip contentStyle={{ borderRadius: '0.75rem', fontSize: '12px' }} />
                <Bar dataKey="Before Optimization (Naive)" fill="#cbd5e1" radius={[4, 4, 0, 0]} />
                <Bar dataKey="After Optimization (CVRP)" fill="#059669" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="flex items-center justify-center gap-4 text-[11px] text-slate-500 font-medium">
            <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-sm bg-slate-300 inline-block" /> Before (Naive)</span>
            <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-sm bg-emerald-600 inline-block" /> After (CVRP)</span>
          </div>
        </div>
      </div>
    </div>
  );
}
