import React, { useEffect, useState } from 'react';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';
import RouteMap, { PRIORITY_COLORS } from '../components/RouteMap';
import { 
  Truck, 
  MapPin, 
  Navigation, 
  CheckCircle2, 
  AlertTriangle, 
  Camera, 
  Play, 
  Scale, 
  Clock, 
  RefreshCw, 
  ChevronRight, 
  Check, 
  X, 
  FileText,
  ShieldAlert,
  Sparkles
} from 'lucide-react';

export default function DriverPortal() {
  const { user } = useAuth();
  const [route, setRoute] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Modals & Action States
  const [isCollectModalOpen, setIsCollectModalOpen] = useState(false);
  const [isIssueModalOpen, setIsIssueModalOpen] = useState(false);
  const [activeStop, setActiveStop] = useState(null);

  // Collection Form State
  const [actualQuantity, setActualQuantity] = useState('');
  const [remarks, setRemarks] = useState('');
  const [proofFile, setProofFile] = useState(null);
  const [uploadingProof, setUploadingProof] = useState(false);
  const [submittingAction, setSubmittingAction] = useState(false);

  // Issue Form State
  const [failureReason, setFailureReason] = useState('NO_WASTE');
  const [issueRemarks, setIssueRemarks] = useState('');

  const fetchDriverRoute = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.get('/driver/my-route');
      setRoute(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed to fetch assigned route');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDriverRoute();
  }, []);

  // Determine current active stop (first stop that is PENDING or ARRIVED)
  const currentPendingStop = route?.stops?.find(
    (s) => s.status === 'PENDING' || s.status === 'ARRIVED'
  ) || null;

  const completedStopsCount = route?.stops?.filter(
    (s) => s.status === 'COLLECTED' || s.status === 'SKIPPED' || s.status === 'FAILED'
  ).length || 0;

  const totalStopsCount = route?.stops?.length || 0;
  const progressPct = totalStopsCount > 0 ? (completedStopsCount / totalStopsCount) * 100 : 0;
  const isRouteFinished = totalStopsCount > 0 && completedStopsCount === totalStopsCount;

  // Start route action
  const handleStartRoute = async () => {
    if (!route) return;
    try {
      setSubmittingAction(true);
      await api.put(`/routes/${route.id}/status`, { status: 'STARTED' });
      await fetchDriverRoute();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to start route');
    } finally {
      setSubmittingAction(false);
    }
  };

  // Mark Arrival action
  const handleMarkArrival = async (stopId) => {
    try {
      setSubmittingAction(true);
      await api.post(`/collections/arrive/${stopId}`);
      await fetchDriverRoute();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to mark arrival');
    } finally {
      setSubmittingAction(false);
    }
  };

  // Upload proof photo helper
  const handleProofUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setProofFile(file);
  };

  // Submit Collection confirmation
  const handleSubmitCollection = async (e) => {
    e.preventDefault();
    if (!activeStop) return;

    try {
      setSubmittingAction(true);
      let proofUrl = null;

      if (proofFile) {
        setUploadingProof(true);
        const formData = new FormData();
        formData.append('file', proofFile);
        const uploadRes = await api.post('/collections/upload-proof', formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });
        proofUrl = uploadRes.data.url;
      }

      await api.post('/collections/complete', {
        route_stop_id: activeStop.id,
        actual_quantity_kg: parseFloat(actualQuantity) || activeStop.estimated_waste_kg,
        proof_image_url: proofUrl,
        remarks: remarks || null,
      });

      setIsCollectModalOpen(false);
      setActiveStop(null);
      setActualQuantity('');
      setRemarks('');
      setProofFile(null);
      await fetchDriverRoute();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to record collection');
    } finally {
      setSubmittingAction(false);
      setUploadingProof(false);
    }
  };

  // Submit Issue / Failure report
  const handleSubmitIssue = async (e) => {
    e.preventDefault();
    if (!activeStop) return;

    try {
      setSubmittingAction(true);
      await api.post('/collections/fail', {
        route_stop_id: activeStop.id,
        failure_reason: failureReason,
        remarks: issueRemarks || null,
      });

      setIsIssueModalOpen(false);
      setActiveStop(null);
      setIssueRemarks('');
      await fetchDriverRoute();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to report collection problem');
    } finally {
      setSubmittingAction(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-5 pb-12 font-sans">
      {/* Top Driver Header */}
      <div className="bg-slate-900 text-white p-5 rounded-2xl shadow-lg border border-slate-800 flex items-center justify-between">
        <div className="space-y-1">
          <div className="inline-flex items-center gap-2 bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 text-[11px] px-2.5 py-0.5 rounded-full font-bold">
            <Truck className="w-3.5 h-3.5" />
            Driver Execution Portal
          </div>
          <h2 className="text-xl font-bold tracking-tight">
            {user?.name || 'Driver Console'}
          </h2>
          <p className="text-slate-400 text-xs">
            {route ? `${route.vehicle_number} • ${route.total_waste_kg} kg scheduled load` : 'No active route assigned'}
          </p>
        </div>

        <button
          onClick={fetchDriverRoute}
          disabled={loading}
          className="p-2.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl transition cursor-pointer"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-red-50 border border-red-200 text-red-700 text-xs flex items-center gap-2 font-medium">
          <AlertTriangle className="w-4 h-4 shrink-0 text-red-500" />
          <span>{error}</span>
        </div>
      )}

      {!route ? (
        <div className="bg-white p-10 rounded-2xl border border-slate-200 text-center text-slate-500 space-y-3">
          <Truck className="w-12 h-12 text-slate-300 mx-auto" />
          <h3 className="text-base font-bold text-slate-800">No Active Collection Route Assigned</h3>
          <p className="text-xs text-slate-400 max-w-md mx-auto">
            You currently have no active collection route. Please contact the Operations Dispatcher or check back later.
          </p>
        </div>
      ) : (
        <>
          {/* Progress Tracker Card */}
          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-3">
            <div className="flex items-center justify-between">
              <div>
                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Trip Progress</span>
                <h4 className="text-sm font-bold text-slate-800">
                  {completedStopsCount} of {totalStopsCount} Stops Processed
                </h4>
              </div>
              <span className={`text-xs font-bold px-3 py-1 rounded-full uppercase ${
                route.status === 'COMPLETED' ? 'bg-emerald-100 text-emerald-700' : 'bg-blue-100 text-blue-700'
              }`}>
                {route.status}
              </span>
            </div>

            {/* Progress Bar */}
            <div className="w-full h-3 bg-slate-100 rounded-full overflow-hidden">
              <div
                className="h-full bg-emerald-600 rounded-full transition-all duration-500"
                style={{ width: `${progressPct}%` }}
              ></div>
            </div>

            {route.status === 'PLANNED' || route.status === 'ASSIGNED' ? (
              <button
                onClick={handleStartRoute}
                disabled={submittingAction}
                className="w-full flex items-center justify-center gap-2 bg-emerald-600 hover:bg-emerald-700 text-white font-bold py-3 px-4 rounded-xl text-sm shadow-md transition cursor-pointer"
              >
                <Play className="w-4 h-4 fill-white" />
                <span>Start Collection Route</span>
              </button>
            ) : null}
          </div>

          {/* Route Finished Celebration Card */}
          {isRouteFinished && (
            <div className="bg-gradient-to-r from-emerald-600 to-teal-700 text-white p-6 rounded-2xl shadow-xl space-y-2 text-center">
              <Sparkles className="w-8 h-8 mx-auto text-emerald-200" />
              <h3 className="text-lg font-bold">Route Successfully Completed!</h3>
              <p className="text-xs text-emerald-100 max-w-md mx-auto">
                All scheduled collection points for {route.vehicle_number} have been collected and verified. Return to central depot for unloading.
              </p>
            </div>
          )}

          {/* Active Next Stop Spotlight Card */}
          {currentPendingStop && (
            <div className="bg-white p-6 rounded-2xl border-2 border-emerald-500 shadow-xl space-y-5">
              <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                <div className="flex items-center gap-2.5">
                  <span className="w-8 h-8 rounded-full bg-emerald-600 text-white font-bold text-sm flex items-center justify-center shadow-md">
                    #{currentPendingStop.sequence_number}
                  </span>
                  <div>
                    <span className="text-[10px] font-bold text-emerald-600 uppercase tracking-wider block">CURRENT STOP TARGET</span>
                    <h3 className="text-base font-bold text-slate-900">{currentPendingStop.point_name}</h3>
                  </div>
                </div>

                <span className={`text-[10px] font-bold px-2.5 py-0.5 rounded-full text-white`} style={{ backgroundColor: PRIORITY_COLORS[currentPendingStop.priority] || '#3b82f6' }}>
                  {currentPendingStop.priority} PRIORITY
                </span>
              </div>

              {/* Stop Info Details */}
              <div className="space-y-2 text-xs">
                <div className="flex items-start gap-2 text-slate-600">
                  <MapPin className="w-4 h-4 text-slate-400 shrink-0 mt-0.5" />
                  <span className="font-medium">{currentPendingStop.point_address}</span>
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-3 gap-2.5 pt-2">
                  <div className="bg-slate-50 p-2.5 rounded-xl border border-slate-100">
                    <span className="text-[10px] text-slate-400 block font-medium">Expected Plastic</span>
                    <span className="text-sm font-bold text-slate-800">{currentPendingStop.estimated_waste_kg} kg</span>
                  </div>
                  <div className="bg-slate-50 p-2.5 rounded-xl border border-slate-100">
                    <span className="text-[10px] text-slate-400 block font-medium">Plastic Type</span>
                    <span className="text-sm font-bold text-slate-800">{currentPendingStop.waste_type}</span>
                  </div>
                  <div className="bg-slate-50 p-2.5 rounded-xl border border-slate-100 col-span-2 sm:col-span-1">
                    <span className="text-[10px] text-slate-400 block font-medium">Est. Arrival</span>
                    <span className="text-sm font-bold text-slate-800 font-mono">
                      {currentPendingStop.estimated_arrival_time ? new Date(currentPendingStop.estimated_arrival_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : 'ASAP'}
                    </span>
                  </div>
                </div>
              </div>

              {/* Driver Action Buttons */}
              <div className="space-y-2.5 pt-2">
                {/* Navigation Link Button */}
                <a
                  href={`https://www.google.com/maps/dir/?api=1&destination=${currentPendingStop.latitude},${currentPendingStop.longitude}`}
                  target="_blank"
                  rel="noreferrer"
                  className="w-full flex items-center justify-center gap-2 bg-slate-900 hover:bg-slate-800 text-white font-bold py-3 px-4 rounded-xl text-xs shadow transition"
                >
                  <Navigation className="w-4 h-4" />
                  <span>Open Turn-by-Turn GPS Navigation</span>
                </a>

                {currentPendingStop.status === 'PENDING' ? (
                  <button
                    onClick={() => handleMarkArrival(currentPendingStop.id)}
                    disabled={submittingAction}
                    className="w-full flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white font-bold py-3.5 px-4 rounded-xl text-sm shadow-md transition cursor-pointer"
                  >
                    <Check className="w-5 h-5" />
                    <span>Mark Arrived at Stop</span>
                  </button>
                ) : (
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                    <button
                      onClick={() => {
                        setActiveStop(currentPendingStop);
                        setActualQuantity(String(currentPendingStop.estimated_waste_kg));
                        setIsCollectModalOpen(true);
                      }}
                      className="w-full flex items-center justify-center gap-2 bg-emerald-600 hover:bg-emerald-700 text-white font-bold py-3.5 px-4 rounded-xl text-sm shadow-md transition cursor-pointer"
                    >
                      <Scale className="w-5 h-5" />
                      <span>Record Collection Weight</span>
                    </button>

                    <button
                      onClick={() => {
                        setActiveStop(currentPendingStop);
                        setIsIssueModalOpen(true);
                      }}
                      className="w-full flex items-center justify-center gap-2 bg-amber-50 hover:bg-amber-100 text-amber-800 border border-amber-200 font-bold py-3.5 px-4 rounded-xl text-sm transition cursor-pointer"
                    >
                      <ShieldAlert className="w-5 h-5 text-amber-600" />
                      <span>Report Problem / Skip</span>
                    </button>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Sequenced Route Stops Timeline */}
          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-4">
            <h3 className="font-bold text-slate-900 text-sm flex items-center gap-2">
              <Clock className="w-4 h-4 text-emerald-600" />
              Complete Stop Schedule ({route.stops?.length || 0} stops)
            </h3>

            <div className="space-y-2 max-h-80 overflow-y-auto pr-1">
              {route.stops?.map((stop) => {
                const isCurrent = currentPendingStop?.id === stop.id;
                const isCollected = stop.status === 'COLLECTED';
                const isFailed = stop.status === 'FAILED' || stop.status === 'SKIPPED';
                return (
                  <div
                    key={stop.id}
                    className={`p-3.5 rounded-xl border flex items-center justify-between text-xs transition ${
                      isCurrent
                        ? 'bg-emerald-50/70 border-emerald-300 ring-2 ring-emerald-500/20'
                        : isCollected
                        ? 'bg-slate-50/70 border-slate-200 opacity-80'
                        : 'bg-white border-slate-200'
                    }`}
                  >
                    <div className="flex items-center gap-3 min-w-0">
                      <span
                        className={`w-6 h-6 rounded-full font-bold text-xs flex items-center justify-center shrink-0 ${
                          isCollected
                            ? 'bg-emerald-600 text-white'
                            : isFailed
                            ? 'bg-red-500 text-white'
                            : isCurrent
                            ? 'bg-emerald-600 text-white'
                            : 'bg-slate-200 text-slate-700'
                        }`}
                      >
                        {isCollected ? '✓' : stop.sequence_number}
                      </span>
                      <div className="min-w-0">
                        <h4 className="font-bold text-slate-800 text-xs truncate">{stop.point_name}</h4>
                        <p className="text-[11px] text-slate-500 truncate">{stop.point_address}</p>
                      </div>
                    </div>

                    <div className="text-right shrink-0 ml-3">
                      <span className="font-bold text-slate-800 text-xs block">{stop.estimated_waste_kg} kg</span>
                      <span
                        className={`text-[9px] font-bold px-1.5 py-0.2 rounded uppercase ${
                          isCollected
                            ? 'bg-emerald-100 text-emerald-700'
                            : isFailed
                            ? 'bg-red-100 text-red-700'
                            : 'bg-slate-100 text-slate-600'
                        }`}
                      >
                        {stop.status}
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Embedded Driver Map View */}
          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-3">
            <h3 className="font-bold text-slate-900 text-sm flex items-center gap-2">
              <MapPin className="w-4 h-4 text-emerald-600" />
              Active Route Snapped Road Map
            </h3>
            <RouteMap
              depot={{
                id: 1,
                name: 'Swargate Central Depot',
                latitude: 18.5018,
                longitude: 73.8636,
              }}
              routes={[route]}
              height="380px"
            />
          </div>
        </>
      )}

      {/* Record Collection Modal */}
      {isCollectModalOpen && activeStop && (
        <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-4 font-sans">
            <div className="flex items-center justify-between">
              <h3 className="font-bold text-slate-900 text-base">Record Collection Weight</h3>
              <button onClick={() => setIsCollectModalOpen(false)} className="text-slate-400 hover:text-slate-600 cursor-pointer">
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="bg-slate-50 p-3 rounded-xl border border-slate-100 text-xs">
              <p className="text-slate-400 text-[10px]">Collection Point:</p>
              <h4 className="font-bold text-slate-900">{activeStop.point_name}</h4>
              <p className="text-slate-500 text-[11px]">{activeStop.point_address}</p>
            </div>

            <form onSubmit={handleSubmitCollection} className="space-y-3.5">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Actual Waste Collected (kg) *
                </label>
                <input
                  type="number"
                  step="0.1"
                  required
                  value={actualQuantity}
                  onChange={(e) => setActualQuantity(e.target.value)}
                  className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm font-bold text-slate-900 focus:ring-2 focus:ring-emerald-500 focus:outline-none"
                  placeholder="e.g. 215.0"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Attach Photo Proof (Optional)
                </label>
                <label className="flex items-center justify-center gap-2 p-3 border-2 border-dashed border-slate-200 hover:border-emerald-500 rounded-xl cursor-pointer bg-slate-50 transition text-xs text-slate-600">
                  <Camera className="w-4 h-4 text-emerald-600" />
                  <span>{proofFile ? proofFile.name : 'Take Photo / Upload Image'}</span>
                  <input
                    type="file"
                    accept="image/*"
                    onChange={handleProofUpload}
                    className="hidden"
                  />
                </label>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Remarks / Observations
                </label>
                <textarea
                  value={remarks}
                  onChange={(e) => setRemarks(e.target.value)}
                  rows={2}
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs focus:ring-2 focus:ring-emerald-500 focus:outline-none"
                  placeholder="e.g. Sorted PET bottles, no contamination found."
                />
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setIsCollectModalOpen(false)}
                  className="px-4 py-2.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submittingAction || uploadingProof}
                  className="px-5 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold shadow transition cursor-pointer"
                >
                  {submittingAction || uploadingProof ? 'Saving...' : 'Confirm & Complete Stop'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Report Problem / Issue Modal */}
      {isIssueModalOpen && activeStop && (
        <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-4 font-sans">
            <div className="flex items-center justify-between">
              <h3 className="font-bold text-slate-900 text-base">Report Problem / Skip Stop</h3>
              <button onClick={() => setIsIssueModalOpen(false)} className="text-slate-400 hover:text-slate-600 cursor-pointer">
                <X className="w-5 h-5" />
              </button>
            </div>

            <p className="text-xs text-slate-500">
              Reporting a failure will log an exception for <strong>{activeStop.point_name}</strong> and advance your route to the next stop.
            </p>

            <form onSubmit={handleSubmitIssue} className="space-y-3.5">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Reason for Exception *
                </label>
                <select
                  value={failureReason}
                  onChange={(e) => setFailureReason(e.target.value)}
                  className="w-full px-3 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs font-semibold text-slate-800 focus:ring-2 focus:ring-amber-500 focus:outline-none"
                >
                  <option value="NO_WASTE">NO WASTE (Bin was empty)</option>
                  <option value="LOCATION_INACCESSIBLE">LOCATION INACCESSIBLE (Road blocked/closed)</option>
                  <option value="VEHICLE_ISSUE">VEHICLE ISSUE (Breakdown / Tire puncture)</option>
                  <option value="COLLECTION_POINT_CLOSED">COLLECTION POINT CLOSED (Gate locked)</option>
                  <option value="EXCESSIVE_WASTE">EXCESSIVE WASTE (Requires larger truck)</option>
                  <option value="OTHER">OTHER REASON</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Detailed Notes / Remarks
                </label>
                <textarea
                  value={issueRemarks}
                  onChange={(e) => setIssueRemarks(e.target.value)}
                  rows={2}
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs focus:ring-2 focus:ring-amber-500 focus:outline-none"
                  placeholder="Explain the situation..."
                />
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setIsIssueModalOpen(false)}
                  className="px-4 py-2.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submittingAction}
                  className="px-5 py-2.5 rounded-xl bg-amber-600 hover:bg-amber-700 text-white text-xs font-bold shadow transition cursor-pointer"
                >
                  {submittingAction ? 'Submitting...' : 'Submit Report & Skip'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
