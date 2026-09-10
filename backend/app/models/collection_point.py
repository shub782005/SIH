from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, Enum as SQLEnum, DateTime
from sqlalchemy.orm import relationship
from app.database.base import Base
from app.models.enums import WasteType, PriorityLevel

class CollectionPoint(Base):
    __tablename__ = "collection_points"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    address = Column(String(255), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    estimated_waste_kg = Column(Float, nullable=False, default=0.0)
    waste_type = Column(SQLEnum(WasteType), default=WasteType.PET, nullable=False)
    priority = Column(SQLEnum(PriorityLevel), default=PriorityLevel.MEDIUM, nullable=False)
    last_collection_date = Column(DateTime, nullable=True)
    overflow_status = Column(Boolean, default=False, nullable=False)
    status = Column(String(20), default="ACTIVE", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    waste_records = relationship("WasteRecord", back_populates="collection_point", cascade="all, delete-orphan")
    route_stops = relationship("RouteStop", back_populates="collection_point")
