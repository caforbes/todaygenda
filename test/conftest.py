import pytest

from config import get_settings


@pytest.fixture(scope="session")
def settings():
    return get_settings(testing=True)
