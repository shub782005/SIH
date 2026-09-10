import React, { useEffect, useState, useMemo } from 'react';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';
import RouteMap, { ROUTE_COLORS } from '../components/RouteMap';
import { 
  Truck, 
  MapPin, 
  Clock, 
  Scale, 
  Calendar, 
  CheckCircle2, 
  Play, 
  UserCheck, 
  RefreshCw, 
  AlertCircle, 
  ChevronRight, 
  Trash2, 
  Check, 
  Layers,
  ArrowRight
} from 'lucide-react';

export default function RoutesView() {
  const { user } = useAuth();
  const [routes, setRoutes] = useState([]);
  const [depot, setDepot] = useState(null);
  const [drivers, setDrivers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Filters & State
  const [selectedRouteId, setSelectedRouteId] = useState(null);
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [search, setSearch] = useState('');

  // Assign Modal
  const [isAssignModalOpen, setIsAssignModalOpen] = useState(false);
  const [assignRouteData, setAssignRouteData] = useState(null);
  const [selectedDriverId, setSelectedDriverId] = useState('');
  const [submittingAction, setSubmittingAction] = useState(false);

  const canManage = user?.role === 'ADMIN' || user?.role === 'MANAGER';

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [routesRes, depotRes, driversRes] = await Promise.all([
        api.get('/routes'),
        api.get('/health'),
        canManage ? api.get('/drivers') : Promise.resolve({ data: [] })
      ]);

      setRoutes(routesRes.data || []);
      setDrivers(driversRes.data || []);

      // Default Pune Depot reference
      setDepot({
        id: 1,
        name: 'Central Recycling & Material Recovery Facility',
        address: 'Swargate Central Depot, Tilak Road, Pune',
        latitude: 18.5018,
        longitude: 73.8636,
      });

      if (routesRes.data && routesRes.data.length > 0 && selectedRouteId === null) {
        setSelectedRouteId(routesRes.data[0].id);
      }
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed to load routes data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  // Filtered routes
  const filteredRoutes = useMemo(() => {
    return routes.filter((r) => {
      const matchesStatus = statusFilter === 'ALL' || r.status === statusFilter;
      const matchesSearch = 
        !search || 
        r.vehicle_number?.toLowerCase().includes(search.toLowerCase()) ||
        r.driver_name?.toLowerCase().includes(search.toLowerCase());
      return matchesStatus && matchesSearch;
    });
  }, [routes, statusFilter, search]);

  const activeSelectedRoute = useMemo(() => {
    return routes.find((r) => r.id === selectedRouteId) || routes[0] || null;
  }, [routes, selectedRouteId]);

  // Route status update
  const handleUpdateStatus = async (routeId, newStatus) => {
    try {
      setSubmittingAction(true);
      await api.put(`/routes/${routeId}/status`, { status: newStatus });
      await fetchData();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to update route status');
    } finally {
      setSubmittingAction(false);
    }
  };

  // Driver Assignment
  const handleAssignDriver = async (e) => {
    e.preventDefault();
    if (!assignRouteData) return;
    try {
      setSubmittingAction(true);
      await api.put(`/routes/${assignRouteData.id}/assign`, {
        driver_id: selectedDriverId ? parseInt(selectedDriverId, 10) : null
      });
      setIsAssignModalOpen(false);
      setAssignRouteData(null);
      await fetchData();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to assign driver');
    } finally {
      setSubmittingAction(false);
    }
  };

  // Delete planned route
  const handleDeleteRoute = async (routeId) => {
    if (!window.confirm('Are you sure you want to delete this planned route?')) return;
    try {
      setSubmittingAction(true);
      await api.delete(`/routes/${routeId}`);
      if (selectedRouteId === routeId) {
        setSelectedRouteId(null);
      }
      await fetchData();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to delete route');
    } finally {
      setSubmittingAction(false);
    }
  };

  const totalDistance = routes.reduce((acc, r) => acc + (r.total_distance_km || 0), 0);
  const totalWaste = routes.reduce((acc, r) => acc + (r.total_waste_kg || 0), 0);

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="p-2 bg-emerald-50 text-emerald-600 rounded-xl">
              <Truck className="w-6 h-6" />
            </span>
            <div>
              <h2 className="text-xl font-bold text-slate-900">Vehicle Routes & Execution Tracking</h2>
              <p className="text-slate-500 text-xs mt-0.5">
                Monitor live collection progress, view OSRM-snapped road geometries, and manage driver assignments.
              </p>
            </div>
          </div>
        </div>

        {/* Global Route Metrics */}
        <div className="flex items-center gap-4 text-xs font-sans">
          <div className="bg-slate-50 px-3.5 py-2 rounded-xl border border-slate-200 text-center">
            <span className="text-slate-400 text-[10px] block uppercase font-bold">Total Routes</span>
            <span className="text-base font-bold text-slate-900">{routes.length}</span>
          </div>
          <div className="bg-slate-50 px-3.5 py-2 rounded-xl border border-slate-200 text-center">
            <span className="text-slate-400 text-[10px] block uppercase font-bold">Total Distance</span>
            <span className="text-base font-bold text-emerald-600">{totalDistance.toFixed(1)} km</span>
          </div>
          <div className="bg-slate-50 px-3.5 py-2 rounded-xl border border-slate-200 text-center">
            <span className="text-slate-400 text-[10px] block uppercase font-bold">Waste Scheduled</span>
            <span className="text-base font-bold text-blue-600">{totalWaste.toFixed(0)} kg</span>
          </div>
          <button
            onClick={fetchData}
            disabled={loading}
            className="p-2.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl transition cursor-pointer"
            title="Refresh routes"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-red-50 border border-red-200 text-red-700 text-xs flex items-center gap-2 font-medium">
          <AlertCircle className="w-4 h-4 shrink-0" />
          {error}
        </div>
      )}

      {/* Filter Tabs */}
      <div className="flex flex-wrap items-center justify-between gap-3 bg-white p-3.5 rounded-2xl border border-slate-200 shadow-sm text-xs">
        <div className="flex items-center gap-1.5 overflow-x-auto">
          {['ALL', 'PLANNED', 'ASSIGNED', 'STARTED', 'IN_PROGRESS', 'COMPLETED'].map((st) => (
            <button
              key={st}
              onClick={() => setStatusFilter(st)}
              className={`px-3 py-1.5 rounded-lg font-semibold transition cursor-pointer ${
                statusFilter === st
                  ? 'bg-slate-900 text-white shadow-sm'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
            >
              {st}
            </button>
          ))}
        </div>

        <input
          type="text"
          placeholder="Filter by vehicle or driver..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="px-3 py-1.5 bg-slate-50 border border-slate-200 rounded-lg text-xs w-64 focus:outline-none focus:ring-2 focus:ring-emerald-500"
        />
      </div>

      {/* Main Content Layout: Left Route Cards & Stop Timeline, Right Map */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Column: Route List & Details */}
        <div className="lg:col-span-5 space-y-4">
          <div className="flex items-center justify-between text-xs font-bold text-slate-500 uppercase tracking-wider px-1">
            <span>Generated Vehicle Routes ({filteredRoutes.length})</span>
            {selectedRouteId && (
              <button 
                onClick={() => setSelectedRouteId(null)} 
                className="text-emerald-600 hover:underline font-semibold cursor-pointer"
              >
                Show All on Map
              </button>
            )}
          </div>

          {filteredRoutes.length === 0 ? (
            <div className="bg-white p-8 rounded-2xl border border-slate-200 text-center text-slate-500 text-xs space-y-2">
              <Layers className="w-8 h-8 text-slate-300 mx-auto" />
              <p className="font-semibold">No routes found matching your filter criteria.</p>
              <p className="text-[11px] text-slate-400">Generate new optimized routes from the Optimization tab.</p>
            </div>
          ) : (
            filteredRoutes.map((route, idx) => {
              const isSelected = selectedRouteId === route.id;
              const color = ROUTE_COLORS[idx % ROUTE_COLORS.length];
              return (
                <div
                  key={route.id}
                  onClick={() => setSelectedRouteId(route.id)}
                  className={`p-4.5 rounded-2xl border transition cursor-pointer bg-white ${
                    isSelected
                      ? 'border-emerald-500 shadow-md ring-2 ring-emerald-500/20'
                      : 'border-slate-200 hover:border-slate-300 shadow-sm'
                  }`}
                >
                  {/* Route Header */}
                  <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                    <div className="flex items-center gap-2.5">
                      <span
                        className="w-3.5 h-3.5 rounded-full"
                        style={{ backgroundColor: color }}
                      ></span>
                      <div>
                        <h4 className="font-bold text-slate-900 text-sm">{route.vehicle_number}</h4>
                        <p className="text-[11px] text-slate-500 font-medium">
                          Driver: {route.driver_name || 'Unassigned'}
                        </p>
                      </div>
                    </div>

                    <span
                      className={`text-[10px] font-bold px-2.5 py-0.5 rounded-full uppercase ${
                        route.status === 'COMPLETED'
                          ? 'bg-emerald-100 text-emerald-700'
                          : route.status === 'STARTED' || route.status === 'IN_PROGRESS'
                          ? 'bg-blue-100 text-blue-700'
                          : route.status === 'ASSIGNED'
                          ? 'bg-purple-100 text-purple-700'
                          : 'bg-slate-100 text-slate-700'
                      }`}
                    >
                      {route.status}
                    </span>
                  </div>

                  {/* Route Metrics */}
                  <div className="grid grid-cols-3 gap-2 py-3 text-xs border-b border-slate-100">
                    <div>
                      <span className="text-slate-400 text-[10px] block font-medium">Distance</span>
                      <span className="font-bold text-slate-800">{route.total_distance_km} km</span>
                    </div>
                    <div>
                      <span className="text-slate-400 text-[10px] block font-medium">Duration</span>
                      <span className="font-bold text-slate-800">{route.estimated_duration_minutes} min</span>
                    </div>
                    <div>
                      <span className="text-slate-400 text-[10px] block font-medium">Capacity Util.</span>
                      <span className="font-bold text-slate-800">{route.utilization_percentage}%</span>
                    </div>
                  </div>

                  {/* Utilization Progress Bar */}
                  <div className="py-2.5 space-y-1">
                    <div className="flex justify-between text-[11px] text-slate-500 font-medium">
                      <span>Total Waste Collected</span>
                      <span className="font-bold text-slate-700">{route.total_waste_kg} kg</span>
                    </div>
                    <div className="w-full h-2 bg-slate-100 rounded-full overflow-hidden">
                      <div
                        className="h-full rounded-full transition-all"
                        style={{
                          width: `${Math.min(route.utilization_percentage, 100)}%`,
                          backgroundColor: color,
                        }}
                      ></div>
                    </div>
                  </div>

                  {/* Stop Sequence Accordion (visible when selected) */}
                  {isSelected && (
                    <div className="mt-3 pt-3 border-t border-slate-100 space-y-2 text-xs">
                      <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider block">
                        Stop Sequence ({route.stops?.length || 0} stops)
                      </span>

                      <div className="space-y-2 max-h-60 overflow-y-auto pr-1">
                        {/* Start Depot */}
                        <div className="flex items-start gap-2.5 p-2 rounded-xl bg-purple-50/50 border border-purple-100">
                          <span className="w-5 h-5 rounded-full bg-purple-700 text-white font-bold text-[10px] flex items-center justify-center shrink-0">
                            D
                          </span>
                          <div className="flex-1 min-w-0">
                            <h5 className="font-bold text-purple-900 text-xs truncate">Swargate Central Depot</h5>
                            <p className="text-[10px] text-purple-700">Route Origin (0 km)</p>
                          </div>
                        </div>

                        {/* Sequenced Collection Stops */}
                        {route.stops?.map((stop) => (
                          <div
                            key={stop.id}
                            className="flex items-start gap-2.5 p-2 rounded-xl bg-slate-50 border border-slate-100 hover:bg-slate-100/80 transition"
                          >
                            <span
                              className="w-5 h-5 rounded-full text-white font-bold text-[10px] flex items-center justify-center shrink-0"
                              style={{ backgroundColor: color }}
                            >
                              {stop.sequence_number}
                            </span>
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center justify-between">
                                <h5 className="font-bold text-slate-800 text-xs truncate">{stop.point_name}</h5>
                                <span className={`text-[9px] font-bold px-1.5 py-0.2 rounded ${
                                  stop.status === 'COLLECTED' ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-200 text-slate-700'
                                }`}>
                                  {stop.status}
                                </span>
                              </div>
                              <p className="text-[10px] text-slate-500 truncate">{stop.point_address}</p>
                              <div className="flex items-center justify-between text-[10px] text-slate-600 mt-1">
                                <span>{stop.estimated_waste_kg} kg • {stop.waste_type}</span>
                                <span className="font-mono text-slate-500">
                                  ETA: {stop.estimated_arrival_time ? new Date(stop.estimated_arrival_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : 'N/A'}
                                </span>
                              </div>
                            </div>
                          </div>
                        ))}

                        {/* End Depot Return */}
                        <div className="flex items-start gap-2.5 p-2 rounded-xl bg-purple-50/50 border border-purple-100">
                          <span className="w-5 h-5 rounded-full bg-purple-700 text-white font-bold text-[10px] flex items-center justify-center shrink-0">
                            D
                          </span>
                          <div className="flex-1 min-w-0">
                            <h5 className="font-bold text-purple-900 text-xs truncate">Swargate Central Depot (Return)</h5>
                            <p className="text-[10px] text-purple-700">Discharge waste & complete trip</p>
                          </div>
                        </div>
                      </div>

                      {/* Action Controls for Route */}
                      {canManage && (
                        <div className="flex flex-wrap gap-2 pt-2 border-t border-slate-100">
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              setAssignRouteData(route);
                              setSelectedDriverId(route.driver_id ? String(route.driver_id) : '');
                              setIsAssignModalOpen(true);
                            }}
                            className="flex items-center gap-1 bg-slate-100 hover:bg-slate-200 text-slate-700 px-2.5 py-1.5 rounded-lg text-xs font-semibold transition cursor-pointer"
                          >
                            <UserCheck className="w-3.5 h-3.5" />
                            Assign Driver
                          </button>

                          {route.status === 'PLANNED' && (
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                handleUpdateStatus(route.id, 'STARTED');
                              }}
                              disabled={submittingAction}
                              className="flex items-center gap-1 bg-blue-600 hover:bg-blue-700 text-white px-2.5 py-1.5 rounded-lg text-xs font-semibold transition cursor-pointer"
                            >
                              <Play className="w-3.5 h-3.5" />
                              Start Route
                            </button>
                          )}

                          {route.status === 'STARTED' && (
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                handleUpdateStatus(route.id, 'COMPLETED');
                              }}
                              disabled={submittingAction}
                              className="flex items-center gap-1 bg-emerald-600 hover:bg-emerald-700 text-white px-2.5 py-1.5 rounded-lg text-xs font-semibold transition cursor-pointer"
                            >
                              <CheckCircle2 className="w-3.5 h-3.5" />
                              Complete Route
                            </button>
                          )}

                          {route.status === 'PLANNED' && (
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                handleDeleteRoute(route.id);
                              }}
                              disabled={submittingAction}
                              className="flex items-center gap-1 bg-red-50 hover:bg-red-100 text-red-600 px-2.5 py-1.5 rounded-lg text-xs font-semibold transition ml-auto cursor-pointer"
                            >
                              <Trash2 className="w-3.5 h-3.5" />
                              Delete
                            </button>
                          )}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              );
            })
          )}
        </div>

        {/* Right Column: Embedded RouteMap Visualizer */}
        <div className="lg:col-span-7 sticky top-6 space-y-3">
          <div className="flex items-center justify-between text-xs font-bold text-slate-700 px-1">
            <span className="flex items-center gap-1.5">
              <MapPin className="w-4 h-4 text-emerald-600" />
              OSRM Snapped Road Geometry Map
            </span>
            {activeSelectedRoute && (
              <span className="text-[11px] font-semibold text-slate-500">
                Viewing: <strong className="text-slate-900">{selectedRouteId ? activeSelectedRoute.vehicle_number : 'All Active Routes'}</strong>
              </span>
            )}
          </div>

          <RouteMap
            depot={depot}
            routes={selectedRouteId ? [activeSelectedRoute] : routes}
            selectedRouteId={selectedRouteId}
            height="620px"
          />
        </div>
      </div>

      {/* Driver Assignment Modal */}
      {isAssignModalOpen && assignRouteData && (
        <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="font-bold text-slate-900 text-base">Assign Driver to Route</h3>
              <button
                onClick={() => setIsAssignModalOpen(false)}
                className="text-slate-400 hover:text-slate-600 cursor-pointer"
              >
                ✕
              </button>
            </div>

            <p className="text-xs text-slate-500">
              Select an available driver for <strong>{assignRouteData.vehicle_number}</strong> ({assignRouteData.total_waste_kg} kg scheduled load).
            </p>

            <form onSubmit={handleAssignDriver} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Registered Driver
                </label>
                <select
                  value={selectedDriverId}
                  onChange={(e) => setSelectedDriverId(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs focus:ring-2 focus:ring-emerald-500 focus:outline-none"
                >
                  <option value="">-- Select Driver --</option>
                  {drivers.map((d) => (
                    <option key={d.id} value={d.id}>
                      {d.user?.name || d.name || `Driver #${d.id}`} ({d.status}) - {d.phone}
                    </option>
                  ))}
                </select>
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setIsAssignModalOpen(false)}
                  className="px-4 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold transition cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submittingAction}
                  className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold transition cursor-pointer"
                >
                  {submittingAction ? 'Saving...' : 'Confirm Assignment'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
