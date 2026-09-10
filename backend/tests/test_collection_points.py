import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from app.main import app
from app.models.enums import WasteType, PriorityLevel, UserRole
from app.services.priority_service import calculate_collection_point_priority

client = TestClient(app)

@pytest.fixture
def admin_token():
    res = client.post("/api/auth/login", json={
        "email": "admin@ecoroute.org",
        "password": "Password123!"
    })
    return res.json()["access_token"]

@pytest.fixture
def driver_token():
    res = client.post("/api/auth/login", json={
        "email": "rahul@ecoroute.org",
        "password": "Password123!"
    })
    return res.json()["access_token"]

def test_priority_calculation_engine_formula():
    now = datetime.utcnow()
    
    # Test 1: Overflow point -> CRITICAL
    level, score = calculate_collection_point_priority(
        estimated_waste_kg=200.0,
        waste_type=WasteType.PET,
        last_collection_date=now - timedelta(days=2),
        overflow_status=True
    )
    assert level == PriorityLevel.CRITICAL
    assert score > 50.0

    # Test 2: Low load point -> LOW or MEDIUM
    level_low, score_low = calculate_collection_point_priority(
        estimated_waste_kg=50.0,
        waste_type=WasteType.OTHER_RECYCLABLE_PLASTIC,
        last_collection_date=now - timedelta(days=1),
        overflow_status=False
    )
    assert level_low in [PriorityLevel.LOW, PriorityLevel.MEDIUM]
    assert score_low < 30.0

def test_list_collection_points():
    res = client.get("/api/collection-points")
    assert res.status_code == 200
    points = res.json()
    assert len(points) >= 30
    assert "priority_score" in points[0]

def test_search_and_filter_collection_points():
    # Filter by search string "Baner"
    res = client.get("/api/collection-points?search=Baner")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 1
    assert "Baner" in data[0]["name"] or "Baner" in data[0]["address"]

    # Filter overflow points only
    res_overflow = client.get("/api/collection-points?overflow_only=true")
    assert res_overflow.status_code == 200
    data_overflow = res_overflow.json()
    assert all(pt["overflow_status"] is True for pt in data_overflow)

def test_create_and_delete_collection_point(admin_token, driver_token):
    # Driver role attempting to create point -> 403 Forbidden
    res_forbidden = client.post(
        "/api/collection-points",
        json={
            "name": "Unauthorized Point",
            "address": "Test Street",
            "latitude": 18.5204,
            "longitude": 73.8567,
            "estimated_waste_kg": 100.0,
            "waste_type": "PET",
            "overflow_status": False
        },
        headers={"Authorization": f"Bearer {driver_token}"}
    )
    assert res_forbidden.status_code == 403

    # Admin role creating point -> 201 Created
    res_create = client.post(
        "/api/collection-points",
        json={
            "name": "New Test Bin",
            "address": "Magarpatta South Gate, Pune",
            "latitude": 18.5140,
            "longitude": 73.9250,
            "estimated_waste_kg": 340.0,
            "waste_type": "HDPE",
            "overflow_status": True
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert res_create.status_code == 201
    created_pt = res_create.json()
    assert created_pt["id"] is not None
    assert created_pt["priority"] == PriorityLevel.CRITICAL.value

    # Admin deleting created point -> 204 No Content
    point_id = created_pt["id"]
    res_del = client.delete(
        f"/api/collection-points/{point_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert res_del.status_code == 204
