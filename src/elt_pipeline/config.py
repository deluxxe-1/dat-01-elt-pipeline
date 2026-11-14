"""Runtime configuration loaded from environment variables.

All secrets/configuration are read from the environment (or a local ``.env``
file during development). Nothing is hard-coded in source control.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings, populated from ``ELT_*`` environment variables."""

    model_config = SettingsConfigDict(
        env_prefix="ELT_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_path: str = "elt_local.db"
    source_seed: int = 42
    source_records: int = 100
    api_title: str = "ELT Pipeline Service"


settings = Settings()
