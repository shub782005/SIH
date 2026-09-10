from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from app.models.enums import WasteType, PriorityLevel

class CollectionPointBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    address: str = Field(..., min_length=3, max_length=255)
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    estimated_waste_kg: float = Field(..., ge=0.0)
    waste_type: WasteType = WasteType.PET
    overflow_status: bool = False
    status: str = "ACTIVE"

class CollectionPointCreate(CollectionPointBase):
    pass

class CollectionPointUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0)
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0)
    estimated_waste_kg: Optional[float] = Field(None, ge=0.0)
    waste_type: Optional[WasteType] = None
    overflow_status: Optional[bool] = None
    status: Optional[str] = None

class CollectionPointResponse(CollectionPointBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    priority: PriorityLevel
    last_collection_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    priority_score: Optional[float] = None
