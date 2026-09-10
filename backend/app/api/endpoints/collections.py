import os
import uuid
import shutil
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session, joinedload

from app.config import settings
from app.database.session import get_db
from app.api.deps import get_current_user, require_roles
from app.models import (
    Route,
    RouteStop,
    Collection,
    CollectionPoint,
    WasteRecord,
    Vehicle,
    Driver,
    User,
)
from app.models.enums import RouteStatus, StopStatus, UserRole, PriorityLevel
from app.schemas.collection import (
    CollectionCreateRequest,
    CollectionFailRequest,
    CollectionResponse,
    ProofUploadResponse,
)
from app.schemas.route import RouteResponse, RouteStopResponse
from app.services.priority_service import calculate_collection_point_priority

router = APIRouter(tags=["Driver Collection Execution"])


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


def _check_and_complete_route_if_finished(route: Route, db: Session):
    """If all stops are in terminal states, mark route completed."""
    all_stops = db.query(RouteStop).filter(RouteStop.route_id == route.id).all()
    if all_stops and all(s.status in [StopStatus.COLLECTED, StopStatus.SKIPPED, StopStatus.FAILED] for s in all_stops):
        route.status = RouteStatus.COMPLETED
        route.updated_at = datetime.utcnow()
        db.commit()


@router.get("/driver/my-route", response_model=Optional[RouteResponse], status_code=status.HTTP_200_OK)
def get_driver_active_route(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get the currently active assigned collection route for the authenticated driver.
    """
    if current_user.role != UserRole.DRIVER or not current_user.driver_profile:
        # For Admin/Manager testing, return the first active route if available
        if current_user.role in [UserRole.ADMIN, UserRole.MANAGER]:
            route = (
                db.query(Route)
                .options(
                    joinedload(Route.vehicle).joinedload(Vehicle.driver).joinedload(Driver.user),
                    joinedload(Route.stops).joinedload(RouteStop.collection_point),
                )
                .filter(Route.status.in_([RouteStatus.PLANNED, RouteStatus.ASSIGNED, RouteStatus.STARTED, RouteStatus.IN_PROGRESS]))
                .order_by(Route.created_at.desc())
                .first()
            )
            return _map_route_to_response(route) if route else None
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Driver profile not found.",
        )

    driver = current_user.driver_profile
    vehicle = db.query(Vehicle).filter(Vehicle.driver_id == driver.id).first()
    if not vehicle:
        return None

    route = (
        db.query(Route)
        .options(
            joinedload(Route.vehicle).joinedload(Vehicle.driver).joinedload(Driver.user),
            joinedload(Route.stops).joinedload(RouteStop.collection_point),
        )
        .filter(
            Route.vehicle_id == vehicle.id,
            Route.status.in_([RouteStatus.ASSIGNED, RouteStatus.STARTED, RouteStatus.IN_PROGRESS, RouteStatus.PLANNED]),
        )
        .order_by(Route.created_at.desc())
        .first()
    )

    if not route:
        return None

    return _map_route_to_response(route)


@router.post("/collections/arrive/{stop_id}", response_model=RouteStopResponse, status_code=status.HTTP_200_OK)
def mark_arrival_at_stop(
    stop_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Mark driver arrival at a collection point stop.
    """
    stop = (
        db.query(RouteStop)
        .options(joinedload(RouteStop.route).joinedload(Route.vehicle), joinedload(RouteStop.collection_point))
        .filter(RouteStop.id == stop_id)
        .first()
    )

    if not stop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Route stop with ID {stop_id} not found.",
        )

    # Transition stop status
    stop.status = StopStatus.ARRIVED
    stop.actual_arrival_time = datetime.utcnow()

    # If route was PLANNED or ASSIGNED, transition to STARTED / IN_PROGRESS
    if stop.route.status in [RouteStatus.PLANNED, RouteStatus.ASSIGNED]:
        stop.route.status = RouteStatus.STARTED
        stop.route.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(stop)

    cp = stop.collection_point
    return RouteStopResponse(
        id=stop.id,
        route_id=stop.route_id,
        collection_point_id=stop.collection_point_id,
        point_name=cp.name if cp else "Point",
        point_address=cp.address if cp else "",
        latitude=cp.latitude if cp else 0.0,
        longitude=cp.longitude if cp else 0.0,
        estimated_waste_kg=cp.estimated_waste_kg if cp else 0.0,
        waste_type=cp.waste_type if cp else "MIXED_PLASTIC",
        priority=cp.priority if cp else "MEDIUM",
        sequence_number=stop.sequence_number,
        estimated_arrival_time=stop.estimated_arrival_time,
        actual_arrival_time=stop.actual_arrival_time,
        status=stop.status,
    )


@router.post("/collections/complete", response_model=CollectionResponse, status_code=status.HTTP_201_CREATED)
def complete_collection(
    payload: CollectionCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Record verified plastic waste collection quantity, attach optional proof photo, and advance route.
    """
    stop = (
        db.query(RouteStop)
        .options(joinedload(RouteStop.route), joinedload(RouteStop.collection_point))
        .filter(RouteStop.id == payload.route_stop_id)
        .first()
    )

    if not stop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Route stop with ID {payload.route_stop_id} not found.",
        )

    cp = stop.collection_point
    now = datetime.utcnow()
    pre_pickup_estimated_waste_kg = cp.estimated_waste_kg if cp else 0.0

    # 1. Create Collection Record
    collection = Collection(
        route_stop_id=stop.id,
        expected_quantity_kg=pre_pickup_estimated_waste_kg,
        actual_quantity_kg=payload.actual_quantity_kg,
        collection_time=now,
        verification_status="VERIFIED",
        proof_image_url=payload.proof_image_url,
        remarks=payload.remarks,
    )
    db.add(collection)

    # 2. Update RouteStop Status
    stop.status = StopStatus.COLLECTED
    if not stop.actual_arrival_time:
        stop.actual_arrival_time = now

    # 3. Update CollectionPoint state & waste records
    if cp:
        # Reduce the point's outstanding estimated waste by what was actually
        # picked up (floored at 0) instead of leaving it at its pre-pickup
        # value. Previously this field was never updated on collection, so it
        # permanently overstated how much waste was still at the point —
        # which silently disagreed with the priority level computed below
        # (which assumed the point was fully emptied) every time something
        # else (e.g. the collection-points list/detail endpoints) recomputed
        # priority live from this same field.
        cp.estimated_waste_kg = max(0.0, pre_pickup_estimated_waste_kg - payload.actual_quantity_kg)
        cp.last_collection_date = now
        cp.overflow_status = False
        # Calculate new priority level & score after pickup, using the point's
        # actual remaining waste rather than an assumed value.
        new_prio, _ = calculate_collection_point_priority(
            estimated_waste_kg=cp.estimated_waste_kg,
            waste_type=cp.waste_type,
            last_collection_date=now,
            overflow_status=False,
        )
        cp.priority = new_prio

        # Log permanent waste record (historical estimate vs. what was
        # actually verified at pickup time)
        waste_record = WasteRecord(
            collection_point_id=cp.id,
            estimated_quantity_kg=pre_pickup_estimated_waste_kg,
            actual_quantity_kg=payload.actual_quantity_kg,
            recorded_at=now,
            source="COLLECTION_VERIFIED",
        )
        db.add(waste_record)

    db.commit()
    db.refresh(collection)

    # 4. Check if route is completed
    _check_and_complete_route_if_finished(stop.route, db)

    return CollectionResponse(
        id=collection.id,
        route_stop_id=collection.route_stop_id,
        expected_quantity_kg=collection.expected_quantity_kg,
        actual_quantity_kg=collection.actual_quantity_kg,
        collection_time=collection.collection_time,
        verification_status=collection.verification_status,
        proof_image_url=collection.proof_image_url,
        failure_reason=None,
        remarks=collection.remarks,
    )


@router.post("/collections/fail", response_model=CollectionResponse, status_code=status.HTTP_201_CREATED)
def report_collection_failure(
    payload: CollectionFailRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Report an issue or failure to collect plastic waste at a stop with a structured reason.
    """
    stop = (
        db.query(RouteStop)
        .options(joinedload(RouteStop.route), joinedload(RouteStop.collection_point))
        .filter(RouteStop.id == payload.route_stop_id)
        .first()
    )

    if not stop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Route stop with ID {payload.route_stop_id} not found.",
        )

    cp = stop.collection_point
    now = datetime.utcnow()

    collection = Collection(
        route_stop_id=stop.id,
        expected_quantity_kg=cp.estimated_waste_kg if cp else 0.0,
        actual_quantity_kg=0.0,
        collection_time=now,
        verification_status="FAILED",
        failure_reason=payload.failure_reason,
        remarks=payload.remarks,
    )
    db.add(collection)

    stop.status = StopStatus.FAILED
    db.commit()
    db.refresh(collection)

    _check_and_complete_route_if_finished(stop.route, db)

    return CollectionResponse(
        id=collection.id,
        route_stop_id=collection.route_stop_id,
        expected_quantity_kg=collection.expected_quantity_kg,
        actual_quantity_kg=collection.actual_quantity_kg,
        collection_time=collection.collection_time,
        verification_status=collection.verification_status,
        proof_image_url=None,
        failure_reason=collection.failure_reason,
        remarks=collection.remarks,
    )


@router.post("/collections/upload-proof", response_model=ProofUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_proof_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    """
    Upload a proof of collection photo.
    """
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    ext = os.path.splitext(file.filename)[1] or ".jpg"
    unique_filename = f"proof_{uuid.uuid4().hex[:10]}{ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return ProofUploadResponse(
        url=f"/uploads/{unique_filename}",
        filename=unique_filename,
        message="Proof photo uploaded successfully",
    )
