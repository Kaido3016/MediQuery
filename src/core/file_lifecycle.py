"""Atomic local-file staging for report/account deletion.

Files are renamed before the database transaction and permanently removed only
after the transaction commits. If the database operation fails, staged files are
restored so the account/report remains usable.
"""

import logging
from pathlib import Path
from uuid import uuid4

logger = logging.getLogger("mediquery.file_lifecycle")


def stage_files(paths: list[Path]) -> list[tuple[Path, Path]]:
    staged: list[tuple[Path, Path]] = []
    try:
        for target in paths:
            if not target.exists():
                continue
            quarantine = target.with_name(f".{target.name}.deleting-{uuid4().hex}")
            target.rename(quarantine)
            staged.append((target, quarantine))
    except OSError:
        restore_staged_files(staged)
        raise
    return staged


def restore_staged_files(staged: list[tuple[Path, Path]]) -> None:
    for target, quarantine in reversed(staged):
        try:
            if quarantine.exists() and not target.exists():
                quarantine.rename(target)
        except OSError:
            # Do not log a path: storage keys can contain sensitive operational data.
            logger.error("report_delete_restore_failed")


def purge_staged_files(staged: list[tuple[Path, Path]]) -> None:
    for _, quarantine in staged:
        try:
            quarantine.unlink(missing_ok=True)
        except OSError:
            # The DB record is already deleted; an operator needs a generic alert
            # to reconcile this orphan without exposing the path in logs.
            logger.error("report_delete_orphan_cleanup_failed")
