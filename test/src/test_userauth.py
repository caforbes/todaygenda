import pytest

import src
from src.userauth import create_user

DB = src.operations.DB


@pytest.mark.parametrize("email,pw", [("test@test.com", "123456789")])
def test_create_user(mocker, email, pw):
    mocker.patch("src.operations.DB.add_registered_user", return_value=1)
    result = create_user(email, pw)
    assert result == 1
    DB.add_registered_user.assert_called()


@pytest.mark.parametrize(
    "email,pw", [("", ""), ("anonymous", "123456789"), ("test@test.com", "_")]
)
def test_create_user_invalid(mocker, email, pw):
    mocker.patch("src.operations.DB.add_registered_user")
    result = create_user(email, pw)
    assert result is None
    DB.add_registered_user.assert_not_called()
