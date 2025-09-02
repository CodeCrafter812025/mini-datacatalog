import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_token():
    response = client.post("/token", data={"username": "admin", "password": "admin123"})
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_protected_route_without_token():
    response = client.get("/meta/datasources")
    assert response.status_code == 401

def test_protected_route_with_token():
    # First get token
    token_response = client.post("/token", data={"username": "admin", "password": "admin123"})
    token = token_response.json()["access_token"]
    
    # Then access protected route
    response = client.get("/meta/datasources", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200

def test_pagination():
    # Get token first
    token_response = client.post("/token", data={"username": "admin", "password": "admin123"})
    token = token_response.json()["access_token"]
    
    # Test pagination
    response = client.get("/meta/datasources?skip=0&limit=5", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "skip" in data
    assert "limit" in data
    assert len(data["items"]) <= 5
