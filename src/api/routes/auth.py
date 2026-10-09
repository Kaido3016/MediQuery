"""Account endpoints. Password reset/email verification require an email provider adapter."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.api.schemas import AuthResponse, LoginRequest, SignUpRequest
from src.api.dependencies import current_user
from src.core.database import AuditEvent, Report, User, get_db
from src.core.file_lifecycle import (
    purge_staged_files,
    restore_staged_files,
    stage_files,
)
from src.core.observability import metrics
from src.core.settings import get_settings
from src.core.security import create_access_token, hash_password, verify_password
from src.core.settings import get_settings
import pyotp

router = APIRouter()


@router.post(
    "/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED
)
def signup(payload: SignUpRequest, db: Session = Depends(get_db)) -> AuthResponse:
    if not payload.acknowledge_medical_limitations:
        raise HTTPException(
            status_code=422,
            detail="You must acknowledge that MediQuery is not medical advice.",
        )
    email = payload.email.strip().lower()
    if db.scalar(select(User).where(User.email == email)):
        raise HTTPException(
            status_code=409, detail="An account with that email already exists"
        )
    try:
        password_hash = hash_password(payload.password)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    user = User(email=email, password_hash=password_hash)
    db.add(user)
    db.flush()
    db.add(AuditEvent(actor_id=user.id, action="account_created", metadata_json={}))
    db.add(
        AuditEvent(
            actor_id=user.id,
            action="medical_limitations_acknowledged",
            metadata_json={"version": "2026-08-25"},
        )
    )
    db.commit()
    if get_settings().environment.lower() == "production":
        from src.api.routes.account_security import send_verification_for_user
        send_verification_for_user(user, db)
    metrics.increment("accounts.signup")
    return AuthResponse(access_token=create_access_token(user.id, user.token_version))


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> AuthResponse:
    user = db.scalar(select(User).where(User.email == payload.email.strip().lower()))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    settings = get_settings()
    if settings.environment.lower() == "production" and not user.email_verified:
        raise HTTPException(status_code=403, detail="Verify your email before signing in.")
    if user.mfa_enabled and (
        not user.mfa_secret
        or not payload.totp_code
        or not pyotp.TOTP(user.mfa_secret).verify(payload.totp_code, valid_window=1)
    ):
        raise HTTPException(status_code=401, detail="Invalid email, password, or authenticator code")
    db.add(AuditEvent(actor_id=user.id, action="login_succeeded", metadata_json={"mfa": user.mfa_enabled}))
    db.commit()
    metrics.increment("accounts.login")
    return AuthResponse(access_token=create_access_token(user.id, user.token_version))


@router.delete("/account", status_code=status.HTTP_204_NO_CONTENT)
def delete_account(
    user: User = Depends(current_user), db: Session = Depends(get_db)
) -> None:
    """Delete the caller's reports and account. Backup purge remains an operational task."""
    upload_root = get_settings().upload_root
    reports = list(db.scalars(select(Report).where(Report.owner_id == user.id)))
    staged = stage_files([upload_root / report.storage_key for report in reports])
    db.add(
        AuditEvent(
            actor_id=user.id, action="account_deletion_requested", metadata_json={}
        )
    )
    db.delete(user)
    try:
        db.commit()
    except Exception:
        db.rollback()
        restore_staged_files(staged)
        raise
    purge_staged_files(staged)
    metrics.increment("accounts.deleted")
