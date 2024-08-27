import pytest
from fastapi.testclient import TestClient

from api.main import app, configure


@pytest.fixture(scope="module")
def client(settings) -> TestClient:
    configure(app, settings=settings)
    return TestClient(app)


def test_get_root(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data == "API server is running!"


def test_get_list(client):
    response = client.get("/today")
    assert response.status_code == 200
    data = response.json()
    assert data["done_tasks"] == []
    assert data["pending_tasks"] == []
    assert "expiry" in data


def test_get_agenda(client):
    response = client.get("/agenda")
    assert response.status_code == 200
    data = response.json()
    assert data["timeline"] == []
    assert data["past_expiry"] is False
    assert "finish" in data
