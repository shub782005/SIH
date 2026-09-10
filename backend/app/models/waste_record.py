from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.base import Base

class WasteRecord(Base):
    __tablename__ = "waste_records"

    id = Column(Integer, primary_key=True, index=True)
    collection_point_id = Column(Integer, ForeignKey("collection_points.id", ondelete="CASCADE"), nullable=False)
    estimated_quantity_kg = Column(Float, nullable=False)
    actual_quantity_kg = Column(Float, nullable=True)
    recorded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    source = Column(String(50), default="ESTIMATE", nullable=False)

    collection_point = relationship("CollectionPoint", back_populates="waste_records")
