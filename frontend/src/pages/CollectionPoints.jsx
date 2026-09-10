import React, { useEffect, useState } from 'react';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';
import { 
  MapPin, 
  Plus, 
  Search, 
  Filter, 
  AlertTriangle, 
  RefreshCw, 
  Edit2, 
  Trash2, 
  X, 
  Check, 
  Zap,
  TrendingUp,
  Scale,
  Calendar
} from 'lucide-react';

export default function CollectionPoints() {
  const { user } = useAuth();
  const [points, setPoints] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Filter States
  const [search, setSearch] = useState('');
  const [priorityFilter, setPriorityFilter] = useState('');
  const [wasteTypeFilter, setWasteTypeFilter] = useState('');
  const [overflowOnly, setOverflowOnly] = useState(false);

  // Modal States
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingPoint, setEditingPoint] = useState(null);
  const [formSubmitting, setFormSubmitting] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    address: '',
    latitude: 18.5204,
    longitude: 73.8567,
    estimated_waste_kg: 250.0,
    waste_type: 'PET',
    overflow_status: false,
  });

  const canManage = user?.role === 'ADMIN' || user?.role === 'MANAGER';
  const canDelete = user?.role === 'ADMIN';

  const fetchCollectionPoints = async () => {
    setLoading(true);
    setError(null);
    try {
      const params = {};
      if (search) params.search = search;
      if (priorityFilter) params.priority = priorityFilter;
      if (wasteTypeFilter) params.waste_type = wasteTypeFilter;
      if (overflowOnly) params.overflow_only = true;

      const res = await api.get('/collection-points', { params });
      setPoints(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch collection points');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCollectionPoints();
  }, [search, priorityFilter, wasteTypeFilter, overflowOnly]);

  const handleOpenModal = (point = null) => {
    if (point) {
      setEditingPoint(point);
      setFormData({
        name: point.name,
        address: point.address,
        latitude: point.latitude,
        longitude: point.longitude,
        estimated_waste_kg: point.estimated_waste_kg,
        waste_type: point.waste_type,
        overflow_status: point.overflow_status,
      });
    } else {
      setEditingPoint(null);
      setFormData({
        name: '',
        address: '',
        latitude: 18.5204,
        longitude: 73.8567,
        estimated_waste_kg: 250.0,
        waste_type: 'PET',
        overflow_status: false,
      });
    }
    setIsModalOpen(true);
  };

  const handleSave = async (e) => {
    e.preventDefault();
    setFormSubmitting(true);
    try {
      if (editingPoint) {
        await api.put(`/collection-points/${editingPoint.id}`, formData);
      } else {
        await api.post('/collection-points', formData);
      }
      setIsModalOpen(false);
      fetchCollectionPoints();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to save collection point');
    } finally {
      setFormSubmitting(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm(`Are you sure you want to delete Collection Point #${id}?`)) return;
    try {
      await api.delete(`/collection-points/${id}`);
      fetchCollectionPoints();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to delete collection point');
    }
  };

  const handleRecalculate = async (id) => {
    try {
      await api.post(`/collection-points/${id}/recalculate-priority`);
      fetchCollectionPoints();
    } catch (err) {
      alert('Failed to recalculate priority');
    }
  };

  const getPriorityBadge = (priority) => {
    switch (priority) {
      case 'CRITICAL':
        return 'bg-red-500/10 text-red-600 border-red-500/30';
      case 'HIGH':
        return 'bg-amber-500/10 text-amber-600 border-amber-500/30';
      case 'MEDIUM':
        return 'bg-blue-500/10 text-blue-600 border-blue-500/30';
      case 'LOW':
        return 'bg-emerald-500/10 text-emerald-600 border-emerald-500/30';
      default:
        return 'bg-slate-100 text-slate-700 border-slate-200';
    }
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
        <div>
          <div className="inline-flex items-center gap-2 bg-emerald-50 text-emerald-700 border border-emerald-200 text-xs px-3 py-1 rounded-full font-semibold mb-1">
            <MapPin className="w-3.5 h-3.5" />
            Phase 3 — Collection Point & Priority Module
          </div>
          <h1 className="text-xl font-bold text-slate-900">Collection Points Directory</h1>
          <p className="text-slate-500 text-xs mt-0.5">
            Geospatial coordinates, recyclable waste load capacity, overflow telemetry, and dynamic priority scoring engine.
          </p>
        </div>

        {canManage && (
          <button
            onClick={() => handleOpenModal()}
            className="flex items-center justify-center gap-2 bg-emerald-600 hover:bg-emerald-700 text-white px-4 py-2.5 rounded-xl font-semibold text-xs transition shadow-md shadow-emerald-600/20 cursor-pointer shrink-0"
          >
            <Plus className="w-4 h-4" />
            Add Collection Point
          </button>
        )}
      </div>

      {/* Filter Toolbar */}
      <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3">
        {/* Search */}
        <div className="relative">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
          <input
            type="text"
            placeholder="Search location or name..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-slate-50 border border-slate-200 rounded-xl pl-9 pr-3 py-2 text-xs text-slate-800 focus:outline-none focus:border-emerald-500"
          />
        </div>

        {/* Priority Filter */}
        <select
          value={priorityFilter}
          onChange={(e) => setPriorityFilter(e.target.value)}
          className="bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-xs text-slate-800 focus:outline-none focus:border-emerald-500"
        >
          <option value="">All Priorities</option>
          <option value="CRITICAL">🔴 CRITICAL</option>
          <option value="HIGH">🟠 HIGH</option>
          <option value="MEDIUM">🔵 MEDIUM</option>
          <option value="LOW">🟢 LOW</option>
        </select>

        {/* Plastic Waste Type Filter */}
        <select
          value={wasteTypeFilter}
          onChange={(e) => setWasteTypeFilter(e.target.value)}
          className="bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-xs text-slate-800 focus:outline-none focus:border-emerald-500"
        >
          <option value="">All Plastic Types</option>
          <option value="PET">PET (Polyethylene Terephthalate)</option>
          <option value="HDPE">HDPE (High-Density Polyethylene)</option>
          <option value="LDPE">LDPE (Low-Density Polyethylene)</option>
          <option value="PP">PP (Polypropylene)</option>
          <option value="MIXED_PLASTIC">Mixed Recyclable Plastic</option>
        </select>

        {/* Overflow Only Toggle */}
        <label className="flex items-center justify-between bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-xs text-slate-700 cursor-pointer select-none">
          <span className="font-medium flex items-center gap-1.5">
            <AlertTriangle className="w-3.5 h-3.5 text-amber-500" />
            Overflowing Only
          </span>
          <input
            type="checkbox"
            checked={overflowOnly}
            onChange={(e) => setOverflowOnly(e.target.checked)}
            className="w-4 h-4 accent-emerald-600 rounded cursor-pointer"
          />
        </label>
      </div>

      {/* Collection Points Data Table */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        {loading ? (
          <div className="p-12 text-center text-slate-400 space-y-3">
            <RefreshCw className="w-6 h-6 animate-spin mx-auto text-emerald-500" />
            <p className="text-xs font-medium">Fetching collection points & calculating priority matrix...</p>
          </div>
        ) : points.length === 0 ? (
          <div className="p-12 text-center text-slate-500">
            <MapPin className="w-8 h-8 text-slate-300 mx-auto mb-2" />
            <p className="font-semibold text-sm">No collection points match criteria</p>
            <p className="text-xs text-slate-400 mt-1">Try clearing filters or search parameters</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-700">
              <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 font-semibold uppercase tracking-wider text-[10px]">
                <tr>
                  <th className="py-3.5 px-4">Point & Location</th>
                  <th className="py-3.5 px-4">Plastic Type</th>
                  <th className="py-3.5 px-4">Waste Load</th>
                  <th className="py-3.5 px-4">Priority Score</th>
                  <th className="py-3.5 px-4">Priority Level</th>
                  <th className="py-3.5 px-4">Overflow</th>
                  <th className="py-3.5 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-medium">
                {points.map((pt) => (
                  <tr key={pt.id} className="hover:bg-slate-50/80 transition">
                    {/* Name & Address */}
                    <td className="py-3.5 px-4">
                      <p className="font-bold text-slate-900">{pt.name}</p>
                      <p className="text-[11px] text-slate-400 truncate max-w-xs">{pt.address}</p>
                      <span className="text-[10px] font-mono text-slate-400">
                        {pt.latitude.toFixed(4)}, {pt.longitude.toFixed(4)}
                      </span>
                    </td>

                    {/* Plastic Type */}
                    <td className="py-3.5 px-4">
                      <span className="bg-indigo-50 text-indigo-700 border border-indigo-200 px-2.5 py-0.5 rounded-full font-mono text-[10px] font-bold">
                        {pt.waste_type}
                      </span>
                    </td>

                    {/* Waste Load */}
                    <td className="py-3.5 px-4">
                      <div className="flex items-center gap-1.5">
                        <Scale className="w-3.5 h-3.5 text-slate-400" />
                        <span className="font-bold text-slate-800">{pt.estimated_waste_kg} kg</span>
                      </div>
                    </td>

                    {/* Priority Score */}
                    <td className="py-3.5 px-4">
                      <div className="flex items-center gap-1">
                        <Zap className="w-3.5 h-3.5 text-amber-500" />
                        <span className="font-mono font-bold text-slate-900">
                          {pt.priority_score ? pt.priority_score.toFixed(1) : 'N/A'} pts
                        </span>
                      </div>
                    </td>

                    {/* Priority Level Badge */}
                    <td className="py-3.5 px-4">
                      <span className={`px-2.5 py-0.5 rounded-full border text-[10px] font-bold tracking-wider uppercase ${getPriorityBadge(pt.priority)}`}>
                        {pt.priority}
                      </span>
                    </td>

                    {/* Overflow Status */}
                    <td className="py-3.5 px-4">
                      {pt.overflow_status ? (
                        <span className="inline-flex items-center gap-1 bg-red-500 text-white text-[10px] font-bold px-2 py-0.5 rounded-md animate-pulse">
                          <AlertTriangle className="w-3 h-3" />
                          OVERFLOWING
                        </span>
                      ) : (
                        <span className="text-slate-400 text-[10px]">Normal</span>
                      )}
                    </td>

                    {/* Action Buttons */}
                    <td className="py-3.5 px-4 text-right">
                      <div className="flex items-center justify-end gap-1.5">
                        <button
                          onClick={() => handleRecalculate(pt.id)}
                          title="Recalculate Priority Engine Score"
                          className="p-1.5 text-slate-500 hover:text-emerald-600 hover:bg-emerald-50 rounded-lg transition cursor-pointer"
                        >
                          <TrendingUp className="w-3.5 h-3.5" />
                        </button>

                        {canManage && (
                          <button
                            onClick={() => handleOpenModal(pt)}
                            title="Edit Point"
                            className="p-1.5 text-slate-500 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition cursor-pointer"
                          >
                            <Edit2 className="w-3.5 h-3.5" />
                          </button>
                        )}

                        {canDelete && (
                          <button
                            onClick={() => handleDelete(pt.id)}
                            title="Delete Point"
                            className="p-1.5 text-slate-500 hover:text-red-600 hover:bg-red-50 rounded-lg transition cursor-pointer"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Add / Edit Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 bg-slate-950/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl border border-slate-200 w-full max-w-lg shadow-2xl p-6 space-y-5">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <h3 className="font-bold text-slate-900 text-base">
                {editingPoint ? `Edit Collection Point #${editingPoint.id}` : 'Create New Collection Point'}
              </h3>
              <button onClick={() => setIsModalOpen(false)} className="text-slate-400 hover:text-slate-600">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleSave} className="space-y-4 text-xs">
              <div className="space-y-1">
                <label className="font-semibold text-slate-700">Point Name</label>
                <input
                  type="text"
                  required
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="e.g. Baner Commercial Bin #3"
                  className="w-full border border-slate-200 rounded-xl px-3.5 py-2 text-xs focus:outline-none focus:border-emerald-500"
                />
              </div>

              <div className="space-y-1">
                <label className="font-semibold text-slate-700">Full Address</label>
                <input
                  type="text"
                  required
                  value={formData.address}
                  onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                  placeholder="Street address, neighborhood, Pune"
                  className="w-full border border-slate-200 rounded-xl px-3.5 py-2 text-xs focus:outline-none focus:border-emerald-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1">
                  <label className="font-semibold text-slate-700">Latitude</label>
                  <input
                    type="number"
                    step="any"
                    required
                    value={formData.latitude}
                    onChange={(e) => setFormData({ ...formData, latitude: parseFloat(e.target.value) })}
                    className="w-full border border-slate-200 rounded-xl px-3.5 py-2 text-xs focus:outline-none focus:border-emerald-500 font-mono"
                  />
                </div>
                <div className="space-y-1">
                  <label className="font-semibold text-slate-700">Longitude</label>
                  <input
                    type="number"
                    step="any"
                    required
                    value={formData.longitude}
                    onChange={(e) => setFormData({ ...formData, longitude: parseFloat(e.target.value) })}
                    className="w-full border border-slate-200 rounded-xl px-3.5 py-2 text-xs focus:outline-none focus:border-emerald-500 font-mono"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1">
                  <label className="font-semibold text-slate-700">Estimated Waste (kg)</label>
                  <input
                    type="number"
                    step="0.1"
                    required
                    value={formData.estimated_waste_kg}
                    onChange={(e) => setFormData({ ...formData, estimated_waste_kg: parseFloat(e.target.value) })}
                    className="w-full border border-slate-200 rounded-xl px-3.5 py-2 text-xs focus:outline-none focus:border-emerald-500 font-mono"
                  />
                </div>
                <div className="space-y-1">
                  <label className="font-semibold text-slate-700">Plastic Waste Type</label>
                  <select
                    value={formData.waste_type}
                    onChange={(e) => setFormData({ ...formData, waste_type: e.target.value })}
                    className="w-full border border-slate-200 rounded-xl px-3.5 py-2 text-xs focus:outline-none focus:border-emerald-500"
                  >
                    <option value="PET">PET (Polyethylene)</option>
                    <option value="HDPE">HDPE (High Density)</option>
                    <option value="LDPE">LDPE (Low Density)</option>
                    <option value="PP">PP (Polypropylene)</option>
                    <option value="MIXED_PLASTIC">Mixed Recyclable</option>
                  </select>
                </div>
              </div>

              <div className="pt-2">
                <label className="flex items-center gap-2 cursor-pointer select-none">
                  <input
                    type="checkbox"
                    checked={formData.overflow_status}
                    onChange={(e) => setFormData({ ...formData, overflow_status: e.target.checked })}
                    className="w-4 h-4 accent-red-600 rounded"
                  />
                  <span className="font-semibold text-slate-800">Mark as Bin Overflowing (Triggers CRITICAL Priority)</span>
                </label>
              </div>

              <div className="flex items-center justify-end gap-2 pt-4 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 rounded-xl text-slate-600 hover:bg-slate-100 font-semibold cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={formSubmitting}
                  className="bg-emerald-600 hover:bg-emerald-700 text-white font-bold px-4 py-2 rounded-xl transition shadow-md shadow-emerald-600/20 cursor-pointer disabled:opacity-50"
                >
                  {formSubmitting ? 'Saving...' : 'Save Collection Point'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
