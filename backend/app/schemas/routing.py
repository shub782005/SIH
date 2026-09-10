from typing import List, Optional
from pydantic import BaseModel, Field, field_validator

class LocationInput(BaseModel):
    latitude: float = Field(..., description="Latitude coordinate between -90 and 90")
    longitude: float = Field(..., description="Longitude coordinate between -180 and 180")
    name: Optional[str] = Field(None, description="Optional label for the point")

    @field_validator("latitude")
    @classmethod
    def validate_latitude(cls, v: float) -> float:
        if not (-90.0 <= v <= 90.0):
            raise ValueError("Latitude must be between -90.0 and 90.0 degrees")
        return v

    @field_validator("longitude")
    @classmethod
    def validate_longitude(cls, v: float) -> float:
        if not (-180.0 <= v <= 180.0):
            raise ValueError("Longitude must be between -180.0 and 180.0 degrees")
        return v


class MatrixRequest(BaseModel):
    locations: List[LocationInput] = Field(..., min_length=1, description="List of location coordinates")


class MatrixResponse(BaseModel):
    distance_matrix_km: List[List[float]]
    duration_matrix_min: List[List[float]]
    is_fallback: bool
    source: str


class RouteGeometryRequest(BaseModel):
    waypoints: List[LocationInput] = Field(..., min_length=1, description="Ordered sequence of route waypoints")


class RouteGeometryResponse(BaseModel):
    distance_km: float
    duration_minutes: float
    geometry_coordinates: List[List[float]]  # List of [lat, lon] tuples
    is_fallback: bool
    source: str
