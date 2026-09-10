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


def test_list_routes(admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    res = client.get("/api/routes", headers=headers)
    assert res.status_code == 200
    routes = res.json()
    assert isinstance(routes, list)
    if routes:
        first_route = routes[0]
        assert "vehicle_id" in first_route
        assert "total_distance_km" in first_route
        assert "status" in first_route
        assert "stops" in first_route


def test_get_route_by_id(admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    list_res = client.get("/api/routes", headers=headers)
    assert list_res.status_code == 200
    routes = list_res.json()
    if not routes:
        # Generate an optimization run first to have routes
        client.post("/api/optimization/generate", json={"persist": True, "time_limit_seconds": 2}, headers=headers)
        routes = client.get("/api/routes", headers=headers).json()

    assert len(routes) > 0
    route_id = routes[0]["id"]

    res = client.get(f"/api/routes/{route_id}", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["id"] == route_id
    assert "stops" in data
    assert "geometry_geojson" in data


def test_update_route_status(admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    routes = client.get("/api/routes", headers=headers).json()
    assert len(routes) > 0
    route_id = routes[0]["id"]

    # Transition to ASSIGNED
    res = client.put(
        f"/api/routes/{route_id}/status",
        json={"status": "ASSIGNED"},
        headers=headers,
    )
    assert res.status_code == 200
    assert res.json()["status"] == "ASSIGNED"

    # Transition to STARTED
    res_start = client.put(
        f"/api/routes/{route_id}/status",
        json={"status": "STARTED"},
        headers=headers,
    )
    assert res_start.status_code == 200
    assert res_start.json()["status"] == "STARTED"


def test_assign_route(admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    routes = client.get("/api/routes", headers=headers).json()
    assert len(routes) > 0
    route_id = routes[0]["id"]

    # Assign vehicle 2
    res = client.put(
        f"/api/routes/{route_id}/assign",
        json={"vehicle_id": 2},
        headers=headers,
    )
    assert res.status_code == 200
    assert res.json()["vehicle_id"] == 2


def test_delete_route(admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    # Create a fresh optimization run to get a deletable route
    opt_res = client.post(
        "/api/optimization/generate",
        json={"persist": True, "time_limit_seconds": 2},
        headers=headers,
    )
    assert opt_res.status_code == 200
    routes = opt_res.json()["routes"]
    assert len(routes) > 0
    route_to_delete = routes[-1]["id"]

    del_res = client.delete(f"/api/routes/{route_to_delete}", headers=headers)
    assert del_res.status_code == 204

    
    get_res = client.get(f"/api/routes/{route_to_delete}", headers=headers)
    assert get_res.status_code == 404
