"""Application configuration.

Settings are loaded from environment variables (and a local .env file in
development). Nothing secret should ever be hardcoded here.
"""

from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

INSECURE_JWT_SECRET_KEY = "dev-only-change-me-in-production"


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
    # before this is ever exposed beyond localhost. Enforced below: anyone
    # who forgets to set it outside of ENVIRONMENT=development can't start
    # the app with a secret an attacker can just read off GitHub and use to
    # forge a valid token for any user.
    JWT_SECRET_KEY: str = INSECURE_JWT_SECRET_KEY
    JWT_EXPIRE_MINUTES: int = 60 * 24

    # For the AI explanation service (app/services/ai). Only ever narrates
    # numbers the FinOps engine already computed — never used for the
    # calculations themselves.
    ANTHROPIC_API_KEY: str = ""

    # For the password-reset email (app/services/email). EMAIL_FROM must be
    # a verified sender/domain in Resend before it can email real customers.
    RESEND_API_KEY: str = ""
    EMAIL_FROM: str = "Cloudheo <onboarding@resend.dev>"

    # Where Cloudheo is notified of a new free-audit lead from the landing
    # page form (app/api/leads.py).
    AUDIT_LEAD_NOTIFICATION_EMAIL: str = "theomaurin875@gmail.com"

    # Base URL of the frontend, used to build the link in reset-password emails.
    FRONTEND_URL: str = "http://localhost:3000"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @model_validator(mode="after")
    def _refuse_insecure_secret_outside_dev(self) -> "Settings":
        if self.ENVIRONMENT != "development" and self.JWT_SECRET_KEY == INSECURE_JWT_SECRET_KEY:
            raise ValueError(
                "JWT_SECRET_KEY is still the default placeholder. Set a real secret "
                "(e.g. python3 -c \"import secrets; print(secrets.token_urlsafe(32))\") "
                "before running with ENVIRONMENT != development."
            )
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
