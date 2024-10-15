from typing import Union
import pytest
from fastapi.testclient import TestClient

from config import Settings, get_settings
from api.main import app, configure
from db.connect import DBQueriesWrapper, query_connect
from src.userauth import hash_password


@pytest.fixture(scope="session")
def settings() -> Settings:
    the_settings = get_settings()
    assert the_settings.testing
    return the_settings


@pytest.fixture(scope="session")
def db(settings) -> DBQueriesWrapper:
    assert "test" in settings.database_url
    queries = query_connect(url=settings.database_url)
    return queries


@pytest.fixture(scope="session")
def client(settings) -> TestClient:
    configure(app, settings=settings)
    return TestClient(app)


@pytest.fixture()
def known_user(db) -> dict[str, Union[str, int]]:
    user_data = {"email": "gandalf@fellowship.com", "password": "gthegrey"}
    uid = db.add_registered_user(
        email=user_data["email"], password_hash=hash_password(user_data["password"])
    )
    user_data["id"] = uid
    return user_data


@pytest.fixture()
def anon_user(db) -> dict[str, int]:
    user_data = {}
    uid = db.add_anon_user()
    user_data["id"] = uid
    return user_data


@pytest.fixture(params=["anon_user", "known_user"])
def any_user(db, request) -> dict[str, int]:
    return request.getfixturevalue(request.param)
