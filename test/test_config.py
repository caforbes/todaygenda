from config import Settings


def test_postgres_url(settings):
    bad_pgurl = "postgres://test:string@url:port/mydb"
    settings.database_url = bad_pgurl
    settings.test_database_url = bad_pgurl

    Settings.model_validate(settings)

    assert settings.database_url != bad_pgurl
    assert settings.test_database_url != bad_pgurl
    assert "postgresql" in settings.database_url
    assert "postgresql" in settings.test_database_url
