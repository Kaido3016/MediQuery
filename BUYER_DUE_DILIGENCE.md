# MediQuery — Buyer Due Diligence

## Executive status

MediQuery is an evidence-first medical-report organization and deterministic extraction software asset. The report workflow does not execute clinical AI/ML inference and is not represented as a diagnostic service or clinically validated medical device.

## Implemented in code

- Authenticated accounts, owner-scoped report access, password hashing, expiring JWTs, and token-version revocation.
- Production email-verification and password-reset flows using hashed, expiring, single-use tokens.
- Optional TOTP MFA with KMS-encrypted production seeds.
- Layered PDF validation and fail-closed ClamAV scanning in production.
- Private S3 object storage with explicit KMS encryption; durable deletion outbox and retry worker.
- Versioned Alembic migrations, shared Redis rate limiting, request IDs, and privacy-conscious logs.
- Stripe checkout/customer portal, signed webhook verification, event-idempotency ledger, and server-side subscription state updates.
- Terraform baseline for encrypted buckets, lifecycle, existing RDS backup plan, WAF, optional HTTPS listener/redirect, and operational alarms.
- Backup/restore scripts, incident-response runbook, and 50-case synthetic extraction regression corpus with precision/recall/F1 and field metrics.

## Evaluation and AI/RAG disclosure

The extraction corpus is synthetic and designed for software regression. Its scores are not clinical accuracy, not a performance estimate on real-world PDFs, and not evidence of clinical validity. No OCR, semantic RAG, LLM report explanation, diagnosis, triage, or treatment recommendation is claimed as an active feature.

## External dependencies and release blockers

The Terraform and application code do not provision an actual production account, managed database, DNS/certificate, application cluster, private network, SMTP provider, Stripe product/webhook, ClamAV fleet, or on-call function. These must be configured and verified by the operator.

**No clinical validation** or independent penetration test, privacy/legal review, or clinical validation has been performed by this repository change. Review templates are provided in docs/PENETRATION_TEST_SCOPE.md, docs/PRIVACY_LEGAL_REVIEW_CHECKLIST.md, and docs/CLINICAL_VALIDATION_PROTOCOL.md. They are preparation documents, not signed assessments.

## Data retention and deletion

Live S3 objects are deleted through the durable outbox. S3 historical object versions may persist until lifecycle expiration (configured up to 7 days). Encrypted database backups are retained for 35 days, so deleted user data may remain in prior backups until those backups expire. Do not promise immediate physical erasure from backups; legal/privacy review must approve the retention policy and user-facing wording.

## Commercial/IP diligence

There is **no verified customer traction** in this repository. No customer revenue, retention, partnership, or market traction is claimed unless separately documented. Verify code ownership, contributor rights, dependency licenses, data/source provenance, trademark rights, privacy/regulatory scope, and transaction/IP-transfer terms before a commercial sale. No certification, clinical validation, or authorization to process real patient data is claimed.
