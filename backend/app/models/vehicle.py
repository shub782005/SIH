from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Enum as SQLEnum, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.base import Base
from app.models.enums import VehicleStatus

class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_number = Column(String(50), unique=True, index=True, nullable=False)
    vehicle_type = Column(String(50), default="Truck", nullable=False)
    capacity_kg = Column(Float, nullable=False)
    driver_id = Column(Integer, ForeignKey("drivers.id", ondelete="SET NULL"), nullable=True)
    status = Column(SQLEnum(VehicleStatus), default=VehicleStatus.AVAILABLE, nullable=False)
    current_latitude = Column(Float, nullable=True)
    current_longitude = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    driver = relationship("Driver", back_populates="vehicles")
    routes = relationship("Route", back_populates="vehicle")
