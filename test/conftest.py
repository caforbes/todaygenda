import pytest

from config import Settings, get_settings
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
