"""For database function testing.

Interacts with the test database.
"""

from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError
import pytest

FUTURE_TIME = "2122-02-22T00:00:00+05"
OLD_TIME = "2020-02-20 00:00:00+05"


@pytest.fixture()
def seed(db):
    userid = db.add_anon_user()
    db.add_daylist(user_id=userid, expiry="2014-02-14T00:00:00+05")
    db.add_daylist(user_id=userid, expiry="2024-07-24T00:00:00+05")
    yield


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

    # get
    # Note: counts and get_anon_user are for TEST purposes

    def test_anon_user_read_none(cls, db):
        assert db.count_anon_users() == 0

        result = db.get_anon_user()
        # no user returns none
        assert result is None

    def test_anon_user_read_some(cls, db, seed):
        assert db.count_anon_users() > 0

        result = db.get_anon_user()
        # good user returns dict of user attrs
        assert isinstance(result, dict)
        assert "id" in result and result["id"] > 0

    # Note: rest of app should use get_user by id

    def test_user_read_some(cls, db, seed):
        uid = db.add_anon_user()
        result = db.get_user(user_id=uid)
        # good user returns dict of user attrs
        assert isinstance(result, dict)
        assert "id" in result and result["id"] > 0

    def test_user_read_invalid(cls, db):
        result = db.get_user(user_id=-1)
        # bad user returns none
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

    # update

    # delete

    def test_delete_user(cls, db, seed):
        uid = db.add_anon_user()
        result = db.delete_user(user_id=uid)
        assert result == 1

    def test_delete_user_invalid(cls, db):
        result = db.delete_user(user_id=-1)
        assert result == 0

    def test_delete_all_users(cls, db, seed):
        result = db.delete_all_users()
        assert result != 0
        assert db.count_users() == 0


# Daylist functions


class TestDaylist:
    def uid(cls, db, anon_user: bool = True):
        if anon_user:
            return db.add_anon_user()
        return db.add_user()  # BOOKMARK: handle real users

    # get

    def test_get_active_daylist_bad_user(cls, db):
        result = db.get_active_daylist(user_id=-1)
        assert result is None

    def test_get_active_daylist_none(cls, db):
        uid = cls.uid(db)
        result = db.get_active_daylist(user_id=uid)
        assert result is None

    def test_get_active_daylist_old(cls, db):
        uid = cls.uid(db)
        db.add_daylist(user_id=uid, expiry=OLD_TIME)
        result = db.get_active_daylist(user_id=uid)
        assert result is None

    def test_get_active_daylist(cls, db):
        uid = cls.uid(db)
        expiry_str = FUTURE_TIME
        db.add_daylist(user_id=uid, expiry=expiry_str)

        result = db.get_active_daylist(user_id=uid)
        assert isinstance(result, dict)
        assert "id" in result
        assert result["expiry"] == datetime.fromisoformat(expiry_str)

    # add

    @pytest.mark.parametrize(
        "expiry",
        [
            FUTURE_TIME,
            datetime.fromisoformat(FUTURE_TIME),
        ],
    )
    def test_add_daylist_types(cls, db, expiry):
        uid = cls.uid(db)

        result = db.add_daylist(user_id=uid, expiry=expiry)
        # successful creation + return id for both types
        assert isinstance(result, int) and result > 0

    @pytest.mark.parametrize("bad_value", [-1, None])
    def test_add_daylist_bad_user(cls, db, bad_value):
        uid = bad_value
        expiry_str = FUTURE_TIME

        # inputting bad user raises error
        with pytest.raises(IntegrityError):
            db.add_daylist(user_id=uid, expiry=expiry_str)

    @pytest.mark.parametrize("is_anon", [True])  # BOOKMARK: test with registered user
    def test_add_daylist(cls, db, is_anon):
        uid = cls.uid(db, is_anon)
        expiry_str = FUTURE_TIME
        db.add_daylist(user_id=uid, expiry=expiry_str)

        result = db.add_daylist(user_id=uid, expiry=expiry_str)
        # successful creation + return id for both types
        assert isinstance(result, int) and result > 0


# Task functions


class TestTask:

    @pytest.fixture
    def uid(cls, db):
        return db.add_anon_user()

    @pytest.fixture
    def lid(cls, db, uid):
        return db.add_daylist(user_id=uid, expiry=FUTURE_TIME)

    @pytest.fixture
    def uid_with_list(cls, uid, lid):
        return uid

    def test_get_task(cls, db, lid):
        the_title = "ssss"
        the_estimate = "PT1M"
        tid = db.add_task_to_list(
            daylist_id=lid, title=the_title, estimate=the_estimate
        )

        result = db.get_task(id=tid)
        assert result["title"] == the_title
        assert isinstance(result["estimate"], timedelta)

    def test_get_task_invalid(cls, db):
        result = db.get_task(id=0)
        assert result is None

    def test_get_active_tasks_for_user(cls, db, uid_with_list):
        task_ids = [
            db.add_task_for_user(user_id=uid_with_list, title="one", estimate="PT1H5M"),
            db.add_task_for_user(user_id=uid_with_list, title="two", estimate="PT1H5M"),
        ]
        done_ids = [
            db.add_task_for_user(user_id=uid_with_list, title="cat", estimate="PT1H5M"),
        ]
        for task_id in done_ids:
            db.complete_task(id=task_id)

        result = list(db.get_current_tasks(user_id=uid_with_list))

        # all tasks are returned
        expected_ids = task_ids + done_ids
        assert len(result) == len(expected_ids)
        assert expected_ids == [task["id"] for task in result]

    def test_get_active_tasks_ordering(cls, db, uid_with_list):
        task_ids = [
            db.add_task_for_user(user_id=uid_with_list, title="one", estimate="PT1H5M"),
            db.add_task_for_user(user_id=uid_with_list, title="two", estimate="PT1H5M"),
        ]
        # BOOKMARK: add test that these are in order after editing might affect
        done_ids = [
            db.add_task_for_user(user_id=uid_with_list, title="cat", estimate="PT1H5M"),
            db.add_task_for_user(user_id=uid_with_list, title="dog", estimate="PT1H5M"),
        ]
        done_ids.reverse()  # check that finish time is different than add time
        for task_id in done_ids:
            db.complete_task(id=task_id)

        result = list(db.get_current_tasks(user_id=uid_with_list))

        # all tasks are returned
        expected_ids = task_ids + done_ids
        assert len(result) == len(expected_ids)
        assert expected_ids == [task["id"] for task in result]

    def test_get_active_tasks_for_user_no_list(cls, db, uid):
        result = db.get_current_tasks(user_id=uid)
        result = list(result)
        assert len(result) == 0

    def test_get_active_tasks_for_user_empty(cls, db, uid_with_list):
        result = db.get_current_tasks(user_id=uid_with_list)
        result = list(result)
        assert len(result) == 0

    def test_get_active_tasks_for_user_expired(cls, db, uid):
        lid = db.add_daylist(user_id=uid, expiry=OLD_TIME)
        db.add_task_to_list(daylist_id=lid, title="first", estimate="PT1H5M")
        db.add_task_to_list(daylist_id=lid, title="second", estimate="PT1H5M")

        result = db.get_current_tasks(user_id=uid)
        result = list(result)
        assert len(result) == 0

    def test_get_pending_tasks_for_user(cls, db, uid_with_list):
        task_ids = [
            db.add_task_for_user(user_id=uid_with_list, title="one", estimate="PT1H5M"),
            db.add_task_for_user(user_id=uid_with_list, title="two", estimate="PT1H5M"),
            db.add_task_for_user(user_id=uid_with_list, title="cat", estimate="PT1H5M"),
        ]
        done_ids = [
            db.add_task_for_user(user_id=uid_with_list, title="cat", estimate="PT1H5M"),
            db.add_task_for_user(user_id=uid_with_list, title="dog", estimate="PT1H5M"),
        ]
        for task_id in done_ids:
            db.complete_task(id=task_id)

        result = db.get_pending_tasks(user_id=uid_with_list)
        result = list(result)

        # only pending tasks are returned
        assert len(result) == len(task_ids)
        assert task_ids == [task["id"] for task in result]

    # BOOKMARK: check ordering once editing is available

    def test_get_pending_tasks_for_user_no_list(cls, db, uid):
        result = db.get_pending_tasks(user_id=uid)
        result = list(result)
        assert len(result) == 0

    def test_get_pending_tasks_for_user_empty(cls, db, uid_with_list):
        result = db.get_pending_tasks(user_id=uid_with_list)
        result = list(result)
        assert len(result) == 0

    def test_get_pending_tasks_for_user_expired(cls, db, uid):
        lid = db.add_daylist(user_id=uid, expiry=OLD_TIME)
        db.add_task_to_list(daylist_id=lid, title="first", estimate="PT1H5M")
        db.add_task_to_list(daylist_id=lid, title="second", estimate="PT1H5M")

        result = db.get_pending_tasks(user_id=uid)
        result = list(result)
        assert len(result) == 0

    def test_get_done_tasks_for_user(cls, db, uid_with_list):
        db.add_task_for_user(user_id=uid_with_list, title="one", estimate="PT1H5M")
        extra = db.add_task_for_user(
            user_id=uid_with_list, title="two", estimate="PT1H5M"
        )
        done_ids = [
            db.add_task_for_user(user_id=uid_with_list, title="cat", estimate="PT1H5M"),
            db.add_task_for_user(user_id=uid_with_list, title="dog", estimate="PT1H5M"),
            extra,
        ]
        for task_id in done_ids:
            db.complete_task(id=task_id)

        result = db.get_done_tasks(user_id=uid_with_list)
        result = list(result)

        # only done tasks are returned
        assert len(result) == len(done_ids)
        assert done_ids == [task["id"] for task in result]

    def test_get_done_tasks_for_user_ordering(cls, db, uid_with_list):
        done_ids = [
            db.add_task_for_user(user_id=uid_with_list, title="cat", estimate="PT1H5M"),
            db.add_task_for_user(user_id=uid_with_list, title="dog", estimate="PT1H5M"),
            db.add_task_for_user(user_id=uid_with_list, title="fly", estimate="PT1H5M"),
        ]
        done_ids.reverse()  # finish time != creation time
        for task_id in done_ids:
            db.complete_task(id=task_id)

        result = db.get_done_tasks(user_id=uid_with_list)
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
