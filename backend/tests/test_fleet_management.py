import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


@pytest.fixture
def admin_token():
    res = client.post("/api/auth/login", json={"email": "admin@ecoroute.org", "password": "Password123!"})
    assert res.status_code == 200, f"Admin login failed: {res.text}"
    return res.json()["access_token"]


@pytest.fixture
def driver_token():
    res = client.post("/api/auth/login", json={"email": "rahul@ecoroute.org", "password": "Password123!"})
    assert res.status_code == 200, f"Driver login failed: {res.text}"
    return res.json()["access_token"]


# ─── VEHICLE TESTS ─────────────────────────────────────────────────────────────

class TestVehicles:
    def test_list_vehicles_requires_auth(self):
        res = client.get("/api/vehicles")
        assert res.status_code == 401

    def test_list_vehicles_authenticated(self, admin_token):
        res = client.get("/api/vehicles", headers={"Authorization": f"Bearer {admin_token}"})
        assert res.status_code == 200
        vehicles = res.json()
        assert len(vehicles) >= 5  # seeded vehicles
        assert "vehicle_number" in vehicles[0]
        assert "capacity_kg" in vehicles[0]

    def test_create_vehicle_requires_admin_or_manager(self, driver_token):
        res = client.post(
            "/api/vehicles",
            json={"vehicle_number": "XX99-ZZ-9999", "capacity_kg": 500, "vehicle_type": "Truck"},
            headers={"Authorization": f"Bearer {driver_token}"},
        )
        assert res.status_code == 403

    def test_create_and_delete_vehicle_lifecycle(self, admin_token):
        headers = {"Authorization": f"Bearer {admin_token}"}
        # Create
        res_create = client.post(
            "/api/vehicles",
            json={
                "vehicle_number": "TEST-VH-0001",
                "vehicle_type": "Mini Truck",
                "capacity_kg": 750.0,
                "status": "AVAILABLE",
            },
            headers=headers,
        )
        assert res_create.status_code == 201, res_create.text
        v = res_create.json()
        assert v["vehicle_number"] == "TEST-VH-0001"
        assert v["capacity_kg"] == 750.0
        vehicle_id = v["id"]

        # Duplicate number must fail
        res_dup = client.post(
            "/api/vehicles",
            json={"vehicle_number": "TEST-VH-0001", "capacity_kg": 100},
            headers=headers,
        )
        assert res_dup.status_code == 409

        # Update status
        res_update = client.put(
            f"/api/vehicles/{vehicle_id}",
            json={"status": "OFF_DUTY"},
            headers=headers,
        )
        assert res_update.status_code == 200
        assert res_update.json()["status"] == "OFF_DUTY"

        # Delete
        res_del = client.delete(f"/api/vehicles/{vehicle_id}", headers=headers)
        assert res_del.status_code == 204

        # Confirm 404 after delete
        assert client.get(f"/api/vehicles/{vehicle_id}", headers=headers).status_code == 404

    def test_vehicle_invalid_capacity(self, admin_token):
        res = client.post(
            "/api/vehicles",
            json={"vehicle_number": "BAD-CAP-0001", "capacity_kg": -100},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert res.status_code == 422


# ─── DRIVER TESTS ───────────────────────────────────────────────────────────────

class TestDrivers:
    def test_list_drivers_requires_auth(self):
        res = client.get("/api/drivers")
        assert res.status_code == 401

    def test_list_drivers_authenticated(self, admin_token):
        res = client.get("/api/drivers", headers={"Authorization": f"Bearer {admin_token}"})
        assert res.status_code == 200
        drivers = res.json()
        assert len(drivers) >= 5  # seeded drivers
        assert "license_number" in drivers[0]
        assert "phone" in drivers[0]

    def test_get_driver_detail(self, admin_token):
        # Get first driver
        all_res = client.get("/api/drivers", headers={"Authorization": f"Bearer {admin_token}"})
        driver_id = all_res.json()[0]["id"]
        res = client.get(f"/api/drivers/{driver_id}", headers={"Authorization": f"Bearer {admin_token}"})
        assert res.status_code == 200
        assert res.json()["id"] == driver_id

    def test_update_driver_status(self, admin_token):
        headers = {"Authorization": f"Bearer {admin_token}"}
        all_res = client.get("/api/drivers", headers=headers)
        driver_id = all_res.json()[0]["id"]
        res = client.put(
            f"/api/drivers/{driver_id}",
            json={"status": "OFF_DUTY"},
            headers=headers,
        )
        assert res.status_code == 200
        assert res.json()["status"] == "OFF_DUTY"
        # Restore
        client.put(f"/api/drivers/{driver_id}", json={"status": "AVAILABLE"}, headers=headers)

    def test_driver_not_found(self, admin_token):
        res = client.get("/api/drivers/999999", headers={"Authorization": f"Bearer {admin_token}"})
        assert res.status_code == 404


# ─── USERS TESTS ────────────────────────────────────────────────────────────────

class TestUsers:
    def test_list_users_admin_only(self, admin_token, driver_token):
        # Admin can list
        res_admin = client.get("/api/users", headers={"Authorization": f"Bearer {admin_token}"})
        assert res_admin.status_code == 200
        assert len(res_admin.json()) >= 1

        # Driver cannot list
        res_driver = client.get("/api/users", headers={"Authorization": f"Bearer {driver_token}"})
        assert res_driver.status_code == 403

    def test_create_user_duplicate_email(self, admin_token):
        res = client.post(
            "/api/users",
            json={"name": "Dup User", "email": "admin@ecoroute.org", "password": "Test1234!", "role": "DRIVER"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert res.status_code == 409
