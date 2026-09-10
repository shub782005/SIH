from datetime import date, datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload

from app.database.session import get_db
from app.api.deps import get_current_user, require_roles
from app.models import Route, RouteStop, Vehicle, Driver, User
from app.models.enums import RouteStatus, UserRole
from app.schemas.route import (
    RouteResponse,
    RouteStopResponse,
    RouteStatusUpdateRequest,
    RouteAssignRequest,
)

router = APIRouter(prefix="/routes", tags=["Route Management"])


def _map_route_to_response(r: Route) -> RouteResponse:
    v = r.vehicle
    driver_id = v.driver.id if v and v.driver else None
    driver_name = v.driver.user.name if v and v.driver and v.driver.user else None

    stops_list = [
        RouteStopResponse(
            id=s.id,
            route_id=r.id,
            collection_point_id=s.collection_point_id,
            point_name=s.collection_point.name if s.collection_point else "Collection Point",
            point_address=s.collection_point.address if s.collection_point else "",
            latitude=s.collection_point.latitude if s.collection_point else 0.0,
            longitude=s.collection_point.longitude if s.collection_point else 0.0,
            estimated_waste_kg=s.collection_point.estimated_waste_kg if s.collection_point else 0.0,
            waste_type=s.collection_point.waste_type if s.collection_point else "MIXED_PLASTIC",
            priority=s.collection_point.priority if s.collection_point else "MEDIUM",
            sequence_number=s.sequence_number,
            estimated_arrival_time=s.estimated_arrival_time,
            actual_arrival_time=s.actual_arrival_time,
            status=s.status,
        )
        for s in r.stops
    ]

    return RouteResponse(
        id=r.id,
        route_date=r.route_date,
        vehicle_id=r.vehicle_id,
        vehicle_number=v.vehicle_number if v else f"Vehicle #{r.vehicle_id}",
        driver_id=driver_id,
        driver_name=driver_name,
        total_distance_km=r.total_distance_km,
        estimated_duration_minutes=r.estimated_duration_minutes,
        total_waste_kg=r.total_waste_kg,
        utilization_percentage=r.utilization_percentage,
        status=r.status,
        optimization_run_id=r.optimization_run_id,
        geometry_geojson=r.geometry_geojson,
        created_at=r.created_at,
        updated_at=r.updated_at,
        stops=stops_list,
    )


@router.get("", response_model=List[RouteResponse], status_code=status.HTTP_200_OK)
def list_routes(
    route_date: Optional[date] = Query(None, description="Filter routes by calendar date"),
    vehicle_id: Optional[int] = Query(None, description="Filter by vehicle ID"),
    driver_id: Optional[int] = Query(None, description="Filter by driver ID"),
    status: Optional[RouteStatus] = Query(None, description="Filter by route status"),
    optimization_run_id: Optional[int] = Query(None, description="Filter by optimization run ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List collection routes with optional query filters.
    """
    query = (
        db.query(Route)
        .options(
            joinedload(Route.vehicle).joinedload(Vehicle.driver).joinedload(Driver.user),
            joinedload(Route.stops).joinedload(RouteStop.collection_point),
        )
    )

    # Drivers can only see their own assigned routes
    if current_user.role == UserRole.DRIVER:
        if current_user.driver_profile:
            query = query.join(Vehicle).filter(Vehicle.driver_id == current_user.driver_profile.id)
        else:
            return []

    if route_date:
        query = query.filter(Route.route_date == route_date)
    if vehicle_id:
        query = query.filter(Route.vehicle_id == vehicle_id)
    if driver_id:
        query = query.join(Vehicle).filter(Vehicle.driver_id == driver_id)
    if status:
        query = query.filter(Route.status == status)
    if optimization_run_id:
        query = query.filter(Route.optimization_run_id == optimization_run_id)

    routes = query.order_by(Route.created_at.desc()).offset(skip).limit(limit).all()
    return [_map_route_to_response(r) for r in routes]


@router.get("/{id}", response_model=RouteResponse, status_code=status.HTTP_200_OK)
def get_route(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get detailed route information by ID including ordered stops and polyline geometry.
    """
    route = (
        db.query(Route)
        .options(
            joinedload(Route.vehicle).joinedload(Vehicle.driver).joinedload(Driver.user),
            joinedload(Route.stops).joinedload(RouteStop.collection_point),
        )
        .filter(Route.id == id)
        .first()
    )

    if not route:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Route with ID {id} not found.",
        )

    # Driver role check
    if current_user.role == UserRole.DRIVER:
        if (
            not current_user.driver_profile
            or not route.vehicle
            or route.vehicle.driver_id != current_user.driver_profile.id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to view this route.",
            )

    return _map_route_to_response(route)


@router.put("/{id}/status", response_model=RouteResponse, status_code=status.HTTP_200_OK)
def update_route_status(
    id: int,
    payload: RouteStatusUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update route lifecycle status (PLANNED, ASSIGNED, STARTED, IN_PROGRESS, COMPLETED, CANCELLED).
    """
    route = (
        db.query(Route)
        .options(
            joinedload(Route.vehicle).joinedload(Vehicle.driver).joinedload(Driver.user),
            joinedload(Route.stops).joinedload(RouteStop.collection_point),
        )
        .filter(Route.id == id)
        .first()
    )

    if not route:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Route with ID {id} not found.",
        )

    # Drivers can only update their own route status
    if current_user.role == UserRole.DRIVER:
        if (
            not current_user.driver_profile
            or not route.vehicle
            or route.vehicle.driver_id != current_user.driver_profile.id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to modify this route.",
            )

    route.status = payload.status
    route.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(route)

    return _map_route_to_response(route)


@router.put("/{id}/assign", response_model=RouteResponse, status_code=status.HTTP_200_OK)
def assign_route(
    id: int,
    payload: RouteAssignRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.MANAGER])),
):
    """
    Assign or reassign a vehicle/driver to a route.
    """
    route = (
        db.query(Route)
        .options(
            joinedload(Route.vehicle).joinedload(Vehicle.driver).joinedload(Driver.user),
            joinedload(Route.stops).joinedload(RouteStop.collection_point),
        )
        .filter(Route.id == id)
        .first()
    )

    if not route:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Route with ID {id} not found.",
        )

    if payload.vehicle_id:
        vehicle = db.query(Vehicle).filter(Vehicle.id == payload.vehicle_id).first()
        if not vehicle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Vehicle with ID {payload.vehicle_id} not found.",
            )
        route.vehicle_id = payload.vehicle_id

    if payload.driver_id and route.vehicle:
        driver = db.query(Driver).filter(Driver.id == payload.driver_id).first()
        if not driver:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Driver with ID {payload.driver_id} not found.",
            )
        route.vehicle.driver_id = payload.driver_id

    if route.status == RouteStatus.PLANNED:
        route.status = RouteStatus.ASSIGNED

    route.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(route)

    return _map_route_to_response(route)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_route(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.MANAGER])),
):
    """
    Delete a planned route.
    """
    route = db.query(Route).filter(Route.id == id).first()
    if not route:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Route with ID {id} not found.",
        )

    db.delete(route)
    db.commit()
    return None
