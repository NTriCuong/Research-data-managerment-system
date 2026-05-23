from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        populate_by_name=True,
    )

    APP_NAME: str
    APP_ENV: str 
    DEBUG: bool 
    API_V1_PREFIX: str 
    CORS_ORIGINS: list[str] = Field(default_factory=lambda: ["*"], alias="cors_origins")

    password_min_length: int = 8

    @field_validator("DEBUG", mode="before")
    @classmethod
    def parse_debug_value(cls, value: object) -> object:
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"release", "prod", "production"}:
                return False
            if normalized in {"dev", "development"}:
                return True
        return value

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origin_list(cls, value: object) -> object:
        if isinstance(value, str):
            if value.strip().startswith("["):
                return value
            return [item.strip() for item in value.split(",") if item.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
