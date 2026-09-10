import React, { useEffect, useMemo } from 'react';
import { 
  MapContainer, 
  TileLayer, 
  Marker, 
  Popup, 
  Polyline, 
  Tooltip, 
  useMap 
} from 'react-leaflet';
import L from 'leaflet';

// Fix default leaflet marker asset paths in Vite
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

// Color palettes for vehicle routes
export const ROUTE_COLORS = [
  '#059669', // Emerald
  '#2563eb', // Blue
  '#7c3aed', // Purple
  '#d97706', // Amber
  '#db2777', // Pink
  '#0891b2', // Cyan
  '#ea580c', // Orange
];

export const PRIORITY_COLORS = {
  CRITICAL: '#ef4444',
  HIGH: '#f59e0b',
  MEDIUM: '#3b82f6',
  LOW: '#10b981',
};

// Custom DivIcon Generators
export function createDepotIcon() {
  return L.divIcon({
    className: 'custom-depot-marker',
    html: `
      <div class="relative flex items-center justify-center w-9 h-9 bg-purple-700 text-white rounded-xl shadow-lg border-2 border-white ring-2 ring-purple-400/50 transform -translate-x-1/2 -translate-y-1/2">
        <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
          <polyline points="9 22 9 12 15 12 15 22"/>
        </svg>
      </div>
    `,
    iconSize: [36, 36],
    iconAnchor: [18, 18],
  });
}

export function createPointIcon(priority = 'MEDIUM', isOverflow = false) {
  const color = PRIORITY_COLORS[priority] || '#3b82f6';
  return L.divIcon({
    className: 'custom-point-marker',
    html: `
      <div class="relative flex items-center justify-center w-6 h-6 rounded-full shadow-md border-2 border-white transform -translate-x-1/2 -translate-y-1/2" style="background-color: ${color};">
        ${isOverflow ? '<span class="absolute -top-1 -right-1 flex h-3 w-3"><span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span><span class="relative inline-flex rounded-full h-3 w-3 bg-red-600"></span></span>' : ''}
        <div class="w-1.5 h-1.5 bg-white rounded-full"></div>
      </div>
    `,
    iconSize: [24, 24],
    iconAnchor: [12, 12],
  });
}

export function createStopIcon(sequenceNumber, routeColor = '#059669', status = 'PENDING') {
  const isCompleted = status === 'COLLECTED';
  return L.divIcon({
    className: 'custom-stop-marker',
    html: `
      <div class="relative flex items-center justify-center w-7 h-7 text-white font-bold text-xs rounded-full shadow-lg border-2 border-white transform -translate-x-1/2 -translate-y-1/2" style="background-color: ${isCompleted ? '#10b981' : routeColor};">
        ${isCompleted ? '✓' : sequenceNumber}
      </div>
    `,
    iconSize: [28, 28],
    iconAnchor: [14, 14],
  });
}

// Controller component to auto-adjust map bounds
function BoundsController({ bounds }) {
  const map = useMap();
  useEffect(() => {
    if (bounds && bounds.length > 0) {
      try {
        map.fitBounds(bounds, { padding: [40, 40], maxZoom: 15 });
      } catch (err) {
        // Fallback gracefully if bounds are single point
      }
    }
  }, [bounds, map]);
  return null;
}

export default function RouteMap({
  depot = null,
  collectionPoints = [],
  routes = [],
  selectedRouteId = null,
  onPointSelect = null,
  height = '500px',
  showLegend = true,
}) {
  // Default Pune center
  const defaultCenter = [18.5204, 73.8567];

  // Compute all map coordinates to calculate bounding box
  const bounds = useMemo(() => {
    const coords = [];
    if (depot && depot.latitude && depot.longitude) {
      coords.push([depot.latitude, depot.longitude]);
    }
    collectionPoints.forEach((pt) => {
      if (pt.latitude && pt.longitude) {
        coords.push([pt.latitude, pt.longitude]);
      }
    });
    routes.forEach((r) => {
      if (r.geometry_geojson) {
        try {
          const geom = typeof r.geometry_geojson === 'string' 
            ? JSON.parse(r.geometry_geojson) 
            : r.geometry_geojson;
          if (Array.isArray(geom)) {
            geom.forEach((coord) => coords.push(coord));
          }
        } catch (e) {
          // ignore parsing error
        }
      }
      if (r.stops) {
        r.stops.forEach((s) => {
          if (s.latitude && s.longitude) {
            coords.push([s.latitude, s.longitude]);
          }
        });
      }
    });
    return coords.length > 0 ? coords : [defaultCenter];
  }, [depot, collectionPoints, routes]);

  // Parse route polylines
  const routePolylines = useMemo(() => {
    return routes.map((route, idx) => {
      const color = ROUTE_COLORS[idx % ROUTE_COLORS.length];
      let coordinates = [];

      if (route.geometry_geojson) {
        try {
          coordinates = typeof route.geometry_geojson === 'string'
            ? JSON.parse(route.geometry_geojson)
            : route.geometry_geojson;
        } catch (e) {
          coordinates = [];
        }
      }

      // Fallback to stop straight lines if geometry is not yet available
      if (!coordinates || coordinates.length === 0) {
        if (route.stops && route.stops.length > 0) {
          if (depot) coordinates.push([depot.latitude, depot.longitude]);
          route.stops.forEach((s) => coordinates.push([s.latitude, s.longitude]));
          if (depot) coordinates.push([depot.latitude, depot.longitude]);
        }
      }

      return {
        id: route.id || `route-${idx}`,
        vehicleId: route.vehicle_id,
        vehicleNumber: route.vehicle_number || `Vehicle #${route.vehicle_id}`,
        driverName: route.driver_name,
        color,
        coordinates,
        distanceKm: route.total_distance_km,
        durationMin: route.estimated_duration_minutes,
        wasteKg: route.total_waste_kg,
        utilization: route.utilization_percentage,
        stops: route.stops || [],
        isSelected: selectedRouteId === null || selectedRouteId === route.id,
      };
    });
  }, [routes, depot, selectedRouteId]);

  return (
    <div className="relative w-full rounded-2xl overflow-hidden border border-slate-200 shadow-sm bg-slate-100" style={{ height }}>
      <MapContainer
        center={defaultCenter}
        zoom={12}
        className="w-full h-full"
        scrollWheelZoom={true}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        <BoundsController bounds={bounds} />

        {/* 1. Central Depot Marker */}
        {depot && depot.latitude && depot.longitude && (
          <Marker
            position={[depot.latitude, depot.longitude]}
            icon={createDepotIcon()}
          >
            <Popup className="custom-popup">
              <div className="p-2 space-y-1.5 max-w-xs">
                <div className="flex items-center gap-1.5 text-purple-700 font-bold text-xs">
                  <span className="w-2 h-2 rounded-full bg-purple-600"></span>
                  CENTRAL RECYCLING DEPOT
                </div>
                <h4 className="font-bold text-slate-900 text-sm">{depot.name || 'Central Facility'}</h4>
                <p className="text-slate-500 text-xs">{depot.address || 'Central Materials Recovery Facility'}</p>
                <div className="pt-1.5 border-t border-slate-100 text-[11px] text-slate-600 flex justify-between font-mono">
                  <span>GPS: {depot.latitude.toFixed(4)}, {depot.longitude.toFixed(4)}</span>
                </div>
              </div>
            </Popup>
          </Marker>
        )}

        {/* 2. Standalone / Unassigned Collection Points */}
        {collectionPoints.map((pt) => (
          <Marker
            key={`cp-${pt.id}`}
            position={[pt.latitude, pt.longitude]}
            icon={createPointIcon(pt.priority, pt.overflow_status)}
            eventHandlers={{
              click: () => onPointSelect && onPointSelect(pt),
            }}
          >
            <Popup className="custom-popup">
              <div className="p-2 space-y-1.5 max-w-xs font-sans">
                <div className="flex items-center justify-between">
                  <span className={`text-[10px] font-bold uppercase px-2 py-0.5 rounded-full text-white`} style={{ backgroundColor: PRIORITY_COLORS[pt.priority] || '#3b82f6' }}>
                    {pt.priority} PRIORITY
                  </span>
                  {pt.overflow_status && (
                    <span className="text-[10px] font-bold bg-red-100 text-red-700 px-1.5 py-0.5 rounded">
                      OVERFLOW
                    </span>
                  )}
                </div>
                <h4 className="font-bold text-slate-900 text-sm">{pt.name}</h4>
                <p className="text-slate-500 text-xs">{pt.address}</p>
                <div className="grid grid-cols-2 gap-2 pt-2 border-t border-slate-100 text-xs">
                  <div>
                    <span className="text-slate-400 text-[10px] block">Est. Waste</span>
                    <span className="font-bold text-slate-800">{pt.estimated_waste_kg} kg</span>
                  </div>
                  <div>
                    <span className="text-slate-400 text-[10px] block">Waste Type</span>
                    <span className="font-medium text-slate-700">{pt.waste_type}</span>
                  </div>
                </div>
              </div>
            </Popup>
          </Marker>
        ))}

        {/* 3. Snapped Road Polylines for Vehicle Routes */}
        {routePolylines.map((route) => {
          if (!route.coordinates || route.coordinates.length < 2) return null;
          return (
            <Polyline
              key={`polyline-${route.id}`}
              positions={route.coordinates}
              pathOptions={{
                color: route.color,
                weight: route.isSelected ? 5 : 2.5,
                opacity: route.isSelected ? 0.9 : 0.4,
                lineCap: 'round',
                lineJoin: 'round',
              }}
            >
              <Tooltip sticky>
                <div className="text-xs space-y-0.5 font-sans">
                  <p className="font-bold text-slate-900">{route.vehicleNumber}</p>
                  {route.driverName && <p className="text-slate-600">Driver: {route.driverName}</p>}
                  <p className="text-slate-500 font-mono">
                    {route.distanceKm} km • {route.durationMin} min • {route.wasteKg} kg
                  </p>
                </div>
              </Tooltip>
            </Polyline>
          );
        })}

        {/* 4. Numbered Stop Markers along Routes */}
        {routePolylines.map((route) => {
          if (!route.isSelected) return null;
          return route.stops.map((stop) => {
            if (!stop.latitude || !stop.longitude) return null;
            return (
              <Marker
                key={`stop-${route.id}-${stop.id || stop.sequence_number}`}
                position={[stop.latitude, stop.longitude]}
                icon={createStopIcon(stop.sequence_number, route.color, stop.status)}
              >
                <Popup className="custom-popup">
                  <div className="p-2 space-y-1.5 max-w-xs font-sans">
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] font-bold px-2 py-0.5 rounded text-white" style={{ backgroundColor: route.color }}>
                        STOP #{stop.sequence_number} • {route.vehicleNumber}
                      </span>
                      <span className={`text-[10px] font-bold px-2 py-0.5 rounded ${
                        stop.status === 'COLLECTED' ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-100 text-slate-700'
                      }`}>
                        {stop.status}
                      </span>
                    </div>
                    <h4 className="font-bold text-slate-900 text-sm">{stop.point_name || `Point #${stop.collection_point_id}`}</h4>
                    {stop.point_address && <p className="text-slate-500 text-xs">{stop.point_address}</p>}
                    
                    <div className="grid grid-cols-2 gap-2 pt-2 border-t border-slate-100 text-xs">
                      <div>
                        <span className="text-slate-400 text-[10px] block">Waste Quantity</span>
                        <span className="font-bold text-slate-800">{stop.estimated_waste_kg || stop.waste_kg || 0} kg</span>
                      </div>
                      <div>
                        <span className="text-slate-400 text-[10px] block">Estimated Arrival</span>
                        <span className="font-medium text-slate-700">
                          {stop.estimated_arrival_time ? new Date(stop.estimated_arrival_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : 'Pending'}
                        </span>
                      </div>
                    </div>
                  </div>
                </Popup>
              </Marker>
            );
          });
        })}
      </MapContainer>

      {/* Floating Interactive Map Legend */}
      {showLegend && (
        <div className="absolute bottom-4 right-4 bg-white/95 backdrop-blur-md p-3.5 rounded-xl border border-slate-200/80 shadow-lg z-[1000] text-xs space-y-2 max-w-xs pointer-events-auto">
          <h5 className="font-bold text-slate-800 text-[11px] uppercase tracking-wider">Map Legend</h5>
          
          <div className="grid grid-cols-2 gap-x-3 gap-y-1.5 text-[11px] text-slate-600">
            <div className="flex items-center gap-1.5">
              <span className="w-3 h-3 rounded bg-purple-700 border border-white"></span>
              <span>Central Depot</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-3 h-3 rounded-full bg-red-500 border border-white"></span>
              <span>Critical (80+)</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-3 h-3 rounded-full bg-amber-500 border border-white"></span>
              <span>High (60-80)</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-3 h-3 rounded-full bg-blue-500 border border-white"></span>
              <span>Medium (30-60)</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-3 h-3 rounded-full bg-emerald-500 border border-white"></span>
              <span>Low (&lt;30)</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-3 h-3 rounded-full bg-emerald-600 text-[8px] text-white flex items-center justify-center font-bold">✓</span>
              <span>Collected Stop</span>
            </div>
          </div>

          {routes.length > 0 && (
            <div className="pt-2 border-t border-slate-100">
              <span className="text-[10px] font-bold text-slate-400 block mb-1">VEHICLE ROUTES</span>
              <div className="flex flex-wrap gap-1.5">
                {routes.map((r, i) => (
                  <span
                    key={i}
                    className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-semibold text-white"
                    style={{ backgroundColor: ROUTE_COLORS[i % ROUTE_COLORS.length] }}
                  >
                    {r.vehicle_number || `V${i+1}`}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
