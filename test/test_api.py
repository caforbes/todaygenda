from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_get_list():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["done_tasks"] == []
    assert data["pending_tasks"] == []
    assert "expiry" in data
