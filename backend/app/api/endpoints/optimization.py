from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.api.deps import get_current_user, require_roles
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.optimization import (
    OptimizationGenerateRequest,
    OptimizationRunSummaryResponse,
    OptimizationRunDetailResponse,
    ReoptimizeRequest,
)
from app.services.optimization_service import optimization_service

router = APIRouter(prefix="/optimization", tags=["Route Optimization Engine"])


@router.post(
    "/generate",
    response_model=OptimizationRunDetailResponse,
    status_code=status.HTTP_200_OK,
)
def generate_optimization_routes(
    payload: OptimizationGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.MANAGER])),
):
    """
    Generate capacity-aware optimized collection routes using Google OR-Tools CVRP
    and OSRM road geometry, with optional database persistence.
    """
    return optimization_service.generate_and_persist_optimization(db, payload)


@router.get(
    "",
    response_model=List[OptimizationRunSummaryResponse],
    status_code=status.HTTP_200_OK,
)
def list_optimization_runs(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List optimization runs history with summary statistics.
    """
    return optimization_service.list_optimization_runs(db, skip=skip, limit=limit)


@router.get(
    "/{id}",
    response_model=OptimizationRunDetailResponse,
    status_code=status.HTTP_200_OK,
)
def get_optimization_run(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get detailed breakdown of an optimization run by ID, including routes, stops, and road geometry.
    """
    return optimization_service.get_optimization_run_by_id(db, run_id=id)


@router.post(
    "/{id}/reoptimize",
    response_model=OptimizationRunDetailResponse,
    status_code=status.HTTP_200_OK,
)
def reoptimize_run(
    id: int,
    payload: ReoptimizeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.MANAGER])),
):
    """
    Re-optimize remaining pending collection stops from an active optimization run.
    """
    return optimization_service.reoptimize_run(db, run_id=id, request=payload)
