import pytest
from app.database.session import SessionLocal
from app.models import (
    User, UserRole,
    Driver,
    Vehicle,
    Depot,
    CollectionPoint, WasteType, PriorityLevel
)

def test_database_seed_data():
    db = SessionLocal()
    try:
        # Verify Users
        users_count = db.query(User).count()
        assert users_count >= 7
        admin = db.query(User).filter_by(email="admin@ecoroute.org").first()
        assert admin is not None
        assert admin.role == UserRole.ADMIN

        # Verify Drivers
        drivers = db.query(Driver).all()
        assert len(drivers) == 5

        # Verify Vehicles & Driver relationships
        vehicles = db.query(Vehicle).all()
        assert len(vehicles) == 5
        for v in vehicles:
            assert v.capacity_kg > 0
            assert v.driver is not None

        # Verify Central Depot
        depot = db.query(Depot).first()
        assert depot is not None
        assert "Swargate" in depot.address or "Recycling" in depot.name
        assert 18.0 <= depot.latitude <= 19.0
        assert 73.0 <= depot.longitude <= 74.0

        # Verify Collection Points
        points = db.query(CollectionPoint).all()
        assert len(points) >= 28
        
        # Check overflow points count
        overflow_points = [p for p in points if p.overflow_status]
        assert len(overflow_points) > 0

        # Check total estimated waste demand
        total_demand = sum(p.estimated_waste_kg for p in points)
        assert total_demand > 3000.0  # Approx 7,000 kg total
    finally:
        db.close()
