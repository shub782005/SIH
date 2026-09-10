from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database.session import get_db
from app.models.vehicle import Vehicle
from app.models.driver import Driver
from app.models.enums import VehicleStatus, UserRole
from app.schemas.vehicle import VehicleCreate, VehicleUpdate, VehicleResponse
from app.api.deps import get_current_user, require_roles

router = APIRouter(prefix="/vehicles", tags=["Vehicle Fleet"])


@router.get("", response_model=List[VehicleResponse])
def list_vehicles(
    search: Optional[str] = None,
    vehicle_status: Optional[VehicleStatus] = None,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles([UserRole.ADMIN, UserRole.MANAGER, UserRole.DRIVER])),
):
    query = db.query(Vehicle)
    if search:
        pattern = f"%{search}%"
        query = query.filter(
            or_(Vehicle.vehicle_number.ilike(pattern), Vehicle.vehicle_type.ilike(pattern))
        )
    if vehicle_status:
        query = query.filter(Vehicle.status == vehicle_status)
    return [VehicleResponse.model_validate(v) for v in query.all()]


@router.post("", response_model=VehicleResponse, status_code=status.HTTP_201_CREATED)
def create_vehicle(
    vehicle_in: VehicleCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles([UserRole.ADMIN, UserRole.MANAGER])),
):
    # Validate capacity
    if vehicle_in.capacity_kg <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Vehicle capacity must be positive",
        )
    # Check unique vehicle number
    existing = db.query(Vehicle).filter(Vehicle.vehicle_number == vehicle_in.vehicle_number).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Vehicle number '{vehicle_in.vehicle_number}' already exists",
        )
    # Validate driver_id if provided
    if vehicle_in.driver_id is not None:
        driver = db.query(Driver).filter(Driver.id == vehicle_in.driver_id).first()
        if not driver:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Driver id={vehicle_in.driver_id} not found",
            )
    vehicle = Vehicle(
        vehicle_number=vehicle_in.vehicle_number,
        vehicle_type=vehicle_in.vehicle_type,
        capacity_kg=vehicle_in.capacity_kg,
        driver_id=vehicle_in.driver_id,
        status=vehicle_in.status,
        current_latitude=vehicle_in.current_latitude,
        current_longitude=vehicle_in.current_longitude,
    )
    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)
    return VehicleResponse.model_validate(vehicle)


@router.get("/{vehicle_id}", response_model=VehicleResponse)
def get_vehicle(
    vehicle_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found")
    return VehicleResponse.model_validate(vehicle)


@router.put("/{vehicle_id}", response_model=VehicleResponse)
def update_vehicle(
    vehicle_id: int,
    vehicle_in: VehicleUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles([UserRole.ADMIN, UserRole.MANAGER])),
):
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found")
    # Validate driver_id if being updated
    update_data = vehicle_in.model_dump(exclude_unset=True)
    if "driver_id" in update_data and update_data["driver_id"] is not None:
        driver = db.query(Driver).filter(Driver.id == update_data["driver_id"]).first()
        if not driver:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Driver id={update_data['driver_id']} not found",
            )
    for field, value in update_data.items():
        setattr(vehicle, field, value)
    db.commit()
    db.refresh(vehicle)
    return VehicleResponse.model_validate(vehicle)


@router.post("/{vehicle_id}/assign-driver", response_model=VehicleResponse)
def assign_driver_to_vehicle(
    vehicle_id: int,
    driver_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles([UserRole.ADMIN, UserRole.MANAGER])),
):
    """Assign a driver to a vehicle. Pass driver_id=0 to unassign."""
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found")
    if driver_id == 0:
        vehicle.driver_id = None
    else:
        driver = db.query(Driver).filter(Driver.id == driver_id).first()
        if not driver:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Driver not found")
        vehicle.driver_id = driver_id
    db.commit()
    db.refresh(vehicle)
    return VehicleResponse.model_validate(vehicle)


@router.delete("/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vehicle(
    vehicle_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles([UserRole.ADMIN])),
):
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found")
    db.delete(vehicle)
    db.commit()
    return None
