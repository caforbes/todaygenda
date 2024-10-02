import pytest
from fastapi.testclient import TestClient

from config import Settings, get_settings
from api.main import app, configure
from db.connect import DBQueriesWrapper, query_connect


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
