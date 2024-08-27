import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    allowed_origins: list[str] = []
    database_url: str = ""
    testing: bool = False

    model_config = SettingsConfigDict(env_file=".env", extra="allow")


def get_settings(testing: bool = False) -> Settings:
    if testing:
        return Settings(
            testing=True,
            database_url=os.getenv("TEST_DATABASE_URL") or "",
            allowed_origins=[],
        )
    else:
        return Settings()
