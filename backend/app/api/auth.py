from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import get_current_user
from app.core.security import create_access_token, hash_password, verify_password
from app.models.organization import Organization
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserResponse
from app.services.audit import AuditAction, log_action

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=201)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
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
def login(payload: LoginRequest, db: Session = Depends(get_db)):
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
