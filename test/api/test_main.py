"""For integration testing, from API call to full response based on database content.

Interacts with the test database.
"""

from datetime import datetime, time, timedelta
import pytest

from src.utils import system_tz
from test.helpers import auth_headers


LOCAL_TZ = system_tz()
OLD_TIME = datetime.fromisoformat("2022-02-22 00:00:00+05")
DUR_20M = timedelta(minutes=20)
DUR_23HR = timedelta(hours=23)


@pytest.fixture(autouse=True)
def db_setup_teardown(db):
    now = datetime.now(LOCAL_TZ)
    uid = db.add_anon_user()
    lid = db.add_daylist(user_id=uid, expiry=OLD_TIME)
    db.add_task_to_list(daylist_id=lid, title="test1", estimate=DUR_20M)
    db.add_daylist(user_id=uid, expiry=now + DUR_23HR)
    db.add_task_for_user(user_id=uid, title="test2", estimate=DUR_20M)
    db.add_task_for_user(user_id=uid, title="test3", estimate=DUR_20M)

    uid = db.add_registered_user(email="merry@lotr.com", password_hash="rohan")
    db.add_daylist(user_id=uid, expiry=now + DUR_20M)
    db.add_task_for_user(user_id=uid, title="test4", estimate=DUR_20M)

    try:
        yield
    finally:
        db.delete_all_users()


# GET healthcheck


def test_get_root(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data == "API server is running!"


# GET today's list


def test_get_list_no_user(client):
    """No authenticated user, no result."""
    response = client.get("/today")
    assert response.status_code == 401


def test_get_list_none(client, any_user):
    """No previous list for this user; create a new one."""
    response = client.get("/today", headers=auth_headers(any_user))
    assert response.status_code == 201

    data = response.json()
    assert data["id"] > 0
    assert datetime.fromisoformat(data["expiry"]) > datetime.now(LOCAL_TZ)
    assert data["done_tasks"] == []
    assert data["pending_tasks"] == []


def test_get_list_expired(client, db, any_user):
    """An expired list exists for this user - make a new blank one."""
    old_lid = db.add_daylist(user_id=any_user["id"], expiry=OLD_TIME)
    db.add_task_to_list(daylist_id=old_lid, title="first", estimate=DUR_20M)
    db.add_task_to_list(daylist_id=old_lid, title="second", estimate=DUR_20M)
    done = db.add_task_to_list(daylist_id=old_lid, title="third", estimate=DUR_20M)
    db.complete_task(id=done)

    response = client.get("/today", headers=auth_headers(any_user))
    assert response.status_code == 201

    data = response.json()
    # return newly created list without old info
    assert data["pending_tasks"] == []
    assert data["done_tasks"] == []
    assert datetime.fromisoformat(data["expiry"]) > datetime.now(LOCAL_TZ)
    # definitely not the old list
    assert data["id"] != old_lid


def test_get_list_active(client, db, any_user):
    """An active list exists for this user - return it with nested tasks."""
    now = datetime.now(LOCAL_TZ)
    # old expired list
    old_lid = db.add_daylist(user_id=any_user["id"], expiry=OLD_TIME)
    db.add_task_to_list(daylist_id=old_lid, title="old", estimate=DUR_20M)

    # current list
    active_lid = db.add_daylist(user_id=any_user["id"], expiry=now + DUR_23HR)
    expected_pending = [
        db.add_task_to_list(daylist_id=active_lid, title="first", estimate=DUR_20M),
        db.add_task_to_list(daylist_id=active_lid, title="second", estimate=DUR_20M),
    ]
    expected_done = [
        db.add_task_to_list(daylist_id=active_lid, title="third", estimate=DUR_20M)
    ]
    for task_id in expected_done:
        db.complete_task(id=task_id)

    response = client.get("/today", headers=auth_headers(any_user))
    assert response.status_code == 200

    data = response.json()
    # return unexpired list
    assert data["id"] == active_lid
    assert datetime.fromisoformat(data["expiry"]) > now
    # return newly created list without old info
    assert [task["id"] for task in data["pending_tasks"]] == expected_pending
    assert [task["id"] for task in data["done_tasks"]] == expected_done


def test_get_list_empty(client, db, any_user):
    """An active list exists for this user - but has no tasks."""
    now = datetime.now(LOCAL_TZ)
    # current list but also old expired list
    old_lid = db.add_daylist(user_id=any_user["id"], expiry=OLD_TIME)
    db.add_task_to_list(daylist_id=old_lid, title="old", estimate=DUR_20M)

    active_lid = db.add_daylist(user_id=any_user["id"], expiry=now + DUR_23HR)

    response = client.get("/today", headers=auth_headers(any_user))
    assert response.status_code == 200

    data = response.json()
    # return unexpired list
    assert data["id"] == active_lid
    assert datetime.fromisoformat(data["expiry"]) > now
    # return blank created list without old info
    assert data["pending_tasks"] == []
    assert data["done_tasks"] == []


# GET today's timeline/agenda


def test_get_agenda_no_user(client):
    """User not found."""
    response = client.get("/agenda")
    assert response.status_code == 401


def test_get_agenda_none(client, any_user):
    """No previous list for this user, just returns empty agenda."""
    response = client.get("/agenda", headers=auth_headers(any_user))
    assert response.status_code == 201

    data = response.json()
    # empty agenda, no warning with finish time = now (prev minute)
    assert data["timeline"] == []
    assert data["past_expiry"] is False
    now = datetime.now(LOCAL_TZ)
    assert datetime.fromisoformat(data["finish"]) <= now
    assert datetime.fromisoformat(data["expiry"]) >= now


def test_get_agenda_expired(client, db, any_user):
    """An expired list exists for this user - list/agenda should be freshly created."""
    old_lid = db.add_daylist(user_id=any_user["id"], expiry=OLD_TIME)
    db.add_task_to_list(daylist_id=old_lid, title="first", estimate=DUR_20M)
    done = db.add_task_to_list(daylist_id=old_lid, title="done", estimate=DUR_20M)
    db.complete_task(id=done)

    response = client.get("/agenda", headers=auth_headers(any_user))
    assert response.status_code == 201

    data = response.json()
    # new empty agenda, no warning with finish time = now (prev minute)
    assert data["timeline"] == []
    assert data["past_expiry"] is False
    now = datetime.now(LOCAL_TZ)
    assert datetime.fromisoformat(data["finish"]) <= now
    assert datetime.fromisoformat(data["expiry"]) >= now


def test_get_agenda_empty(client, db, any_user):
    """An active list exists for this user - return the agenda."""
    now = datetime.now(LOCAL_TZ)
    # current list but also old expired list
    old_lid = db.add_daylist(user_id=any_user["id"], expiry=OLD_TIME)
    db.add_task_to_list(daylist_id=old_lid, title="old", estimate=DUR_20M)
    done = db.add_task_to_list(daylist_id=old_lid, title="done", estimate=DUR_20M)
    db.complete_task(id=done)

    db.add_daylist(user_id=any_user["id"], expiry=now + DUR_23HR)
    expected_pending = []

    response = client.get("/agenda", headers=auth_headers(any_user))
    assert response.status_code == 200

    data = response.json()
    # empty agenda, no warning with finish time = now (prev minute)
    assert data["timeline"] == expected_pending
    assert data["past_expiry"] is False
    assert datetime.fromisoformat(data["finish"]) <= now
    assert datetime.fromisoformat(data["expiry"]) >= now


def test_get_agenda_active(client, db, any_user):
    """An active list exists for this user - return it with nested tasks."""
    now = datetime.now(LOCAL_TZ)
    # current list but also old expired list
    old_lid = db.add_daylist(user_id=any_user["id"], expiry=OLD_TIME)
    db.add_task_to_list(daylist_id=old_lid, title="old", estimate=DUR_20M)

    active_lid = db.add_daylist(user_id=any_user["id"], expiry=now + DUR_23HR)
    expected_pending = [
        db.add_task_to_list(daylist_id=active_lid, title="first", estimate=DUR_20M),
        db.add_task_to_list(daylist_id=active_lid, title="second", estimate=DUR_20M),
    ]
    expected_done = [
        db.add_task_to_list(daylist_id=active_lid, title="third", estimate=DUR_20M)
    ]
    for task_id in expected_done:
        db.complete_task(id=task_id)

    response = client.get("/agenda", headers=auth_headers(any_user))
    assert response.status_code == 200

    data = response.json()
    # should contain the agenda for pending items only
    assert len(data["timeline"]) == len(expected_pending)
    assert data["past_expiry"] is False
    assert datetime.fromisoformat(data["finish"]) >= now
    assert datetime.fromisoformat(data["expiry"]) >= now


# Test providing custom expiry for both endpoints


@pytest.mark.parametrize("endpoint", ["/today", "/agenda"])
def test_get_list_custom_expiry(client, endpoint, anon_user):
    """Create a new list that expires at a custom time."""
    # provide custom expiry time
    sample_time = time.fromisoformat("20:16:00+06:00")
    sample_timestr = sample_time.isoformat()
    params = {"expire": sample_timestr}

    response = client.get(endpoint, params=params, headers=auth_headers(anon_user))
    assert response.status_code == 201

    data = response.json()
    # new list's expiry time matches what was provided
    result_expiry = datetime.fromisoformat(data["expiry"])
    result_expiry_rezoned = result_expiry.astimezone(sample_time.tzinfo)
    assert result_expiry_rezoned.hour == sample_time.hour
    assert result_expiry_rezoned.minute == sample_time.minute


@pytest.mark.parametrize("endpoint", ["/today", "/agenda"])
def test_get_list_irrelevant_expiry(client, db, endpoint, anon_user):
    """An active list exists for this user - adding custom expiry has no effect."""
    expiry = datetime.now(LOCAL_TZ) + DUR_23HR
    db.add_daylist(user_id=anon_user["id"], expiry=expiry)
    # provide custom expiry time
    sample_time = time.fromisoformat("12:16:00+06:00")
    sample_timestr = sample_time.isoformat()
    params = {"expire": sample_timestr}

    response = client.get(endpoint, params=params, headers=auth_headers(anon_user))
    assert response.status_code == 200

    data = response.json()
    # return original list with original expiry, not custom expiry
    assert data["expiry"] != sample_timestr
    assert data["expiry"] == expiry.isoformat()


@pytest.mark.parametrize("endpoint", ["/today", "/agenda"])
def test_get_list_expiry_no_tz(client, db, endpoint, anon_user):
    """Providing a custom expiry without timezone fails."""
    db.add_daylist(user_id=anon_user["id"], expiry=datetime.now(LOCAL_TZ) + DUR_23HR)
    # provide custom expiry time
    sample_time = time.fromisoformat("12:16:00")
    sample_timestr = sample_time.isoformat()
    params = {"expire": sample_timestr}

    response = client.get(endpoint, params=params, headers=auth_headers(anon_user))
    assert response.status_code == 422
    # has error message in correct schema
    data = response.json()
    assert "detail" in data
    assert "msg" in data["detail"][0]
