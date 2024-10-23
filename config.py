from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    testing: bool = False
    allowed_origins: list[str] = []
    secret_key: str = "mysupersecrettestingkey"
    guest_user_key: str = ""
    database_url: str = ""
    test_database_url: str = ""

    model_config = SettingsConfigDict(env_file=("docker.env", ".env"), extra="allow")

    @model_validator(mode="after")
    def psql_dialect(self):
        """Ensure correct psql dialect is used in db url."""
        bad_form = "postgres://"
        good_form = "postgresql://"

        if bad_form in self.database_url:
            self.database_url = self.database_url.replace(bad_form, good_form)
        if bad_form in self.test_database_url:
            self.test_database_url = self.test_database_url.replace(bad_form, good_form)
        return self


def get_settings() -> Settings:
    settings = Settings()
    if settings.testing:
        settings.database_url = settings.test_database_url
    return settings
