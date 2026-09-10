from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from app.models.enums import DriverStatus

class DriverBase(BaseModel):
    user_id: int = Field(..., gt=0)
    license_number: str = Field(..., min_length=2, max_length=50)
    phone: str = Field(..., min_length=5, max_length=20)
    status: DriverStatus = DriverStatus.AVAILABLE

class DriverCreate(DriverBase):
    pass

class DriverUpdate(BaseModel):
    license_number: Optional[str] = None
    phone: Optional[str] = None
    status: Optional[DriverStatus] = None
    user_id: Optional[int] = None

class DriverResponse(DriverBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    updated_at: datetime
