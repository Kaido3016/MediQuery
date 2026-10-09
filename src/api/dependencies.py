"""Reusable security dependencies for API routes."""

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from src.core.database import User, get_db
from src.core.security import access_token_version, decode_access_token

bearer = HTTPBearer(auto_error=False)


def current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
) -> User:
    user_id = decode_access_token(credentials.credentials) if credentials else None
    token_version = access_token_version(credentials.credentials) if credentials else None
    user = db.get(User, user_id) if user_id else None
    if not user or token_version is None or token_version != user.token_version:
        raise HTTPException(
            status_code=401,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
