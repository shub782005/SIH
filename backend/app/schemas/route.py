from datetime import datetime, date
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from app.models.enums import RouteStatus, StopStatus, WasteType, PriorityLevel


class RouteStopResponse(BaseModel):
    id: int
    route_id: int
    collection_point_id: int
    point_name: str
    point_address: str
    latitude: float
    longitude: float
    estimated_waste_kg: float
    waste_type: WasteType
    priority: PriorityLevel
    sequence_number: int
    estimated_arrival_time: Optional[datetime] = None
    actual_arrival_time: Optional[datetime] = None
    status: StopStatus

    model_config = ConfigDict(from_attributes=True)


class RouteResponse(BaseModel):
    id: int
    route_date: date
    vehicle_id: int
    vehicle_number: str
    driver_id: Optional[int] = None
    driver_name: Optional[str] = None
    total_distance_km: float
    estimated_duration_minutes: float
    total_waste_kg: float
    utilization_percentage: float
    status: RouteStatus
    optimization_run_id: Optional[int] = None
    geometry_geojson: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    stops: List[RouteStopResponse] = []

    model_config = ConfigDict(from_attributes=True)


class RouteSummaryResponse(BaseModel):
    id: int
    route_date: date
    vehicle_id: int
    vehicle_number: str
    driver_id: Optional[int] = None
    driver_name: Optional[str] = None
    total_distance_km: float
    estimated_duration_minutes: float
    total_waste_kg: float
    utilization_percentage: float
    status: RouteStatus
    stops_count: int
    optimization_run_id: Optional[int] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RouteStatusUpdateRequest(BaseModel):
    status: RouteStatus


class RouteAssignRequest(BaseModel):
    driver_id: Optional[int] = None
    vehicle_id: Optional[int] = None
