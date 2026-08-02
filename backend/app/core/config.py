from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "local"
    web_origin: str = "http://localhost:5173"
    web_origins: str = ""
    database_url: str = "sqlite:///./mandrong.db"
    storage_root: Path = Path("../storage")
    max_upload_mb: int = 20
    openai_api_key: str = Field(default="", repr=False)

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def allowed_web_origins(self) -> list[str]:
        raw_origins = self.web_origins or self.web_origin
        return [origin.strip() for origin in raw_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
