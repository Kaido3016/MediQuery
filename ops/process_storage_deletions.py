"""Process the durable storage-deletion outbox.

Run as a scheduled, least-privilege worker. Output and logs intentionally omit
storage keys and account identifiers because they may be sensitive.
"""
import logging
from datetime import datetime

from sqlalchemy import select

from src.core.database import SessionLocal, StorageDeletion
from src.core.storage import delete_report

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("mediquery.storage_deletions")


def run_batch(batch_size: int = 100) -> tuple[int, int]:
    processed = failed = 0
    with SessionLocal() as db:
        items = list(
            db.scalars(
                select(StorageDeletion)
                .where(StorageDeletion.processed_at.is_(None))
                .order_by(StorageDeletion.requested_at)
                .limit(batch_size)
            )
        )
        for item in items:
            try:
                delete_report(item.storage_key)
                item.processed_at = datetime.utcnow()
                item.last_error = None
                processed += 1
            except Exception:
                item.attempts += 1
                item.last_error = "storage_provider_error"
                failed += 1
                logger.error("storage_deletion_failed attempts=%s", item.attempts)
        db.commit()
    logger.info("storage_deletion_batch processed=%s failed=%s", processed, failed)
    return processed, failed


if __name__ == "__main__":
    _, failures = run_batch()
    raise SystemExit(1 if failures else 0)
