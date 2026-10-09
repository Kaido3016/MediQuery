#!/usr/bin/env bash
set -Eeuo pipefail
umask 077

: "${BACKUP_S3_URI:?Set BACKUP_S3_URI to one encrypted backup object}"
: "${AGE_IDENTITY_FILE:?Set AGE_IDENTITY_FILE to the restore-only private identity}"
: "${RESTORE_TEST_DATABASE_URL:?Set RESTORE_TEST_DATABASE_URL to a disposable isolated database}"
: "${PRODUCTION_DATABASE_URL:?Set PRODUCTION_DATABASE_URL so the script can refuse accidental production restore}"
: "${EXPECTED_ALEMBIC_REVISION:=0002_account_security_payments}"

python3 - "$RESTORE_TEST_DATABASE_URL" "$PRODUCTION_DATABASE_URL" <<'PY'
import sys
from urllib.parse import unquote, urlparse

def target(value):
    parsed = urlparse(value)
    return (parsed.hostname, parsed.port, unquote(parsed.path.lstrip("/")))

restore_target, production_target = map(target, sys.argv[1:])
if restore_target == production_target:
    raise SystemExit("Refusing to restore into the production database.")
PY

command -v aws >/dev/null
command -v age >/dev/null
command -v pg_restore >/dev/null
aws s3 cp "$BACKUP_S3_URI" - | age --decrypt --identity "$AGE_IDENTITY_FILE" > restore-test.dump
trap 'rm -f restore-test.dump' EXIT
pg_restore --list restore-test.dump >/dev/null
pg_restore --dbname="$RESTORE_TEST_DATABASE_URL" --clean --if-exists --no-owner --no-privileges restore-test.dump
revision="$(psql "$RESTORE_TEST_DATABASE_URL" -Atqc 'select version_num from alembic_version limit 1')"
[[ "$revision" == "$EXPECTED_ALEMBIC_REVISION" ]]
psql "$RESTORE_TEST_DATABASE_URL" -v ON_ERROR_STOP=1 -Atqc \
  "select count(*) from information_schema.tables where table_schema='public' and table_name in ('users','reports','report_findings','account_tokens','payment_events','storage_deletions')" \
  | awk '$1 == 6 { ok=1 } END { exit !ok }'
aws cloudwatch put-metric-data --namespace MediQuery/Backup --metric-name RestoreVerification --value 1 --unit Count --region "${AWS_REGION:-ca-central-1}"
printf 'restore_verification=passed migration_revision=%s\n' "$revision"
