#!/usr/bin/env bash
set -Eeuo pipefail
umask 077

: "${DATABASE_URL:?Set DATABASE_URL for the managed PostgreSQL database}"
: "${BACKUP_BUCKET:?Set a private versioned S3 backup bucket}"
: "${BACKUP_KMS_KEY_ID:?Set the backup KMS key ARN}"
: "${AGE_RECIPIENT:?Set the age public recipient for client-side backup encryption}"

command -v pg_dump >/dev/null
command -v age >/dev/null
command -v aws >/dev/null
backup_id="$(date -u +%Y%m%dT%H%M%SZ)"
object_key="postgres/${backup_id}.dump.age"
# Client-side age encryption complements S3 KMS encryption. Never emit plaintext dumps.
pg_dump --dbname="$DATABASE_URL" --format=custom --no-owner --no-acl \
  | age --recipient "$AGE_RECIPIENT" \
  | aws s3 cp - "s3://${BACKUP_BUCKET}/${object_key}" \
      --sse aws:kms --sse-kms-key-id "$BACKUP_KMS_KEY_ID" \
      --metadata "created-at=${backup_id},format=pg-custom-age"
printf 'backup_uploaded key=%s\n' "$object_key"
