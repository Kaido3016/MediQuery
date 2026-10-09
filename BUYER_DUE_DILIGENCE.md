# MediQuery — Buyer Due Diligence (Current Release)

## Executive status

MediQuery is a **working health-tech software asset** for authenticated medical-report organization and deterministic evidence-preserving extraction.

Primary journey:

`Signup/Login → PDF Upload → Validation → Processing → Structured Findings → Page Evidence → Report History/Detail → Account Deletion`

The release is intentionally **not** represented as a clinically validated medical device or autonomous clinical AI.

## Implemented controls

- Authenticated signup/login with password hashing, validation, and expiring JWTs.
- Protected report routes and owner-scoped database queries.
- Cross-owner report access denied without confirming resource existence.
- Layered PDF validation: extension, advisory MIME, magic bytes, size, parser validity, page count, and encryption.
- Server-generated storage identifiers rather than user-controlled filesystem paths.
- Deterministic `pypdf` extraction and conservative laboratory parsing.
- Numeric multiplier units such as `10^3/uL` and `10*9/L`, including common WBC/Platelets notation.
- Explicit extraction-attention notes when lab-shaped lines cannot be safely parsed.
- Page numbers and source-derived evidence persisted with findings.
- Report/account deletion lifecycle with database/file cleanup.
- Security headers, CORS controls, Redis-backed shared sliding-window rate limits with endpoint-specific budgets, safe errors, and production fail-closed configuration.
- Versioned Alembic schema migrations; production startup refuses to run against an absent or outdated migration revision.
- Rollback-safe report/account deletion staging and upload-file cleanup when persistence fails.
- Automated unit/API/security/E2E testing and CI quality gates.
- Real Docker image build and Compose configuration validation in GitHub Actions.

## AI/RAG disclosure

The protected report workflow does **not execute AI/ML inference**. This is intentional and should be described as an evidence-first deterministic workflow.

Unreachable experimental ML/retrieval scaffolding was removed. Literature search is deterministic keyword-overlap ranking. No clinical AI capability is claimed by this release.

## Frontend disclosure

The supported client is `app.py` (Streamlit). The unused React package stub was removed so the repository no longer presents a nonexistent second application surface.

## Testing status

The repository contains extraction, API/security, safety/evaluation, and buyer-facing E2E tests. The E2E test covers signup, login, upload, extraction, WBC/Platelets numeric units, evidence, report listing/detail, account deletion, and post-deletion authentication failure.

CI checks formatting, linting, tests, compilation, credential-shaped secrets, Docker image build, and Compose configuration.

## Docker status

The Dockerfile builds the FastAPI API as a non-root user with a read-only runtime filesystem and private upload volume support. Compose requires a managed PostgreSQL URL, unique JWT secret, HTTPS CORS origins, and a private Redis URL for shared rate limiting. Streamlit is deployed separately.

The repository CI performs the Docker build and Compose configuration check on GitHub-hosted Linux. Buyer-specific staging/production deployment must still be tested in the buyer's infrastructure.

## Security / privacy limitations

Repository controls do not by themselves establish a compliant production health-data environment. A buyer must independently review threat modeling, penetration testing, secrets, dependencies/SBOM, TLS/WAF, Redis availability and trusted-proxy configuration, malware scanning, backups/restore, monitoring, incident response, data retention, residency, and deletion from backups.

## Medical and regulatory limitations

No claim is made for:

- clinical validation;
- diagnostic accuracy;
- regulatory clearance/certification;
- HIPAA, PIPEDA, PHIPA, GDPR, or SOC 2 certification;
- production authorization for real patient data;
- clinical decision support;
- treatment recommendations.

**No clinical validation is claimed.**

## IP and transaction diligence

There is currently no general repository licence grant. Before acquisition, verify source-code ownership, contributor rights, dependency licences, data/source provenance, trademarks, historical artifacts, and the exact assets included in the transaction. **Legal review is required before any commercial transfer.**

## Commercial diligence

No customer revenue, retention, partnership, or market traction is claimed unless separately documented.

**No verified customer traction is claimed unless independently documented.**

A CAD $100,000+ asking price can be used as a negotiation anchor, but it is not a guaranteed valuation. Final consideration depends on strategic fit, transferable IP, technical diligence, buyer-specific replacement cost, and demonstrated time-to-market benefit.

## Buyer acceptance checklist

1. Verify the exact release commit.
2. Reproduce Python CI checks.
3. Reproduce the Docker build and Compose validation.
4. Run the E2E journey with synthetic data.
5. Review security/threat-model documentation.
6. Run buyer-specific penetration/security assessment.
7. Review dependency/SBOM and IP ownership.
8. Review privacy and medical-safety boundaries.
9. Validate deployment in buyer infrastructure.
10. Execute explicit IP/software transfer terms.
