from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_get_root():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data == "API server is running!"


def test_get_list():
    response = client.get("/today")
    assert response.status_code == 200
    data = response.json()
    assert data["done_tasks"] == []
    assert data["pending_tasks"] == []
    assert "expiry" in data


def test_get_agenda():
    response = client.get("/agenda")
    assert response.status_code == 200
    data = response.json()
    assert data["timeline"] == []
    assert data["past_expiry"] is False
    assert "finish" in data
