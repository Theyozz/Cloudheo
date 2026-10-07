"""Application configuration.

Settings are loaded from environment variables (and a local .env file in
development). Nothing secret should ever be hardcoded here.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "Cloudheo API"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Comma-separated list of origins allowed to call the API (the Next.js dev server).
    CORS_ORIGINS: str = "http://localhost:3000"

    DATABASE_URL: str = "postgresql+psycopg2://cloudheo:cloudheo@localhost:5432/cloudheo"

    # Cloudheo's own AWS account (the `cloudheo-backend` IAM user). These
    # credentials only ever call sts:AssumeRole into customer accounts —
    # they have no direct access to customer resources themselves.
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "eu-west-3"

    # JWT signing secret. The default is an obvious, insecure placeholder —
    # it is fine for local dev but MUST be overridden (a long random string)
    # before this is ever exposed beyond localhost.
    JWT_SECRET_KEY: str = "dev-only-change-me-in-production"
    JWT_EXPIRE_MINUTES: int = 60 * 24

    # For the AI explanation service (app/services/ai). Only ever narrates
    # numbers the FinOps engine already computed — never used for the
    # calculations themselves.
    ANTHROPIC_API_KEY: str = ""

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
