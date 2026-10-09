import pytest

from app.core.config import Settings


def test_insecure_default_secret_is_rejected_outside_dev():
    with pytest.raises(ValueError, match="JWT_SECRET_KEY"):
        Settings(ENVIRONMENT="production", JWT_SECRET_KEY="dev-only-change-me-in-production")


def test_insecure_default_secret_is_allowed_in_dev():
    Settings(ENVIRONMENT="development", JWT_SECRET_KEY="dev-only-change-me-in-production")


def test_real_secret_is_allowed_outside_dev():
    Settings(ENVIRONMENT="production", JWT_SECRET_KEY="a-real-generated-secret")
