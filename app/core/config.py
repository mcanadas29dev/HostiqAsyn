from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # App
    app_name: str = Field(default="Mi Proyecto FastAPI")
    app_port: int = Field(default=8150)
    app_secret_key: str = Field(..., min_length=32)
    frontend_url: str = Field(default="http://localhost:3000")

    # Base de datos
    database_url: str = Field(...)

    # JWT
    jwt_lifetime_seconds: int = Field(default=3600)

    # Secretos para tokens
    reset_password_token_secret: str = Field(..., min_length=32)
    verification_token_secret: str = Field(..., min_length=32)

    # TTLs de tokens
    reset_password_token_lifetime_seconds: int = Field(default=3600)
    verification_token_lifetime_seconds: int = Field(default=86400)

    # SMTP
    smtp_host: str = Field(default="127.0.0.1")
    smtp_port: int = Field(default=1025)
    smtp_user: str = Field(...)
    smtp_password: str = Field(...)
    smtp_from: str = Field(...)


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()