import pytest

from src.userauth import hash_password


@pytest.fixture(autouse=True)
def db_setup_teardown(db):
    # There are always other unrelated users in the db
    for _ in range(2):
        db.add_anon_user()
        db.add_registered_user(email="one@test.com", password_hash=hash_password("1"))
        db.add_registered_user(email="two@test.com", password_hash=hash_password("2"))
    try:
        yield
    finally:
        db.delete_all_users()


@pytest.fixture()
def test_user(db):
    user_data = {"email": "sample@test.com", "password": "mypw123"}
    db.add_registered_user(
        email=user_data["email"], password_hash=hash_password(user_data["password"])
    )
    return user_data


# POST signup


def test_signup(client):
    form_data = {
        "username": "jester@example.com",
        "password": "unicorn",
        "grant_type": "password",
    }
    response = client.post("/user", data=form_data)
    assert response.status_code == 200
    # TODO: return token instead?


def test_signup_duplicate(client):
    form_data = {
        "username": "one@test.com",
        "password": "123",
        "grant_type": "password",
    }
    response = client.post("/user", data=form_data)
    # TODO: check why this is 400 - is there correct db error handling
    assert response.status_code == 400


def test_signup_invalid(client):
    form_data = {
        "username": "username",  # should be an email
        "password": "123",
        "grant_type": "password",
    }
    response = client.post("/user", data=form_data)
    assert response.status_code == 400
