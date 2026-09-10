from datetime import datetime
from sqlalchemy import Column, Integer, Float, Enum as SQLEnum, DateTime
from sqlalchemy.orm import relationship
from app.database.base import Base
from app.models.enums import OptimizationStatus

class OptimizationRun(Base):
    __tablename__ = "optimization_runs"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    number_of_vehicles = Column(Integer, nullable=False)
    number_of_collection_points = Column(Integer, nullable=False)
    total_distance_before = Column(Float, nullable=True)
    total_distance_after = Column(Float, nullable=True)
    total_duration_before = Column(Float, nullable=True)
    total_duration_after = Column(Float, nullable=True)
    waste_collected = Column(Float, nullable=False, default=0.0)
    distance_saved_percentage = Column(Float, nullable=True)
    time_saved_percentage = Column(Float, nullable=True)
    status = Column(SQLEnum(OptimizationStatus), default=OptimizationStatus.SUCCESS, nullable=False)

    routes = relationship("Route", back_populates="optimization_run")
