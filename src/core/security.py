"""Password and bearer-token helpers; no secret is exposed to browser code."""

from datetime import datetime, timedelta, timezone
import base64
import hashlib
import hmac
import os
from jose import JWTError, jwt

from src.core.settings import get_settings

_ITERATIONS = 2**14


def hash_password(password: str) -> str:
    if len(password) < 12:
        raise ValueError("Password must contain at least 12 characters")
    salt = os.urandom(16)
    derived = hashlib.scrypt(
        password.encode("utf-8"), salt=salt, n=_ITERATIONS, r=8, p=1
    )
    return "scrypt$16384$8$1$%s$%s" % (
        base64.b64encode(salt).decode(),
        base64.b64encode(derived).decode(),
    )


def verify_password(password: str, stored: str) -> bool:
    try:
        _, n, r, p, encoded_salt, encoded_hash = stored.split("$")
        candidate = hashlib.scrypt(
            password.encode("utf-8"),
            salt=base64.b64decode(encoded_salt),
            n=int(n),
            r=int(r),
            p=int(p),
        )
        return hmac.compare_digest(candidate, base64.b64decode(encoded_hash))
    except (ValueError, TypeError):
        return False


def create_access_token(user_id: int, token_version: int = 0) -> str:
    settings = get_settings()
    expires = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_minutes
    )
    return jwt.encode(
        {"sub": str(user_id), "exp": expires, "type": "access", "ver": token_version},
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )


def access_token_version(token: str) -> int | None:
    """Return the revocation version from a valid access token."""
    settings = get_settings()
    try:
        payload = jwt.decode(
            token, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
        )
        if payload.get("type") != "access":
            return None
        return int(payload.get("ver", 0))
    except (JWTError, ValueError, TypeError):
        return None


def decode_access_token(token: str) -> int | None:
    settings = get_settings()
    try:
        payload = jwt.decode(
            token, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
        )
        subject = payload.get("sub") if payload.get("type") == "access" else None
        return int(subject) if subject else None
    except (JWTError, ValueError):
        return None
