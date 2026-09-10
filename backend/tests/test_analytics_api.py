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


def test_analytics_overview_requires_auth():
    res = client.get("/api/analytics/overview")
    assert res.status_code == 401


def test_analytics_overview_authenticated(admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    res = client.get("/api/analytics/overview", headers=headers)
    assert res.status_code == 200
    data = res.json()

    assert "collection_stats" in data
    assert "route_stats" in data
    assert "optimization_impact" in data
    assert "summary_cards" in data

    col = data["collection_stats"]
    assert col["total_waste_kg"] > 0
    assert len(col["waste_by_type"]) > 0
    assert len(col["daily_trend"]) == 7

    impact = data["optimization_impact"]
    assert impact["estimated_fuel_saved_liters"] >= 0
    assert impact["estimated_cost_saved_inr"] >= 0
    assert "benchmark" in impact["disclaimer"].lower()


def test_analytics_collections_breakdown(admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    res = client.get("/api/analytics/collections", headers=headers)
    assert res.status_code == 200
    data = res.json()

    assert data["total_waste_kg"] > 0
    assert len(data["waste_by_type"]) > 0
    # First polymer type should have percentage
    assert data["waste_by_type"][0]["percentage"] > 0


def test_analytics_routes_fleet_utilization(admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    res = client.get("/api/analytics/routes", headers=headers)
    assert res.status_code == 200
    data = res.json()

    assert "total_routes_count" in data
    assert "vehicle_utilization" in data
    assert len(data["vehicle_utilization"]) >= 5


def test_analytics_optimization_impact_endpoint(admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    res = client.get("/api/analytics/optimization-impact", headers=headers)
    assert res.status_code == 200
    data = res.json()

    assert data["total_distance_before_km"] > 0
    assert data["total_distance_after_km"] > 0
    assert data["distance_saved_percentage"] >= 0
    assert data["estimated_co2_avoided_kg"] >= 0
