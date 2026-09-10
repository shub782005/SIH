import io
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


def test_get_driver_active_route(driver_token, admin_token):
    # Ensure at least one route is generated
    opt_res = client.post(
        "/api/optimization/generate",
        json={"persist": True, "time_limit_seconds": 2},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert opt_res.status_code == 200

    # Query as driver
    res = client.get("/api/driver/my-route", headers={"Authorization": f"Bearer {driver_token}"})
    assert res.status_code == 200
    data = res.json()
    assert data is not None
    assert "vehicle_number" in data
    assert "stops" in data
    assert len(data["stops"]) > 0


def test_driver_mark_arrival_at_stop(driver_token):
    res_route = client.get("/api/driver/my-route", headers={"Authorization": f"Bearer {driver_token}"})
    assert res_route.status_code == 200
    route = res_route.json()
    assert route is not None
    stop = route["stops"][0]
    stop_id = stop["id"]

    # Mark arrival
    res_arrive = client.post(
        f"/api/collections/arrive/{stop_id}",
        headers={"Authorization": f"Bearer {driver_token}"},
    )
    assert res_arrive.status_code == 200
    stop_data = res_arrive.json()
    assert stop_data["status"] == "ARRIVED"
    assert stop_data["actual_arrival_time"] is not None


def test_driver_complete_collection(driver_token):
    res_route = client.get("/api/driver/my-route", headers={"Authorization": f"Bearer {driver_token}"})
    route = res_route.json()
    stop = route["stops"][0]
    stop_id = stop["id"]

    payload = {
        "route_stop_id": stop_id,
        "actual_quantity_kg": 210.5,
        "proof_image_url": "/uploads/test_proof.jpg",
        "remarks": "Clean sorted PET bottles collected without issues.",
    }

    res_complete = client.post(
        "/api/collections/complete",
        json=payload,
        headers={"Authorization": f"Bearer {driver_token}"},
    )
    assert res_complete.status_code == 201
    col_data = res_complete.json()
    assert col_data["actual_quantity_kg"] == 210.5
    assert col_data["verification_status"] == "VERIFIED"
    assert col_data["route_stop_id"] == stop_id


def test_driver_report_failure(driver_token):
    res_route = client.get("/api/driver/my-route", headers={"Authorization": f"Bearer {driver_token}"})
    route = res_route.json()
    if len(route["stops"]) > 1:
        stop = route["stops"][1]
        stop_id = stop["id"]

        payload = {
            "route_stop_id": stop_id,
            "failure_reason": "NO_WASTE",
            "remarks": "Bin was already empty upon arrival.",
        }

        res_fail = client.post(
            "/api/collections/fail",
            json=payload,
            headers={"Authorization": f"Bearer {driver_token}"},
        )
        assert res_fail.status_code == 201
        data = res_fail.json()
        assert data["verification_status"] == "FAILED"
        assert data["failure_reason"] == "NO_WASTE"


def test_driver_upload_proof_image(driver_token):
    file_content = b"fake image bytes content"
    files = {"file": ("pickup_proof.jpg", io.BytesIO(file_content), "image/jpeg")}

    res = client.post(
        "/api/collections/upload-proof",
        files=files,
        headers={"Authorization": f"Bearer {driver_token}"},
    )
    assert res.status_code == 201
    data = res.json()
    assert "url" in data
    assert "/uploads/" in data["url"]
