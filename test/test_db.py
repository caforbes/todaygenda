"""For database function testing.

Interacts with the test database.
"""

from datetime import datetime
from sqlalchemy.exc import IntegrityError
import pytest


@pytest.fixture()
def seed(db):
    userid = db.add_anon_user()
    db.add_daylist(user_id=userid, expiry="2014-02-14T00:00:00")
    db.add_daylist(user_id=userid, expiry="2024-07-24T00:00:00")
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

    # TODO: add registered user

    # update

    # TODO: register a guest user
    # TODO: update registered user's pw

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
        return db.add_user()  # FIX

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
        db.add_daylist(user_id=uid, expiry="2022-02-22T00:00:00")
        result = db.get_active_daylist(user_id=uid)
        assert result is None

    def test_get_active_daylist(cls, db):
        uid = cls.uid(db)
        expiry_str = "2122-02-22T00:00:00"
        db.add_daylist(user_id=uid, expiry=expiry_str)

        result = db.get_active_daylist(user_id=uid)
        assert isinstance(result, dict)
        assert "id" in result
        assert result["expiry"] == datetime.fromisoformat(expiry_str)

    # add

    @pytest.mark.parametrize(
        "expiry",
        [
            "2122-02-22T00:00:00",
            datetime.fromisoformat("2122-02-22T00:00:00"),
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
        expiry_str = "2122-02-22T00:00:00"

        # inputting bad user raises error
        with pytest.raises(IntegrityError):
            db.add_daylist(user_id=uid, expiry=expiry_str)

    @pytest.mark.parametrize("is_anon", [True])  # FIX: add registered user
    def test_add_daylist(cls, db, is_anon):
        uid = cls.uid(db, is_anon)
        expiry_str = "2122-02-22T00:00:00"
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
        return db.add_daylist(user_id=uid, expiry="2122-02-22T00:00:00")

    # get

    # TODO: check anything about the order?

    # add

    def test_add_task_ordered(cls, db, lid):
        result = db.add_task(daylist_id=lid, title="first", estimate="PT1H5M")
        # successful insertion returns task index
        assert isinstance(result, int) and result > 0
        result = db.add_task(daylist_id=lid, title="second", estimate="PT1H5M")
        result = db.add_task(daylist_id=lid, title="third", estimate="PT1H5M")
        # multiple inserts are successful
        assert db.count_tasks(daylist_id=lid) == 3
