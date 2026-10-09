import logging
from datetime import UTC, datetime, timedelta

import resend.exceptions
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.db import get_db
from app.core.deps import get_current_user
from app.core.rate_limit import limiter
from app.core.security import (
    create_access_token,
    generate_reset_token,
    hash_password,
    hash_reset_token,
    verify_password,
)
from app.models.organization import Organization
from app.models.password_reset_token import PasswordResetToken
from app.models.user import User
from app.schemas.auth import (
    ForgotPasswordRequest,
    LoginRequest,
    MessageResponse,
    RegisterRequest,
    ResetPasswordRequest,
    TokenResponse,
    UserResponse,
)
from app.services.audit import AuditAction, log_action
from app.services.email import get_email_provider
from app.services.email.base import EmailProvider

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])

RESET_TOKEN_EXPIRE_MINUTES = 60
# Always the same regardless of whether the email is registered — the
# endpoint must not reveal whether an account exists.
FORGOT_PASSWORD_GENERIC_MESSAGE = "If an account exists for this email, a reset link has been sent."


@router.post("/register", response_model=TokenResponse, status_code=201)
@limiter.limit("5/hour")
def register(request: Request, payload: RegisterRequest, db: Session = Depends(get_db)):
    """Create a new Organization and its first (and, for now, only) user.
    Registration is always open — each call onboards a new customer."""
    if db.query(User).filter(User.email == payload.email).first() is not None:
        raise HTTPException(status_code=409, detail="An account with this email already exists")

    organization = Organization(name=payload.organization_name)
    db.add(organization)
    db.flush()

    user = User(
        organization_id=organization.id,
        email=payload.email,
        hashed_password=hash_password(payload.password),
    )
    db.add(user)
    db.flush()  # populate user.id (a Python-side default, only set on flush) for the log entry below
    log_action(
        db,
        organization_id=organization.id,
        user_id=user.id,
        action=AuditAction.AUTH_REGISTER,
        details={"email": user.email, "organization_name": organization.name},
    )
    db.commit()
    db.refresh(user)

    return TokenResponse(access_token=create_access_token(user.id))


@router.post("/login", response_model=TokenResponse)
@limiter.limit("10/minute")
def login(request: Request, payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if user is None or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    log_action(
        db,
        organization_id=user.organization_id,
        user_id=user.id,
        action=AuditAction.AUTH_LOGIN,
        details={"email": user.email},
    )
    db.commit()

    return TokenResponse(access_token=create_access_token(user.id))


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse(id=current_user.id, email=current_user.email, organization_id=current_user.organization_id)


@router.post("/forgot-password", response_model=MessageResponse)
@limiter.limit("5/hour")
def forgot_password(
    request: Request,
    payload: ForgotPasswordRequest,
    db: Session = Depends(get_db),
    email_provider: EmailProvider = Depends(get_email_provider),
):
    """Always returns the same message, whether or not the email is
    registered — otherwise this endpoint would let anyone check which
    emails have a Cloudheo account."""
    user = db.query(User).filter(User.email == payload.email).first()
    if user is not None:
        raw_token = generate_reset_token()
        reset_token = PasswordResetToken(
            user_id=user.id,
            token_hash=hash_reset_token(raw_token),
            expires_at=datetime.now(UTC) + timedelta(minutes=RESET_TOKEN_EXPIRE_MINUTES),
        )
        db.add(reset_token)
        log_action(
            db,
            organization_id=user.organization_id,
            user_id=user.id,
            action=AuditAction.AUTH_PASSWORD_RESET_REQUESTED,
            details={"email": user.email},
        )
        db.commit()

        settings = get_settings()
        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={raw_token}"
        try:
            email_provider.send_password_reset(user.email, reset_url)
        except resend.exceptions.ResendError:
            # The token is already saved — don't fail the request (that would
            # tell the caller whether the email exists, via the status code).
            # Log it server-side; the user can always ask for another link.
            logger.exception("Failed to send password-reset email to user %s", user.id)

    return MessageResponse(message=FORGOT_PASSWORD_GENERIC_MESSAGE)


@router.post("/reset-password", response_model=MessageResponse)
@limiter.limit("10/hour")
def reset_password(request: Request, payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    token_hash = hash_reset_token(payload.token)
    reset_token = (
        db.query(PasswordResetToken)
        .filter(
            PasswordResetToken.token_hash == token_hash,
            PasswordResetToken.used_at.is_(None),
            PasswordResetToken.expires_at > datetime.now(UTC),
        )
        .first()
    )
    if reset_token is None:
        raise HTTPException(status_code=400, detail="Invalid or expired reset link")

    user = db.query(User).filter(User.id == reset_token.user_id).first()

    now = datetime.now(UTC)
    user.hashed_password = hash_password(payload.new_password)
    user.password_changed_at = now
    reset_token.used_at = now
    log_action(
        db,
        organization_id=user.organization_id,
        user_id=user.id,
        action=AuditAction.AUTH_PASSWORD_RESET_COMPLETED,
        details={"email": user.email},
    )
    db.commit()

    return MessageResponse(message="Password updated. Please log in again.")
