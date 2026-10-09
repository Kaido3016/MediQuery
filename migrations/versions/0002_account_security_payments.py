"""Add account verification, MFA, revocation, and webhook idempotency.

Revision ID: 0002_account_security_payments
Revises: 0001_initial_schema
"""
from alembic import op
import sqlalchemy as sa

revision = "0002_account_security_payments"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("email_verified", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("users", sa.Column("mfa_enabled", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("users", sa.Column("mfa_secret", sa.String(length=64), nullable=True))
    op.add_column("users", sa.Column("token_version", sa.Integer(), nullable=False, server_default="0"))
    op.create_table(
        "account_tokens",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("purpose", sa.String(length=32), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("consumed_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_account_tokens_user_id", "account_tokens", ["user_id"])
    op.create_index("ix_account_tokens_purpose", "account_tokens", ["purpose"])
    op.create_index("ix_account_tokens_token_hash", "account_tokens", ["token_hash"], unique=True)
    op.create_index("ix_account_tokens_expires_at", "account_tokens", ["expires_at"])
    op.create_table(
        "storage_deletions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("storage_key", sa.String(length=512), nullable=False),
        sa.Column("requested_at", sa.DateTime(), nullable=False),
        sa.Column("processed_at", sa.DateTime(), nullable=True),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_error", sa.String(length=64), nullable=True),
    )
    op.create_index("ix_storage_deletions_processed_at", "storage_deletions", ["processed_at"])
    op.create_table(
        "payment_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("provider_event_id", sa.String(length=255), nullable=False),
        sa.Column("event_type", sa.String(length=128), nullable=False),
        sa.Column("processed_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_payment_events_provider_event_id", "payment_events", ["provider_event_id"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_storage_deletions_processed_at", table_name="storage_deletions")
    op.drop_table("storage_deletions")
    op.drop_index("ix_payment_events_provider_event_id", table_name="payment_events")
    op.drop_table("payment_events")
    op.drop_index("ix_account_tokens_expires_at", table_name="account_tokens")
    op.drop_index("ix_account_tokens_token_hash", table_name="account_tokens")
    op.drop_index("ix_account_tokens_purpose", table_name="account_tokens")
    op.drop_index("ix_account_tokens_user_id", table_name="account_tokens")
    op.drop_table("account_tokens")
    op.drop_column("users", "token_version")
    op.drop_column("users", "mfa_secret")
    op.drop_column("users", "mfa_enabled")
    op.drop_column("users", "email_verified")
