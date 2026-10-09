# Security and privacy posture

## Implemented in the repository

- Owner-scoped report access, strict PDF validation, server-generated storage keys, and evidence-preserving deterministic extraction.
- Versioned Alembic schema and production startup guard.
- Production S3 adapter explicitly requests KMS encryption; the AWS baseline creates private, versioned buckets and lifecycle rules.
- ClamAV INSTREAM upload scanning. Production configuration requires a scanner, and uploads fail closed when it is unavailable or returns an unknown response.
- Durable storage-deletion outbox for S3 erasure, with a scheduled worker that retries failures without logging object keys.
- Expiring, hashed, single-use email-verification and password-reset tokens; generic recovery responses; SMTP delivery adapter.
- Optional TOTP MFA, production KMS encryption for TOTP seeds, and account token-version revocation after logout, password reset, or MFA changes.
- Stripe-hosted subscription checkout and customer portal, signed webhook verification, event idempotency, and server-side plan state updates.
- Shared Redis rate limits in production, trusted-proxy configuration, security headers, request IDs, and PHI-conscious aggregate logging.
- AWS Terraform for KMS/S3, RDS backup plan, WAF, optional HTTPS redirect/listener, and operational alarms.
- Synthetic labeled extraction corpus and reproducible precision/recall/F1/field-level evaluation script.

## Still required before processing real medical reports

- Apply and review the infrastructure in the target AWS account; configure IAM least privilege, VPC/network restrictions, TLS certificate/DNS, service log routing, secret management/rotation, Redis, ClamAV capacity/signature updates, SMTP, Stripe, and database operations.
- Independently perform a penetration test and threat-model review; remediate findings and retain evidence. CodeQL and automated tests are not substitutes for this.
- Obtain privacy/legal review for applicable laws, data residency, consent, retention, vendor agreements/DPAs, breach reporting, user rights, and deletion from backups.
- Obtain independent clinical review and validation appropriate to the intended product and target market. The synthetic regression corpus is not a clinical benchmark.
- Implement/evaluate OCR for scanned PDFs and any future semantic RAG/LLM path before marketing those capabilities. No clinical AI inference is active in the report workflow.
- Test load/capacity, restore and disaster recovery, accessibility, session lifecycle, email deliverability, Stripe retries/refunds/disputes, and incident response with named owners.

## Retention and deletion semantics

Deleting a report or account removes the database-visible record and queues live S3 object deletion. Versioned object data can persist until the configured 7-day noncurrent-version lifecycle expires it. Database backups are retained for 35 days and can contain records deleted after the backup was made until that backup expires. This must be disclosed accurately; do not promise immediate physical erasure from backups.

## Provider responsibilities

Cloud/database/object-storage/AI providers control parts of physical security, infrastructure encryption, availability, backups, and regional processing. MediQuery must select suitable services, configure encryption and access controls, execute relevant agreements, and verify their settings. Source code alone does not create those controls.

## Compliance statement

Nothing in this repository establishes HIPAA, PIPEDA, PHIPA, GDPR, SOC 2, regulatory clearance, clinical validation, or production authorization for real patient data. Those conclusions require independent review of the deployed environment, contracts, policies, people, and operations.
