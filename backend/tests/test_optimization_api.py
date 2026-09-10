import pytest
from fastapi.testclient import TestClient
from app.main import app

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


def test_optimization_generate_requires_auth():
    res = client.post("/api/optimization/generate", json={})
    assert res.status_code == 401


def test_optimization_generate_forbidden_for_driver(driver_token):
    res = client.post(
        "/api/optimization/generate",
        json={},
        headers={"Authorization": f"Bearer {driver_token}"},
    )
    assert res.status_code == 403


def test_optimization_generate_success_and_persist(admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    payload = {
        "persist": True,
        "time_limit_seconds": 3,
    }
    res = client.post("/api/optimization/generate", json=payload, headers=headers)
    assert res.status_code == 200, res.text
    data = res.json()

    assert data["id"] is not None
    assert data["status"] in ["SUCCESS", "PARTIAL_SUCCESS"]
    assert data["number_of_vehicles"] >= 5
    assert data["number_of_collection_points"] >= 30
    assert data["total_distance_after"] > 0
    assert data["waste_collected"] > 0
    assert len(data["routes"]) > 0

    # Inspect generated routes
    first_route = data["routes"][0]
    assert first_route["id"] > 0
    assert first_route["total_distance_km"] > 0
    assert first_route["total_waste_kg"] > 0
    assert first_route["geometry_geojson"] is not None
    assert len(first_route["stops"]) > 0

    first_stop = first_route["stops"][0]
    assert first_stop["point_name"] is not None
    assert first_stop["sequence_number"] == 1
    assert first_stop["status"] == "PENDING"
    assert first_stop["estimated_arrival_time"] is not None


def test_list_optimization_runs(admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    res = client.get("/api/optimization", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 1
    first_run = data[0]
    assert "id" in first_run
    assert "status" in first_run
    assert "routes_count" in first_run
    assert first_run["routes_count"] > 0


def test_get_optimization_run_detail(admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    # List to get first run ID
    list_res = client.get("/api/optimization", headers=headers)
    assert list_res.status_code == 200
    run_id = list_res.json()[0]["id"]

    res = client.get(f"/api/optimization/{run_id}", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["id"] == run_id
    assert len(data["routes"]) > 0
    assert data["waste_collected"] > 0


def test_reoptimize_run(admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    # Get latest run
    list_res = client.get("/api/optimization", headers=headers)
    assert list_res.status_code == 200
    run_id = list_res.json()[0]["id"]

    res = client.post(
        f"/api/optimization/{run_id}/reoptimize",
        json={"time_limit_seconds": 3},
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()
    assert data["id"] is not None
    assert data["id"] != run_id  # New run created
    assert len(data["routes"]) > 0


def test_get_nonexistent_optimization_run(admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    res = client.get("/api/optimization/999999", headers=headers)
    assert res.status_code == 404
