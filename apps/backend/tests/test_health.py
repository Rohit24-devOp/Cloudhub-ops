from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_register_and_dashboard_flow():
    response = client.post("/api/auth/register", json={"email": "test@example.com", "name": "Test User", "password": "secure-pass-123"})
    assert response.status_code in {200, 409}
    if response.status_code == 409:
        response = client.post("/api/auth/login", json={"email": "test@example.com", "password": "secure-pass-123"})
    token = response.json()["access_token"]
    dashboard = client.get("/api/dashboard", headers={"Authorization": f"Bearer {token}"})
    assert dashboard.status_code == 200
    assert "security_score" in dashboard.json()
