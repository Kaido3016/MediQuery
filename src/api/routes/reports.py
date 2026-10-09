"""Authenticated, owner-scoped report lifecycle endpoints."""

import asyncio
import logging
from pathlib import Path
from time import perf_counter
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from src.api.dependencies import current_user
from src.api.schemas import PlanResponse, ReportResponse
from src.core.billing import can_consume, current_usage, get_plan, record_usage
from src.core.database import AuditEvent, Report, ReportFinding, User, get_db
from src.core.file_lifecycle import purge_staged_files, restore_staged_files, stage_files
from src.core.observability import elapsed_ms, metrics
from src.core.settings import get_settings
from src.services.report_analysis import (
    ReportValidationError,
    extract_report,
    validate_pdf,
)

router = APIRouter()
logger = logging.getLogger("mediquery.reports")


def _get_owned_report(report_id: str, user: User, db: Session) -> Report:
    report = db.scalar(
        select(Report)
        .where(
            Report.id == report_id,
            Report.owner_id == user.id,
            Report.deleted_at.is_(None),
        )
        .options(selectinload(Report.findings))
    )
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


def _store_report_bytes(target: Path, raw: bytes) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(raw)


@router.post("", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
async def upload_report(
    file: UploadFile = File(...),
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
) -> Report:
    started = perf_counter()
    settings = get_settings()
    if not can_consume(db, user, "report"):
        metrics.increment("billing.report_limit_reached")
        raise HTTPException(
            status_code=402,
            detail="Report limit reached for the current plan",
        )

    raw = await file.read(settings.max_report_bytes + 1)
    try:
        validate_pdf(file.filename, file.content_type, raw, settings.max_report_bytes)
        extraction = await asyncio.to_thread(
            extract_report, raw, settings.max_pdf_pages
        )
    except ReportValidationError as exc:
        metrics.increment("reports.upload_failed")
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    finally:
        await file.close()

    report_id = str(uuid4())
    storage_key = f"{user.id}/{report_id}.pdf"
    target = settings.upload_root / storage_key
    await asyncio.to_thread(_store_report_bytes, target, raw)
    report = Report(
        id=report_id,
        owner_id=user.id,
        original_filename=Path(file.filename or "report.pdf").name,
        storage_key=storage_key,
        page_count=extraction.page_count,
        extraction_note=extraction.note,
    )
    db.add(report)
    db.flush()
    for finding in extraction.findings:
        db.add(ReportFinding(report_id=report.id, **finding.__dict__))
    db.add(
        AuditEvent(
            actor_id=user.id,
            action="report_uploaded",
            target_id=report.id,
            metadata_json={
                "pages": extraction.page_count,
                "finding_count": len(extraction.findings),
            },
        )
    )
    if not record_usage(
        db,
        user,
        "report",
        idempotency_key=f"report:{report.id}",
    ):
        target.unlink(missing_ok=True)
        db.rollback()
        metrics.increment("billing.report_limit_race")
        raise HTTPException(
            status_code=402,
            detail="Report limit reached for the current plan",
        )
    db.commit()
    db.refresh(report)
    metrics.increment("reports.processed")
    metrics.observe_ms("reports.processing_latency", elapsed_ms(started))
    if extraction.note:
        metrics.increment("reports.extraction_attention_required")
    return _get_owned_report(report.id, user, db)


@router.get("", response_model=list[ReportResponse])
def list_reports(
    user: User = Depends(current_user), db: Session = Depends(get_db)
) -> list[Report]:
    return list(
        db.scalars(
            select(Report)
            .where(Report.owner_id == user.id, Report.deleted_at.is_(None))
            .options(selectinload(Report.findings))
            .order_by(Report.created_at.desc())
        )
    )


@router.get("/plan", response_model=PlanResponse)
def get_plan_status(
    user: User = Depends(current_user), db: Session = Depends(get_db)
) -> PlanResponse:
    plan = get_plan(user, db)
    return PlanResponse(
        plan=plan.name,
        reports_used=current_usage(db, user.id, "report"),
        reports_limit=plan.report_limit,
    )


@router.get("/{report_id}", response_model=ReportResponse)
def get_report(
    report_id: str, user: User = Depends(current_user), db: Session = Depends(get_db)
) -> Report:
    return _get_owned_report(report_id, user, db)


@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_report(
    report_id: str, user: User = Depends(current_user), db: Session = Depends(get_db)
) -> None:
    report = _get_owned_report(report_id, user, db)
    settings = get_settings()
    target = settings.upload_root / report.storage_key
    staged = stage_files([target])
    db.delete(report)
    db.add(
        AuditEvent(
            actor_id=user.id,
            action="report_deleted",
            target_id=report_id,
            metadata_json={},
        )
    )
    try:
        db.commit()
    except Exception:
        db.rollback()
        restore_staged_files(staged)
        raise
    purge_staged_files(staged)
    metrics.increment("reports.deleted")
