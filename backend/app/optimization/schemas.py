from typing import List, Optional
from pydantic import BaseModel, Field


class DepotNode(BaseModel):
    id: Optional[int] = 1
    name: str = "Central Depot"
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)


class CollectionPointNode(BaseModel):
    id: int
    name: str
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    estimated_waste_kg: float = Field(..., ge=0.0)
    priority_score: float = Field(default=50.0, ge=0.0)


class VehicleNode(BaseModel):
    id: int
    vehicle_number: str
    capacity_kg: float = Field(..., gt=0.0)


class OptimizationInput(BaseModel):
    depot: DepotNode
    collection_points: List[CollectionPointNode]
    vehicles: List[VehicleNode]
    distance_matrix_km: Optional[List[List[float]]] = None
    duration_matrix_min: Optional[List[List[float]]] = None
    time_limit_seconds: int = Field(default=5, ge=1, le=60)


class RouteStop(BaseModel):
    sequence_number: int
    point_id: Optional[int] = None  # None for depot
    name: str
    latitude: float
    longitude: float
    waste_kg: float
    accumulated_waste_kg: float
    accumulated_distance_km: float
    estimated_arrival_minutes: float


class VehicleRoute(BaseModel):
    vehicle_id: int
    vehicle_number: str
    capacity_kg: float
    stops: List[RouteStop]
    total_distance_km: float
    total_duration_minutes: float
    total_waste_kg: float
    utilization_percentage: float


class UnassignedPoint(BaseModel):
    point_id: int
    name: str
    estimated_waste_kg: float
    priority_score: float
    reason: str


class OptimizationOutput(BaseModel):
    status: str  # OPTIMAL, FEASIBLE, INSUFFICIENT_CAPACITY, NO_VEHICLES_AVAILABLE, NO_COLLECTION_POINTS, NO_SOLUTION
    routes: List[VehicleRoute]
    unassigned_points: List[UnassignedPoint]
    total_distance_km: float
    total_duration_minutes: float
    total_waste_collected_kg: float
    fleet_utilization_percentage: float
    warnings: List[str] = []
