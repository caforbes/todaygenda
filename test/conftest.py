import pytest

from config import get_settings


@pytest.fixture(scope="session")
def settings():
    the_settings = get_settings()
    assert the_settings.testing
    return the_settings
