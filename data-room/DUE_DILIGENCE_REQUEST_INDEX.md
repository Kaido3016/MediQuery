# MediQuery — Buyer Due Diligence Request Index

## Purpose

This index defines the evidence package to provide to a serious prospective acquirer. It separates verified repository facts from items that require seller-provided or independently verified evidence.

## Corporate / ownership

Buyer may request seller authority, source-code ownership, contributor/contractor agreements, IP assignments, trademark/domain ownership, third-party license inventory, and known IP disputes.

**Status:** transaction-specific evidence required.

## Source code

Provide the exact repository/release, complete source tree, build/run instructions, dependencies, tests, CI configuration, known limitations, and technical debt.

**Status:** repository evidence available; buyer should independently reproduce the release.

## Security

Review authentication, authorization/tenant isolation, upload validation, secrets/configuration, CORS/security headers, logging/audit patterns, dependency vulnerabilities, infrastructure, and penetration-test evidence where available.

**Status:** repository evidence exists for implemented controls; independent security testing is not represented as completed unless separately evidenced.

## Privacy / healthcare

Review data flows, retention/deletion, residency, encryption, access control, incident response, PHI/PII handling, and legal requirements for the intended jurisdiction and use case.

**Status:** no certification/compliance claim is made by this repository.

## AI / ML

Require evidence for production model integrations, model versions, evaluation datasets, retrieval corpora, prompts, safety evaluations, inference costs, and latency.

**Status:** production AI/RAG must not be inferred from documentation or unused extension points.

## Product / traction

Request hosted-demo details, customer/user evidence, usage analytics, revenue, contracts, pilots/LOIs, retention, and roadmap evidence where applicable.

**Status:** no customer, revenue, or production-usage claim should be made without evidence.

## Operations

Review deployment, environment configuration, backups/recovery, monitoring, incident history, uptime, vendors, and runbooks.

**Status:** documentation exists; production history requires external evidence.

## Transaction scope

Define source-code rights, repository/history, domains/brands/assets, datasets/models, transferable licenses, support/transition, warranties, exclusions, payment, confidentiality, liability, and governing law.

## Evidence rule

Every material buyer-facing claim must be classified as **Verified in repository**, **Verified by external evidence**, **Seller representation — requires diligence**, or **Not implemented / not claimed**.

Never convert a planned capability into an implemented capability merely because documentation describes it.
