from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_get_list():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"done_tasks": [], "pending_tasks": []}
