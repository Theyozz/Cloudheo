"""Password hashing, JWT access tokens, and password-reset tokens."""

import hashlib
import secrets
from datetime import UTC, datetime, timedelta

import bcrypt
import jwt

from app.core.config import get_settings

JWT_ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))


def create_access_token(user_id: str) -> str:
    settings = get_settings()
    now = datetime.now(UTC)
    expire = now + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    # iat lets get_current_user reject tokens issued before a password reset.
    payload = {"sub": user_id, "iat": now, "exp": expire}
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> dict | None:
    settings = get_settings()
    try:
        return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except jwt.PyJWTError:
        return None


def generate_reset_token() -> str:
    """A high-entropy, URL-safe token to email the user — never stored in
    plaintext, see hash_reset_token."""
    return secrets.token_urlsafe(32)


def hash_reset_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
