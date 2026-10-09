#!/usr/bin/env bash
set -Eeuo pipefail
umask 077

: "${BACKUP_S3_URI:?Set BACKUP_S3_URI to one encrypted backup object}"
: "${AGE_IDENTITY_FILE:?Set AGE_IDENTITY_FILE to the restore-only private identity}"
: "${RESTORE_TEST_DATABASE_URL:?Set RESTORE_TEST_DATABASE_URL to a disposable isolated database}"
: "${PRODUCTION_DATABASE_URL:?Set PRODUCTION_DATABASE_URL so the script can refuse accidental production restore}"

if [[ "$RESTORE_TEST_DATABASE_URL" == "$PRODUCTION_DATABASE_URL" ]]; then
  echo "Refusing to restore into the production database." >&2
  exit 2
fi
command -v aws >/dev/null
command -v age >/dev/null
command -v pg_restore >/dev/null
aws s3 cp "$BACKUP_S3_URI" - | age --decrypt --identity "$AGE_IDENTITY_FILE" > restore-test.dump
trap 'rm -f restore-test.dump' EXIT
pg_restore --list restore-test.dump >/dev/null
pg_restore --dbname="$RESTORE_TEST_DATABASE_URL" --clean --if-exists --no-owner --no-privileges restore-test.dump
revision="$(psql "$RESTORE_TEST_DATABASE_URL" -Atqc 'select version_num from alembic_version limit 1')"
[[ -n "$revision" ]]
psql "$RESTORE_TEST_DATABASE_URL" -v ON_ERROR_STOP=1 -Atqc \
  "select count(*) from information_schema.tables where table_schema='public' and table_name in ('users','reports','report_findings','account_tokens','payment_events','storage_deletions')" \
  | awk '$1 == 6 { ok=1 } END { exit !ok }'
printf 'restore_verification=passed migration_revision=%s\n' "$revision"
