from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, Text, Enum as SQLEnum, DateTime, ForeignKey, Date
from sqlalchemy.orm import relationship
from app.database.base import Base
from app.models.enums import RouteStatus

class Route(Base):
    __tablename__ = "routes"

    id = Column(Integer, primary_key=True, index=True)
    route_date = Column(Date, default=datetime.utcnow().date, nullable=False)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id", ondelete="CASCADE"), nullable=False)
    total_distance_km = Column(Float, nullable=False, default=0.0)
    estimated_duration_minutes = Column(Float, nullable=False, default=0.0)
    total_waste_kg = Column(Float, nullable=False, default=0.0)
    utilization_percentage = Column(Float, nullable=False, default=0.0)
    status = Column(SQLEnum(RouteStatus), default=RouteStatus.PLANNED, nullable=False)
    optimization_run_id = Column(Integer, ForeignKey("optimization_runs.id", ondelete="SET NULL"), nullable=True)
    geometry_geojson = Column(Text, nullable=True)  # Stores OSRM snapped polyline geometry as JSON string
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    vehicle = relationship("Vehicle", back_populates="routes")
    optimization_run = relationship("OptimizationRun", back_populates="routes")
    stops = relationship("RouteStop", back_populates="route", cascade="all, delete-orphan", order_by="RouteStop.sequence_number")
