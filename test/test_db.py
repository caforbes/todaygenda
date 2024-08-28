"""For database function testing.

Interacts with the test database.
"""

import pytest


@pytest.fixture()
def seed(db):
    db.add_anon_user()
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


def test_anon_user_read_none(db):
    assert db.count_anon_users() == 0

    result = db.get_anon_user()
    assert result is None


def test_anon_user_read_some(db, seed):
    assert db.count_anon_users() > 0

    result = db.get_anon_user()
    assert isinstance(result, dict)
    assert "id" in result


@pytest.mark.skip()
def test_user_read_some(db, seed):
    # FIX: user lookup by id - get an id
    result = db.get_user(user_id="?")
    assert isinstance(result, dict)
    assert "id" in result


@pytest.mark.skip()
def test_user_read_invalid(db):
    # FIX: user lookup by id - get an id
    result = db.get_user(user_id="?")
    assert isinstance(result, dict)
    assert "id" in result


def test_add_user(db):
    result = db.add_anon_user()
    assert isinstance(result, int)
    assert result != 0  # should be id of the created user, not 0
    assert db.count_anon_users() == 1


# TODO: add registered user

# TODO: update


@pytest.mark.skip()
def test_delete_user(db, seed):
    # FIX: user lookup by id - get an id
    result = db.delete_user(user_id="?")
    assert result == 1


@pytest.mark.skip()
def test_delete_user_invalid(db):
    # FIX: user lookup by id - get an id
    result = db.delete_user(user_id="?")
    assert result == 0


def test_delete_all_users(db, seed):
    result = db.delete_all_users(user_id="?")
    assert result != 0
    assert db.count_users() == 0
