import React, { useEffect, useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';
import RouteMap, { ROUTE_COLORS, PRIORITY_COLORS } from '../components/RouteMap';
import { 
  Zap, 
  Truck, 
  MapPin, 
  Scale, 
  Clock, 
  CheckCircle2, 
  AlertTriangle, 
  RefreshCw, 
  TrendingUp, 
  ShieldAlert, 
  ArrowRight, 
  Layers,
  Filter,
  Check
} from 'lucide-react';

export default function Optimization() {
  const { user } = useAuth();
  const navigate = useNavigate();

  // Data states
  const [vehicles, setVehicles] = useState([]);
  const [collectionPoints, setCollectionPoints] = useState([]);
  const [loadingInitial, setLoadingInitial] = useState(true);
  const [error, setError] = useState(null);

  // Selection states
  const [selectedVehicleIds, setSelectedVehicleIds] = useState([]);
  const [selectedPointIds, setSelectedPointIds] = useState([]);
  const [timeLimit, setTimeLimit] = useState(5);
  const [persistRoutes, setPersistRoutes] = useState(true);

  // Filters for collection points list
  const [pointSearch, setPointSearch] = useState('');
  const [prioFilter, setPrioFilter] = useState('');
  const [overflowOnly, setOverflowOnly] = useState(false);

  // Optimization Execution States
  const [isOptimizing, setIsOptimizing] = useState(false);
  const [optStage, setOptStage] = useState('');
  const [optResult, setOptResult] = useState(null);

  const canOptimize = user?.role === 'ADMIN' || user?.role === 'MANAGER';

  // Central Pune Depot reference
  const depot = {
    id: 1,
    name: 'Central Recycling & Material Recovery Facility',
    address: 'Swargate Central Depot, Tilak Road, Pune',
    latitude: 18.5018,
    longitude: 73.8636,
  };

  useEffect(() => {
    const fetchInitialData = async () => {
      setLoadingInitial(true);
      setError(null);
      try {
        const [vehiclesRes, pointsRes] = await Promise.all([
          api.get('/vehicles'),
          api.get('/collection-points'),
        ]);

        const availVehicles = (vehiclesRes.data || []).filter(
          (v) => v.status === 'AVAILABLE' || v.status === 'ON_ROUTE'
        );
        const activePoints = (pointsRes.data || []).filter(
          (p) => p.status === 'ACTIVE'
        );

        setVehicles(availVehicles);
        setCollectionPoints(activePoints);

        // Pre-select all by default
        setSelectedVehicleIds(availVehicles.map((v) => v.id));
        setSelectedPointIds(activePoints.map((p) => p.id));
      } catch (err) {
        setError(err.response?.data?.detail || err.message || 'Failed to fetch setup data');
      } finally {
        setLoadingInitial(false);
      }
    };

    fetchInitialData();
  }, []);

  // Filtered collection points
  const filteredPoints = useMemo(() => {
    return collectionPoints.filter((pt) => {
      const matchSearch =
        !pointSearch ||
        pt.name.toLowerCase().includes(pointSearch.toLowerCase()) ||
        pt.address.toLowerCase().includes(pointSearch.toLowerCase());
      const matchPrio = !prioFilter || pt.priority === prioFilter;
      const matchOverflow = !overflowOnly || pt.overflow_status === true;
      return matchSearch && matchPrio && matchOverflow;
    });
  }, [collectionPoints, pointSearch, prioFilter, overflowOnly]);

  // Live Metrics
  const totalSelectedCapacity = useMemo(() => {
    return vehicles
      .filter((v) => selectedVehicleIds.includes(v.id))
      .reduce((sum, v) => sum + (v.capacity_kg || 0), 0);
  }, [vehicles, selectedVehicleIds]);

  const totalSelectedDemand = useMemo(() => {
    return collectionPoints
      .filter((p) => selectedPointIds.includes(p.id))
      .reduce((sum, p) => sum + (p.estimated_waste_kg || 0), 0);
  }, [collectionPoints, selectedPointIds]);

  const capacityRatio = totalSelectedCapacity > 0 ? (totalSelectedDemand / totalSelectedCapacity) * 100 : 0;

  // Toggle helpers
  const handleToggleAllPoints = () => {
    if (selectedPointIds.length === collectionPoints.length) {
      setSelectedPointIds([]);
    } else {
      setSelectedPointIds(collectionPoints.map((p) => p.id));
    }
  };

  const handleToggleAllVehicles = () => {
    if (selectedVehicleIds.length === vehicles.length) {
      setSelectedVehicleIds([]);
    } else {
      setSelectedVehicleIds(vehicles.map((v) => v.id));
    }
  };

  const handleTogglePoint = (id) => {
    setSelectedPointIds((prev) =>
      prev.includes(id) ? prev.filter((pId) => pId !== id) : [...prev, id]
    );
  };

  const handleToggleVehicle = (id) => {
    setSelectedVehicleIds((prev) =>
      prev.includes(id) ? prev.filter((vId) => vId !== id) : [...prev, id]
    );
  };

  // Run Optimization Trigger
  const handleRunOptimization = async () => {
    if (selectedVehicleIds.length === 0) {
      alert('Please select at least 1 vehicle for optimization.');
      return;
    }
    if (selectedPointIds.length === 0) {
      alert('Please select at least 1 collection point.');
      return;
    }

    setIsOptimizing(true);
    setError(null);
    setOptResult(null);

    // Multi-stage progress indicators
    setOptStage('1/4: Validating Depot, Fleet & Collection Point Inputs...');
    await new Promise((r) => setTimeout(r, 400));

    setOptStage('2/4: Computing OSRM Road Distance & Travel Duration Matrices...');
    await new Promise((r) => setTimeout(r, 600));

    setOptStage('3/4: Solving Google OR-Tools CVRP (Capacitated Vehicle Routing Problem)...');

    try {
      const response = await api.post('/optimization/generate', {
        depot_id: depot.id,
        vehicle_ids: selectedVehicleIds,
        collection_point_ids: selectedPointIds,
        persist: persistRoutes,
        time_limit_seconds: timeLimit,
      });

      setOptStage('4/4: Retrieving OSRM Road Polylines & Persisting Results...');
      await new Promise((r) => setTimeout(r, 400));

      setOptResult(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Optimization solver failed');
    } finally {
      setIsOptimizing(false);
      setOptStage('');
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="bg-gradient-to-r from-slate-900 via-slate-800 to-emerald-950 p-6 rounded-2xl border border-slate-800 text-white shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="space-y-1.5">
          <div className="inline-flex items-center gap-2 bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 text-xs px-3 py-1 rounded-full font-semibold">
            <Zap className="w-3.5 h-3.5 text-emerald-400" />
            Google OR-Tools CVRP Engine + OSRM Road Routing
          </div>
          <h2 className="text-2xl font-bold tracking-tight">Capacitated Route Optimization Studio</h2>
          <p className="text-slate-400 text-xs max-w-2xl">
            Configure central depot, select fleet vehicles, select plastic collection demand points, and execute multi-vehicle road-snapped routing.
          </p>
        </div>

        {optResult && (
          <button
            onClick={() => navigate('/routes')}
            className="flex items-center gap-2 bg-emerald-600 hover:bg-emerald-500 text-white px-4 py-2.5 rounded-xl font-bold text-xs shadow-lg transition cursor-pointer self-start md:self-auto"
          >
            <span>View in Routes Dashboard</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        )}
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-red-50 border border-red-200 text-red-700 text-xs flex items-center gap-2 font-medium">
          <AlertTriangle className="w-4 h-4 shrink-0 text-red-500" />
          <span>{error}</span>
        </div>
      )}

      {/* Main Studio Grid: Configuration Panel on Left, Map & Results on Right */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Setup Drawer (Col 5) */}
        <div className="lg:col-span-5 space-y-4">
          {/* Capacity vs Demand Live Monitor */}
          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-3 font-sans">
            <div className="flex items-center justify-between">
              <h3 className="font-bold text-slate-800 text-sm flex items-center gap-2">
                <Scale className="w-4 h-4 text-emerald-600" />
                Fleet Capacity Feasibility
              </h3>
              <span
                className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                  capacityRatio > 100
                    ? 'bg-amber-100 text-amber-700'
                    : 'bg-emerald-100 text-emerald-700'
                }`}
              >
                {capacityRatio > 100 ? 'OVER CAPACITY' : 'FEASIBLE'}
              </span>
            </div>

            <div className="grid grid-cols-2 gap-3 text-xs">
              <div className="bg-slate-50 p-2.5 rounded-xl border border-slate-100">
                <span className="text-slate-400 text-[10px] block font-medium">Selected Demand</span>
                <span className="text-base font-bold text-slate-900">{totalSelectedDemand.toFixed(0)} kg</span>
              </div>
              <div className="bg-slate-50 p-2.5 rounded-xl border border-slate-100">
                <span className="text-slate-400 text-[10px] block font-medium">Fleet Capacity</span>
                <span className="text-base font-bold text-emerald-600">{totalSelectedCapacity.toFixed(0)} kg</span>
              </div>
            </div>

            {/* Capacity Meter */}
            <div className="space-y-1">
              <div className="flex justify-between text-[11px] text-slate-500 font-medium">
                <span>Fleet Load Ratio</span>
                <span className="font-bold text-slate-700">{capacityRatio.toFixed(1)}%</span>
              </div>
              <div className="w-full h-2.5 bg-slate-100 rounded-full overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all ${
                    capacityRatio > 100 ? 'bg-amber-500' : 'bg-emerald-600'
                  }`}
                  style={{ width: `${Math.min(capacityRatio, 100)}%` }}
                ></div>
              </div>
              {capacityRatio > 100 && (
                <p className="text-[10px] text-amber-600 font-medium pt-1">
                  Demand exceeds capacity. OR-Tools solver will prioritize High/Critical bins.
                </p>
              )}
            </div>
          </div>

          {/* Vehicle Fleet Selector */}
          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="font-bold text-slate-800 text-sm flex items-center gap-2">
                <Truck className="w-4 h-4 text-blue-600" />
                Select Fleet Vehicles ({selectedVehicleIds.length}/{vehicles.length})
              </h3>
              <button
                type="button"
                onClick={handleToggleAllVehicles}
                className="text-xs text-blue-600 font-semibold hover:underline cursor-pointer"
              >
                {selectedVehicleIds.length === vehicles.length ? 'Deselect All' : 'Select All'}
              </button>
            </div>

            <div className="space-y-2 max-h-48 overflow-y-auto pr-1">
              {vehicles.map((v) => {
                const isSelected = selectedVehicleIds.includes(v.id);
                return (
                  <div
                    key={v.id}
                    onClick={() => handleToggleVehicle(v.id)}
                    className={`p-3 rounded-xl border flex items-center justify-between cursor-pointer transition ${
                      isSelected
                        ? 'bg-blue-50/60 border-blue-200'
                        : 'bg-slate-50 border-slate-200 opacity-60'
                    }`}
                  >
                    <div className="flex items-center gap-2.5">
                      <input
                        type="checkbox"
                        checked={isSelected}
                        onChange={() => {}}
                        className="rounded text-blue-600 focus:ring-blue-500"
                      />
                      <div>
                        <h4 className="font-bold text-slate-900 text-xs">{v.vehicle_number}</h4>
                        <p className="text-[10px] text-slate-500">{v.vehicle_type} • Driver: {v.driver?.user?.name || 'Available'}</p>
                      </div>
                    </div>
                    <span className="text-xs font-bold text-slate-700 font-mono">{v.capacity_kg} kg</span>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Collection Points Selector */}
          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="font-bold text-slate-800 text-sm flex items-center gap-2">
                <MapPin className="w-4 h-4 text-emerald-600" />
                Select Collection Points ({selectedPointIds.length}/{collectionPoints.length})
              </h3>
              <button
                type="button"
                onClick={handleToggleAllPoints}
                className="text-xs text-emerald-600 font-semibold hover:underline cursor-pointer"
              >
                {selectedPointIds.length === collectionPoints.length ? 'Deselect All' : 'Select All'}
              </button>
            </div>

            {/* Filter controls */}
            <div className="flex items-center gap-2">
              <input
                type="text"
                placeholder="Search collection points..."
                value={pointSearch}
                onChange={(e) => setPointSearch(e.target.value)}
                className="flex-1 px-3 py-1.5 bg-slate-50 border border-slate-200 rounded-lg text-xs focus:ring-2 focus:ring-emerald-500 focus:outline-none"
              />
              <select
                value={prioFilter}
                onChange={(e) => setPrioFilter(e.target.value)}
                className="px-2.5 py-1.5 bg-slate-50 border border-slate-200 rounded-lg text-xs focus:outline-none"
              >
                <option value="">All Priorities</option>
                <option value="CRITICAL">Critical</option>
                <option value="HIGH">High</option>
                <option value="MEDIUM">Medium</option>
                <option value="LOW">Low</option>
              </select>
            </div>

            <div className="space-y-2 max-h-64 overflow-y-auto pr-1">
              {filteredPoints.map((pt) => {
                const isSelected = selectedPointIds.includes(pt.id);
                return (
                  <div
                    key={pt.id}
                    onClick={() => handleTogglePoint(pt.id)}
                    className={`p-2.5 rounded-xl border flex items-center justify-between cursor-pointer transition ${
                      isSelected
                        ? 'bg-emerald-50/50 border-emerald-200'
                        : 'bg-slate-50 border-slate-200 opacity-60'
                    }`}
                  >
                    <div className="flex items-center gap-2.5 min-w-0">
                      <input
                        type="checkbox"
                        checked={isSelected}
                        onChange={() => {}}
                        className="rounded text-emerald-600 focus:ring-emerald-500"
                      />
                      <div className="min-w-0">
                        <div className="flex items-center gap-1.5">
                          <h4 className="font-bold text-slate-800 text-xs truncate">{pt.name}</h4>
                          <span
                            className="text-[9px] font-bold px-1.5 py-0.2 rounded-full text-white"
                            style={{ backgroundColor: PRIORITY_COLORS[pt.priority] || '#3b82f6' }}
                          >
                            {pt.priority}
                          </span>
                        </div>
                        <p className="text-[10px] text-slate-500 truncate">{pt.address}</p>
                      </div>
                    </div>
                    <span className="text-xs font-bold text-slate-700 font-mono ml-2">{pt.estimated_waste_kg} kg</span>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Action Trigger Button */}
          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-3">
            <div className="flex items-center justify-between text-xs">
              <label className="flex items-center gap-2 cursor-pointer font-medium text-slate-700">
                <input
                  type="checkbox"
                  checked={persistRoutes}
                  onChange={(e) => setPersistRoutes(e.target.checked)}
                  className="rounded text-emerald-600 focus:ring-emerald-500"
                />
                Persist Generated Routes to Database
              </label>

              <div className="flex items-center gap-1 text-slate-500">
                <span>Solver limit:</span>
                <select
                  value={timeLimit}
                  onChange={(e) => setTimeLimit(parseInt(e.target.value, 10))}
                  className="bg-slate-50 border border-slate-200 rounded px-1.5 py-0.5 text-xs"
                >
                  <option value={3}>3s</option>
                  <option value={5}>5s</option>
                  <option value={10}>10s</option>
                </select>
              </div>
            </div>

            <button
              onClick={handleRunOptimization}
              disabled={isOptimizing || !canOptimize}
              className="w-full flex items-center justify-center gap-2 bg-gradient-to-r from-emerald-600 to-teal-700 hover:from-emerald-500 hover:to-teal-600 text-white font-bold py-3.5 px-4 rounded-xl shadow-lg transition text-sm cursor-pointer disabled:opacity-50"
            >
              {isOptimizing ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>Optimizing Routes...</span>
                </>
              ) : (
                <>
                  <Zap className="w-4 h-4" />
                  <span>Execute CVRP Route Optimization</span>
                </>
              )}
            </button>

            {isOptimizing && (
              <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-xl space-y-1.5 animate-pulse">
                <span className="text-[11px] font-bold text-emerald-800 block">Solving in Progress...</span>
                <p className="text-xs text-emerald-700 font-mono">{optStage}</p>
              </div>
            )}
          </div>
        </div>

        {/* Right Map & Results Visualization (Col 7) */}
        <div className="lg:col-span-7 space-y-4">
          {/* Optimization Results KPI Cards */}
          {optResult && (
            <div className="space-y-4 animate-fadeIn">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm text-center">
                  <span className="text-slate-400 text-[10px] block uppercase font-bold">Distance Saved</span>
                  <span className="text-xl font-bold text-emerald-600">
                    {optResult.distance_saved_percentage ?? 0}%
                  </span>
                  <span className="text-[10px] text-slate-400 block mt-0.5">vs. naive routing</span>
                </div>

                <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm text-center">
                  <span className="text-slate-400 text-[10px] block uppercase font-bold">Time Saved</span>
                  <span className="text-xl font-bold text-blue-600">
                    {optResult.time_saved_percentage ?? 0}%
                  </span>
                  <span className="text-[10px] text-slate-400 block mt-0.5">travel reduction</span>
                </div>

                <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm text-center">
                  <span className="text-slate-400 text-[10px] block uppercase font-bold">Total Waste</span>
                  <span className="text-xl font-bold text-slate-900">
                    {optResult.waste_collected} kg
                  </span>
                  <span className="text-[10px] text-slate-400 block mt-0.5">collected plastic</span>
                </div>

                <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm text-center">
                  <span className="text-slate-400 text-[10px] block uppercase font-bold">Total Road Travel</span>
                  <span className="text-xl font-bold text-purple-600">
                    {optResult.total_distance_after} km
                  </span>
                  <span className="text-[10px] text-slate-400 block mt-0.5">snapped OSRM</span>
                </div>
              </div>

              {/* Infeasible / Unassigned Points Warning */}
              {optResult.unassigned_points && optResult.unassigned_points.length > 0 && (
                <div className="p-4 rounded-2xl bg-amber-50 border border-amber-200 space-y-2">
                  <div className="flex items-center gap-2 text-amber-800 font-bold text-xs">
                    <AlertTriangle className="w-4 h-4 text-amber-600" />
                    <span>Unassigned / Infeasible Points ({optResult.unassigned_points.length})</span>
                  </div>
                  <div className="space-y-1.5 max-h-32 overflow-y-auto pr-1">
                    {optResult.unassigned_points.map((un, idx) => (
                      <div key={idx} className="text-xs text-amber-900 bg-white/80 p-2 rounded-lg border border-amber-100 flex justify-between">
                        <span><strong>{un.name}</strong> ({un.estimated_waste_kg} kg)</span>
                        <span className="text-[11px] text-amber-700">{un.reason}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Interactive Leaflet Route Map */}
          <div className="space-y-2">
            <div className="flex items-center justify-between text-xs font-bold text-slate-700 px-1">
              <span className="flex items-center gap-1.5">
                <MapPin className="w-4 h-4 text-emerald-600" />
                {optResult ? 'Optimized Capacity-Aware Road Routes' : 'Collection Points & Depot Map Preview'}
              </span>
              <span className="text-[11px] text-slate-500 font-semibold">
                {optResult ? `${optResult.routes?.length || 0} Vehicle Routes Generated` : `${collectionPoints.length} Points Configured`}
              </span>
            </div>

            <RouteMap
              depot={depot}
              collectionPoints={optResult ? [] : collectionPoints}
              routes={optResult?.routes || []}
              height="600px"
            />
          </div>
        </div>
      </div>
    </div>
  );
}
