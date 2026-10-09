"""Stripe webhook signature and idempotency tests without live payment calls."""

from types import SimpleNamespace
from uuid import uuid4

from fastapi.testclient import TestClient
import stripe

from src.api.main import app


def _account(client):
    email = f"billing-{uuid4().hex}@example.test"
    password = "secure-password-for-tests"
    client.post(
        "/api/auth/signup",
        json={
            "email": email,
            "password": password,
            "acknowledge_medical_limitations": True,
        },
    )
    token = client.post("/api/auth/login", json={"email": email, "password": password}).json()["access_token"]
    return email, {"Authorization": f"Bearer {token}"}


def test_checkout_never_claims_payment_when_stripe_is_not_configured():
    with TestClient(app) as client:
        _, headers = _account(client)
        response = client.post("/api/billing/checkout", headers=headers)
        assert response.status_code == 200
        assert response.json()["available"] is False
        assert response.json()["checkout_url"] is None


def test_stripe_webhook_requires_a_valid_signature(monkeypatch):
    from src.api.routes import billing

    monkeypatch.setattr(billing, "get_settings", lambda: SimpleNamespace(stripe_webhook_secret="whsec_test"))
    monkeypatch.setattr(stripe.Webhook, "construct_event", lambda *args, **kwargs: (_ for _ in ()).throw(ValueError("bad signature")))
    with TestClient(app) as client:
        response = client.post("/api/billing/webhook", content=b"{}", headers={"Stripe-Signature": "invalid"})
        assert response.status_code == 400


def test_subscription_webhook_is_verified_idempotently_and_updates_entitlements(monkeypatch):
    from src.api.routes import billing

    event_id = f"evt_{uuid4().hex}"
    event = {
        "id": event_id,
        "type": "customer.subscription.created",
        "data": {
            "object": {
                "id": f"sub_{uuid4().hex}",
                "customer": f"cus_{uuid4().hex}",
                "status": "active",
                "current_period_end": 2_000_000_000,
                "metadata": {},
            }
        },
    }
    monkeypatch.setattr(billing, "get_settings", lambda: SimpleNamespace(stripe_webhook_secret="whsec_test"))
    monkeypatch.setattr(stripe.Webhook, "construct_event", lambda *args, **kwargs: event)
    with TestClient(app) as client:
        _, headers = _account(client)
        user_id = int(__import__("src.core.security", fromlist=["decode_access_token"]).decode_access_token(headers["Authorization"].split()[1]))
        event["data"]["object"]["metadata"]["user_id"] = str(user_id)
        first = client.post("/api/billing/webhook", content=b"signed-payload", headers={"Stripe-Signature": "valid"})
        second = client.post("/api/billing/webhook", content=b"signed-payload", headers={"Stripe-Signature": "valid"})
        assert first.status_code == second.status_code == 200
        summary = client.get("/api/billing/summary", headers=headers)
        assert summary.status_code == 200
        assert summary.json()["plan"] == "pro"
