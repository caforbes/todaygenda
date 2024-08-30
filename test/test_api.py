"""For integration testing, from API call to full response based on database content.

Interacts with the test database.
"""

from datetime import datetime, timedelta
import pytest
from fastapi.testclient import TestClient

from api.main import app, configure

OLD_TIME_STR = "2022-02-22 00:00:00"
OLD_TIME = datetime.fromisoformat(OLD_TIME_STR)
FUTURE_TIME = datetime.now() + timedelta(hours=12)
FUTURE_TIME_STR = FUTURE_TIME.isoformat()


@pytest.fixture(scope="module")
def client(settings) -> TestClient:
    configure(app, settings=settings)
    return TestClient(app)


@pytest.fixture(autouse=True)
def db_setup_teardown(db):
    # TODO: need to make sure there is always a user even in a fresh environment
    # TODO: should add some unrelated data to make sure we don't return it
    for _ in range(2):
        db.add_anon_user()
    try:
        yield
    finally:
        db.delete_all_users()


@pytest.fixture()
def temp_userid(db):
    """Currently we only use 1 user for everything."""
    return db.get_anon_user()["id"]


def test_get_root(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data == "API server is running!"


# GET today's list


@pytest.mark.skip()
def test_get_list_no_user(client):
    """User not found."""
    response = client.get("/today")
    assert response.status_code == 400  # or something


def test_get_list_none(client):
    """No previous list for this user."""
    response = client.get("/today")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] > 0
    assert datetime.fromisoformat(data["expiry"]) > datetime.now()
    assert data["done_tasks"] == []
    assert data["pending_tasks"] == []


def test_get_list_expired(client, db, temp_userid):
    """An expired list exists for this user - make a new blank one."""
    old_list_id = db.add_daylist(user_id=temp_userid, expiry=OLD_TIME)
    db.add_task_to_list(daylist_id=old_list_id, title="first", estimate="PT20M")
    db.add_task_to_list(daylist_id=old_list_id, title="second", estimate="PT20M")
    db.add_task_to_list(daylist_id=old_list_id, title="third", estimate="PT20M")
    # TODO: a done task too

    response = client.get("/today")
    assert response.status_code == 200

    data = response.json()
    # return newly created list without old info
    assert data["pending_tasks"] == []
    assert data["pending_tasks"] == []
    assert datetime.fromisoformat(data["expiry"]) > datetime.now()
    # definitely not the old list
    assert data["id"] != old_list_id


def test_get_list_active(client, db, temp_userid):
    """An active list exists for this user - return it with nested tasks."""
    # current list but also old expired list
    old_lid = db.add_daylist(user_id=temp_userid, expiry=OLD_TIME)
    db.add_task_to_list(daylist_id=old_lid, title="old", estimate="PT20M")

    active_lid = db.add_daylist(user_id=temp_userid, expiry=FUTURE_TIME)
    expected_pending = [
        db.add_task_to_list(daylist_id=active_lid, title="first", estimate="PT20M"),
        db.add_task_to_list(daylist_id=active_lid, title="second", estimate="PT20M"),
        db.add_task_to_list(daylist_id=active_lid, title="third", estimate="PT20M"),
    ]
    # TODO: add done tasks to this list too

    response = client.get("/today")
    assert response.status_code == 200

    data = response.json()
    # return unexpired list
    assert data["id"] == active_lid
    assert data["expiry"] == FUTURE_TIME_STR
    assert datetime.fromisoformat(data["expiry"]) > datetime.now()
    # return newly created list without old info
    assert [task["id"] for task in data["pending_tasks"]] == expected_pending
    assert data["done_tasks"] == []  # add some


def test_get_list_empty(client, db, temp_userid):
    """An active list exists for this user - but has no tasks."""
    # current list but also old expired list
    old_lid = db.add_daylist(user_id=temp_userid, expiry=OLD_TIME)
    db.add_task_to_list(daylist_id=old_lid, title="old", estimate="PT20M")

    active_lid = db.add_daylist(user_id=temp_userid, expiry=FUTURE_TIME)
    expected_pending = []

    response = client.get("/today")
    assert response.status_code == 200

    data = response.json()
    # return unexpired list
    assert data["id"] == active_lid
    assert data["expiry"] == FUTURE_TIME_STR
    assert datetime.fromisoformat(data["expiry"]) > datetime.now()
    # return newly created list without old info
    assert [task["id"] for task in data["pending_tasks"]] == expected_pending
    assert data["done_tasks"] == []


# TODO: GET today's timeline/agenda


@pytest.mark.skip()
def test_get_agenda_no_user(client):
    """User not found."""
    response = client.get("/agenda")
    assert response.status_code == 400  # or something


def test_get_agenda_none(client):
    """No previous list for this user, just returns empty agenda."""
    response = client.get("/agenda")
    assert response.status_code == 200

    data = response.json()
    # empty agenda, no warning with finish time = now (prev minute)
    assert data["timeline"] == []
    assert data["past_expiry"] is False
    assert datetime.fromisoformat(data["finish"]) <= datetime.now()


def test_get_agenda_expired(client, db, temp_userid):
    """An expired list exists for this user - agenda should be blank."""
    old_list_id = db.add_daylist(user_id=temp_userid, expiry=OLD_TIME)
    db.add_task_to_list(daylist_id=old_list_id, title="first", estimate="PT20M")
    # TODO: a done task too

    response = client.get("/agenda")
    assert response.status_code == 200

    data = response.json()
    # empty agenda, no warning with finish time = now (prev minute)
    assert data["timeline"] == []
    assert data["past_expiry"] is False
    assert datetime.fromisoformat(data["finish"]) <= datetime.now()


def test_get_agenda_empty(client, db, temp_userid):
    """An active list with tasks exists for this user - return the agenda."""
    # current list but also old expired list
    old_lid = db.add_daylist(user_id=temp_userid, expiry=OLD_TIME)
    db.add_task_to_list(daylist_id=old_lid, title="old", estimate="PT20M")

    db.add_daylist(user_id=temp_userid, expiry=FUTURE_TIME)
    expected_pending = []

    response = client.get("/agenda")
    assert response.status_code == 200

    data = response.json()
    # empty agenda, no warning with finish time = now (prev minute)
    assert data["timeline"] == expected_pending
    assert data["past_expiry"] is False
    assert datetime.fromisoformat(data["finish"]) <= datetime.now()


def test_get_agenda_active(client, db, temp_userid):
    """An active list exists for this user - return it with nested tasks."""
    # current list but also old expired list
    old_lid = db.add_daylist(user_id=temp_userid, expiry=OLD_TIME)
    db.add_task_to_list(daylist_id=old_lid, title="old", estimate="PT20M")

    active_lid = db.add_daylist(user_id=temp_userid, expiry=FUTURE_TIME)
    expected_pending = [
        db.add_task_to_list(daylist_id=active_lid, title="first", estimate="PT20M"),
        db.add_task_to_list(daylist_id=active_lid, title="second", estimate="PT20M"),
        db.add_task_to_list(daylist_id=active_lid, title="third", estimate="PT20M"),
    ]
    # TODO: add done tasks to this list too

    response = client.get("/agenda")
    assert response.status_code == 200

    data = response.json()
    # should contain the agenda for these items
    assert len(data["timeline"]) == len(expected_pending)
    assert "past_expiry" in data
    assert "finish" in data
