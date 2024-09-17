"""For integration testing, from API call to full response based on database content.

Interacts with the test database.
"""

from datetime import datetime, time, timedelta
import pytest
from fastapi.testclient import TestClient

from api.main import app, configure
from src.utils import system_tz


LOCAL_TZ = system_tz()
OLD_TIME_STR = "2022-02-22 00:00:00+05"
OLD_TIME = datetime.fromisoformat(OLD_TIME_STR)
FUTURE_TIME = datetime.now(LOCAL_TZ) + timedelta(hours=12)
FUTURE_TIME_STR = FUTURE_TIME.isoformat()
TZNOW = datetime.now(LOCAL_TZ)


@pytest.fixture(scope="module")
def client(settings) -> TestClient:
    configure(app, settings=settings)
    return TestClient(app)


@pytest.fixture(autouse=True)
def db_setup_teardown(db):
    # BOOKMARK: need to make sure there is always a user even in a fresh environment
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
    """No previous list for this user; create a new one."""
    response = client.get("/today")
    assert response.status_code == 201

    data = response.json()
    assert data["id"] > 0
    assert datetime.fromisoformat(data["expiry"]) > TZNOW
    assert data["done_tasks"] == []
    assert data["pending_tasks"] == []


def test_get_list_expired(client, db, temp_userid):
    """An expired list exists for this user - make a new blank one."""
    old_list_id = db.add_daylist(user_id=temp_userid, expiry=OLD_TIME)
    db.add_task_to_list(daylist_id=old_list_id, title="first", estimate="PT20M")
    db.add_task_to_list(daylist_id=old_list_id, title="second", estimate="PT20M")
    db.add_task_to_list(daylist_id=old_list_id, title="third", estimate="PT20M")
    # BOOKMARK: a done task too

    response = client.get("/today")
    assert response.status_code == 201

    data = response.json()
    # return newly created list without old info
    assert data["pending_tasks"] == []
    assert data["pending_tasks"] == []
    assert datetime.fromisoformat(data["expiry"]) > TZNOW
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
    # BOOKMARK: add done tasks to this list too

    response = client.get("/today")
    assert response.status_code == 200

    data = response.json()
    # return unexpired list
    assert data["id"] == active_lid
    assert datetime.fromisoformat(data["expiry"]) > TZNOW
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
    assert datetime.fromisoformat(data["expiry"]) > TZNOW
    # return newly created list without old info
    assert [task["id"] for task in data["pending_tasks"]] == expected_pending
    assert data["done_tasks"] == []


# GET today's timeline/agenda


@pytest.mark.skip()
def test_get_agenda_no_user(client):
    """User not found."""
    response = client.get("/agenda")
    assert response.status_code == 400  # or something


def test_get_agenda_none(client):
    """No previous list for this user, just returns empty agenda."""
    response = client.get("/agenda")
    assert response.status_code == 201

    data = response.json()
    # empty agenda, no warning with finish time = now (prev minute)
    assert data["timeline"] == []
    assert data["past_expiry"] is False
    assert datetime.fromisoformat(data["finish"]) <= TZNOW
    assert datetime.fromisoformat(data["expiry"]) >= TZNOW


def test_get_agenda_expired(client, db, temp_userid):
    """An expired list exists for this user - list/agenda should be freshly created."""
    old_list_id = db.add_daylist(user_id=temp_userid, expiry=OLD_TIME)
    db.add_task_to_list(daylist_id=old_list_id, title="first", estimate="PT20M")
    # BOOKMARK: a done task too

    response = client.get("/agenda")
    assert response.status_code == 201

    data = response.json()
    # new empty agenda, no warning with finish time = now (prev minute)
    assert data["timeline"] == []
    assert data["past_expiry"] is False
    assert datetime.fromisoformat(data["finish"]) <= TZNOW
    assert datetime.fromisoformat(data["expiry"]) >= TZNOW


def test_get_agenda_empty(client, db, temp_userid):
    """An active list exists for this user - return the agenda."""
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
    assert datetime.fromisoformat(data["finish"]) <= TZNOW
    assert datetime.fromisoformat(data["expiry"]) >= TZNOW


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
    # BOOKMARK: add done tasks to this list too

    response = client.get("/agenda")
    assert response.status_code == 200

    data = response.json()
    # should contain the agenda for these items
    assert len(data["timeline"]) == len(expected_pending)
    assert data["past_expiry"] is False
    assert datetime.fromisoformat(data["finish"]) >= TZNOW
    assert datetime.fromisoformat(data["expiry"]) >= TZNOW


# Test providing custom expiry for both endpoints


@pytest.mark.parametrize("endpoint", ["/today", "/agenda"])
def test_get_list_custom_expiry(client, endpoint):
    """Create a new list that expires at a custom time."""
    # provide custom expiry time
    sample_time = time.fromisoformat("20:16:00+06:00")
    sample_timestr = sample_time.isoformat()
    params = {"expire": sample_timestr}

    response = client.get(endpoint, params=params)
    assert response.status_code == 201

    data = response.json()
    # new list's expiry time matches what was provided
    result_expiry = datetime.fromisoformat(data["expiry"])
    result_expiry_rezoned = result_expiry.astimezone(sample_time.tzinfo)
    assert result_expiry_rezoned.hour == sample_time.hour
    assert result_expiry_rezoned.minute == sample_time.minute


@pytest.mark.parametrize("endpoint", ["/today", "/agenda"])
def test_get_list_irrelevant_expiry(client, db, temp_userid, endpoint):
    """An active list exists for this user - adding custom expiry has no effect."""
    db.add_daylist(user_id=temp_userid, expiry=FUTURE_TIME)
    # provide custom expiry time
    sample_time = time.fromisoformat("12:16:00+06:00")
    sample_timestr = sample_time.isoformat()
    params = {"expire": sample_timestr}

    response = client.get(endpoint, params=params)
    assert response.status_code == 200

    data = response.json()
    # return original list with original expiry, not custom expiry
    assert data["expiry"] != sample_timestr
    assert data["expiry"] == FUTURE_TIME_STR


@pytest.mark.parametrize("endpoint", ["/today", "/agenda"])
def test_get_list_expiry_no_tz(client, db, temp_userid, endpoint):
    """Providing a custom expiry without timezone fails."""
    db.add_daylist(user_id=temp_userid, expiry=FUTURE_TIME)
    # provide custom expiry time
    sample_time = time.fromisoformat("12:16:00")
    sample_timestr = sample_time.isoformat()
    params = {"expire": sample_timestr}

    response = client.get(endpoint, params=params)
    assert response.status_code == 422
    # has error message in correct schema
    data = response.json()
    assert "detail" in data
    assert "msg" in data["detail"][0]


# POST: add new task


@pytest.mark.parametrize("prior_listsize", [0, 1])
def test_post_task(client, db, temp_userid, prior_listsize):
    """Create a new task for today's empty list."""
    # a list already exists for this user
    active_lid = db.add_daylist(user_id=temp_userid, expiry=FUTURE_TIME)
    # have some tasks in the list already?
    for _ in range(prior_listsize):
        db.add_task_to_list(daylist_id=active_lid, title="some task", estimate="PT20M")

    sample_name = "my new task"
    sample_time = "PT1H15M"
    input_data = {"title": sample_name, "estimate": sample_time}

    response = client.post("/task", json=input_data)
    assert response.status_code == 201

    data = response.json()
    # return new task info
    assert "id" in data
    assert data["title"] == sample_name
    assert data["estimate"] == sample_time
    # new task is in db
    assert db.count_tasks(daylist_id=active_lid) == prior_listsize + 1


@pytest.mark.parametrize(
    "bad_task",
    [
        {},  # blank
        {"title": "a" * 1000, "estimate": "PT20M"},  # title too long
        {"title": "sample", "estimate": "P1DT20H"},  # estimate too long
    ],
)
def test_post_task_invalid(client, db, temp_userid, bad_task):
    """Can't create a task that fails basic validation."""
    # a list already exists for this user
    db.add_daylist(user_id=temp_userid, expiry=FUTURE_TIME)

    response = client.post("/task", json=bad_task)
    assert response.status_code == 422
    # has error message in correct schema
    data = response.json()
    assert "detail" in data
    assert "msg" in data["detail"][0]


def test_post_task_no_list(client, db, temp_userid):
    """Attempt to create a task but list does not exist yet."""
    sample_name = "my new task"
    sample_time = "PT1H15M"
    input_data = {"title": sample_name, "estimate": sample_time}

    response = client.post("/task", json=input_data)
    assert response.status_code == 404
    # has error message in correct schema
    data = response.json()
    assert "detail" in data
    assert "msg" in data["detail"][0]
