from datetime import datetime
from sqlalchemy import Column, Integer, Enum as SQLEnum, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.base import Base
from app.models.enums import StopStatus

class RouteStop(Base):
    __tablename__ = "route_stops"

    id = Column(Integer, primary_key=True, index=True)
    route_id = Column(Integer, ForeignKey("routes.id", ondelete="CASCADE"), nullable=False)
    collection_point_id = Column(Integer, ForeignKey("collection_points.id", ondelete="RESTRICT"), nullable=False)
    sequence_number = Column(Integer, nullable=False)
    estimated_arrival_time = Column(DateTime, nullable=True)
    actual_arrival_time = Column(DateTime, nullable=True)
    status = Column(SQLEnum(StopStatus), default=StopStatus.PENDING, nullable=False)

    route = relationship("Route", back_populates="stops")
    collection_point = relationship("CollectionPoint", back_populates="route_stops")
    collection_record = relationship("Collection", back_populates="route_stop", uselist=False, cascade="all, delete-orphan")
