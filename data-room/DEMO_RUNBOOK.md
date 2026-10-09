# MediQuery — Acquisition Demo Runbook

**Release:** `release/v1.0.0`

## Purpose

This runbook defines the reproducible live demonstration for a prospective technical, product, security, or acquisition buyer.

The demo is intentionally limited to capabilities represented as implemented in the repository. It must not imply clinical validation, regulatory clearance, production PHI authorization, customer traction, revenue, or production generative-AI capability.

## 1. Demo objective

Demonstrate that MediQuery provides a coherent medical-report organization workflow with authenticated access, report upload, server-side PDF validation, conservative structured extraction, page/source evidence preservation, owner-scoped report access, report deletion, usage/entitlement controls, and automated engineering quality evidence.

## 2. Environment

Run the demo from a clean checkout of the acquisition candidate. Record the exact release reference and commit SHA, runtime/OS, Docker version if used, test command/result, application start command, and demonstration timestamp.

Use synthetic/non-PHI reports only.

## 3. Pre-demo verification

1. Confirm the checkout is the intended acquisition revision.
2. Confirm no real patient data is present.
3. Confirm environment secrets are supplied through the local environment and are not displayed.
4. Run the documented test suite.
5. Confirm the application starts successfully.
6. Prepare a supported synthetic text-based medical report and an invalid/unsupported PDF fixture if available.

Record resulting evidence in the buyer data room.

## 4. Primary workflow

### A. Account creation

Create a disposable demonstration account and show the product-limitation acknowledgement. Never use real identifying information.

### B. Authentication

Sign in and show that authenticated access is required for report operations.

### C. Report upload

Upload the synthetic PDF. Show server-side validation and explain that file extension/MIME metadata alone is not treated as proof of a valid PDF.

### D. Extraction

Show extracted findings including value, unit, reference range, explicit flag when present, page number, and source evidence. Explain that the current extraction path is conservative and deterministic; do not describe it as a clinically validated AI model.

### E. Evidence review

Show the evidence text and page reference. Explain that the design preserves a traceable relationship between an extracted candidate and its source document.

### F. Privacy boundary

Explain owner-scoped report access. If two disposable accounts are available, demonstrate that one cannot retrieve the other's report. Never use real PHI.

### G. Deletion

Delete the demonstration report and show the resulting state. If account deletion is supported, demonstrate it with a disposable account.

## 5. Security demonstration

Explain authentication/authorization, generated storage keys, PDF validation and upload limits, CORS/security-header posture, safe operational logging/request IDs, rate limiting/telemetry foundations, and fail-closed production configuration requirements.

State clearly that these controls do not constitute HIPAA, PIPEDA, PHIPA, GDPR, SOC 2, or other certification.

## 6. AI/RAG boundary

Use this distinction if asked about AI:

> MediQuery contains reusable retrieval and AI-safety foundations, but the acquisition candidate should not be represented as a production generative-AI medical assistant or populated clinical RAG system.

Do not demonstrate or claim functionality that is not executable in the selected release.

## 7. Engineering evidence

Show the repository structure, architecture documentation, test results, CI quality gates, security documentation, acquisition data room, IP/licensing audit, and known limitations. The buyer should be able to reproduce the basic workflow from a clean checkout.

## 8. Five-minute executive version

**0:00–0:30 — Problem:** Medical reports contain structured information that is difficult to organize safely.

**0:30–1:30 — Product:** Create account → upload report → extraction → evidence review.

**1:30–2:30 — Trust:** Show owner isolation, validation, deletion, and evidence preservation.

**2:30–3:30 — Engineering:** Show architecture, tests, CI, deployment artifacts, and security boundaries.

**3:30–4:15 — Acquisition value:** Explain what engineering foundation the buyer receives and which components remain future work.

**4:15–5:00 — Diligence:** Show the data room and explain the external evidence still required.

## 9. Buyer questions

Be ready to answer directly: What is implemented? What is not? Is extraction AI-based? Is there production RAG? Is the product clinically validated? Can it process real PHI today? What security review exists? Who owns the IP? What licences apply? Are there customers or revenue? What must the buyer build next? Why acquire instead of building internally?

Never substitute documentation for evidence.

## 10. Demo acceptance criteria

The demo is ready when a supported synthetic PDF can be uploaded from a clean environment; extraction succeeds; evidence and page references are visible; authentication is demonstrated; owner isolation is demonstrated or supported by automated tests; deletion is demonstrated; tests pass; no PHI is used; every claim is supported by the release; and the exact release SHA is recorded.

## 11. Prohibited claims

Do not claim HIPAA/PHIPA/PIPEDA compliance, clinical validation, FDA/Health Canada approval, AI doctor/diagnostic AI, production medical RAG, production PHI processing, enterprise customers, revenue, patents, or guaranteed valuation.
