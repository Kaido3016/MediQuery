"""Database session management and tenant-scoped product models."""

from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    Text,
    create_engine,
    inspect,
    text,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    sessionmaker,
)

from src.core.settings import get_settings

settings = get_settings()
connect_args = (
    {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
)
engine = create_engine(
    settings.database_url, connect_args=connect_args, pool_pre_ping=True
)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(512))
    plan: Mapped[str] = mapped_column(String(20), default="free")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    reports: Mapped[list["Report"]] = relationship(
        back_populates="owner", cascade="all, delete-orphan"
    )
    subscriptions: Mapped[list["Subscription"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    usage_events: Mapped[list["UsageEvent"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class Report(Base):
    __tablename__ = "reports"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    original_filename: Mapped[str] = mapped_column(String(255))
    storage_key: Mapped[str] = mapped_column(String(255), unique=True)
    status: Mapped[str] = mapped_column(String(32), default="processed")
    page_count: Mapped[int] = mapped_column(Integer, default=0)
    extraction_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, index=True
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True, index=True
    )
    owner: Mapped[User] = relationship(back_populates="reports")
    findings: Mapped[list["ReportFinding"]] = relationship(
        back_populates="report", cascade="all, delete-orphan"
    )
    __table_args__ = (Index("ix_reports_owner_created", "owner_id", "created_at"),)


class ReportFinding(Base):
    __tablename__ = "report_findings"
    id: Mapped[int] = mapped_column(primary_key=True)
    report_id: Mapped[str] = mapped_column(ForeignKey("reports.id"), index=True)
    name: Mapped[str] = mapped_column(String(255))
    value: Mapped[str] = mapped_column(String(255))
    unit: Mapped[str | None] = mapped_column(String(64), nullable=True)
    reference_range: Mapped[str | None] = mapped_column(String(128), nullable=True)
    flag: Mapped[str] = mapped_column(String(16), default="unknown")
    page: Mapped[int] = mapped_column(Integer)
    evidence: Mapped[str] = mapped_column(Text)
    report: Mapped[Report] = relationship(back_populates="findings")


class Subscription(Base):
    """Provider-neutral subscription state populated by a payment adapter."""

    __tablename__ = "subscriptions"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    plan: Mapped[str] = mapped_column(String(20), default="free")
    status: Mapped[str] = mapped_column(String(32), default="none", index=True)
    provider: Mapped[str | None] = mapped_column(String(32), nullable=True)
    external_customer_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    external_subscription_id: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )
    current_period_end: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    user: Mapped[User] = relationship(back_populates="subscriptions")


class UsageEvent(Base):
    """Durable, privacy-safe usage events used for entitlement enforcement."""

    __tablename__ = "usage_events"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    metric: Mapped[str] = mapped_column(String(64), index=True)
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    idempotency_key: Mapped[str | None] = mapped_column(
        String(255), unique=True, nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, index=True
    )
    user: Mapped[User] = relationship(back_populates="usage_events")


class AuditEvent(Base):
    """Non-PHI audit metadata only. Never place report text or filenames here."""

    __tablename__ = "audit_events"
    id: Mapped[int] = mapped_column(primary_key=True)
    actor_id: Mapped[int | None] = mapped_column(nullable=True, index=True)
    action: Mapped[str] = mapped_column(String(64), index=True)
    target_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, index=True
    )
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)


def create_database() -> None:
    """Create development tables or require a fully migrated production database."""
    if settings.environment.lower() == "production":
        if not inspect(engine).has_table("alembic_version"):
            raise RuntimeError(
                "Production database has no Alembic revision; run 'alembic upgrade head' before startup"
            )
        from alembic.config import Config
        from alembic.script import ScriptDirectory

        with engine.connect() as connection:
            applied_revisions = set(
                connection.execute(text("SELECT version_num FROM alembic_version")).scalars()
            )
        expected_revisions = set(ScriptDirectory.from_config(Config("alembic.ini")).get_heads())
        if applied_revisions != expected_revisions:
            raise RuntimeError(
                "Production database schema is not at the current Alembic migration head"
            )
        return
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
