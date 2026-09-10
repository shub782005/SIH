from fastapi import APIRouter, Depends, status
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.routing import (
    MatrixRequest,
    MatrixResponse,
    RouteGeometryRequest,
    RouteGeometryResponse,
)
from app.services.osrm_service import osrm_service

router = APIRouter(prefix="/routing", tags=["OSRM Routing Service"])


@router.post("/matrix", response_model=MatrixResponse, status_code=status.HTTP_200_OK)
def get_distance_duration_matrix(
    payload: MatrixRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Calculate road distance matrix (km) and travel duration matrix (minutes)
    for a list of coordinates using OSRM Table API, with automatic Haversine fallback.
    """
    coords = [(loc.latitude, loc.longitude) for loc in payload.locations]
    dist_matrix, dur_matrix, is_fallback, source = osrm_service.get_table_matrix(coords)
    
    return MatrixResponse(
        distance_matrix_km=dist_matrix,
        duration_matrix_min=dur_matrix,
        is_fallback=is_fallback,
        source=source
    )


@router.post("/route", response_model=RouteGeometryResponse, status_code=status.HTTP_200_OK)
def get_route_geometry(
    payload: RouteGeometryRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Get detailed road distance, duration, and road geometry coordinates [lat, lon]
    for an ordered sequence of waypoints using OSRM Route API, with Haversine fallback.
    """
    waypoints = [(wp.latitude, wp.longitude) for wp in payload.waypoints]
    result = osrm_service.get_route_geometry(waypoints)

    return RouteGeometryResponse(
        distance_km=result["distance_km"],
        duration_minutes=result["duration_minutes"],
        geometry_coordinates=result["geometry_coordinates"],
        is_fallback=result["is_fallback"],
        source=result["source"]
    )
