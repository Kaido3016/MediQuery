"""Private report storage with local development and encrypted S3 production backends."""

from pathlib import Path
from urllib.parse import urlparse

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from src.core.settings import get_settings


class StorageUnavailable(RuntimeError):
    """Private object storage failed; do not fall back to local disk in production."""


def put_report(storage_key: str, raw: bytes) -> None:
    settings = get_settings()
    if settings.storage_backend == "s3":
        if not settings.object_storage_bucket or not settings.object_storage_kms_key_id:
            raise StorageUnavailable("Encrypted object storage is not configured")
        try:
            client = _s3_client()
            client.put_object(
                Bucket=settings.object_storage_bucket,
                Key=storage_key,
                Body=raw,
                ContentType="application/pdf",
                ServerSideEncryption="aws:kms",
                SSEKMSKeyId=settings.object_storage_kms_key_id,
                Metadata={"data-classification": "sensitive-health-document"},
            )
            return
        except (BotoCoreError, ClientError) as exc:
            raise StorageUnavailable("Private object storage write failed") from exc
    target = settings.upload_root / storage_key
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(raw)


def delete_report(storage_key: str) -> None:
    settings = get_settings()
    if settings.storage_backend == "s3":
        try:
            _s3_client().delete_object(
                Bucket=settings.object_storage_bucket,
                Key=storage_key,
            )
            return
        except (BotoCoreError, ClientError) as exc:
            raise StorageUnavailable("Private object storage deletion failed") from exc
    target = settings.upload_root / storage_key
    target.unlink(missing_ok=True)


def get_report_bytes(storage_key: str) -> bytes:
    settings = get_settings()
    if settings.storage_backend == "s3":
        try:
            response = _s3_client().get_object(
                Bucket=settings.object_storage_bucket, Key=storage_key
            )
            return response["Body"].read()
        except (BotoCoreError, ClientError) as exc:
            raise StorageUnavailable("Private object storage read failed") from exc
    try:
        return (settings.upload_root / storage_key).read_bytes()
    except OSError as exc:
        raise StorageUnavailable("Private report file is unavailable") from exc


def _s3_client():
    settings = get_settings()
    return boto3.client(
        "s3",
        region_name=settings.object_storage_region,
        endpoint_url=settings.object_storage_endpoint_url,
    )
