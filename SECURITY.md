# Security and privacy posture

## Implemented in this repository

- Bearer-token authentication, password hashing, and owner-scoped report queries.
- Server-side PDF extension, advisory MIME, magic-byte, byte-size, page-count, encryption, and malformed-file checks.
- Generated storage keys; report files are no longer served through a public static route or returned as filesystem paths.
- Report deletion and account deletion remove local report objects and database records in the local implementation.
- Production configuration fails when a default/short JWT secret, SQLite, or HTTP CORS origin is used.
- Explicit CORS allowlist, restrictive API methods/headers, baseline security headers, safe error messages, and non-PHI audit-event fields.
- Redis-backed shared sliding-window rate limiting in production, tighter request budgets for authentication/report/search endpoints, request IDs, and aggregate counters that omit report text, filenames, emails, and tokens. Development fallback is memory-bounded and process-local.
- A versioned acknowledgement that MediQuery is not medical advice is required at account creation and is recorded as non-PHI audit metadata.
- `.env` and local report/database paths are ignored; Compose requires injected secrets and binds the API to loopback by default.

## Still required before processing real medical reports

- A managed Postgres database, private encrypted object storage, a versioned migration/release workflow, backups, restore testing, and verified deletion from backups on the documented schedule.
- TLS termination, WAF, malware scanning, asynchronous extraction with resource isolation, rate/usage enforcement across replicas, session revocation, email verification/password reset, MFA/admin controls, and immutable audit-log retention. Redis-backed rate limits are implemented in code but still require an operated Redis service and deployment validation.
- Secret manager, rotation, dependency/SBOM scanning, CI security gates, pen test, threat model, incident response, vendor DPA review, and security monitoring.
- OCR implementation/evaluation for scanned PDFs; content-disarm/reconstruction policy as appropriate; a review of parser CVEs and sandboxing.
- A privacy notice, consent flow, retention policy, data-subject request workflow, data residency decision, and legal/regulatory review.

## Provider responsibilities

Cloud/database/object-storage/AI providers control parts of physical security, infrastructure encryption, availability, backups, and regional processing. MediQuery must select suitable services, configure encryption and access controls, execute relevant agreements, and verify their settings. Those provider controls are not created merely by this source code.

## Compliance statement

Nothing in this repository establishes HIPAA, PIPEDA, PHIPA, GDPR, SOC 2, or any other certification/compliance status. Suitability depends on the deployed environment, contracts, policies, people, operations, and independent legal/compliance assessment.
