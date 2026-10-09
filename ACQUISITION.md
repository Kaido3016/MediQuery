# MediQuery — Acquisition Package

## 1. Executive summary

MediQuery is a lean health-tech software asset built around authenticated medical-report upload, deterministic structured extraction, page-level evidence, owner-scoped access, usage controls, deletion, security engineering, testing, and deployment documentation.

The acquisition thesis is **engineering acceleration and reusable product/IP**, not claimed clinical capability, regulatory approval, revenue, or market traction.

**Current status:** working production-shaped engineering foundation; **not approved for real patient/PHI processing**.

**Medical boundary:** MediQuery is not a diagnostic service, emergency service, doctor replacement, clinically validated medical device, or autonomous clinical AI.

## 2. Implemented

- FastAPI API with authenticated signup/login.
- Owner-scoped report history, detail, and deletion.
- Layered PDF validation.
- Conservative deterministic extraction using `pypdf` and regex.
- Laboratory values, units, reference ranges, flags, page numbers, and source evidence.
- Numeric CBC units such as `10^3/uL` and `10*9/L`.
- Partial-extraction attention warnings.
- Account deletion with report/file cleanup.
- Usage entitlement and metering foundation.
- Request IDs, aggregate telemetry, Redis-backed shared rate limiting with endpoint-specific budgets, protected metrics, and fail-closed behavior when the production limiter is unavailable.
- Streamlit reference client.
- Automated tests including the primary E2E journey.
- GitHub quality and Docker gates.
- Security, architecture, safety, deployment, diligence, and commercial documentation.

## 3. Deliberately not claimed as implemented

- LLM-based medical interpretation.
- Clinical diagnosis or treatment recommendations.
- Production medical RAG.
- OCR for scanned reports.
- Clinical validation or regulatory clearance.
- HIPAA/PIPEDA/PHIPA/GDPR/SOC 2 certification.
- Live payment-provider integration.
- Managed production infrastructure.
- Verified customer traction or revenue.

## 4. Technical asset

The buyer receives, subject to the definitive transaction agreement:

- Source repository.
- API and persistence layer.
- Authentication/authorization controls.
- Document validation/extraction pipeline.
- Evidence-preserving report/finding schemas.
- Streamlit client.
- Tests and synthetic fixtures.
- Docker/Compose deployment artifacts.
- Engineering, security, safety, deployment, and buyer documentation.

## 5. Why the asset can save engineering time

A buyer does not need to begin from an empty repository. The release already establishes a coherent secure document workflow, ownership boundary, evidence model, deletion lifecycle, testing discipline, CI quality gates, and deployment shape.

The remaining work is explicit rather than hidden: production infrastructure, broader document coverage, OCR, clinical/product validation, privacy/legal work, customer validation, and any future AI layer.

## 6. Security and privacy

Application controls include authenticated access, owner-scoped authorization, layered PDF validation, server-generated storage paths, safe errors, security headers, CORS controls, shared Redis-backed rate limiting, versioned schema migrations, rollback-safe file deletion, and deletion paths.

These controls do not constitute a compliance certification. Real sensitive-data deployment requires managed infrastructure, private storage, secret management, malware scanning, isolated processing, backups/restore testing, monitoring, incident response, and applicable privacy/security/legal review.

## 7. Commercial positioning

Present MediQuery as a **health-tech software/IP asset** that accelerates a medical-document workflow. Do not present it as a certified medical product or autonomous medical AI.

A CAD $100,000+ asking price may be used as a negotiation anchor, but it is not a guaranteed valuation. Final price depends on strategic fit, clean transferable IP, buyer replacement cost, product roadmap fit, and demonstrated time-to-market benefit.

No verified customer traction is claimed unless independently documented.

## 8. Buyer demo

Use `docs/BUYER_DEMO_SCRIPT.md` and synthetic data. Demonstrate:

`Login → Upload PDF → Processing → Extracted Values → Evidence → Report → Account Deletion`

For the video version use `docs/BUYER_VIDEO_SCRIPT.md`.

## 9. Buyer diligence

Use `BUYER_DUE_DILIGENCE.md`, `BUYER_DATA_ROOM.md`, and `docs/FINAL_SECURITY_AUDIT.md`. A buyer should reproduce the CI/Docker gates, run the E2E test, review the threat model, inspect IP/dependencies, and conduct its own security/privacy/clinical/legal diligence.

## 10. Strategic buyer outreach

The initial Canada/Québec target strategy is documented in `docs/BUYER_OUTREACH_STRATEGY.md`. Target existing healthcare software, clinical workflow, laboratory, patient-experience, and health-data companies. Contact CEO/founder, CTO/VP Engineering, product leadership, partnerships, or corporate development rather than generic recruiting channels.

## 11. Acquisition structures

Possible transaction structures include:

1. Full software/IP acquisition.
2. Asset acquisition with source/documentation transfer.
3. Exclusive commercial licence with transition support.
4. Acquisition plus a short technical handover period.

Legal counsel should define the final asset schedule, representations, warranties, IP assignment, confidentiality, liabilities, and post-closing obligations. Commercial and legal diligence are required before any transaction.

## 12. Final disclosure

MediQuery's strongest assets are its working secure workflow, deterministic evidence preservation, owner isolation, deletion controls, tests, CI, deployment shape, and explicit engineering boundaries.

Its principal risks are also explicit: no verified customers/revenue, no clinical validation, no regulatory certification, no production authorization for real patient data, and no implemented clinical AI.

The correct acquisition pitch is therefore **“buy a disciplined, working health-tech software foundation and accelerate the remaining productization and validation”**, not “buy a finished medical AI company.”
