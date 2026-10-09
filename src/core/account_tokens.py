"""Hashed, expiring, single-use account tokens."""

from datetime import datetime, timedelta
import hashlib
import secrets

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from src.core.database import AccountToken
from src.core.settings import get_settings


def issue_account_token(db: Session, user_id: int, purpose: str) -> str:
    if purpose not in {"verify_email", "password_reset"}:
        raise ValueError("unsupported account-token purpose")
    now = datetime.utcnow()
    db.execute(
        update(AccountToken)
        .where(
            AccountToken.user_id == user_id,
            AccountToken.purpose == purpose,
            AccountToken.consumed_at.is_(None),
        )
        .values(consumed_at=now)
    )
    raw = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(raw.encode()).hexdigest()
    db.add(
        AccountToken(
            user_id=user_id,
            purpose=purpose,
            token_hash=token_hash,
            expires_at=now + timedelta(minutes=get_settings().email_token_minutes),
        )
    )
    db.flush()
    return raw


def consume_account_token(db: Session, raw: str, purpose: str) -> AccountToken | None:
    if not raw or len(raw) > 256:
        return None
    token_hash = hashlib.sha256(raw.encode()).hexdigest()
    now = datetime.utcnow()
    token = db.scalar(
        select(AccountToken)
        .where(
            AccountToken.token_hash == token_hash,
            AccountToken.purpose == purpose,
            AccountToken.consumed_at.is_(None),
            AccountToken.expires_at > now,
        )
        .with_for_update()
    )
    if token:
        token.consumed_at = now
        db.flush()
    return token
