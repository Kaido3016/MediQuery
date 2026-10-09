"""Strict API contracts for accounts, billing, and structured report processing."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class SignUpRequest(BaseModel):
    email: str = Field(
        min_length=3,
        max_length=320,
        pattern=r"^[^\s@]+@[^\s@]+\.[^\s@]+$",
    )
    password: str = Field(min_length=12, max_length=128)
    acknowledge_medical_limitations: bool = False


class LoginRequest(BaseModel):
    email: str = Field(
        min_length=3,
        max_length=320,
        pattern=r"^[^\s@]+@[^\s@]+\.[^\s@]+$",
    )
    password: str = Field(min_length=12, max_length=128)
    totp_code: str | None = Field(default=None, min_length=6, max_length=8)


class TokenRequest(BaseModel):
    token: str = Field(min_length=20, max_length=256)


class PasswordResetRequest(BaseModel):
    email: str = Field(min_length=3, max_length=320, pattern=r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


class PasswordResetConfirm(BaseModel):
    token: str = Field(min_length=20, max_length=256)
    new_password: str = Field(min_length=12, max_length=128)


class TotpRequest(BaseModel):
    code: str = Field(min_length=6, max_length=8)


class MfaDisableRequest(BaseModel):
    code: str = Field(min_length=6, max_length=8)
    password: str = Field(min_length=12, max_length=128)


class AuthResponse(BaseModel):
    access_token: str | None = None
    token_type: Literal["bearer"] = "bearer"
    verification_required: bool = False


class FindingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    value: str
    unit: str | None
    reference_range: str | None
    flag: Literal["high", "low", "normal", "unknown"]
    page: int
    evidence: str


class ReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    original_filename: str
    status: str
    page_count: int
    extraction_note: str | None
    created_at: datetime
    findings: list[FindingResponse] = Field(default_factory=list)


class PlanResponse(BaseModel):
    plan: Literal["free", "pro"]
    reports_used: int
    reports_limit: int | None


class UsageResponse(BaseModel):
    used: int
    limit: int | None


class BillingResponse(BaseModel):
    plan: Literal["free", "pro"]
    subscription_status: str
    billing_provider: str | None
    reports: UsageResponse
    ai_requests: UsageResponse


class CheckoutResponse(BaseModel):
    available: bool
    checkout_url: str | None
    message: str
