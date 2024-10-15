from datetime import datetime, timedelta
import pytest

from src.utils import system_tz
from test.helpers import auth_headers

LOCAL_TZ = system_tz()
OLD_TIME = datetime(year=2022, month=2, day=22, hour=2, tzinfo=LOCAL_TZ)
FUTURE_TIME = datetime.now(LOCAL_TZ) + timedelta(hours=12)


@pytest.fixture(autouse=True)
def db_setup_teardown(db):
    uid = db.add_anon_user()
    lid = db.add_daylist(user_id=uid, expiry=OLD_TIME)
    db.add_task_to_list(daylist_id=lid, title="test1", estimate=timedelta(minutes=5))
    db.add_daylist(user_id=uid, expiry=FUTURE_TIME)
    db.add_task_for_user(user_id=uid, title="test2", estimate=timedelta(minutes=5))
    db.add_task_for_user(user_id=uid, title="test3", estimate=timedelta(minutes=5))

    uid = db.add_registered_user(email="pippin@lotr.com", password_hash="foolofatook")
    db.add_daylist(user_id=uid, expiry=FUTURE_TIME)
    db.add_task_for_user(user_id=uid, title="test4", estimate=timedelta(minutes=5))

    try:
        yield
    finally:
        db.delete_all_users()


# POST: add new task


def test_post_add_task_no_auth(client, db, anon_user):
    db.add_daylist(user_id=anon_user["id"], expiry=FUTURE_TIME)
    sample_name = "my new task"
    sample_time = "PT1H15M"
    input_data = {"title": sample_name, "estimate": sample_time}

    response = client.post("/task", json=input_data)
    assert response.status_code == 401


@pytest.mark.parametrize("prior_listsize", [0, 1])
def test_post_add_task(client, db, any_user, prior_listsize):
    """Create a new task for today's empty list."""
    # a list already exists for this user
    active_lid = db.add_daylist(user_id=any_user["id"], expiry=FUTURE_TIME)
    # have some tasks in the list already?
    for _ in range(prior_listsize):
        db.add_task_to_list(daylist_id=active_lid, title="some task", estimate="PT20M")

    sample_name = "my new task"
    sample_time = "PT1H15M"
    input_data = {"title": sample_name, "estimate": sample_time}

    response = client.post("/task", json=input_data, headers=auth_headers(any_user))
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
def test_post_add_task_invalid(client, db, bad_task, anon_user):
    """Can't create a task that fails basic validation."""
    # a list already exists for this user
    db.add_daylist(user_id=anon_user["id"], expiry=FUTURE_TIME)

    response = client.post("/task", json=bad_task, headers=auth_headers(anon_user))
    assert response.status_code == 422
    # has error message in correct schema
    data = response.json()
    assert "detail" in data
    assert "msg" in data["detail"][0]


def test_post_add_task_no_list(client, anon_user):
    """Attempt to create a task but list does not exist yet."""
    sample_name = "my new task"
    sample_time = "PT1H15M"
    input_data = {"title": sample_name, "estimate": sample_time}

    response = client.post("/task", json=input_data, headers=auth_headers(anon_user))
    assert response.status_code == 404
    # has error message in correct schema
    data = response.json()
    assert "detail" in data
    assert "msg" in data["detail"][0]


# POST: mark task done


def test_post_do_task_no_auth(client, db, anon_user):
    db.add_daylist(user_id=anon_user["id"], expiry=FUTURE_TIME)
    # task exists but no auth
    task_id = db.add_task_for_user(
        user_id=anon_user["id"], title="forbidden", estimate=timedelta(hours=1)
    )

    response = client.post(f"/task/{task_id}/do")
    assert response.status_code == 401


@pytest.mark.parametrize("task_is_done", (True, False))
def test_post_do_task(client, db, any_user, task_is_done):
    """Mark a single task as done: both pending and done tasks work."""
    active_lid = db.add_daylist(user_id=any_user["id"], expiry=FUTURE_TIME)
    name = "test"
    time = "PT1H15M"
    task_id = db.add_task_to_list(daylist_id=active_lid, title=name, estimate=time)
    # works for tasks regardless of status
    if task_is_done:
        db.complete_task(id=task_id)

    response = client.post(f"/task/{task_id}/do", headers=auth_headers(any_user))
    assert response.status_code == 200

    data = response.json()
    # return completion message
    assert "success" in data
    assert data["success"] == [task_id]
    assert db.get_task(id=task_id)["done"] is True


def test_post_do_task_none(client, any_user):
    """Marking a task done but task doesn't exist."""
    response = client.post("/task/0/do", headers=auth_headers(any_user))
    # validation error status
    assert response.status_code == 422
    # with error message in correct location
    data = response.json()
    assert "detail" in data
    assert "msg" in data["detail"][0]


def test_post_do_task_bad_list(client, db, any_user):
    """Marking a task done but task is not in today's list."""
    old_lid = db.add_daylist(user_id=any_user["id"], expiry=OLD_TIME)
    task_id = db.add_task_to_list(daylist_id=old_lid, title="old", estimate="PT20M")
    db.add_daylist(user_id=any_user["id"], expiry=FUTURE_TIME)

    response = client.post(f"/task/{task_id}/do", headers=auth_headers(any_user))
    # validation error status
    assert response.status_code == 422
    # with error message in correct location
    data = response.json()
    assert "detail" in data
    assert "msg" in data["detail"][0]


def test_post_do_task_bad_user(client, db, any_user):
    """Marking a task done but task is for a different user."""
    other_uid = db.add_anon_user()
    db.add_daylist(user_id=other_uid, expiry=FUTURE_TIME)
    other_task_id = db.add_task_for_user(
        user_id=other_uid, title="forbidden", estimate=timedelta(minutes=1)
    )

    response = client.post(f"/task/{other_task_id}/do", headers=auth_headers(any_user))
    # validation error status
    assert response.status_code == 422


# POST: bulk mark task done


def test_post_bulk_do_task_no_auth(client, db, anon_user):
    db.add_daylist(user_id=anon_user["id"], expiry=FUTURE_TIME)
    # task exists but no auth
    attempted_tasks = [
        db.add_task_for_user(
            user_id=anon_user["id"], title="forbidden", estimate=timedelta(hours=1)
        )
    ]

    response = client.post("/task/bulk/do", json=attempted_tasks)
    assert response.status_code == 401


def test_post_bulk_do_tasks(client, db, any_user):
    """Mark a list of multiple tasks as done."""
    active_lid = db.add_daylist(user_id=any_user["id"], expiry=FUTURE_TIME)
    expected_pending = [
        db.add_task_to_list(daylist_id=active_lid, title="first", estimate="PT20M"),
        db.add_task_to_list(daylist_id=active_lid, title="second", estimate="PT20M"),
    ]

    response = client.post(
        "/task/bulk/do", json=expected_pending, headers=auth_headers(any_user)
    )
    assert response.status_code == 200

    # return completion message
    data = response.json()
    assert "success" in data
    assert data["success"] == expected_pending


def test_post_bulk_do_tasks_bad_missing(client, db, any_user):
    """Mark a list of tasks as done but one is invalid, doesn't exist."""
    active_lid = db.add_daylist(user_id=any_user["id"], expiry=FUTURE_TIME)
    attempted_tasks = [
        db.add_task_to_list(daylist_id=active_lid, title="first", estimate="PT20M"),
        0,
    ]

    response = client.post(
        "/task", json=attempted_tasks, headers=auth_headers(any_user)
    )
    # validation error status
    assert response.status_code == 422
    # with error message in correct location
    data = response.json()
    assert "detail" in data
    assert "msg" in data["detail"][0]


def test_post_bulk_do_tasks_bad_list(client, db, known_user):
    """Mark a list of tasks as done but one is invalid, wrong list."""
    old_lid = db.add_daylist(user_id=known_user["id"], expiry=OLD_TIME)
    old_task_id = db.add_task_to_list(daylist_id=old_lid, title="old", estimate="PT20M")
    active_lid = db.add_daylist(user_id=known_user["id"], expiry=FUTURE_TIME)
    attempted_tasks = [
        db.add_task_to_list(daylist_id=active_lid, title="first", estimate="PT20M"),
        old_task_id,
    ]

    response = client.post(
        "/task", json=attempted_tasks, headers=auth_headers(known_user)
    )
    # validation error status
    assert response.status_code == 422
    # with error message in correct location
    data = response.json()
    assert "detail" in data
    assert "msg" in data["detail"][0]


def test_post_bulk_do_tasks_all_bad_user(client, db, any_user):
    """Marking list of tasks done but task is for a different user."""
    other_uid = db.add_anon_user()
    db.add_daylist(user_id=other_uid, expiry=FUTURE_TIME)
    attempted_tasks = [
        db.add_task_for_user(
            user_id=other_uid, title="forbidden", estimate=timedelta(minutes=1)
        ),
        db.add_task_for_user(
            user_id=other_uid, title="nope", estimate=timedelta(minutes=1)
        ),
    ]

    response = client.post(
        "/task/bulk/do", json=attempted_tasks, headers=auth_headers(any_user)
    )
    # validation error if all tasks are bad
    assert response.status_code == 422
    # give a message with specific problem ids
    data = response.json()
    assert "detail" in data
    assert "msg" in data["detail"][0]
    for task_id in attempted_tasks:
        assert str(task_id) in data["detail"][0]["msg"]


def test_post_bulk_do_tasks_some_invalid(client, db, any_user):
    """Marking list of tasks done but some are for a different user."""
    other_uid = db.add_anon_user()

    db.add_daylist(user_id=any_user["id"], expiry=FUTURE_TIME)
    db.add_daylist(user_id=other_uid, expiry=FUTURE_TIME)

    attempted_tasks = [
        db.add_task_for_user(
            user_id=other_uid, title="forbidden", estimate=timedelta(minutes=1)
        ),
        db.add_task_for_user(
            user_id=any_user["id"], title="ok", estimate=timedelta(minutes=1)
        ),
    ]

    response = client.post(
        "/task/bulk/do", json=attempted_tasks, headers=auth_headers(any_user)
    )
    # validation error if tasks are partially bad
    assert response.status_code == 422
    # give a message with specific problem ids
    data = response.json()
    assert "detail" in data
    assert "msg" in data["detail"][0]
    assert str(attempted_tasks[0]) in data["detail"][0]["msg"]
    assert str(attempted_tasks[1]) not in data["detail"][0]["msg"]


# POST: undo task


def test_post_undo_task_no_auth(client, db, anon_user):
    db.add_daylist(user_id=anon_user["id"], expiry=FUTURE_TIME)
    # task exists but no auth
    task_id = db.add_task_for_user(
        user_id=anon_user["id"], title="forbidden", estimate=timedelta(hours=1)
    )
    db.complete_task(id=task_id)

    response = client.post(f"/task/{task_id}/undo")
    assert response.status_code == 401


def test_post_undo_task(client, db, any_user):
    """Mark a single done task as pending."""
    active_lid = db.add_daylist(user_id=any_user["id"], expiry=FUTURE_TIME)
    name = "test"
    time = "PT1H15M"
    task_id = db.add_task_to_list(daylist_id=active_lid, title=name, estimate=time)
    db.complete_task(id=task_id)

    response = client.post(f"/task/{task_id}/undo", headers=auth_headers(any_user))
    assert response.status_code == 200

    data = response.json()
    # return completion message
    assert "success" in data
    assert data["success"] == [task_id]
    assert db.get_task(id=task_id)["done"] is False


def test_post_undo_task_pending(client, db, any_user):
    """Mark a pending task as pending: no change."""
    active_lid = db.add_daylist(user_id=any_user["id"], expiry=FUTURE_TIME)
    name = "test"
    time = "PT1H15M"
    task_id = db.add_task_to_list(daylist_id=active_lid, title=name, estimate=time)
    db.add_task_to_list(daylist_id=active_lid, title="buffer", estimate=time)
    initial_pending = list(db.get_pending_tasks(user_id=any_user["id"]))

    response = client.post(f"/task/{task_id}/undo", headers=auth_headers(any_user))
    assert response.status_code == 200

    data = response.json()
    # return completion message
    assert "success" in data
    # task was not changed, not in result
    assert data["success"] == []
    # task is still pending
    assert db.get_task(id=task_id)["done"] is False
    # task list order is unaffected
    final_pending = list(db.get_pending_tasks(user_id=any_user["id"]))
    assert initial_pending == final_pending


def test_post_undo_task_none(client, known_user):
    """Marking a task pending but task doesn't exist."""
    response = client.post("/task/0/undo", headers=auth_headers(known_user))
    # validation error status
    assert response.status_code == 422
    # with error message in correct location
    data = response.json()
    assert "detail" in data
    assert "msg" in data["detail"][0]


def test_post_undo_task_bad_list(client, db, any_user):
    """Marking a task pending but task is not in today's list."""
    old_lid = db.add_daylist(user_id=any_user["id"], expiry=OLD_TIME)
    task_id = db.add_task_to_list(daylist_id=old_lid, title="old", estimate="PT20M")
    db.add_daylist(user_id=any_user["id"], expiry=FUTURE_TIME)

    response = client.post(f"/task/{task_id}/undo", headers=auth_headers(any_user))
    # validation error status
    assert response.status_code == 422
    # with error message in correct location
    data = response.json()
    assert "detail" in data
    assert "msg" in data["detail"][0]


def test_post_undo_task_bad_user(client, db, any_user):
    """Marking a task pending but task is for a different user."""
    other_uid = db.add_anon_user()
    db.add_daylist(user_id=other_uid, expiry=FUTURE_TIME)
    other_task_id = db.add_task_for_user(
        user_id=other_uid, title="forbidden", estimate=timedelta(minutes=1)
    )
    db.complete_task(id=other_task_id)

    response = client.post(
        f"/task/{other_task_id}/undo", headers=auth_headers(any_user)
    )
    # validation error status
    assert response.status_code == 422
