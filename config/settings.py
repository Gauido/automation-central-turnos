from functools import lru_cache

from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="CT_",
        extra="ignore",
    )

    env: str = "dev"
    web_base_url: AnyHttpUrl = "https://72-60-241-195.nip.io:8443"
    api_base_url: AnyHttpUrl = "https://72-60-241-195.nip.io:8443"

    admin_email: str | None = None
    admin_password: str | None = None
    staff_email: str | None = None
    staff_password: str | None = None
    owner_email: str | None = None
    owner_password: str | None = None

    tenant_a_id: str | None = None
    tenant_b_id: str | None = None

    default_timeout_ms: int = Field(default=30_000, ge=1_000)
    api_timeout_seconds: float = Field(default=30.0, gt=0)
    ignore_https_errors: bool = True


@lru_cache
def get_settings() -> Settings:
    return Settings()
