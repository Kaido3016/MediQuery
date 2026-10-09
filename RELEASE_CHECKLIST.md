# MediQuery — Release / Buyer Handoff Checklist

## Repository gates

### Phase acceptance

- [ ] Phase 17 acceptance: differentiation evidence and claims are reviewed.
- [ ] Phase 18 acceptance: medical safety tests and non-claims are reviewed.
- [ ] Phase 19 acceptance: production-readiness tests and external blockers are reviewed.
- [ ] Phase 20 acceptance: commercial handoff and buyer evidence are reviewed.

- [ ] Pin the exact release commit SHA.
- [ ] Black formatting, Flake8 lint, pytest, and compileall pass for src, tests, app.py, evaluation, and ops.
- [ ] Fresh-database Alembic migration passes; upgrade and rollback/restore are tested on a disposable copy.
- [ ] Synthetic extraction evaluation passes and its scope is described as regression-only, not clinical accuracy.
- [ ] GitHub Actions quality and Terraform validation are green.
- [ ] Docker build and production Compose configuration validation pass.
- [ ] CodeQL/dependency/security gates have no unresolved release-blocking findings.
- [ ] No local database, private uploads, .env, PHI, token, or credential-shaped secret is committed.

## Production infrastructure

- [ ] Provision managed PostgreSQL, private S3/KMS, Redis, ClamAV, SMTP, Stripe, secret manager, and least-privilege workload roles.
- [ ] Apply reviewed Terraform for private buckets, lifecycle, database backup plan, WAF, HTTPS listener/redirect, and CloudWatch/SNS alerts.
- [ ] Verify TLS certificate, DNS, ALB security groups, WAF association, private networking, and trusted proxy IPs in the actual cloud account.
- [ ] Schedule encrypted backups, isolated restore verification, and storage-deletion outbox worker.
- [ ] Confirm backup retention and historical-version deletion behavior match the published privacy policy.
- [ ] Confirm monitoring, alarm routing, backup age, restore-drill metric, and deletion backlog alerts.
- [ ] Assign named on-call owners and complete an incident-response tabletop.

## Account and billing lifecycle

- [ ] Verify email delivery, token expiry/replay prevention, password recovery, TOTP MFA, KMS seed encryption, and logout/session revocation.
- [ ] Test Stripe checkout, portal, signed webhook, duplicate/out-of-order webhook, cancellation, past-due transition, and entitlement enforcement in test mode.
- [ ] Confirm customer support, refunds/disputes, tax, subscription terms, and billing disclosures with the payment/legal owners.

## Extraction and medical safety

- [ ] Run the labeled synthetic regression corpus and retain metrics for exact precision/recall/F1 and field-level correctness.
- [ ] Obtain a representative legally authorized and independently double-labeled evaluation corpus before real-world accuracy claims.
- [ ] Complete clinical review of intended use, risk criteria, high-risk extraction errors, and human-factors wording.
- [ ] Do not market OCR or clinical AI/RAG as implemented until each is built and separately evaluated.

## Independent assurance — external sign-off required

- [ ] Independent penetration test and retest complete; no unresolved critical/high findings.
- [ ] Privacy/legal review complete for target markets, consent, data residency, retention, vendor agreements, deletion, breach duties, and regulatory scope.
- [ ] Clinical validation appropriate to intended use completed by qualified reviewers.
- [ ] IP ownership, contributor rights, dependency licenses, and data/source provenance reviewed.
- [ ] Production deployment, backup/restore, incident-response, accessibility, and load tests reviewed and signed off.

The repository prepares evidence and controls but cannot self-certify an external assessment. Passing CI does not mean any independent review or production authorization is complete.
