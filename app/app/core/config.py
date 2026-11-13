from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    project_name: str = "finacial-support-assistant"
    version: str = "1.0.0"
    openrouter_api_key: str
    openrouter_model: str
    api_version: str = "/v1"
    openrouter_url: str
    postgres_password: str
    database_url: str

    model_config = SettingsConfigDict(env_file=".env")


@lru_cache
def get_settings() -> Settings:
    return Settings()
