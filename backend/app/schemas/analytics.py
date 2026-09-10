from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field, ConfigDict


class DailyWasteTrendItem(BaseModel):
    date: str
    waste_kg: float
    stops_count: int


class WasteByTypeItem(BaseModel):
    waste_type: str
    waste_kg: float
    percentage: float


class VehicleUtilizationItem(BaseModel):
    vehicle_number: str
    capacity_kg: float
    waste_collected_kg: float
    utilization_percentage: float
    status: str


class CollectionStats(BaseModel):
    total_waste_kg: float
    total_stops_completed: int
    avg_waste_per_point_kg: float
    waste_by_type: List[WasteByTypeItem]
    daily_trend: List[DailyWasteTrendItem]

    model_config = ConfigDict(from_attributes=True)


class RouteStats(BaseModel):
    total_distance_km: float
    total_duration_minutes: float
    avg_distance_per_route_km: float
    avg_duration_per_route_min: float
    total_routes_count: int
    completed_routes_count: int
    active_routes_count: int
    fleet_utilization_percentage: float
    vehicle_utilization: List[VehicleUtilizationItem]

    model_config = ConfigDict(from_attributes=True)


class OptimizationImpact(BaseModel):
    total_distance_before_km: float
    total_distance_after_km: float
    distance_saved_km: float
    distance_saved_percentage: float
    total_duration_before_hours: float
    total_duration_after_hours: float
    time_saved_hours: float
    time_saved_percentage: float
    estimated_fuel_saved_liters: float
    estimated_cost_saved_inr: float
    estimated_co2_avoided_kg: float
    disclaimer: str = "Estimated fuel saving calculated based on 3.5 km/L (0.28 L/km) commercial diesel fleet benchmark"

    model_config = ConfigDict(from_attributes=True)


class AnalyticsOverviewResponse(BaseModel):
    collection_stats: CollectionStats
    route_stats: RouteStats
    optimization_impact: OptimizationImpact
    summary_cards: Dict[str, Any]

    model_config = ConfigDict(from_attributes=True)
