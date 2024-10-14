import pytest
from fastapi.testclient import TestClient

from config import Settings, get_settings
from api.main import app, configure
from api.routes.auth import build_token_object
from db.connect import DBQueriesWrapper, query_connect
from src.models import User
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
def test_user(db):
    user_data = {"email": "gandalf@fellowship.com", "password": "gthegrey"}
    uid = db.add_registered_user(
        email=user_data["email"], password_hash=hash_password(user_data["password"])
    )
    user_data["id"] = uid
    return user_data


@pytest.fixture()
def auth_headers(test_user):
    user = User(**test_user)
    token = build_token_object(user).access_token
    headers = {"Authorization": f"Bearer {token}"}
    return headers
