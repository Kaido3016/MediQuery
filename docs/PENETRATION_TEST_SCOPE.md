# Independent penetration-test scope — MediQuery

**Status: not performed.** This document defines a proposed engagement scope. It is not a report, certification, or evidence that any test has occurred. Testing must be conducted by an independent qualified assessor under written authorization and an agreed rules-of-engagement document.

## Systems in scope

- FastAPI API and Streamlit client in an isolated staging environment.
- Authentication, email verification, password reset, TOTP MFA, token revocation, account deletion.
- PDF upload validation, ClamAV integration, private S3/KMS, report lifecycle and deletion outbox.
- Redis rate limiting, trusted-proxy handling, database authorization boundaries.
- Stripe checkout/portal and webhook processing in Stripe test mode.
- Terraform-managed AWS configuration and CI/CD permissions.

## Required test cases

1. Cross-account report read/delete and guessed identifier enumeration.
2. Expired, reused, tampered, and purpose-confused account tokens; account enumeration; password-reset token replay.
3. MFA enrollment takeover, invalid/replayed TOTP windows, recovery/lost-device procedures, KMS failure behavior, and session revocation.
4. Malformed, encrypted, oversized, decompression/pathological PDFs; EICAR test file in an isolated scanner test; ClamAV outage and timeout behavior.
5. Object-key manipulation, unauthorized S3 access, KMS permission boundaries, deletion queue replay, and lifecycle/version retention.
6. Redis outage, distributed rate-limit bypass attempts, spoofed forwarding headers, and proxy trust configuration.
7. Forged Stripe signatures, duplicate/out-of-order webhooks, incorrect metadata, canceled/past-due subscriptions, and entitlement consistency.
8. TLS policy, WAF rules, public exposure of database/Redis/ClamAV/worker endpoints, IAM privilege escalation, secret leakage, and log/metric PHI exposure.
9. Dependency/container findings and GitHub Actions permission/supply-chain risks.

## Evidence and exit criteria

The assessor should deliver methodology, tested commit/image digest, scope and exclusions, reproducible findings, severity ratings, exploitability, data-impact analysis, retest status, and a signed final report. Block launch for unresolved critical/high findings and any finding that permits unauthorized report access or uncontrolled disclosure of health data. Have the accountable security owner and privacy/legal lead approve residual risks.

Use synthetic data only. Do not test production or real patient data without explicit authorization and a separate plan.
