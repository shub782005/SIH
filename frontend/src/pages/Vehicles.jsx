import React, { useEffect, useState } from 'react';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';
import {
  Truck, Plus, Search, AlertTriangle, RefreshCw, Edit2, Trash2,
  X, UserCheck, CheckCircle, XCircle, Activity, Package, MapPin,
  ChevronDown
} from 'lucide-react';

const STATUS_STYLES = {
  AVAILABLE:  'bg-emerald-50 text-emerald-700 border-emerald-200',
  ON_ROUTE:   'bg-blue-50 text-blue-700 border-blue-200',
  OFF_DUTY:   'bg-amber-50 text-amber-700 border-amber-200',
  INACTIVE:   'bg-slate-100 text-slate-500 border-slate-200',
};

const EMPTY_FORM = {
  vehicle_number: '', vehicle_type: 'Truck',
  capacity_kg: 1000, driver_id: '', status: 'AVAILABLE',
  current_latitude: '', current_longitude: '',
};

export default function Vehicles() {
  const { user } = useAuth();
  const [vehicles, setVehicles] = useState([]);
  const [drivers, setDrivers] = useState([]);
  const [driverUsers, setDriverUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingVehicle, setEditingVehicle] = useState(null);
  const [formData, setFormData] = useState(EMPTY_FORM);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);

  const canManage = user?.role === 'ADMIN' || user?.role === 'MANAGER';
  const isAdmin = user?.role === 'ADMIN';

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const params = {};
      if (search) params.search = search;
      if (statusFilter) params.vehicle_status = statusFilter;
      const [vRes, dRes, uRes] = await Promise.all([
        api.get('/vehicles', { params }),
        api.get('/drivers'),
        api.get('/users', { params: { role: 'DRIVER' } }).catch(() => ({ data: [] })),
      ]);
      setVehicles(vRes.data);
      setDrivers(dRes.data);
      setDriverUsers(uRes.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchData(); }, [search, statusFilter]);

  const openModal = (vehicle = null) => {
    setEditingVehicle(vehicle);
    setFormData(vehicle ? {
      vehicle_number: vehicle.vehicle_number,
      vehicle_type: vehicle.vehicle_type,
      capacity_kg: vehicle.capacity_kg,
      driver_id: vehicle.driver_id ?? '',
      status: vehicle.status,
      current_latitude: vehicle.current_latitude ?? '',
      current_longitude: vehicle.current_longitude ?? '',
    } : EMPTY_FORM);
    setIsModalOpen(true);
  };

  const handleSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      const payload = {
        ...formData,
        driver_id: formData.driver_id === '' ? null : Number(formData.driver_id),
        current_latitude: formData.current_latitude === '' ? null : Number(formData.current_latitude),
        current_longitude: formData.current_longitude === '' ? null : Number(formData.current_longitude),
      };
      if (editingVehicle) {
        await api.put(`/vehicles/${editingVehicle.id}`, payload);
      } else {
        await api.post('/vehicles', payload);
      }
      setIsModalOpen(false);
      fetchData();
    } catch (err) {
      alert(err.response?.data?.detail || 'Save failed');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm(`Delete vehicle #${id}?`)) return;
    try {
      await api.delete(`/vehicles/${id}`);
      fetchData();
    } catch (err) {
      alert(err.response?.data?.detail || 'Delete failed');
    }
  };

  const getDriverName = (driverId) => {
    if (!driverId) return null;
    const d = drivers.find(dr => dr.id === driverId);
    if (!d) return `Driver #${driverId}`;
    const u = driverUsers.find(usr => usr.id === d.user_id);
    const label = u?.name || `Driver #${d.id}`;
    return `${label} (Lic: ${d.license_number})`;
  };

  const stats = {
    total: vehicles.length,
    available: vehicles.filter(v => v.status === 'AVAILABLE').length,
    onRoute: vehicles.filter(v => v.status === 'ON_ROUTE').length,
    totalCapacity: vehicles.reduce((s, v) => s + v.capacity_kg, 0),
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
        <div>
          <div className="inline-flex items-center gap-2 bg-blue-50 text-blue-700 border border-blue-200 text-xs px-3 py-1 rounded-full font-semibold mb-1">
            <Truck className="w-3.5 h-3.5" />
            Phase 4 — Vehicle Fleet Management
          </div>
          <h1 className="text-xl font-bold text-slate-900">Fleet Directory</h1>
          <p className="text-slate-500 text-xs mt-0.5">Manage vehicle capacities, types, GPS positions, and driver assignments.</p>
        </div>
        {canManage && (
          <button onClick={() => openModal()}
            className="flex items-center gap-2 bg-emerald-600 hover:bg-emerald-700 text-white px-4 py-2.5 rounded-xl font-semibold text-xs shadow-md shadow-emerald-600/20 transition shrink-0 cursor-pointer">
            <Plus className="w-4 h-4" /> Add Vehicle
          </button>
        )}
      </div>

      {/* Stats Row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: 'Total Vehicles', value: stats.total, icon: Truck, color: 'text-blue-600', bg: 'bg-blue-50' },
          { label: 'Available', value: stats.available, icon: CheckCircle, color: 'text-emerald-600', bg: 'bg-emerald-50' },
          { label: 'On Route', value: stats.onRoute, icon: Activity, color: 'text-amber-600', bg: 'bg-amber-50' },
          { label: 'Total Capacity', value: `${stats.totalCapacity.toLocaleString()} kg`, icon: Package, color: 'text-indigo-600', bg: 'bg-indigo-50' },
        ].map((stat, i) => (
          <div key={i} className="bg-white rounded-2xl border border-slate-200 p-4 shadow-sm flex items-center gap-3">
            <div className={`${stat.bg} p-2.5 rounded-xl`}>
              <stat.icon className={`w-5 h-5 ${stat.color}`} />
            </div>
            <div>
              <p className="text-xs text-slate-500 font-medium">{stat.label}</p>
              <p className="text-lg font-bold text-slate-900">{stat.value}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Filters */}
      <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm grid grid-cols-1 sm:grid-cols-2 gap-3">
        <div className="relative">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
          <input type="text" placeholder="Search by number or type..."
            value={search} onChange={e => setSearch(e.target.value)}
            className="w-full bg-slate-50 border border-slate-200 rounded-xl pl-9 pr-3 py-2 text-xs text-slate-800 focus:outline-none focus:border-blue-500" />
        </div>
        <select value={statusFilter} onChange={e => setStatusFilter(e.target.value)}
          className="bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-xs text-slate-800 focus:outline-none focus:border-blue-500">
          <option value="">All Statuses</option>
          <option value="AVAILABLE">✅ Available</option>
          <option value="ON_ROUTE">🚛 On Route</option>
          <option value="OFF_DUTY">🟡 Off Duty</option>
          <option value="INACTIVE">⚫ Inactive</option>
        </select>
      </div>

      {/* Table */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        {loading ? (
          <div className="p-12 text-center text-slate-400 space-y-3">
            <RefreshCw className="w-6 h-6 animate-spin mx-auto text-blue-500" />
            <p className="text-xs font-medium">Loading fleet data...</p>
          </div>
        ) : vehicles.length === 0 ? (
          <div className="p-12 text-center text-slate-500">
            <Truck className="w-8 h-8 text-slate-300 mx-auto mb-2" />
            <p className="font-semibold text-sm">No vehicles found</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-xs text-left text-slate-700">
              <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 font-semibold uppercase tracking-wider text-[10px]">
                <tr>
                  <th className="py-3.5 px-4">Vehicle</th>
                  <th className="py-3.5 px-4">Type</th>
                  <th className="py-3.5 px-4">Capacity</th>
                  <th className="py-3.5 px-4">Status</th>
                  <th className="py-3.5 px-4">Assigned Driver</th>
                  <th className="py-3.5 px-4">GPS</th>
                  {canManage && <th className="py-3.5 px-4 text-right">Actions</th>}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-medium">
                {vehicles.map(v => (
                  <tr key={v.id} className="hover:bg-slate-50/80 transition">
                    <td className="py-3.5 px-4">
                      <p className="font-bold text-slate-900 font-mono">{v.vehicle_number}</p>
                      <p className="text-[10px] text-slate-400">ID #{v.id}</p>
                    </td>
                    <td className="py-3.5 px-4">
                      <span className="bg-indigo-50 text-indigo-700 border border-indigo-200 px-2.5 py-0.5 rounded-full font-semibold text-[10px]">
                        {v.vehicle_type}
                      </span>
                    </td>
                    <td className="py-3.5 px-4">
                      <div className="flex items-center gap-1">
                        <Package className="w-3.5 h-3.5 text-slate-400" />
                        <span className="font-mono font-bold text-slate-800">{v.capacity_kg.toLocaleString()} kg</span>
                      </div>
                    </td>
                    <td className="py-3.5 px-4">
                      <span className={`px-2.5 py-0.5 rounded-full border text-[10px] font-bold tracking-wider uppercase ${STATUS_STYLES[v.status] || ''}`}>
                        {v.status}
                      </span>
                    </td>
                    <td className="py-3.5 px-4">
                      {v.driver_id ? (
                        <div className="flex items-center gap-1 text-slate-700">
                          <UserCheck className="w-3.5 h-3.5 text-emerald-500" />
                          <span className="text-[11px]">{getDriverName(v.driver_id)}</span>
                        </div>
                      ) : (
                        <span className="text-slate-400 text-[11px]">Unassigned</span>
                      )}
                    </td>
                    <td className="py-3.5 px-4">
                      {v.current_latitude ? (
                        <div className="flex items-center gap-1 text-slate-600 font-mono text-[10px]">
                          <MapPin className="w-3 h-3 text-blue-400" />
                          {v.current_latitude.toFixed(4)}, {v.current_longitude?.toFixed(4)}
                        </div>
                      ) : (
                        <span className="text-slate-300 text-[11px]">—</span>
                      )}
                    </td>
                    {canManage && (
                      <td className="py-3.5 px-4 text-right">
                        <div className="flex items-center justify-end gap-1.5">
                          <button onClick={() => openModal(v)}
                            className="p-1.5 text-slate-500 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition cursor-pointer" title="Edit">
                            <Edit2 className="w-3.5 h-3.5" />
                          </button>
                          {isAdmin && (
                            <button onClick={() => handleDelete(v.id)}
                              className="p-1.5 text-slate-500 hover:text-red-600 hover:bg-red-50 rounded-lg transition cursor-pointer" title="Delete">
                              <Trash2 className="w-3.5 h-3.5" />
                            </button>
                          )}
                        </div>
                      </td>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 bg-slate-950/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl border border-slate-200 w-full max-w-lg shadow-2xl p-6 space-y-5">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <h3 className="font-bold text-slate-900 text-base">
                {editingVehicle ? `Edit Vehicle ${editingVehicle.vehicle_number}` : 'Register New Vehicle'}
              </h3>
              <button onClick={() => setIsModalOpen(false)} className="text-slate-400 hover:text-slate-600 cursor-pointer">
                <X className="w-5 h-5" />
              </button>
            </div>
            <form onSubmit={handleSave} className="space-y-4 text-xs">
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1">
                  <label className="font-semibold text-slate-700">Vehicle Number *</label>
                  <input required value={formData.vehicle_number}
                    onChange={e => setFormData({ ...formData, vehicle_number: e.target.value })}
                    placeholder="MH12-AB-1234"
                    className="w-full border border-slate-200 rounded-xl px-3.5 py-2 font-mono text-xs focus:outline-none focus:border-blue-500" />
                </div>
                <div className="space-y-1">
                  <label className="font-semibold text-slate-700">Vehicle Type</label>
                  <select value={formData.vehicle_type}
                    onChange={e => setFormData({ ...formData, vehicle_type: e.target.value })}
                    className="w-full border border-slate-200 rounded-xl px-3.5 py-2 text-xs focus:outline-none focus:border-blue-500">
                    <option>Truck</option>
                    <option>Mini Truck</option>
                    <option>Compactor</option>
                    <option>Tractor</option>
                    <option>Auto Rickshaw</option>
                  </select>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1">
                  <label className="font-semibold text-slate-700">Capacity (kg) *</label>
                  <input required type="number" min="1" step="50"
                    value={formData.capacity_kg}
                    onChange={e => setFormData({ ...formData, capacity_kg: parseFloat(e.target.value) })}
                    className="w-full border border-slate-200 rounded-xl px-3.5 py-2 text-xs font-mono focus:outline-none focus:border-blue-500" />
                </div>
                <div className="space-y-1">
                  <label className="font-semibold text-slate-700">Status</label>
                  <select value={formData.status}
                    onChange={e => setFormData({ ...formData, status: e.target.value })}
                    className="w-full border border-slate-200 rounded-xl px-3.5 py-2 text-xs focus:outline-none focus:border-blue-500">
                    <option value="AVAILABLE">Available</option>
                    <option value="ON_ROUTE">On Route</option>
                    <option value="OFF_DUTY">Off Duty</option>
                    <option value="INACTIVE">Inactive</option>
                  </select>
                </div>
              </div>
              <div className="space-y-1">
                <label className="font-semibold text-slate-700">Assign Driver (optional)</label>
                <select value={formData.driver_id}
                  onChange={e => setFormData({ ...formData, driver_id: e.target.value })}
                  className="w-full border border-slate-200 rounded-xl px-3.5 py-2 text-xs focus:outline-none focus:border-blue-500">
                  <option value="">— Unassigned —</option>
                  {drivers.map(d => (
                    <option key={d.id} value={d.id}>{driverUsers.find(usr => usr.id === d.user_id)?.name || `Driver #${d.id}`} — Lic: {d.license_number} — {d.phone}</option>
                  ))}
                </select>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1">
                  <label className="font-semibold text-slate-700">Current Latitude</label>
                  <input type="number" step="any" value={formData.current_latitude}
                    onChange={e => setFormData({ ...formData, current_latitude: e.target.value })}
                    placeholder="18.5204"
                    className="w-full border border-slate-200 rounded-xl px-3.5 py-2 text-xs font-mono focus:outline-none focus:border-blue-500" />
                </div>
                <div className="space-y-1">
                  <label className="font-semibold text-slate-700">Current Longitude</label>
                  <input type="number" step="any" value={formData.current_longitude}
                    onChange={e => setFormData({ ...formData, current_longitude: e.target.value })}
                    placeholder="73.8567"
                    className="w-full border border-slate-200 rounded-xl px-3.5 py-2 text-xs font-mono focus:outline-none focus:border-blue-500" />
                </div>
              </div>
              <div className="flex items-center justify-end gap-2 pt-4 border-t border-slate-100">
                <button type="button" onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 rounded-xl text-slate-600 hover:bg-slate-100 font-semibold cursor-pointer text-xs">Cancel</button>
                <button type="submit" disabled={saving}
                  className="bg-emerald-600 hover:bg-emerald-700 text-white font-bold px-4 py-2 rounded-xl transition shadow-md shadow-emerald-600/20 cursor-pointer disabled:opacity-50 text-xs">
                  {saving ? 'Saving...' : 'Save Vehicle'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
