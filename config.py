from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    testing: bool = False
    allowed_origins: list[str] = []
    database_url: str = ""
    test_database_url: str = ""

    model_config = SettingsConfigDict(env_file=("docker.env", ".env"), extra="allow")


def get_settings() -> Settings:
    settings = Settings()
    if settings.testing:
        settings.database_url = settings.test_database_url
    return settings
