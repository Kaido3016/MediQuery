"""Verified email, password recovery, TOTP MFA, and session revocation endpoints."""

from datetime import datetime
import logging
from urllib.parse import quote

import pyotp
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.api.dependencies import current_user
from src.api.schemas import PasswordResetConfirm, PasswordResetRequest, TokenRequest, TotpRequest
from src.core.account_tokens import consume_account_token, issue_account_token
from src.core.database import AuditEvent, User, get_db
from src.core.email_delivery import send_account_email
from src.core.observability import metrics
from src.core.mfa_crypto import decrypt_mfa_secret, encrypt_mfa_secret
from src.core.security import hash_password, verify_password
from src.core.settings import get_settings

router = APIRouter()
logger = logging.getLogger("mediquery.account_security")


def send_verification_for_user(user: User, db: Session) -> None:
    raw = issue_account_token(db, user.id, "verify_email")
    db.commit()
    settings = get_settings()
    link = f"{settings.frontend_base_url.rstrip('/')}/?verify_email_token={quote(raw)}"
    try:
        send_account_email(user.email, "Verify your MediQuery email", f"Open MediQuery and confirm your email:\\n\\n{link}\\n\\nThis link expires in {settings.email_token_minutes} minutes.")
    except Exception as exc:
        logger.warning("account_email_delivery_failed purpose=verify_email")
        raise HTTPException(status_code=503, detail="Email delivery is temporarily unavailable.") from exc


@router.post("/verification/resend", status_code=202)
def resend_verification(payload: PasswordResetRequest, db: Session = Depends(get_db)) -> dict[str, str]:
    user = db.scalar(select(User).where(User.email == payload.email.strip().lower()))
    if user and not user.email_verified:
        raw = issue_account_token(db, user.id, "verify_email")
        db.commit()
        settings = get_settings()
        link = f"{settings.frontend_base_url.rstrip('/')}/?verify_email_token={quote(raw)}"
        try:
            send_account_email(user.email, "Verify your MediQuery email", f"Open MediQuery and confirm your email:\n\n{link}\n\nThis link expires in {settings.email_token_minutes} minutes.")
        except Exception:
            logger.warning("account_email_delivery_failed purpose=verify_email")
    return {"message": "If the account needs verification, an email will be sent."}


@router.post("/verify-email")
def verify_email(payload: TokenRequest, db: Session = Depends(get_db)) -> dict[str, str]:
    token = consume_account_token(db, payload.token, "verify_email")
    if not token:
        db.rollback()
        raise HTTPException(status_code=400, detail="Verification link is invalid or expired")
    user = db.get(User, token.user_id)
    if not user:
        db.rollback()
        raise HTTPException(status_code=400, detail="Verification link is invalid or expired")
    user.email_verified = True
    db.add(AuditEvent(actor_id=user.id, action="email_verified", metadata_json={}))
    db.commit()
    metrics.increment("accounts.email_verified")
    return {"message": "Email verified. You can now sign in."}


@router.post("/password-reset/request", status_code=202)
def request_password_reset(payload: PasswordResetRequest, db: Session = Depends(get_db)) -> dict[str, str]:
    user = db.scalar(select(User).where(User.email == payload.email.strip().lower()))
    if user:
        raw = issue_account_token(db, user.id, "password_reset")
        db.commit()
        settings = get_settings()
        link = f"{settings.frontend_base_url.rstrip('/')}/?password_reset_token={quote(raw)}"
        try:
            send_account_email(user.email, "Reset your MediQuery password", f"Use this link to reset your password:\n\n{link}\n\nThis link expires in {settings.email_token_minutes} minutes. Ignore this message if you did not request it.")
        except Exception:
            logger.warning("account_email_delivery_failed purpose=password_reset")
    return {"message": "If the account exists, a password-reset email will be sent."}


@router.post("/password-reset/confirm")
def confirm_password_reset(payload: PasswordResetConfirm, db: Session = Depends(get_db)) -> dict[str, str]:
    token = consume_account_token(db, payload.token, "password_reset")
    if not token:
        db.rollback()
        raise HTTPException(status_code=400, detail="Reset link is invalid or expired")
    user = db.get(User, token.user_id)
    if not user:
        db.rollback()
        raise HTTPException(status_code=400, detail="Reset link is invalid or expired")
    try:
        user.password_hash = hash_password(payload.new_password)
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    user.token_version += 1
    db.add(AuditEvent(actor_id=user.id, action="password_reset_completed", metadata_json={}))
    db.commit()
    metrics.increment("accounts.password_reset")
    return {"message": "Password changed. Please sign in again."}


@router.post("/mfa/setup")
def setup_mfa(user: User = Depends(current_user), db: Session = Depends(get_db)) -> dict[str, str]:
    if user.mfa_enabled:
        raise HTTPException(status_code=409, detail="MFA is already enabled.")
    secret = pyotp.random_base32()
    user.mfa_secret = encrypt_mfa_secret(secret)
    db.commit()
    uri = pyotp.TOTP(secret).provisioning_uri(name=user.email, issuer_name=get_settings().mfa_issuer)
    return {"secret": secret, "otpauth_uri": uri, "message": "Add this account to an authenticator app, then confirm with a current code."}


@router.post("/mfa/enable")
def enable_mfa(payload: TotpRequest, user: User = Depends(current_user), db: Session = Depends(get_db)) -> dict[str, str]:
    if not user.mfa_secret or not pyotp.TOTP(decrypt_mfa_secret(user.mfa_secret)).verify(payload.code, valid_window=1):
        raise HTTPException(status_code=400, detail="Authenticator code is invalid.")
    user.mfa_enabled = True
    user.token_version += 1
    db.add(AuditEvent(actor_id=user.id, action="mfa_enabled", metadata_json={}))
    db.commit()
    return {"message": "MFA enabled. Sign in again with your authenticator code."}


@router.post("/mfa/disable")
def disable_mfa(payload: TotpRequest, password: str, user: User = Depends(current_user), db: Session = Depends(get_db)) -> dict[str, str]:
    if not user.mfa_enabled or not user.mfa_secret or not verify_password(password, user.password_hash) or not pyotp.TOTP(user.mfa_secret).verify(payload.code, valid_window=1):
        raise HTTPException(status_code=401, detail="Password or authenticator code is invalid.")
    user.mfa_enabled = False
    user.mfa_secret = None
    user.token_version += 1
    db.add(AuditEvent(actor_id=user.id, action="mfa_disabled", metadata_json={}))
    db.commit()
    return {"message": "MFA disabled. All previous sessions were revoked."}


@router.post("/logout", status_code=204)
def logout(user: User = Depends(current_user), db: Session = Depends(get_db)) -> None:
    """Invalidate every access token issued before this account version."""
    user.token_version += 1
    db.add(AuditEvent(actor_id=user.id, action="sessions_revoked", metadata_json={"scope": "all"}))
    db.commit()
    metrics.increment("accounts.sessions_revoked")
