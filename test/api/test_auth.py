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
    user_data = {"email": "gandalf@fellowship.com", "password": "gthegrey"}
    db.add_registered_user(
        email=user_data["email"], password_hash=hash_password(user_data["password"])
    )
    return user_data


# POST signup


@pytest.mark.parametrize("has_grant_type", [True, False])
def test_signup(client, has_grant_type):
    form_data = {
        "username": "jester@example.com",
        "password": "unicorn",
    }
    if has_grant_type:
        form_data["grant_type"] = "password"

    response = client.post("/user", data=form_data)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["access_token"], str)
    assert data["token_type"] == "bearer"


def test_signup_duplicate(client, test_user):
    form_data = {
        "username": test_user["email"],
        "password": "123456789",
        "grant_type": "password",
    }
    response = client.post("/user", data=form_data)
    assert response.status_code == 422


@pytest.mark.parametrize(
    "username,password", [("bad", "123456789"), ("someuser@example.com", "bad")]
)
def test_signup_invalid(client, username, password):
    form_data = {
        "username": username,
        "password": password,
        "grant_type": "password",
    }
    response = client.post("/user", data=form_data)
    assert response.status_code == 422


# POST login / get token


@pytest.mark.parametrize("has_grant_type", [True, False])
def test_login(client, test_user, has_grant_type):
    form_data = {
        "username": test_user["email"],
        "password": test_user["password"],
    }
    if has_grant_type:
        form_data["grant_type"] = "password"

    response = client.post("/user/token", data=form_data)
    assert response.status_code == 200
    # get a token
    data = response.json()
    assert isinstance(data["access_token"], str)
    assert data["token_type"] == "bearer"


def test_login_bad_pw(client, test_user):
    form_data = {
        "username": test_user["email"],
        "password": "wrong pwd",
    }

    response = client.post("/user/token", data=form_data)
    assert response.status_code == 401


@pytest.mark.parametrize("username", ["nobody@email.com", "anonymous"])
def test_login_not_a_user(client, username):
    form_data = {
        "username": username,
        "password": "notapassword",
    }

    response = client.post("/user/token", data=form_data)
    assert response.status_code == 401


def test_login_as_guest(client, db, settings):
    orig_users = db.count_anon_users()
    form_data = {
        "username": "anonymous",
        "password": settings.guest_user_key,
    }

    response = client.post("/user/token", data=form_data)
    assert response.status_code == 200
    # get a token
    data = response.json()
    assert isinstance(data["access_token"], str)
    assert data["token_type"] == "bearer"
    # added a temp user
    assert db.count_anon_users() == orig_users + 1
