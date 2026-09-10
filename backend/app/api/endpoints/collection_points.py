from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database.session import get_db
from app.models.collection_point import CollectionPoint
from app.models.route_stop import RouteStop
from app.models.waste_record import WasteRecord
from app.models.enums import UserRole, WasteType, PriorityLevel
from app.schemas.collection_point import (
    CollectionPointCreate,
    CollectionPointUpdate,
    CollectionPointResponse
)
from app.api.deps import get_current_user, require_roles
from app.services.priority_service import calculate_collection_point_priority

router = APIRouter(prefix="/collection-points", tags=["Collection Points"])

@router.get("", response_model=List[CollectionPointResponse])
def list_collection_points(
    search: Optional[str] = Query(None, description="Filter by name or address"),
    waste_type: Optional[WasteType] = Query(None, description="Filter by plastic waste type"),
    priority: Optional[PriorityLevel] = Query(None, description="Filter by priority level"),
    overflow_only: bool = Query(False, description="Filter only points with overflow_status=True"),
    db: Session = Depends(get_db)
):
    query = db.query(CollectionPoint)

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                CollectionPoint.name.ilike(search_pattern),
                CollectionPoint.address.ilike(search_pattern)
            )
        )
    
    if waste_type:
        query = query.filter(CollectionPoint.waste_type == waste_type)
    
    if overflow_only:
        query = query.filter(CollectionPoint.overflow_status == True)

    points = query.all()

    # Priority level/score are derived live from current point data rather than
    # trusted from the stored `priority` column, which is only ever written at
    # creation time (or via an explicit recalculate call) and can otherwise go
    # stale relative to the point's current waste load/overflow state. Filtering
    # by priority is therefore applied AFTER recomputation so the filter and the
    # displayed badge always agree.
    response_list = []
    for pt in points:
        calc_level, calc_score = calculate_collection_point_priority(
            estimated_waste_kg=pt.estimated_waste_kg,
            waste_type=pt.waste_type,
            last_collection_date=pt.last_collection_date,
            overflow_status=pt.overflow_status
        )

        if priority and calc_level != priority:
            continue

        # Build response item
        res_data = CollectionPointResponse.model_validate(pt)
        res_data.priority = calc_level
        res_data.priority_score = calc_score
        response_list.append(res_data)

    # Sort response list by priority score descending
    response_list.sort(key=lambda x: x.priority_score or 0.0, reverse=True)
    return response_list

@router.post("", response_model=CollectionPointResponse, status_code=status.HTTP_201_CREATED)
def create_collection_point(
    cp_in: CollectionPointCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles([UserRole.ADMIN, UserRole.MANAGER]))
):
    # Calculate priority level
    now = datetime.utcnow()
    calculated_level, calc_score = calculate_collection_point_priority(
        estimated_waste_kg=cp_in.estimated_waste_kg,
        waste_type=cp_in.waste_type,
        last_collection_date=now,
        overflow_status=cp_in.overflow_status
    )

    new_point = CollectionPoint(
        name=cp_in.name,
        address=cp_in.address,
        latitude=cp_in.latitude,
        longitude=cp_in.longitude,
        estimated_waste_kg=cp_in.estimated_waste_kg,
        waste_type=cp_in.waste_type,
        priority=calculated_level,
        overflow_status=cp_in.overflow_status,
        status=cp_in.status,
        last_collection_date=now
    )

    db.add(new_point)
    db.commit()
    db.refresh(new_point)

    res = CollectionPointResponse.model_validate(new_point)
    res.priority_score = calc_score
    return res

@router.get("/{point_id}", response_model=CollectionPointResponse)
def get_collection_point(point_id: int, db: Session = Depends(get_db)):
    cp = db.query(CollectionPoint).filter(CollectionPoint.id == point_id).first()
    if not cp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Collection Point #{point_id} not found"
        )
    
    calc_level, calc_score = calculate_collection_point_priority(
        estimated_waste_kg=cp.estimated_waste_kg,
        waste_type=cp.waste_type,
        last_collection_date=cp.last_collection_date,
        overflow_status=cp.overflow_status
    )

    res = CollectionPointResponse.model_validate(cp)
    res.priority = calc_level
    res.priority_score = calc_score
    return res

@router.put("/{point_id}", response_model=CollectionPointResponse)
def update_collection_point(
    point_id: int,
    cp_in: CollectionPointUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles([UserRole.ADMIN, UserRole.MANAGER]))
):
    cp = db.query(CollectionPoint).filter(CollectionPoint.id == point_id).first()
    if not cp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Collection Point #{point_id} not found"
        )
    
    update_data = cp_in.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(cp, field, val)

    # Recalculate priority level
    calc_level, calc_score = calculate_collection_point_priority(
        estimated_waste_kg=cp.estimated_waste_kg,
        waste_type=cp.waste_type,
        last_collection_date=cp.last_collection_date,
        overflow_status=cp.overflow_status
    )
    cp.priority = calc_level

    db.commit()
    db.refresh(cp)

    res = CollectionPointResponse.model_validate(cp)
    res.priority_score = calc_score
    return res

@router.delete("/{point_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_collection_point(
    point_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles([UserRole.ADMIN]))
):
    cp = db.query(CollectionPoint).filter(CollectionPoint.id == point_id).first()
    if not cp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Collection Point #{point_id} not found"
        )
    
    # Cascade delete route_stops and waste_records linked to this point
    db.query(RouteStop).filter(RouteStop.collection_point_id == point_id).delete(synchronize_session=False)
    db.query(WasteRecord).filter(WasteRecord.collection_point_id == point_id).delete(synchronize_session=False)
    db.delete(cp)
    db.commit()
    return None


@router.post("/{point_id}/recalculate-priority", response_model=CollectionPointResponse)
def recalculate_priority(
    point_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles([UserRole.ADMIN, UserRole.MANAGER]))
):
    cp = db.query(CollectionPoint).filter(CollectionPoint.id == point_id).first()
    if not cp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Collection Point #{point_id} not found"
        )
    
    calc_level, calc_score = calculate_collection_point_priority(
        estimated_waste_kg=cp.estimated_waste_kg,
        waste_type=cp.waste_type,
        last_collection_date=cp.last_collection_date,
        overflow_status=cp.overflow_status
    )
    cp.priority = calc_level
    db.commit()
    db.refresh(cp)

    res = CollectionPointResponse.model_validate(cp)
    res.priority_score = calc_score
    return res
