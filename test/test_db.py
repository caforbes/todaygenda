"""For database function testing.

Interacts with the test database.
"""

from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError
import pytest

FUTURE_TIME = "2122-02-22T00:00:00+05"
OLD_TIME = "2020-02-20 00:00:00+05"
TEST_EMAIL = "test@example.com"


@pytest.fixture(autouse=True)
def teardown(db):
    try:
        yield
    finally:
        db.delete_all_users()


# General


def test_blank(db):
    """The test db begins blank with no users in it, and the function counts."""
    assert db.count_users() == 0


# User functions


class TestUsers:

    @staticmethod
    @pytest.fixture()
    def seed(db):
        db.add_anon_user()
        db.add_registered_user(email=TEST_EMAIL, password_hash="12345")
        yield

    # get
    # Note: counts and get_anon_user are for TEST purposes

    @pytest.mark.parametrize(
        "fn_string", ["count_users", "count_anon_users", "count_registered_users"]
    )
    def test_count_users_none(cls, db, fn_string):
        count_function = getattr(db, fn_string)
        assert count_function() == 0

    @pytest.mark.parametrize(
        "fn_string", ["count_users", "count_anon_users", "count_registered_users"]
    )
    def test_count_users_some(cls, db, seed, fn_string):
        count_function = getattr(db, fn_string)
        assert count_function() > 0

    def test_read_any_anon_user_none(cls, db):
        result = db.get_anon_user()
        assert result is None

    def test_read_any_anon_user(cls, db, seed):
        # Note: returns random user; rest of app should get user by id or email
        assert db.count_anon_users() > 0
        result = db.get_anon_user()
        # good user returns dict of user attrs
        assert isinstance(result, dict)
        assert "id" in result and result["id"] > 0

    def test_read_user_anon(cls, db, seed):
        uid = db.add_anon_user()
        result = db.get_user(id=uid)
        # good user returns dict of user attrs
        assert isinstance(result, dict)
        assert "id" in result and result["id"] > 0
        assert "email" in result and result["email"] is None
        assert "password_hash" in result and result["password_hash"] is None

    def test_read_user_reg(cls, db, seed):
        test_value = "lalala"
        uid = db.add_registered_user(email=test_value, password_hash=test_value)
        result = db.get_user(id=uid)
        # good user returns dict of user attrs
        assert isinstance(result, dict)
        assert "id" in result and result["id"] > 0
        assert "email" in result and result["email"] == test_value
        assert "password_hash" in result and result["password_hash"] == test_value

    def test_user_read_invalid(cls, db):
        result = db.get_user(id=-1)
        # bad user returns none
        assert result is None

    def test_read_registered_user(cls, db, seed):
        # values from seed data
        test_pw = "12345"
        result = db.get_registered_user(email=TEST_EMAIL)
        # good user returns dict of user attrs
        assert isinstance(result, dict)
        # has requested values
        assert "id" in result
        assert "email" in result
        assert "password_hash" in result
        assert "registered_at" in result
        # values are as expected
        assert result["email"] == TEST_EMAIL
        assert result["password_hash"] == test_pw
        assert isinstance(result["registered_at"], datetime)

    def test_read_registered_user_invalid(cls, db, seed):
        result = db.get_registered_user(email="misc")
        # bad user returns None
        assert result is None

    # add

    def test_add_anon_user(cls, db):
        result = db.add_anon_user()
        # successfully add user
        assert db.count_anon_users() == 1
        # return id of the new user, not placeholder
        assert isinstance(result, int) and result > 0
        # once more for good measure
        result = db.add_anon_user()
        assert db.count_anon_users() == 2

    def test_add_registered_user(cls, db, seed):
        test_email = "my@email.com"
        test_pw = "hashyhash"
        uid = db.add_registered_user(email=test_email, password_hash=test_pw)
        # returns new user id
        assert isinstance(uid, int)

        result = db.get_user(id=uid)
        # good user returns dict of user attrs
        assert isinstance(result, dict)
        # has requested values
        assert "id" in result
        assert "email" in result
        assert "password_hash" in result
        assert "registered_at" in result
        # values are as expected
        assert result["id"] == uid
        assert result["email"] == test_email
        assert result["password_hash"] == test_pw
        assert isinstance(result["registered_at"], datetime)

    def test_add_registered_user_duplicate(cls, db, seed):
        test_pw = "hashyhash"

        with pytest.raises(IntegrityError):
            db.add_registered_user(email=TEST_EMAIL, password_hash=test_pw)

    # update

    def test_register_anon_user(cls, db, seed):
        uid = db.get_anon_user()["id"]

        sample_email = "gimli@gloin.com"
        sample_hash = "123423409280349"

        result = db.register_anon_user(
            id=uid, email=sample_email, password_hash=sample_hash
        )
        assert result == 1
        user = db.get_user(id=uid)
        assert user["email"] == sample_email

    def test_register_anon_user_invalid_known(cls, db, seed):
        uid = db.get_registered_user(email=TEST_EMAIL)["id"]

        result = db.register_anon_user(id=uid, email="new@email.com", password_hash="x")
        assert result == 0
        user = db.get_user(id=uid)
        assert user["email"] == TEST_EMAIL

    def test_register_anon_user_duplicate(cls, db, seed):
        uid = db.get_anon_user()["id"]

        with pytest.raises(IntegrityError):
            db.register_anon_user(id=uid, email=TEST_EMAIL, password_hash="x")

    def test_register_anon_user_bad_param(cls, db, seed):
        uid = db.get_registered_user(email=TEST_EMAIL)["id"]

        result = db.register_anon_user(
            id=uid, email="new@email.com", password_hash=None
        )

        assert result == 0
        user = db.get_user(id=uid)
        assert user["email"] == TEST_EMAIL

    # delete

    def test_delete_user_anon(cls, db, seed):
        uid = db.get_anon_user()["id"]
        result = db.delete_user(id=uid)
        assert result == 1

    def test_delete_user_known(cls, db, seed):
        uid = db.get_registered_user(email=TEST_EMAIL)["id"]
        result = db.delete_user(id=uid)
        assert result == 1

    def test_delete_user_invalid(cls, db):
        result = db.delete_user(id=-1)
        assert result == 0

    def test_delete_all_users(cls, db, seed):
        result = db.delete_all_users()
        assert result != 0
        assert db.count_users() == 0


# Daylist functions


class TestDaylist:

    @staticmethod
    @pytest.fixture(autouse=True)
    def seed(db):
        userid = db.add_anon_user()
        db.add_daylist(user_id=userid, expiry="2014-02-14T00:00:00+05")
        db.add_daylist(user_id=userid, expiry="2024-07-24T00:00:00+05")

        userid = db.add_registered_user(email="test@example.com", password_hash="12345")
        db.add_daylist(user_id=userid, expiry="2022-03-14T00:00:00-04")
        db.add_daylist(user_id=userid, expiry="2024-08-03T00:00:00+07")

        yield

    @staticmethod
    @pytest.fixture(params=[True, False])  # is user registered?
    def uid(db, request) -> int:
        if request.param:
            uid = db.add_registered_user(email="sam@lotr.com", password_hash="mrfrodo")
        else:
            uid = db.add_anon_user()
        return uid

    # get

    def test_get_active_daylist_bad_user(cls, db):
        result = db.get_active_daylist(user_id=-1)
        assert result is None

    def test_get_active_daylist_none(cls, db, uid):
        result = db.get_active_daylist(user_id=uid)
        assert result is None

    def test_get_active_daylist_old(cls, db, uid):
        db.add_daylist(user_id=uid, expiry=OLD_TIME)
        result = db.get_active_daylist(user_id=uid)
        assert result is None

    def test_get_active_daylist(cls, db, uid):
        expiry_str = FUTURE_TIME
        db.add_daylist(user_id=uid, expiry=expiry_str)

        result = db.get_active_daylist(user_id=uid)
        assert isinstance(result, dict)
        assert "id" in result
        assert result["expiry"] == datetime.fromisoformat(expiry_str)

    # add

    def test_add_daylist(cls, db, uid):
        expiry_str = FUTURE_TIME
        db.add_daylist(user_id=uid, expiry=expiry_str)

        result = db.add_daylist(user_id=uid, expiry=expiry_str)
        # successful creation + return id for both registered and anon
        assert isinstance(result, int) and result > 0

    @pytest.mark.parametrize(
        "expiry",
        [
            FUTURE_TIME,
            datetime.fromisoformat(FUTURE_TIME),
        ],
    )
    def test_add_daylist_types(cls, db, uid, expiry):
        result = db.add_daylist(user_id=uid, expiry=expiry)
        # successful creation + return id for both types
        assert isinstance(result, int) and result > 0

    @pytest.mark.parametrize("bad_uid", [-1, None, 1_000_000])
    def test_add_daylist_bad_user(cls, db, bad_uid):
        uid = bad_uid
        expiry_str = FUTURE_TIME

        # inputting bad user raises error
        with pytest.raises(IntegrityError):
            db.add_daylist(user_id=uid, expiry=expiry_str)


# Task functions


class TestTask:

    @staticmethod
    @pytest.fixture(autouse=True)
    def seed(db):
        userid = db.add_anon_user()
        db.add_daylist(user_id=userid, expiry=FUTURE_TIME)
        db.add_task_for_user(user_id=userid, title="A1", estimate="PT1M")
        db.add_task_for_user(user_id=userid, title="A2", estimate="PT1M")

        userid = db.add_registered_user(email="test@example.com", password_hash="12345")
        db.add_daylist(user_id=userid, expiry=FUTURE_TIME)
        db.add_task_for_user(user_id=userid, title="B1", estimate="PT1H")

        yield

    @staticmethod
    @pytest.fixture(params=[True, False])  # is user registered?
    def uid(db, request) -> int:
        if request.param:
            uid = db.add_registered_user(email="sam@lotr.com", password_hash="ring")
        else:
            uid = db.add_anon_user()
        return uid

    @staticmethod
    @pytest.fixture
    def lid(db, uid):
        return db.add_daylist(user_id=uid, expiry=FUTURE_TIME)

    def test_get_task(cls, db, lid):
        the_title = "ssss"
        the_estimate = "PT1M"
        task_id = db.add_task_to_list(
            daylist_id=lid, title=the_title, estimate=the_estimate
        )

        result = db.get_task(id=task_id)
        assert result["title"] == the_title
        assert isinstance(result["estimate"], timedelta)

    def test_get_task_invalid(cls, db):
        result = db.get_task(id=0)
        assert result is None

    def test_get_active_tasks_for_user(cls, db, uid, lid):
        task_ids = [
            db.add_task_for_user(user_id=uid, title="one", estimate="PT1H5M"),
            db.add_task_for_user(user_id=uid, title="two", estimate="PT1H5M"),
        ]
        done_ids = [
            db.add_task_for_user(user_id=uid, title="cat", estimate="PT1H5M"),
        ]
        for task_id in done_ids:
            db.complete_task(id=task_id)

        result = list(db.get_current_tasks(user_id=uid))

        # all tasks are returned
        expected_ids = task_ids + done_ids
        assert len(result) == len(expected_ids)
        assert expected_ids == [task["id"] for task in result]

    def test_get_active_tasks_ordering(cls, db, uid, lid):
        task_ids = [
            db.add_task_for_user(user_id=uid, title="one", estimate="PT1H5M"),
            db.add_task_for_user(user_id=uid, title="two", estimate="PT1H5M"),
        ]
        # BOOKMARK: add test that these are in order after editing might affect
        done_ids = [
            db.add_task_for_user(user_id=uid, title="cat", estimate="PT1H5M"),
            db.add_task_for_user(user_id=uid, title="dog", estimate="PT1H5M"),
        ]
        done_ids.reverse()  # check that finish time is different than add time
        for task_id in done_ids:
            db.complete_task(id=task_id)

        result = list(db.get_current_tasks(user_id=uid))

        # all tasks are returned
        expected_ids = task_ids + done_ids
        assert len(result) == len(expected_ids)
        assert expected_ids == [task["id"] for task in result]

    def test_get_active_tasks_for_user_no_list(cls, db, uid):
        result = db.get_current_tasks(user_id=uid)
        result = list(result)
        assert len(result) == 0

    def test_get_active_tasks_for_user_empty(cls, db, uid, lid):
        result = db.get_current_tasks(user_id=uid)
        result = list(result)
        assert len(result) == 0

    def test_get_active_tasks_for_user_expired(cls, db, uid):
        lid = db.add_daylist(user_id=uid, expiry=OLD_TIME)
        db.add_task_to_list(daylist_id=lid, title="first", estimate="PT1H5M")
        db.add_task_to_list(daylist_id=lid, title="second", estimate="PT1H5M")

        result = db.get_current_tasks(user_id=uid)
        result = list(result)
        assert len(result) == 0

    def test_get_pending_tasks_for_user(cls, db, uid, lid):
        task_ids = [
            db.add_task_for_user(user_id=uid, title="one", estimate="PT1H5M"),
            db.add_task_for_user(user_id=uid, title="two", estimate="PT1H5M"),
            db.add_task_for_user(user_id=uid, title="cat", estimate="PT1H5M"),
        ]
        done_ids = [
            db.add_task_for_user(user_id=uid, title="cat", estimate="PT1H5M"),
            db.add_task_for_user(user_id=uid, title="dog", estimate="PT1H5M"),
        ]
        for task_id in done_ids:
            db.complete_task(id=task_id)

        result = db.get_pending_tasks(user_id=uid)
        result = list(result)

        # only pending tasks are returned
        assert len(result) == len(task_ids)
        assert task_ids == [task["id"] for task in result]

    # BOOKMARK: check ordering once editing is available

    def test_get_pending_tasks_for_user_no_list(cls, db, uid):
        result = db.get_pending_tasks(user_id=uid)
        result = list(result)
        assert len(result) == 0

    def test_get_pending_tasks_for_user_empty(cls, db, uid, lid):
        result = db.get_pending_tasks(user_id=uid)
        result = list(result)
        assert len(result) == 0

    def test_get_pending_tasks_for_user_expired(cls, db, uid):
        lid = db.add_daylist(user_id=uid, expiry=OLD_TIME)
        db.add_task_to_list(daylist_id=lid, title="first", estimate="PT1H5M")
        db.add_task_to_list(daylist_id=lid, title="second", estimate="PT1H5M")

        result = db.get_pending_tasks(user_id=uid)
        result = list(result)
        assert len(result) == 0

    def test_get_done_tasks_for_user(cls, db, uid, lid):
        db.add_task_for_user(user_id=uid, title="one", estimate="PT1H5M")
        extra = db.add_task_for_user(user_id=uid, title="two", estimate="PT1H5M")
        done_ids = [
            db.add_task_for_user(user_id=uid, title="cat", estimate="PT1H5M"),
            db.add_task_for_user(user_id=uid, title="dog", estimate="PT1H5M"),
            extra,
        ]
        for task_id in done_ids:
            db.complete_task(id=task_id)

        result = db.get_done_tasks(user_id=uid)
        result = list(result)

        # only done tasks are returned
        assert len(result) == len(done_ids)
        assert done_ids == [task["id"] for task in result]

    def test_get_done_tasks_for_user_ordering(cls, db, uid, lid):
        done_ids = [
            db.add_task_for_user(user_id=uid, title="cat", estimate="PT1H5M"),
            db.add_task_for_user(user_id=uid, title="dog", estimate="PT1H5M"),
            db.add_task_for_user(user_id=uid, title="fly", estimate="PT1H5M"),
        ]
        done_ids.reverse()  # finish time != creation time
        for task_id in done_ids:
            db.complete_task(id=task_id)

        result = db.get_done_tasks(user_id=uid)
        result = list(result)

        # tasks in finish order not creation order
        assert len(result) == len(done_ids)
        assert done_ids == [task["id"] for task in result]

    # add

    def test_add_usertask_no_list(cls, db, uid):
        with pytest.raises(IntegrityError):
            db.add_task_for_user(user_id=uid, title="first", estimate="PT1H5M")

    def test_add_usertask_ordered(cls, db, uid, lid):
        assert db.count_tasks(daylist_id=lid) == 0
        result = db.add_task_for_user(user_id=uid, title="first", estimate="PT1H5M")

        # successful insertion returns task index
        assert isinstance(result, int) and result > 0
        result = db.add_task_for_user(user_id=uid, title="second", estimate="PT1H5M")
        result = db.add_task_for_user(user_id=uid, title="third", estimate="PT1H5M")

        # multiple inserts are successful
        assert db.count_tasks(daylist_id=lid) == 3

    def test_add_listtask_no_list(cls, db, lid):
        db.add_task_to_list(daylist_id=lid, title="first", estimate="PT1H5M")

    def test_add_listtask_ordered(cls, db, lid):
        assert db.count_tasks(daylist_id=lid) == 0

        # successful insertion returns task index
        result = db.add_task_to_list(daylist_id=lid, title="first", estimate="PT1H5M")
        assert isinstance(result, int) and result > 0

        # multiple inserts are successful
        result = db.add_task_to_list(daylist_id=lid, title="second", estimate="PT1H5M")
        result = db.add_task_to_list(daylist_id=lid, title="third", estimate="PT1H5M")
        assert db.count_tasks(daylist_id=lid) == 3

    # update

    def test_complete_task(cls, db, lid):
        new_id = db.add_task_to_list(daylist_id=lid, title="tester", estimate="PT10M")
        task = db.get_task(id=new_id)
        assert task["done"] is False

        result = db.complete_task(id=new_id)
        assert result == 1

        task = db.get_task(id=new_id)
        assert task["done"] is True

    def test_complete_task_useless(cls, db, lid):
        new_id = db.add_task_to_list(daylist_id=lid, title="tester", estimate="PT10M")
        db.complete_task(id=new_id)

        # still affect the task and update metadata
        result = db.complete_task(id=new_id)
        assert result == 1
        task = db.get_task(id=new_id)
        assert task["done"] is True

    def test_complete_task_invalid(cls, db, lid):
        result = db.complete_task(id=0)
        assert result == 0

    def test_uncomplete_task(cls, db, lid):
        new_id = db.add_task_to_list(daylist_id=lid, title="tester", estimate="PT10M")
        db.complete_task(id=new_id)
        initial_task = db.get_task(id=new_id)
        assert initial_task["done"] is True

        result = db.uncomplete_task(id=new_id)
        assert result == 1

        task = db.get_task(id=new_id)
        assert task["done"] is False

    def test_uncomplete_task_end_of_list(cls, db, uid, lid):
        tasks = [
            db.add_task_to_list(daylist_id=lid, title="tester", estimate="PT10M"),
            db.add_task_to_list(daylist_id=lid, title="2", estimate="PT10M"),
            db.add_task_to_list(daylist_id=lid, title="3", estimate="PT10M"),
        ]
        target = tasks[0]
        db.complete_task(id=target)
        initial_task = db.get_task(id=target)
        assert initial_task["done"] is True

        # task is affected, return num affected (=1)
        result = db.uncomplete_task(id=target)
        assert result == 1
        # task is undone
        task = db.get_task(id=target)
        assert task["done"] is False
        # task appears last in pending list
        pending = list(db.get_pending_tasks(user_id=uid))
        assert pending[-1]["id"] == target

    def test_uncomplete_task_useless(cls, db, lid):
        new_id = db.add_task_to_list(daylist_id=lid, title="tester", estimate="PT10M")
        result = db.uncomplete_task(id=new_id)
        # not affected
        assert result == 0

    def test_uncomplete_task_invalid(cls, db, lid):
        result = db.uncomplete_task(id=0)
        assert result == 0

    # delete

    def test_delete_task(cls, db, lid):
        new_id = db.add_task_to_list(daylist_id=lid, title="tester", estimate="PT10M")
        assert db.count_tasks(daylist_id=lid) == 1

        result = db.delete_task(id=new_id)
        assert result == 1
        assert db.count_tasks(daylist_id=lid) == 0

    def test_delete_task_invalid(cls, db, lid):
        result = db.delete_task(id=0)
        assert result == 0
