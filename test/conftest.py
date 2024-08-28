import pytest

from config import get_settings
from db.connect import query_connect


@pytest.fixture(scope="session")
def settings():
    the_settings = get_settings()
    assert the_settings.testing
    return the_settings


@pytest.fixture(scope="session")
def db(settings):
    assert "test" in settings.database_url
    queries = query_connect(url=settings.database_url)
    return queries
