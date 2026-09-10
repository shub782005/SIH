from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database.session import get_db
from app.models.driver import Driver
from app.models.vehicle import Vehicle
from app.models.enums import DriverStatus, UserRole
from app.schemas.driver import DriverCreate, DriverUpdate, DriverResponse
from app.api.deps import get_current_user, require_roles

router = APIRouter(prefix="/drivers", tags=["Driver Management"])


@router.get("", response_model=List[DriverResponse])
def list_drivers(
    search: Optional[str] = None,
    driver_status: Optional[DriverStatus] = None,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles([UserRole.ADMIN, UserRole.MANAGER, UserRole.DRIVER])),
):
    query = db.query(Driver)
    if search:
        pattern = f"%{search}%"
        query = query.filter(
            or_(Driver.license_number.ilike(pattern), Driver.phone.ilike(pattern))
        )
    if driver_status:
        query = query.filter(Driver.status == driver_status)
    return [DriverResponse.model_validate(d) for d in query.all()]


@router.post("", response_model=DriverResponse, status_code=status.HTTP_201_CREATED)
def create_driver(
    driver_in: DriverCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles([UserRole.ADMIN, UserRole.MANAGER])),
):
    # Prevent duplicate driver profile for same user
    existing = db.query(Driver).filter(Driver.user_id == driver_in.user_id).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A driver profile already exists for user_id={driver_in.user_id}",
        )
    driver = Driver(
        user_id=driver_in.user_id,
        license_number=driver_in.license_number,
        phone=driver_in.phone,
        status=driver_in.status,
    )
    db.add(driver)
    db.commit()
    db.refresh(driver)
    return DriverResponse.model_validate(driver)


@router.get("/{driver_id}", response_model=DriverResponse)
def get_driver(
    driver_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    driver = db.query(Driver).filter(Driver.id == driver_id).first()
    if not driver:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Driver not found")
    return DriverResponse.model_validate(driver)


@router.put("/{driver_id}", response_model=DriverResponse)
def update_driver(
    driver_id: int,
    driver_in: DriverUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles([UserRole.ADMIN, UserRole.MANAGER])),
):
    driver = db.query(Driver).filter(Driver.id == driver_id).first()
    if not driver:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Driver not found")
    for field, value in driver_in.model_dump(exclude_unset=True).items():
        setattr(driver, field, value)
    db.commit()
    db.refresh(driver)
    return DriverResponse.model_validate(driver)


@router.delete("/{driver_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_driver(
    driver_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles([UserRole.ADMIN])),
):
    driver = db.query(Driver).filter(Driver.id == driver_id).first()
    if not driver:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Driver not found")
    db.delete(driver)
    db.commit()
    return None
