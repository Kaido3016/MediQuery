"""Account lifecycle regression tests using synthetic accounts and mocked email delivery."""

import re
from uuid import uuid4

import pyotp
from fastapi.testclient import TestClient

from src.api.main import app


def _signup(client: TestClient) -> tuple[str, str]:
    email = f"security-{uuid4().hex}@example.test"
    password = "secure-password-for-tests"
    response = client.post(
        "/api/auth/signup",
        json={
            "email": email,
            "password": password,
            "acknowledge_medical_limitations": True,
        },
    )
    assert response.status_code == 201
    return email, password


def test_logout_revokes_previously_issued_access_tokens():
    with TestClient(app) as client:
        email, password = _signup(client)
        token = client.post("/api/auth/login", json={"email": email, "password": password}).json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        assert client.post("/api/auth/logout", headers=headers).status_code == 204
        assert client.get("/api/reports", headers=headers).status_code == 401
        refreshed = client.post("/api/auth/login", json={"email": email, "password": password})
        assert refreshed.status_code == 200
        assert client.get("/api/reports", headers={"Authorization": f"Bearer {refreshed.json()['access_token']}"}).status_code == 200


def test_mfa_is_required_at_login_and_enabling_revokes_old_token():
    with TestClient(app) as client:
        email, password = _signup(client)
        token = client.post("/api/auth/login", json={"email": email, "password": password}).json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        setup = client.post("/api/auth/mfa/setup", headers=headers)
        assert setup.status_code == 200
        secret = setup.json()["secret"]
        enabled = client.post("/api/auth/mfa/enable", headers=headers, json={"code": pyotp.TOTP(secret).now()})
        assert enabled.status_code == 200
        assert client.get("/api/reports", headers=headers).status_code == 401
        assert client.post("/api/auth/login", json={"email": email, "password": password}).status_code == 401
        login = client.post("/api/auth/login", json={"email": email, "password": password, "totp_code": pyotp.TOTP(secret).now()})
        assert login.status_code == 200


def test_password_reset_is_single_use_and_revokes_old_tokens(monkeypatch):
    from src.api.routes import account_security

    sent = []
    monkeypatch.setattr(account_security, "send_account_email", lambda recipient, subject, body: sent.append(body))
    with TestClient(app) as client:
        email, password = _signup(client)
        old_token = client.post("/api/auth/login", json={"email": email, "password": password}).json()["access_token"]
        requested = client.post("/api/auth/password-reset/request", json={"email": email})
        assert requested.status_code == 202
        assert sent
        match = re.search(r"password_reset_token=([A-Za-z0-9_-]+)", sent[-1])
        assert match
        reset_token = match.group(1)
        reset = client.post("/api/auth/password-reset/confirm", json={"token": reset_token, "new_password": "a-different-strong-password"})
        assert reset.status_code == 200
        assert client.post("/api/auth/password-reset/confirm", json={"token": reset_token, "new_password": "another-strong-password"}).status_code == 400
        assert client.post("/api/auth/login", json={"email": email, "password": password}).status_code == 401
        new_login = client.post("/api/auth/login", json={"email": email, "password": "a-different-strong-password"})
        assert new_login.status_code == 200
        assert client.get("/api/reports", headers={"Authorization": f"Bearer {old_token}"}).status_code == 401


def test_email_verification_token_is_single_use(monkeypatch):
    from src.api.routes import account_security
    from src.core.database import SessionLocal, User
    from sqlalchemy import select

    sent = []
    monkeypatch.setattr(account_security, "send_account_email", lambda recipient, subject, body: sent.append(body))
    with TestClient(app) as client:
        email, _ = _signup(client)
        with SessionLocal() as db:
            user = db.scalar(select(User).where(User.email == email))
            user.email_verified = False
            db.commit()
        response = client.post("/api/auth/verification/resend", json={"email": email})
        assert response.status_code == 202
        match = re.search(r"verify_email_token=([A-Za-z0-9_-]+)", sent[-1])
        assert match
        token = match.group(1)
        assert client.post("/api/auth/verify-email", json={"token": token}).status_code == 200
        assert client.post("/api/auth/verify-email", json={"token": token}).status_code == 400
