# MediQuery — Buyer Data Room

**Release under review:** `release/v1.0.0`

**Purpose:** organized evidence index for prospective technical, product, security, and acquisition diligence.

This data room distinguishes repository evidence from items that must be supplied or independently verified outside the source tree. Documentation is not evidence of customers, revenue, clinical validation, regulatory clearance, compliance certification, production authorization for PHI, or guaranteed acquisition value.

## 1. Product & architecture

- [`../README.md`](../README.md) — product overview and scope
- [`../ARCHITECTURE.md`](../ARCHITECTURE.md) — architecture and trust boundaries
- [`../DEPLOYMENT.md`](../DEPLOYMENT.md) — deployment guidance
- [`../PERFORMANCE.md`](../PERFORMANCE.md) — performance assumptions/evidence
- [`../TESTING.md`](../TESTING.md) — testing strategy and results

## 2. Security & medical-AI safety

- [`../SECURITY.md`](../SECURITY.md) — implemented security controls and limitations
- [`../AI_SAFETY.md`](../AI_SAFETY.md) — medical-AI safety boundary
- [`../docs/PHASE18_MEDICAL_AI_SAFETY.md`](../docs/PHASE18_MEDICAL_AI_SAFETY.md) — Phase 18 evidence
- [`../docs/PHASE24_TRUST_SECURITY_COMPLIANCE.md`](../docs/PHASE24_TRUST_SECURITY_COMPLIANCE.md) — Phase 24 evidence

## 3. Production & release evidence

- [`../docs/PHASE19_PRODUCTION_READINESS.md`](../docs/PHASE19_PRODUCTION_READINESS.md)
- [`../docs/PHASE21_PRODUCTION_INFRASTRUCTURE.md`](../docs/PHASE21_PRODUCTION_INFRASTRUCTURE.md)
- [`../docs/PHASE20_COMMERCIAL_HANDOFF.md`](../docs/PHASE20_COMMERCIAL_HANDOFF.md)
- [`../docs/PHASE25_FINAL_SALE_READINESS.md`](../docs/PHASE25_FINAL_SALE_READINESS.md)
- [`../RELEASE_CHECKLIST.md`](../RELEASE_CHECKLIST.md)
- [`../src/services/release_manifest.py`](../src/services/release_manifest.py)

**External evidence still required:** staging/production environment evidence, uptime history, backup/restore exercise, operational monitoring evidence, and any provider-level controls.

## 4. AI & evaluation evidence

- [`../docs/PHASE22_AI_EVALUATION.md`](../docs/PHASE22_AI_EVALUATION.md)
- [`../src/services/evaluation.py`](../src/services/evaluation.py)
- Synthetic report fixtures and evaluation tests in the repository

**Important:** retrieval/AI-related repository components must not be represented as proof of a populated production medical knowledge base, clinical accuracy, or production generative-AI capability unless separately verified.

## 5. Commercial product evidence

- [`../docs/PHASE23_COMMERCIAL_PRODUCT.md`](../docs/PHASE23_COMMERCIAL_PRODUCT.md)
- [`../ACQUISITION.md`](../ACQUISITION.md)
- [`../BUYER_DUE_DILIGENCE.md`](../BUYER_DUE_DILIGENCE.md)

**External evidence still required:** customer interviews, pilots, usage analytics, retention, willingness-to-pay, revenue, payment-provider evidence, and any production customer references.

## 6. Legal, IP & licensing

- [`../ACQUISITION.md`](../ACQUISITION.md) — current acquisition scope and limitations
- [`../BUYER_DUE_DILIGENCE.md`](../BUYER_DUE_DILIGENCE.md) — diligence questions and blockers

**External evidence required before closing:** contributor/IP ownership records, dependency/model/data licence inventory, trademark review, generated/copied-code review, and legal/privacy/regulatory opinions where applicable.

## 7. Release identity

The acquisition candidate is the exact tip of `release/v1.0.0` at the time of buyer handoff. Verify the branch SHA immediately before sharing the repository or data room. Application source code has not been changed as part of this data-room organization work; only acquisition documentation was added/updated.

## 8. Evidence rules

1. **Implemented** means supported by source code and/or executable tests.
2. **Documented** means described in repository documentation but not necessarily independently verified.
3. **External evidence required** means the repository cannot establish the claim by itself.
4. No document in this data room creates a warranty, certification, clinical claim, regulatory claim, customer claim, or valuation guarantee.
5. Prospective buyers should verify the exact release commit before technical diligence.
