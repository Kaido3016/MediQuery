"""Encrypt TOTP seeds at rest using AWS KMS in production."""

import base64

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from src.core.settings import get_settings


def encrypt_mfa_secret(secret: str) -> str:
    settings = get_settings()
    if settings.environment.lower() != "production":
        return "plain$" + secret
    if not settings.object_storage_kms_key_id:
        raise RuntimeError("MFA secret encryption requires the configured KMS key")
    try:
        result = boto3.client(
            "kms", region_name=settings.object_storage_region
        ).encrypt(
            KeyId=settings.object_storage_kms_key_id,
            Plaintext=secret.encode("utf-8"),
            EncryptionContext={"application": "MediQuery", "purpose": "TOTP"},
        )
        return "kms$" + base64.b64encode(result["CiphertextBlob"]).decode("ascii")
    except (BotoCoreError, ClientError) as exc:
        raise RuntimeError("MFA secret encryption failed") from exc


def decrypt_mfa_secret(stored: str) -> str:
    settings = get_settings()
    if stored.startswith("plain$") and settings.environment.lower() != "production":
        return stored.removeprefix("plain$")
    if not stored.startswith("kms$") or not settings.object_storage_kms_key_id:
        raise RuntimeError("MFA secret cannot be decrypted with current configuration")
    try:
        result = boto3.client(
            "kms", region_name=settings.object_storage_region
        ).decrypt(
            KeyId=settings.object_storage_kms_key_id,
            CiphertextBlob=base64.b64decode(stored.removeprefix("kms$")),
            EncryptionContext={"application": "MediQuery", "purpose": "TOTP"},
        )
        return result["Plaintext"].decode("utf-8")
    except (BotoCoreError, ClientError, ValueError) as exc:
        raise RuntimeError("MFA secret decryption failed") from exc
