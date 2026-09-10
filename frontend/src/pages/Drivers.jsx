import React, { useEffect, useState } from 'react';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';
import {
  Users, Plus, Search, RefreshCw, Edit2, Trash2, X,
  CheckCircle, XCircle, Phone, CreditCard, Shield,
  UserCheck, Activity
} from 'lucide-react';

const STATUS_STYLES = {
  AVAILABLE: 'bg-emerald-50 text-emerald-700 border-emerald-200',
  ON_ROUTE:  'bg-blue-50 text-blue-700 border-blue-200',
  OFF_DUTY:  'bg-amber-50 text-amber-700 border-amber-200',
  INACTIVE:  'bg-slate-100 text-slate-500 border-slate-200',
};

const EMPTY_FORM = {
  license_number: '',
  phone: '',
  status: 'AVAILABLE',
  user_id: '',
};

export default function Drivers() {
  const { user } = useAuth();
  const [drivers, setDrivers] = useState([]);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingDriver, setEditingDriver] = useState(null);
  const [formData, setFormData] = useState(EMPTY_FORM);
  const [saving, setSaving] = useState(false);

  const canManage = user?.role === 'ADMIN' || user?.role === 'MANAGER';
  const isAdmin = user?.role === 'ADMIN';

  const fetchData = async () => {
    setLoading(true);
    try {
      const params = {};
      if (search) params.search = search;
      if (statusFilter) params.driver_status = statusFilter;
      const [dRes, uRes] = await Promise.all([
        api.get('/drivers', { params }),
        api.get('/users', { params: { role: 'DRIVER' } }),
      ]);
      setDrivers(dRes.data);
      setUsers(uRes.data);
    } catch (err) {
      console.error('Failed to fetch drivers', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchData(); }, [search, statusFilter]);

  const openModal = (driver = null) => {
    setEditingDriver(driver);
    setFormData(driver ? {
      license_number: driver.license_number,
      phone: driver.phone,
      status: driver.status,
      user_id: driver.user_id,
    } : EMPTY_FORM);
    setIsModalOpen(true);
  };

  const handleSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      const payload = { ...formData, user_id: Number(formData.user_id) };
      if (editingDriver) {
        await api.put(`/drivers/${editingDriver.id}`, payload);
      } else {
        await api.post('/drivers', payload);
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
    if (!window.confirm(`Delete driver profile #${id}? The linked user account will NOT be deleted.`)) return;
    try {
      await api.delete(`/drivers/${id}`);
      fetchData();
    } catch (err) {
      alert(err.response?.data?.detail || 'Delete failed');
    }
  };

  const getUserName = (userId) => {
    const u = users.find(u => u.id === userId);
    return u ? `${u.name} (${u.email})` : `User #${userId}`;
  };

  const stats = {
    total: drivers.length,
    available: drivers.filter(d => d.status === 'AVAILABLE').length,
    onRoute: drivers.filter(d => d.status === 'ON_ROUTE').length,
    offDuty: drivers.filter(d => d.status === 'OFF_DUTY').length,
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
        <div>
          <div className="inline-flex items-center gap-2 bg-violet-50 text-violet-700 border border-violet-200 text-xs px-3 py-1 rounded-full font-semibold mb-1">
            <Users className="w-3.5 h-3.5" />
            Phase 4 — Driver Roster Management
          </div>
          <h1 className="text-xl font-bold text-slate-900">Driver Roster</h1>
          <p className="text-slate-500 text-xs mt-0.5">Manage driver profiles, license numbers, phone contacts, and operational statuses.</p>
        </div>
        {canManage && (
          <button onClick={() => openModal()}
            className="flex items-center gap-2 bg-emerald-600 hover:bg-emerald-700 text-white px-4 py-2.5 rounded-xl font-semibold text-xs shadow-md shadow-emerald-600/20 transition shrink-0 cursor-pointer">
            <Plus className="w-4 h-4" /> Register Driver
          </button>
        )}
      </div>

      {/* Stats Row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: 'Total Drivers', value: stats.total, icon: Users, color: 'text-violet-600', bg: 'bg-violet-50' },
          { label: 'Available', value: stats.available, icon: CheckCircle, color: 'text-emerald-600', bg: 'bg-emerald-50' },
          { label: 'On Route', value: stats.onRoute, icon: Activity, color: 'text-blue-600', bg: 'bg-blue-50' },
          { label: 'Off Duty', value: stats.offDuty, icon: XCircle, color: 'text-amber-600', bg: 'bg-amber-50' },
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
          <input type="text" placeholder="Search by license or phone..."
            value={search} onChange={e => setSearch(e.target.value)}
            className="w-full bg-slate-50 border border-slate-200 rounded-xl pl-9 pr-3 py-2 text-xs text-slate-800 focus:outline-none focus:border-violet-500" />
        </div>
        <select value={statusFilter} onChange={e => setStatusFilter(e.target.value)}
          className="bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-xs text-slate-800 focus:outline-none focus:border-violet-500">
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
            <RefreshCw className="w-6 h-6 animate-spin mx-auto text-violet-500" />
            <p className="text-xs font-medium">Loading driver roster...</p>
          </div>
        ) : drivers.length === 0 ? (
          <div className="p-12 text-center text-slate-500">
            <Users className="w-8 h-8 text-slate-300 mx-auto mb-2" />
            <p className="font-semibold text-sm">No drivers found</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-xs text-left text-slate-700">
              <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 font-semibold uppercase tracking-wider text-[10px]">
                <tr>
                  <th className="py-3.5 px-4">Driver Profile</th>
                  <th className="py-3.5 px-4">Linked User Account</th>
                  <th className="py-3.5 px-4">License Number</th>
                  <th className="py-3.5 px-4">Phone</th>
                  <th className="py-3.5 px-4">Status</th>
                  {canManage && <th className="py-3.5 px-4 text-right">Actions</th>}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-medium">
                {drivers.map(d => (
                  <tr key={d.id} className="hover:bg-slate-50/80 transition">
                    <td className="py-3.5 px-4">
                      <div className="flex items-center gap-2">
                        <div className="w-8 h-8 bg-violet-100 rounded-full flex items-center justify-center text-violet-700 font-bold text-xs">
                          D{d.id}
                        </div>
                        <div>
                          <p className="font-bold text-slate-900">Driver #{d.id}</p>
                          <p className="text-[10px] text-slate-400">Created {new Date(d.created_at).toLocaleDateString()}</p>
                        </div>
                      </div>
                    </td>
                    <td className="py-3.5 px-4">
                      <div className="flex items-center gap-1 text-slate-600">
                        <UserCheck className="w-3.5 h-3.5 text-violet-400" />
                        <span className="text-[11px]">{getUserName(d.user_id)}</span>
                      </div>
                    </td>
                    <td className="py-3.5 px-4">
                      <div className="flex items-center gap-1">
                        <CreditCard className="w-3.5 h-3.5 text-slate-400" />
                        <span className="font-mono font-bold text-slate-800">{d.license_number}</span>
                      </div>
                    </td>
                    <td className="py-3.5 px-4">
                      <div className="flex items-center gap-1">
                        <Phone className="w-3.5 h-3.5 text-slate-400" />
                        <span>{d.phone}</span>
                      </div>
                    </td>
                    <td className="py-3.5 px-4">
                      <span className={`px-2.5 py-0.5 rounded-full border text-[10px] font-bold tracking-wider uppercase ${STATUS_STYLES[d.status] || ''}`}>
                        {d.status}
                      </span>
                    </td>
                    {canManage && (
                      <td className="py-3.5 px-4 text-right">
                        <div className="flex items-center justify-end gap-1.5">
                          <button onClick={() => openModal(d)}
                            className="p-1.5 text-slate-500 hover:text-violet-600 hover:bg-violet-50 rounded-lg transition cursor-pointer" title="Edit">
                            <Edit2 className="w-3.5 h-3.5" />
                          </button>
                          {isAdmin && (
                            <button onClick={() => handleDelete(d.id)}
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
          <div className="bg-white rounded-3xl border border-slate-200 w-full max-w-md shadow-2xl p-6 space-y-5">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <h3 className="font-bold text-slate-900 text-base">
                {editingDriver ? `Edit Driver #${editingDriver.id}` : 'Register Driver Profile'}
              </h3>
              <button onClick={() => setIsModalOpen(false)} className="text-slate-400 hover:text-slate-600 cursor-pointer">
                <X className="w-5 h-5" />
              </button>
            </div>
            <form onSubmit={handleSave} className="space-y-4 text-xs">
              {!editingDriver && (
                <div className="space-y-1">
                  <label className="font-semibold text-slate-700">Link to User Account *</label>
                  <select required value={formData.user_id}
                    onChange={e => setFormData({ ...formData, user_id: e.target.value })}
                    className="w-full border border-slate-200 rounded-xl px-3.5 py-2 text-xs focus:outline-none focus:border-violet-500">
                    <option value="">— Select User —</option>
                    {users.map(u => (
                      <option key={u.id} value={u.id}>{u.name} ({u.email})</option>
                    ))}
                  </select>
                  <p className="text-[10px] text-slate-400">Only users with DRIVER role are listed. Create user first if needed.</p>
                </div>
              )}
              <div className="space-y-1">
                <label className="font-semibold text-slate-700">License Number *</label>
                <input required value={formData.license_number}
                  onChange={e => setFormData({ ...formData, license_number: e.target.value })}
                  placeholder="MH1234567890"
                  className="w-full border border-slate-200 rounded-xl px-3.5 py-2 font-mono text-xs focus:outline-none focus:border-violet-500" />
              </div>
              <div className="space-y-1">
                <label className="font-semibold text-slate-700">Phone Number *</label>
                <input required value={formData.phone}
                  onChange={e => setFormData({ ...formData, phone: e.target.value })}
                  placeholder="+91 98765 43210"
                  className="w-full border border-slate-200 rounded-xl px-3.5 py-2 text-xs focus:outline-none focus:border-violet-500" />
              </div>
              <div className="space-y-1">
                <label className="font-semibold text-slate-700">Operational Status</label>
                <select value={formData.status}
                  onChange={e => setFormData({ ...formData, status: e.target.value })}
                  className="w-full border border-slate-200 rounded-xl px-3.5 py-2 text-xs focus:outline-none focus:border-violet-500">
                  <option value="AVAILABLE">Available</option>
                  <option value="ON_ROUTE">On Route</option>
                  <option value="OFF_DUTY">Off Duty</option>
                  <option value="INACTIVE">Inactive</option>
                </select>
              </div>
              <div className="flex items-center justify-end gap-2 pt-4 border-t border-slate-100">
                <button type="button" onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 rounded-xl text-slate-600 hover:bg-slate-100 font-semibold cursor-pointer text-xs">Cancel</button>
                <button type="submit" disabled={saving}
                  className="bg-emerald-600 hover:bg-emerald-700 text-white font-bold px-4 py-2 rounded-xl transition shadow-md shadow-emerald-600/20 cursor-pointer disabled:opacity-50 text-xs">
                  {saving ? 'Saving...' : 'Save Driver'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
