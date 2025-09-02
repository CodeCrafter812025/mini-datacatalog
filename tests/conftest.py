import io
import pytest
from fastapi.testclient import TestClient
from fastapi_app import app  # اپ FastAPI از همین فایل می‌آید

@pytest.fixture(scope="session")
def client():
    return TestClient(app)

@pytest.fixture(scope="session")
def token(client):
    # یوزر/پسورد از .env: admin / admin123
    resp = client.post(
        "/token",
        data={"username": "admin", "password": "admin123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]

@pytest.fixture
def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def sample_csv_bytes():
    data = "name,schema,etl\nsample_table,public,etl1\n"
    return io.BytesIO(data.encode("utf-8"))
