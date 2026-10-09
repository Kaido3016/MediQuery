# Deployment and production operations

## Required providers

The production API fails closed unless these are configured:

- Managed PostgreSQL and a current Alembic schema.
- Private S3-compatible object storage with a KMS key; production uploads explicitly request KMS encryption.
- Private Redis for shared rate limiting.
- ClamAV scanner reachable only on a private network.
- Transactional SMTP delivery for email verification and password recovery.
- Stripe secret key, webhook signing secret, recurring price ID, success/cancel URLs, and customer-portal return URL.
- HTTPS frontend URL, unique JWT secret, metrics token, and exact trusted proxy IP/CIDR values.

Never use real patient data in local Compose or CI. The provided Compose file is a production-shaped smoke environment; it is not a complete cloud network.

## AWS infrastructure baseline

See infra/aws/README.md. The module provides a KMS key, private versioned S3 buckets, report-version lifecycle, a 35-day database-backup plan, regional WAF rules, optional HTTPS/HTTP-redirect listeners on an existing ALB, and CloudWatch/SNS alerts. Review every plan and run Terraform format/validation before applying.

The module does not create your VPC, RDS instance, DNS, ACM certificate, ECS/Fargate service, ClamAV fleet, Stripe product, SMTP provider, or IAM workload role. Configure an ACM certificate and an existing ALB/target group, set the optional ALB/certificate/target-group variables, and restrict network ingress to trusted paths. Keep database, Redis, ClamAV, object storage, and deletion worker private.

## Migrations

Before startup, apply migrations:

    alembic upgrade head

For an existing database created by create_all(), take a verified backup and compare the live schema to revision 0001_initial_schema. Only if it matches exactly, stamp that revision and apply the newer migration. Do not stamp or migrate a populated database blindly. Test both upgrade and restore against a disposable copy first.

## Backup, restore, and deletion

- Schedule bash ops/backup_postgres.sh with a restricted role, an AGE_RECIPIENT, an encrypted private backup bucket, and a KMS key.
- Schedule bash ops/verify_restore.sh against a disposable isolated database. It refuses a restore URL equal to the configured production URL and emits a CloudWatch restore-verification metric after passing.
- Schedule python -m ops.process_storage_deletions as a private worker. Alert on failures and on the age/count of pending deletion rows.
- Terraform sets report-object noncurrent-version expiration to 7 days and database-backup retention to 35 days. Those are retention windows, not immediate physical erasure. User data can remain in encrypted database backups until expiry. Publish this accurately in the privacy notice and obtain legal approval.
- Restore tests prove technical recoverability, not that every backup is compliant or every individual deletion is physically purged. Record each drill's revision, integrity checks, RPO/RTO, operator, and sign-off.

## Account security

Production signup requires email verification before protected API access. Recovery links are hashed at rest, single-use, and expiring. TOTP MFA is optional per account; seeds are encrypted with KMS in production. Password reset, MFA changes, and logout revoke all previously issued bearer tokens for that account. Configure SMTP delivery, KMS permissions, and alerting before rollout.

## Stripe subscriptions

Configure Stripe Checkout and the customer portal with HTTPS URLs. Register the webhook endpoint at /api/billing/webhook for checkout completion, subscription created/updated/deleted, and invoice payment failures. Copy the exact signing secret to the secret manager. The API verifies Stripe signatures and records provider event IDs to make webhook processing idempotent. Test successful payment, delayed webhook, duplicate webhook, cancellation, payment failure, and refund/dispute handling in Stripe test mode. Do not grant entitlements from a frontend redirect.

## Monitoring and incident response

Route API stdout/stderr to the CloudWatch log group named by api_log_group_name; Terraform creates metric filters and alerts for scanner failures, storage-deletion failures, email-delivery failures, ALB 5xx, and RDS CPU. Confirm the SNS email subscription. The /health endpoint is a liveness endpoint, not proof all dependencies are healthy. Monitor Redis, S3/KMS, ClamAV, SMTP, Stripe webhook delivery, backup age, restore drills, and deletion queue backlog separately.

Use ops/INCIDENT_RESPONSE.md. Assign named on-call owners and test the playbook before launch. Logs, metrics, tickets, and alerts must never contain report text, patient identifiers, filenames, access tokens, MFA secrets, or reset tokens.

## Independent release gates

A passing CI run does not complete an independent penetration test, privacy/legal review, clinical validation, regulator assessment, or production deployment review. Keep the relevant release checklist items open until named external reviewers have signed off. OCR and clinical AI/RAG remain unimplemented; the checked-in extraction metrics are for synthetic regression fixtures only.
