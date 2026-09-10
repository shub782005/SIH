import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.osrm_service import haversine_matrix

client = TestClient(app)


@pytest.fixture
def admin_token():
    res = client.post("/api/auth/login", json={
        "email": "admin@ecoroute.org",
        "password": "Password123!"
    })
    assert res.status_code == 200
    return res.json()["access_token"]


@pytest.fixture
def driver_token():
    res = client.post("/api/auth/login", json={
        "email": "rahul@ecoroute.org",
        "password": "Password123!"
    })
    assert res.status_code == 200
    return res.json()["access_token"]


# =====================================================================
# 1. RBAC (Role-Based Access Control) Security Tests
# =====================================================================

def test_driver_denied_admin_optimization(driver_token):
    res = client.post(
        "/api/optimization/generate",
        json={"persist": False, "time_limit_seconds": 2},
        headers={"Authorization": f"Bearer {driver_token}"},
    )
    assert res.status_code == 403


def test_driver_denied_collection_point_creation(driver_token):
    res = client.post(
        "/api/collection-points",
        json={
            "name": "Unauthorized Point",
            "address": "Unauthorized Address",
            "latitude": 18.5,
            "longitude": 73.8,
            "estimated_waste_kg": 100.0,
            "waste_type": "PET",
        },
        headers={"Authorization": f"Bearer {driver_token}"},
    )
    assert res.status_code == 403


def test_driver_denied_route_deletion(driver_token):
    res = client.delete(
        "/api/routes/9999",
        headers={"Authorization": f"Bearer {driver_token}"},
    )
    assert res.status_code == 403


# =====================================================================
# 2. Authentication & Credential Security Tests
# =====================================================================

def test_invalid_password_rejected():
    res = client.post("/api/auth/login", json={
        "email": "admin@ecoroute.org",
        "password": "WrongPassword999!"
    })
    assert res.status_code == 401
    assert "invalid email or password" in res.json()["detail"].lower()


def test_nonexistent_user_login_rejected():
    res = client.post("/api/auth/login", json={
        "email": "ghost_user_does_not_exist@ecoroute.org",
        "password": "Password123!"
    })
    assert res.status_code == 401


def test_malformed_jwt_token_rejected():
    res = client.get(
        "/api/analytics/overview",
        headers={"Authorization": "Bearer invalid.fake.token123"},
    )
    assert res.status_code == 401


def test_missing_auth_header_rejected():
    res = client.get("/api/analytics/overview")
    assert res.status_code == 401


# =====================================================================
# 3. Edge Cases & Resilience Tests
# =====================================================================

def test_infeasible_demand_handled_gracefully(admin_token):
    """
    Test Rule #16: A collection point with demand > max vehicle capacity
    must be diagnosed and reported in unassigned_points without crashing.
    """
    # Create point with 10,000 kg demand (exceeds all vehicles)
    cp_res = client.post(
        "/api/collection-points",
        json={
            "name": "Massive Infeasible Industrial Depot",
            "address": "Industrial Zone",
            "latitude": 18.5204,
            "longitude": 73.8567,
            "estimated_waste_kg": 10000.0,
            "waste_type": "MIXED_PLASTIC",
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert cp_res.status_code == 201
    infeasible_cp_id = cp_res.json()["id"]

    try:
        opt_res = client.post(
            "/api/optimization/generate",
            json={
                "collection_point_ids": [infeasible_cp_id],
                "vehicle_ids": [1],  # Max capacity 1,200 kg
                "persist": False,
                "time_limit_seconds": 2,
            },
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert opt_res.status_code == 200
        data = opt_res.json()
        assert len(data["unassigned_points"]) > 0
        un = data["unassigned_points"][0]
        assert un["point_id"] == infeasible_cp_id
        assert "capacity" in un["reason"].lower()
    finally:
        client.delete(f"/api/collection-points/{infeasible_cp_id}", headers={"Authorization": f"Bearer {admin_token}"})


def test_nonexistent_entity_404_handling(admin_token):
    res_route = client.get("/api/routes/999999", headers={"Authorization": f"Bearer {admin_token}"})
    assert res_route.status_code == 404

    res_cp = client.get("/api/collection-points/999999", headers={"Authorization": f"Bearer {admin_token}"})
    assert res_cp.status_code == 404


def test_negative_collection_weight_validation(driver_token):
    res = client.post(
        "/api/collections/complete",
        json={
            "route_stop_id": 1,
            "actual_quantity_kg": -50.0,  # Invalid negative weight
        },
        headers={"Authorization": f"Bearer {driver_token}"},
    )
    assert res.status_code == 422


def test_haversine_fallback_resilience():
    origins_and_destinations = [(18.5018, 73.8636), (18.5204, 73.8567), (18.5308, 73.8290)]

    dist_matrix, dur_matrix = haversine_matrix(origins_and_destinations)
    assert len(dist_matrix) == 3
    assert len(dist_matrix[0]) == 3
    assert dist_matrix[0][0] == 0.0
    assert dist_matrix[0][1] > 0.0
    assert dur_matrix[0][1] > 0.0
