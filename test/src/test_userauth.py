import pytest

import src
from src.models import User
from src.userauth import (
    acceptable_user_creds,
    create_guest_user,
    create_user,
    fetch_user,
    make_user_sub,
)
import src.userauth

DB = src.operations.DB


@pytest.mark.parametrize("email,pw", [("test@test.com", "123456789")])
def test_create_user(mocker, email, pw):
    mocker.patch("src.operations.DB.add_registered_user", return_value=1)
    result = create_user(email, pw)
    assert result == 1
    DB.add_registered_user.assert_called()


def test_create_guest_user(mocker, settings):
    mocker.patch("src.operations.DB.add_anon_user")
    mocker.patch("src.userauth.fetch_user")

    create_guest_user(settings.guest_user_key)
    # called correctly
    DB.add_anon_user.assert_called()
    src.userauth.fetch_user.assert_called()


def test_create_guest_user_bad(mocker):
    mocker.patch("src.operations.DB.add_anon_user")
    result = create_guest_user(pw="wrong")
    assert result is None
    DB.add_anon_user.assert_not_called()


@pytest.mark.parametrize(
    "email,pw",
    [
        ("admin@example.com", "myTestPwd123"),
        ("admin+123@example.com", "aaaaaaaaaaaaa"),
    ],
)
def test_user_creds_ok(email, pw):
    result = acceptable_user_creds(email, pw)
    assert result is True


@pytest.mark.parametrize(
    "email,pw",
    [
        ("", ""),
        ("anonymous", "123456789"),
        ("hello at email dot com", "123456789"),
        ("email@hello,com", "123456789"),
        ("test@test.com", "_"),
    ],
)
def test_user_creds_invalid(email, pw):
    result = acceptable_user_creds(email, pw)
    assert result is False


@pytest.mark.parametrize(
    "user,expected_sub",
    [(User(id=123), "anon:123"), (User(id=123, email="my@email.com"), "my@email.com")],
)
def test_make_user_sub(user, expected_sub):
    result = make_user_sub(user)
    assert result == expected_sub


def test_fetch_user_email(mocker):
    dummy_user = {"id": 123, "email": "my@email.com"}
    mocker.patch("src.operations.DB.get_registered_user", return_value=dummy_user)
    mocker.patch("src.operations.DB.get_user", return_value=dummy_user)

    result = fetch_user(email=dummy_user["email"])
    # use the correct function
    DB.get_registered_user.assert_called()
    DB.get_user.assert_not_called()
    # correct result properties
    assert result.id == dummy_user["id"]


def test_fetch_user_anon(mocker):
    dummy_user = {"id": 123}
    mocker.patch("src.operations.DB.get_registered_user", return_value=dummy_user)
    mocker.patch("src.operations.DB.get_user", return_value=dummy_user)

    result = fetch_user(id=dummy_user["id"])
    # use the correct function
    DB.get_user.assert_called()
    DB.get_registered_user.assert_not_called()
    # correct result properties
    assert result.id == dummy_user["id"]


@pytest.mark.parametrize(
    "sub_value,dummy_user",
    [
        ("anon:123", {"id": 123}),
        ("my@email.com", {"id": 123, "email": "my@email.com"}),
    ],
)
def test_fetch_user_sub(mocker, sub_value, dummy_user):
    mocker.patch("src.operations.DB.get_registered_user", return_value=dummy_user)
    mocker.patch("src.operations.DB.get_user", return_value=dummy_user)

    result = fetch_user(sub=sub_value)
    # use the correct function
    if "anon" in sub_value:
        DB.get_user.assert_called()
        DB.get_registered_user.assert_not_called()
    else:
        DB.get_registered_user.assert_called()
        DB.get_user.assert_not_called()
    # correct result properties
    assert result.id == dummy_user["id"]


@pytest.mark.parametrize(
    "kwargs", [{"id": 123}, {"email": "hi@there.com"}, {"sub": "username"}]
)
def test_fetch_user_not_found(mocker, kwargs):
    mocker.patch("src.operations.DB.get_registered_user", return_value=None)
    mocker.patch("src.operations.DB.get_user", return_value=None)

    result = fetch_user(**kwargs)
    assert result is None


def test_fetch_user_no_key(mocker):
    mocker.patch("src.operations.DB.get_registered_user")
    mocker.patch("src.operations.DB.get_user")

    with pytest.raises(ValueError):
        fetch_user()
