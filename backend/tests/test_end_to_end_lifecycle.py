import io
import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_full_platform_end_to_end_lifecycle():
    """
    Master End-to-End Test covering the entire software lifecycle:
    1. Admin Authentication
    2. Dynamic Collection Point Creation & Priority Evaluation
    3. Road Distance Matrix Computation
    4. Google OR-Tools CVRP Route Optimization & Persistence
    5. Driver Route Assignment
    6. Driver Login & Active Route Retrieval
    7. Stop Arrival Verification
    8. Photo Proof Upload
    9. Verified Weight Collection Recording & Waste Ledger Update
    10. Collection Failure Reporting & Exception Handling
    11. Automatic Route Completion Trigger
    12. Collection Point Priority Recalibration
    13. Real-Time Operational Analytics & Fuel Savings Audit
    """
    # -------------------------------------------------------------
    # Step 1: Admin Authentication
    # -------------------------------------------------------------
    login_res = client.post("/api/auth/login", json={
        "email": "admin@ecoroute.org",
        "password": "Password123!"
    })
    assert login_res.status_code == 200, f"Admin login failed: {login_res.text}"
    admin_token = login_res.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # -------------------------------------------------------------
    # Step 2: Create a High Priority Collection Point
    # -------------------------------------------------------------
    cp_payload = {
        "name": "E2E Test Pune Central Mall Bins",
        "address": "Senapati Bapat Road, Pune",
        "latitude": 18.5308,
        "longitude": 73.8290,
        "estimated_waste_kg": 350.0,
        "waste_type": "PET",
        "overflow_status": True,
        "contact_person": "Facility Manager",
        "contact_phone": "+91 98765 43210",
        "is_active": True,
    }
    create_cp_res = client.post("/api/collection-points", json=cp_payload, headers=admin_headers)
    assert create_cp_res.status_code == 201, f"Failed to create CP: {create_cp_res.text}"
    created_cp = create_cp_res.json()
    cp_id = created_cp["id"]
    # Verify priority was dynamically computed to CRITICAL due to 350kg + PET + Overflow
    assert created_cp["priority"] == "CRITICAL"
    assert created_cp["overflow_status"] is True

    # -------------------------------------------------------------
    # Step 3: Road Distance Matrix Query
    # -------------------------------------------------------------
    matrix_payload = {
        "locations": [
            {"latitude": 18.5018, "longitude": 73.8636, "name": "Depot"},
            {"latitude": 18.5308, "longitude": 73.8290, "name": "Mall"},
            {"latitude": 18.5204, "longitude": 73.8567, "name": "Market"},
        ],
    }
    matrix_res = client.post("/api/routing/matrix", json=matrix_payload, headers=admin_headers)
    assert matrix_res.status_code == 200
    matrix_data = matrix_res.json()
    assert len(matrix_data["distance_matrix_km"]) == 3
    assert len(matrix_data["distance_matrix_km"][0]) == 3
    assert matrix_data["distance_matrix_km"][0][1] > 0

    # -------------------------------------------------------------
    # Step 4: Execute OR-Tools CVRP Route Optimization
    # -------------------------------------------------------------
    opt_payload = {
        "depot_id": 1,
        "persist": True,
        "time_limit_seconds": 3,
    }
    opt_res = client.post("/api/optimization/generate", json=opt_payload, headers=admin_headers)
    assert opt_res.status_code == 200, f"Optimization failed: {opt_res.text}"
    opt_data = opt_res.json()
    assert "routes" in opt_data
    assert len(opt_data["routes"]) > 0
    assert opt_data["distance_saved_percentage"] >= 0

    target_route = opt_data["routes"][0]
    route_id = target_route["id"]
    assert target_route["geometry_geojson"] is not None
    assert len(target_route["stops"]) > 0

    # -------------------------------------------------------------
    # Step 5: Assign Driver to Route
    # -------------------------------------------------------------
    assign_res = client.put(
        f"/api/routes/{route_id}/assign",
        json={"driver_id": 1},  # Rahul Sharma (driver_id=1)
        headers=admin_headers,
    )
    assert assign_res.status_code == 200
    assert assign_res.json()["driver_id"] == 1

    # -------------------------------------------------------------
    # Step 6: Driver Authentication & Route Retrieval
    # -------------------------------------------------------------
    driver_login_res = client.post("/api/auth/login", json={
        "email": "rahul@ecoroute.org",
        "password": "Password123!"
    })
    assert driver_login_res.status_code == 200
    driver_token = driver_login_res.json()["access_token"]
    driver_headers = {"Authorization": f"Bearer {driver_token}"}

    my_route_res = client.get("/api/driver/my-route", headers=driver_headers)
    assert my_route_res.status_code == 200
    driver_route = my_route_res.json()
    assert driver_route is not None
    assert driver_route["id"] == route_id
    assert len(driver_route["stops"]) > 0

    # -------------------------------------------------------------
    # Step 7: Driver Marks Arrival at Stop #1
    # -------------------------------------------------------------
    stop_1 = driver_route["stops"][0]
    arrive_res = client.post(f"/api/collections/arrive/{stop_1['id']}", headers=driver_headers)
    assert arrive_res.status_code == 200
    assert arrive_res.json()["status"] == "ARRIVED"

    # -------------------------------------------------------------
    # Step 8: Upload Collection Proof Photo
    # -------------------------------------------------------------
    photo_file = b"BINARY_IMAGE_DATA_MOCK_PROOF"
    upload_res = client.post(
        "/api/collections/upload-proof",
        files={"file": ("waste_pickup_verified.jpg", io.BytesIO(photo_file), "image/jpeg")},
        headers=driver_headers,
    )
    assert upload_res.status_code == 201
    proof_url = upload_res.json()["url"]
    assert "/uploads/" in proof_url

    # -------------------------------------------------------------
    # Step 9: Complete Stop #1 with Verified Waste Quantity
    # -------------------------------------------------------------
    collect_payload = {
        "route_stop_id": stop_1["id"],
        "actual_quantity_kg": 240.0,
        "proof_image_url": proof_url,
        "remarks": "Clean sorted PET collected from commercial bin.",
    }
    complete_res = client.post("/api/collections/complete", json=collect_payload, headers=driver_headers)
    assert complete_res.status_code == 201
    col_data = complete_res.json()
    assert col_data["actual_quantity_kg"] == 240.0
    assert col_data["verification_status"] == "VERIFIED"

    # -------------------------------------------------------------
    # Step 10: Report Exception at Stop #2 (if present)
    # -------------------------------------------------------------
    if len(driver_route["stops"]) > 1:
        stop_2 = driver_route["stops"][1]
        fail_payload = {
            "route_stop_id": stop_2["id"],
            "failure_reason": "NO_WASTE",
            "remarks": "Bin cleared early by municipal team.",
        }
        fail_res = client.post("/api/collections/fail", json=fail_payload, headers=driver_headers)
        assert fail_res.status_code == 201
        assert fail_res.json()["verification_status"] == "FAILED"

    # -------------------------------------------------------------
    # Step 11: Process Remaining Stops & Verify Route Completion
    # -------------------------------------------------------------
    for remaining_stop in driver_route["stops"][2:]:
        client.post("/api/collections/complete", json={
            "route_stop_id": remaining_stop["id"],
            "actual_quantity_kg": 150.0,
            "remarks": "Routine pickup completed.",
        }, headers=driver_headers)

    # Check updated route status
    route_check_res = client.get(f"/api/routes/{route_id}", headers=admin_headers)
    assert route_check_res.status_code == 200
    assert route_check_res.json()["status"] == "COMPLETED"

    # -------------------------------------------------------------
    # Step 12: Verify Collection Point Priority Recalibration
    # -------------------------------------------------------------
    cp_check_res = client.get(f"/api/collection-points/{stop_1['collection_point_id']}", headers=admin_headers)
    assert cp_check_res.status_code == 200
    updated_cp = cp_check_res.json()
    assert updated_cp["overflow_status"] is False
    assert updated_cp["priority"] == "LOW"

    # -------------------------------------------------------------
    # Step 13: Operational Analytics & Fuel Savings Audit
    # -------------------------------------------------------------
    analytics_res = client.get("/api/analytics/overview", headers=admin_headers)
    assert analytics_res.status_code == 200
    analytics_data = analytics_res.json()

    assert analytics_data["collection_stats"]["total_waste_kg"] > 0
    assert analytics_data["optimization_impact"]["estimated_fuel_saved_liters"] > 0
    assert analytics_data["optimization_impact"]["estimated_cost_saved_inr"] > 0
    assert analytics_data["optimization_impact"]["estimated_co2_avoided_kg"] > 0
    assert "benchmark" in analytics_data["optimization_impact"]["disclaimer"].lower()

    # Clean up test route and test collection point
    client.delete(f"/api/routes/{route_id}", headers=admin_headers)
    client.delete(f"/api/collection-points/{cp_id}", headers=admin_headers)

