from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.database.base import Base
from app.models.enums import FailureReason

class Collection(Base):
    __tablename__ = "collections"

    id = Column(Integer, primary_key=True, index=True)
    route_stop_id = Column(Integer, ForeignKey("route_stops.id", ondelete="CASCADE"), nullable=False, unique=True)
    expected_quantity_kg = Column(Float, nullable=False)
    actual_quantity_kg = Column(Float, nullable=False, default=0.0)
    collection_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    verification_status = Column(String(30), default="VERIFIED", nullable=False)
    proof_image_url = Column(String(255), nullable=True)
    failure_reason = Column(SQLEnum(FailureReason), nullable=True)
    remarks = Column(Text, nullable=True)

    route_stop = relationship("RouteStop", back_populates="collection_record")
