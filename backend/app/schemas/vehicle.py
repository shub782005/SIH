from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from app.models.enums import VehicleStatus

class VehicleBase(BaseModel):
    vehicle_number: str = Field(..., min_length=1, max_length=50)
    vehicle_type: str = Field(default="Truck", max_length=50)
    capacity_kg: float = Field(..., gt=0)
    driver_id: Optional[int] = None
    status: VehicleStatus = VehicleStatus.AVAILABLE
    current_latitude: Optional[float] = None
    current_longitude: Optional[float] = None

class VehicleCreate(VehicleBase):
    pass

class VehicleUpdate(BaseModel):
    vehicle_type: Optional[str] = None
    capacity_kg: Optional[float] = None
    driver_id: Optional[int] = None
    status: Optional[VehicleStatus] = None
    current_latitude: Optional[float] = None
    current_longitude: Optional[float] = None

class VehicleResponse(VehicleBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    updated_at: datetime
