import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.enums import UserRole
from app.api.deps import require_roles

client = TestClient(app)

def test_login_success():
    response = client.post("/api/auth/login", json={
        "email": "admin@ecoroute.org",
        "password": "Password123!"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "admin@ecoroute.org"
    assert data["user"]["role"] == UserRole.ADMIN.value

def test_login_invalid_password():
    response = client.post("/api/auth/login", json={
        "email": "admin@ecoroute.org",
        "password": "WrongPassword!"
    })
    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["detail"]

def test_login_invalid_email():
    response = client.post("/api/auth/login", json={
        "email": "nonexistent@ecoroute.org",
        "password": "Password123!"
    })
    assert response.status_code == 401

def test_get_me_authenticated():
    # First login to get token
    login_res = client.post("/api/auth/login", json={
        "email": "admin@ecoroute.org",
        "password": "Password123!"
    })
    token = login_res.json()["access_token"]

    # Request /auth/me with Bearer token
    me_res = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert me_res.status_code == 200
    user_data = me_res.json()
    assert user_data["email"] == "admin@ecoroute.org"
    assert user_data["name"] == "Operations Admin"

def test_get_me_unauthorized():
    me_res = client.get("/api/auth/me")
    assert me_res.status_code == 401

def test_logout():
    login_res = client.post("/api/auth/login", json={
        "email": "admin@ecoroute.org",
        "password": "Password123!"
    })
    token = login_res.json()["access_token"]

    logout_res = client.post(
        "/api/auth/logout",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert logout_res.status_code == 200
    assert logout_res.json()["message"] == "Successfully logged out"
