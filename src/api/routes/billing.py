"""Stripe subscription checkout and signature-verified, idempotent webhooks."""

from datetime import datetime, timezone
import logging

import stripe
from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.api.dependencies import current_user
from src.api.schemas import BillingResponse, CheckoutResponse
from src.core.billing import billing_summary
from src.core.database import PaymentEvent, Subscription, User, get_db
from src.core.observability import metrics
from src.core.settings import get_settings

router = APIRouter()
logger = logging.getLogger("mediquery.billing")


@router.get("/summary", response_model=BillingResponse)
def summary(
    user: User = Depends(current_user), db: Session = Depends(get_db)
) -> BillingResponse:
    return BillingResponse(**billing_summary(db, user))


@router.post("/checkout", response_model=CheckoutResponse)
def checkout(user: User = Depends(current_user)) -> CheckoutResponse:
    settings = get_settings()
    if not all(
        (
            settings.stripe_secret_key,
            settings.stripe_price_id,
            settings.stripe_success_url,
            settings.stripe_cancel_url,
        )
    ):
        metrics.increment("billing.checkout_unconfigured")
        return CheckoutResponse(
            available=False,
            checkout_url=None,
            message="Subscription checkout is not configured.",
        )
    stripe.api_key = settings.stripe_secret_key
    try:
        session = stripe.checkout.Session.create(
            mode="subscription",
            line_items=[{"price": settings.stripe_price_id, "quantity": 1}],
            customer_email=user.email,
            client_reference_id=str(user.id),
            metadata={"user_id": str(user.id)},
            subscription_data={"metadata": {"user_id": str(user.id), "plan": "pro"}},
            success_url=settings.stripe_success_url,
            cancel_url=settings.stripe_cancel_url,
            idempotency_key=f"mediquery-checkout-user-{user.id}-{int(datetime.now(timezone.utc).timestamp()) // 60}",
        )
    except Exception as exc:
        logger.warning("stripe_checkout_creation_failed")
        raise HTTPException(
            status_code=502, detail="Checkout is temporarily unavailable."
        ) from exc
    metrics.increment("billing.checkout_created")
    return CheckoutResponse(
        available=True,
        checkout_url=session.url,
        message="Continue to Stripe to complete your subscription.",
    )


@router.post("/portal", response_model=CheckoutResponse)
def billing_portal(
    user: User = Depends(current_user), db: Session = Depends(get_db)
) -> CheckoutResponse:
    """Create a Stripe customer portal session for subscription management/cancellation."""
    settings = get_settings()
    if not settings.stripe_secret_key or not settings.stripe_portal_return_url:
        raise HTTPException(
            status_code=503, detail="Billing management is not configured."
        )
    subscription = db.scalar(
        select(Subscription)
        .where(Subscription.user_id == user.id, Subscription.provider == "stripe")
        .order_by(Subscription.created_at.desc())
    )
    if not subscription or not subscription.external_customer_id:
        raise HTTPException(
            status_code=404, detail="No Stripe customer is linked to this account."
        )
    stripe.api_key = settings.stripe_secret_key
    try:
        session = stripe.billing_portal.Session.create(
            customer=subscription.external_customer_id,
            return_url=settings.stripe_portal_return_url,
        )
    except Exception as exc:
        logger.warning("stripe_portal_creation_failed")
        raise HTTPException(
            status_code=502, detail="Billing management is temporarily unavailable."
        ) from exc
    return CheckoutResponse(
        available=True,
        checkout_url=session.url,
        message="Manage or cancel your subscription through Stripe.",
    )


def _unix_datetime(value: object) -> datetime | None:
    try:
        return datetime.fromtimestamp(int(value), tz=timezone.utc).replace(tzinfo=None)
    except (TypeError, ValueError, OSError):
        return None


def _apply_subscription_event(db: Session, event_type: str, obj: dict) -> None:
    subscription_id = (
        obj.get("id")
        if event_type.startswith("customer.subscription.")
        else obj.get("subscription")
    )
    if not subscription_id:
        return
    subscription_data = obj if event_type.startswith("customer.subscription.") else {}
    metadata = subscription_data.get("metadata") or obj.get("metadata") or {}
    user_id_raw = metadata.get("user_id") or obj.get("client_reference_id")
    existing = db.scalar(
        select(Subscription).where(
            Subscription.external_subscription_id == str(subscription_id)
        )
    )
    user = (
        db.get(User, int(user_id_raw))
        if user_id_raw and str(user_id_raw).isdigit()
        else (db.get(User, existing.user_id) if existing else None)
    )
    if not user:
        logger.warning("stripe_subscription_event_unmatched")
        return
    default_status = (
        "active"
        if event_type == "checkout.session.completed"
        else ("past_due" if event_type == "invoice.payment_failed" else "unknown")
    )
    status_value = str(subscription_data.get("status") or default_status)
    plan = "pro" if status_value in {"active", "trialing"} else "free"
    customer_id = subscription_data.get("customer") or obj.get("customer")
    period_end = _unix_datetime(subscription_data.get("current_period_end"))
    if existing is None:
        existing = Subscription(
            user_id=user.id,
            plan=plan,
            status=status_value,
            provider="stripe",
            external_customer_id=str(customer_id) if customer_id else None,
            external_subscription_id=str(subscription_id),
            current_period_end=period_end,
        )
        db.add(existing)
    else:
        existing.plan = plan
        existing.status = status_value
        existing.external_customer_id = (
            str(customer_id) if customer_id else existing.external_customer_id
        )
        existing.current_period_end = period_end or existing.current_period_end
    user.plan = plan


@router.post("/webhook", status_code=200)
async def stripe_webhook(
    request: Request,
    stripe_signature: str | None = Header(default=None, alias="Stripe-Signature"),
    db: Session = Depends(get_db),
) -> dict[str, bool]:
    settings = get_settings()
    if not settings.stripe_webhook_secret or not stripe_signature:
        raise HTTPException(status_code=400, detail="Invalid webhook.")
    payload = await request.body()
    try:
        event = stripe.Webhook.construct_event(
            payload, stripe_signature, settings.stripe_webhook_secret
        )
    except Exception as exc:
        metrics.increment("billing.webhook_signature_rejected")
        raise HTTPException(
            status_code=400, detail="Invalid webhook signature."
        ) from exc
    event_id = str(event.get("id", ""))
    event_type = str(event.get("type", ""))
    if not event_id:
        raise HTTPException(status_code=400, detail="Invalid webhook event.")
    if db.scalar(
        select(PaymentEvent).where(PaymentEvent.provider_event_id == event_id)
    ):
        return {"received": True}
    obj = event.get("data", {}).get("object", {})
    if event_type in {
        "checkout.session.completed",
        "customer.subscription.created",
        "customer.subscription.updated",
        "customer.subscription.deleted",
        "invoice.payment_failed",
    }:
        _apply_subscription_event(db, event_type, obj)
    db.add(PaymentEvent(provider_event_id=event_id, event_type=event_type))
    try:
        db.commit()
    except Exception:
        db.rollback()
        # Unique provider_event_id makes concurrent retries safe; provider will retry if
        # the transaction genuinely failed.
        if db.scalar(
            select(PaymentEvent).where(PaymentEvent.provider_event_id == event_id)
        ):
            return {"received": True}
        raise
    metrics.increment("billing.webhook_processed")
    return {"received": True}
