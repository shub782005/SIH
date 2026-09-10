from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from app.models.enums import FailureReason


class CollectionCreateRequest(BaseModel):
    route_stop_id: int = Field(..., description="ID of the RouteStop being collected")
    actual_quantity_kg: float = Field(..., ge=0.0, description="Actual measured plastic waste in kg")
    proof_image_url: Optional[str] = Field(None, description="Uploaded proof photo URL")
    remarks: Optional[str] = Field(None, description="Optional driver notes or observations")


class CollectionFailRequest(BaseModel):
    route_stop_id: int = Field(..., description="ID of the RouteStop")
    failure_reason: FailureReason = Field(..., description="Reason why collection could not occur")
    remarks: Optional[str] = Field(None, description="Detailed explanation of failure")


class CollectionResponse(BaseModel):
    id: int
    route_stop_id: int
    expected_quantity_kg: float
    actual_quantity_kg: float
    collection_time: datetime
    verification_status: str
    proof_image_url: Optional[str] = None
    failure_reason: Optional[FailureReason] = None
    remarks: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ProofUploadResponse(BaseModel):
    url: str
    filename: str
    message: str = "Proof photo uploaded successfully"
