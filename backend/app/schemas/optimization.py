from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict
from app.models.enums import OptimizationStatus
from app.optimization.schemas import OptimizationOutput, VehicleRoute, UnassignedPoint
from app.schemas.route import RouteResponse


class OptimizationGenerateRequest(BaseModel):
    depot_id: Optional[int] = Field(None, description="Depot ID (default: first active depot)")
    vehicle_ids: Optional[List[int]] = Field(None, description="Optional list of vehicle IDs to use (default: all available vehicles)")
    collection_point_ids: Optional[List[int]] = Field(None, description="Optional list of collection point IDs (default: all active points)")
    persist: bool = Field(True, description="Whether to persist generated routes and stops to database")
    time_limit_seconds: int = Field(5, ge=1, le=60, description="Max OR-Tools solver duration in seconds")


class ReoptimizeRequest(BaseModel):
    vehicle_ids: Optional[List[int]] = Field(None, description="Optional list of vehicle IDs to use")
    time_limit_seconds: int = Field(5, ge=1, le=60, description="Max OR-Tools solver duration in seconds")


class OptimizationRunSummaryResponse(BaseModel):
    id: int
    created_at: datetime
    number_of_vehicles: int
    number_of_collection_points: int
    total_distance_before: Optional[float] = None
    total_distance_after: Optional[float] = None
    total_duration_before: Optional[float] = None
    total_duration_after: Optional[float] = None
    waste_collected: float
    distance_saved_percentage: Optional[float] = None
    time_saved_percentage: Optional[float] = None
    status: OptimizationStatus
    routes_count: int

    model_config = ConfigDict(from_attributes=True)


class OptimizationRunDetailResponse(BaseModel):
    id: Optional[int] = None
    created_at: datetime
    status: OptimizationStatus
    optimization_status_code: str
    number_of_vehicles: int
    number_of_collection_points: int
    total_distance_before: Optional[float] = None
    total_distance_after: Optional[float] = None
    total_duration_before: Optional[float] = None
    total_duration_after: Optional[float] = None
    waste_collected: float
    distance_saved_percentage: Optional[float] = None
    time_saved_percentage: Optional[float] = None
    fleet_utilization_percentage: float
    routes: List[RouteResponse] = []
    unassigned_points: List[UnassignedPoint] = []
    warnings: List[str] = []

    model_config = ConfigDict(from_attributes=True)
