import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.osrm_service import haversine_distance, haversine_matrix, OSRMService, osrm_service

client = TestClient(app)


@pytest.fixture
def admin_token():
    res = client.post("/api/auth/login", json={
        "email": "admin@ecoroute.org",
        "password": "Password123!"
    })
    assert res.status_code == 200
    return res.json()["access_token"]


def test_haversine_distance_calculation():
    # Baner (18.5590, 73.7868) to Wakad (18.5987, 73.7621)
    dist = haversine_distance(18.5590, 73.7868, 18.5987, 73.7621)
    assert dist > 3.0 and dist < 8.0
    # Same point distance should be 0
    assert haversine_distance(18.5590, 73.7868, 18.5590, 73.7868) == 0.0


def test_haversine_matrix_calculation():
    coords = [(18.5590, 73.7868), (18.5987, 73.7621), (18.5018, 73.8636)]
    dist_mat, dur_mat = haversine_matrix(coords, avg_speed_kmh=30.0)

    assert len(dist_mat) == 3
    assert len(dur_mat) == 3
    assert dist_mat[0][0] == 0.0
    assert dist_mat[0][1] > 0.0
    assert dur_mat[0][1] > 0.0


def test_osrm_table_matrix_service():
    coords = [(18.5590, 73.7868), (18.5987, 73.7621)]
    dist_mat, dur_mat, is_fallback, source = osrm_service.get_table_matrix(coords)

    assert len(dist_mat) == 2
    assert len(dur_mat) == 2
    assert dist_mat[0][0] == 0.0
    assert dist_mat[0][1] >= 0.0
    assert isinstance(is_fallback, bool)
    assert source in ["osrm", "haversine_fallback"]


def test_osrm_route_geometry_service():
    waypoints = [(18.5590, 73.7868), (18.5987, 73.7621)]
    result = osrm_service.get_route_geometry(waypoints)

    assert "distance_km" in result
    assert "duration_minutes" in result
    assert "geometry_coordinates" in result
    assert len(result["geometry_coordinates"]) >= 2
    # Geometry coordinates should be list of [lat, lon]
    first_coord = result["geometry_coordinates"][0]
    assert len(first_coord) == 2
    assert 18.0 <= first_coord[0] <= 19.0


def test_routing_api_requires_auth():
    res_mat = client.post("/api/routing/matrix", json={
        "locations": [{"latitude": 18.5590, "longitude": 73.7868}]
    })
    assert res_mat.status_code == 401

    res_route = client.post("/api/routing/route", json={
        "waypoints": [{"latitude": 18.5590, "longitude": 73.7868}]
    })
    assert res_route.status_code == 401


def test_routing_api_matrix_authenticated(admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    payload = {
        "locations": [
            {"latitude": 18.5018, "longitude": 73.8636, "name": "Swargate Depot"},
            {"latitude": 18.5590, "longitude": 73.7868, "name": "Baner Bin"},
            {"latitude": 18.5987, "longitude": 73.7621, "name": "Wakad Bin"}
        ]
    }
    res = client.post("/api/routing/matrix", json=payload, headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "distance_matrix_km" in data
    assert "duration_matrix_min" in data
    assert len(data["distance_matrix_km"]) == 3
    assert len(data["duration_matrix_min"]) == 3
    assert "is_fallback" in data
    assert "source" in data


def test_routing_api_route_authenticated(admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    payload = {
        "waypoints": [
            {"latitude": 18.5018, "longitude": 73.8636, "name": "Swargate Depot"},
            {"latitude": 18.5590, "longitude": 73.7868, "name": "Baner Bin"},
            {"latitude": 18.5987, "longitude": 73.7621, "name": "Wakad Bin"}
        ]
    }
    res = client.post("/api/routing/route", json=payload, headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["distance_km"] > 0
    assert data["duration_minutes"] > 0
    assert len(data["geometry_coordinates"]) >= 2
    assert "is_fallback" in data
    assert "source" in data


def test_routing_input_validation(admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    # Invalid latitude 999.0
    payload = {
        "locations": [
            {"latitude": 999.0, "longitude": 73.8636}
        ]
    }
    res = client.post("/api/routing/matrix", json=payload, headers=headers)
    assert res.status_code == 422
