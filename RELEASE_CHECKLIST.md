# MediQuery — Release / Buyer Handoff Checklist

## Repository gate

- [ ] Pin the exact release commit SHA.
- [ ] `python -m black --check src tests app.py`
- [ ] `python -m flake8 src tests app.py --max-line-length=120`
- [ ] `python -m pytest -q`
- [ ] `python -m compileall -q src app.py`
- [ ] Fresh-database migration passes with `alembic upgrade head`.
- [ ] Production startup rejects a missing/outdated Alembic revision.
- [ ] Production Redis rate-limit backend and trusted proxy IPs are configured and verified.
- [ ] GitHub Actions quality gate is green.
- [ ] Phase 17 acceptance is green.
- [ ] Phase 18 acceptance is green.
- [ ] Phase 19 acceptance is green.
- [ ] Phase 20 acceptance is green.
- [ ] Phase 21 acceptance is green.
- [ ] Phase 22 acceptance is green.
- [ ] Phase 23 acceptance is green.
- [ ] Phase 24 acceptance is green.
- [ ] Phase 25 acceptance is green.
- [ ] No local database, private uploads, `.env`, or credential-shaped secret is committed.

## Phase 21–25 engineering evidence

- [ ] Production deployment contract passes with managed-database, storage, TLS/WAF, secret, scanning, and backup controls represented.
- [ ] Deterministic synthetic extraction/retrieval evaluation passes.
- [ ] Accessibility and commercial UI contracts pass.
- [ ] Trust/security/compliance evidence map is complete without claiming certification.
- [ ] Final release manifest identifies the exact revision and all completed phase gates.

## Buyer demonstration

- [ ] Create account with synthetic data only.
- [ ] Upload synthetic text-based PDF.
- [ ] Verify structured findings and source evidence.
- [ ] Verify owner isolation with a second account.
- [ ] Verify report deletion and rollback-safe local-file cleanup.
- [ ] Verify invalid PDF rejection.
- [ ] Verify Free entitlement enforcement.
- [ ] Verify retrieval provenance and prompt-injection framing.

## Diligence package

- [ ] `ARCHITECTURE.md`
- [ ] `SECURITY.md`
- [ ] `AI_SAFETY.md`
- [ ] `TESTING.md`
- [ ] `DEPLOYMENT.md`
- [ ] `PERFORMANCE.md`
- [ ] `ACQUISITION.md`
- [ ] `BUYER_DUE_DILIGENCE.md`
- [ ] `docs/DEMONSTRABLE_DIFFERENTIATION.md`
- [ ] `docs/PHASE18_MEDICAL_AI_SAFETY.md`
- [ ] `docs/PHASE19_PRODUCTION_READINESS.md`
- [ ] `docs/PHASE20_COMMERCIAL_HANDOFF.md`
- [ ] `docs/PHASE21_PRODUCTION_INFRASTRUCTURE.md`
- [ ] `docs/PHASE22_AI_EVALUATION.md`
- [ ] `docs/PHASE23_COMMERCIAL_PRODUCT.md`
- [ ] `docs/PHASE24_TRUST_SECURITY_COMPLIANCE.md`
- [ ] `docs/PHASE25_FINAL_SALE_READINESS.md`

## External closing gates

- [ ] IP ownership and contributor rights verified.
- [ ] Dependency/model/data licences reviewed.
- [ ] Security/threat-model review completed.
- [ ] Target-market privacy/legal/regulatory review completed.
- [ ] Clinical review/validation appropriate to intended use completed.
- [ ] Extraction quality independently evaluated.
- [ ] Customer demand and willingness to pay validated.
- [ ] Production deployment evidence reviewed.
- [ ] Transaction and IP-transfer agreements executed.

These external items are intentionally not represented as completed by repository CI. Passing Phase 25 means the engineering package is organized for diligence, not that an acquisition has occurred or that medical-data processing is authorized.
