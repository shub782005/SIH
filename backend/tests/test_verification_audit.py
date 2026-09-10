import os
import pytest
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker

from app.database.base import Base
from app.models import (
    User, UserRole,
    Driver, DriverStatus,
    Vehicle, VehicleStatus,
    Depot,
    CollectionPoint, WasteType, PriorityLevel,
    WasteRecord, Route, RouteStop, Collection, OptimizationRun, Notification
)
from app.core.security import get_password_hash

TEST_DB_URL = "sqlite:///./test_verification_isolated.db"

@pytest.fixture(scope="module")
def isolated_db():
    # Remove old test DB if present
    if os.path.exists("./test_verification_isolated.db"):
        os.remove("./test_verification_isolated.db")

    engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSession()

    yield session, engine

    session.close()
    engine.dispose()
    if os.path.exists("./test_verification_isolated.db"):
        try:
            os.remove("./test_verification_isolated.db")
        except OSError:
            pass

def test_isolated_schema_creation(isolated_db):
    session, engine = isolated_db
    inspector = inspect(engine)
    table_names = inspector.get_table_names()

    required_tables = [
        "users", "drivers", "vehicles", "depots",
        "collection_points", "waste_records", "routes",
        "route_stops", "collections", "notifications", "optimization_runs"
    ]

    for table in required_tables:
        assert table in table_names, f"Missing table {table} in database schema"

def test_crud_integration(isolated_db):
    session, engine = isolated_db

    # Create User & Driver
    user = User(name="Audit User", email="audit@ecoroute.org", password_hash=get_password_hash("pass123"), role=UserRole.ADMIN)
    session.add(user)
    session.commit()
    assert user.id is not None

    driver = Driver(user_id=user.id, license_number="AUDIT-123", phone="+91 99999 88888")
    session.add(driver)
    session.commit()
    assert driver.id is not None

    # Create Vehicle
    vehicle = Vehicle(vehicle_number="MH-01-AA-1111", capacity_kg=1000.0, driver_id=driver.id)
    session.add(vehicle)
    session.commit()
    assert vehicle.id is not None

    # Read & Update
    v_db = session.query(Vehicle).filter_by(vehicle_number="MH-01-AA-1111").first()
    assert v_db is not None
    assert v_db.capacity_kg == 1000.0
    v_db.capacity_kg = 1200.0
    session.commit()

    v_updated = session.query(Vehicle).filter_by(vehicle_number="MH-01-AA-1111").first()
    assert v_updated.capacity_kg == 1200.0

    # Delete
    session.delete(v_updated)
    session.commit()
    assert session.query(Vehicle).filter_by(vehicle_number="MH-01-AA-1111").first() is None

def test_coordinate_and_capacity_constraints(isolated_db):
    session, engine = isolated_db
    
    # Valid collection point
    cp = CollectionPoint(
        name="Valid Point",
        address="Test Address",
        latitude=18.5204,
        longitude=73.8567,
        estimated_waste_kg=150.0,
        waste_type=WasteType.PET,
        priority=PriorityLevel.MEDIUM
    )
    session.add(cp)
    session.commit()
    assert cp.id is not None
    assert -90.0 <= cp.latitude <= 90.0
    assert -180.0 <= cp.longitude <= 180.0
    assert cp.estimated_waste_kg >= 0.0
