"""
For integration testing, from API call to full response based on database content.
Interacts with the test database.
"""

import pytest
from fastapi.testclient import TestClient

from api.main import app, configure


@pytest.fixture(scope="module")
def client(settings) -> TestClient:
    configure(app, settings=settings)
    return TestClient(app)


@pytest.fixture(autouse=True)
def db_setup_teardown(db):
    # TODO: need to make sure there is always a user even in a fresh environment
    for _ in range(2):
        db.add_anon_user()
    try:
        yield
    finally:
        db.delete_all_users()


def test_get_root(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data == "API server is running!"


# First time user


def test_get_list_empty(client):
    response = client.get("/today")
    assert response.status_code == 200

    data = response.json()
    assert data["done_tasks"] == []
    assert data["pending_tasks"] == []
    assert "expiry" in data


def test_get_agenda_empty(client):
    response = client.get("/agenda")
    assert response.status_code == 200

    data = response.json()
    assert data["timeline"] == []
    assert data["past_expiry"] is False
    assert "finish" in data


# User has old lists


def test_get_list_is_new(client, db):
    userid = db.get_anon_user()["id"]
    test_expiry = "2024-06-01 12:00 AM"
    old_list = db.add_daylist(user_id=userid, expiry=test_expiry)
    # FIX: add done/pending tasks to this list

    response = client.get("/today")
    assert response.status_code == 200

    data = response.json()
    assert data["done_tasks"] == []
    assert data["pending_tasks"] == []
    assert data["expiry"] != test_expiry
    # FIX: we actually need list ids from the model now
    # assert data["id"] != old_list["id"]
