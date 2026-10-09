# Privacy and legal review checklist — MediQuery

**Status: pending independent professional review.** This is an issue-spotting checklist, not legal advice and not a compliance attestation.

A qualified privacy/legal reviewer should identify applicable laws and contractual duties based on the operator, customers, users, hosting regions, intended use, and data flows.

## Data map and purpose

- Identify controller/organization, processor/service-provider roles, user categories, and intended purposes.
- Inventory account identifiers, auth logs, uploaded reports, extracted lab findings, evidence snippets, payment identifiers, backups, and support/incident artifacts.
- Confirm lawful basis/consent and authority to upload reports; minimize collected data and document prohibited secondary uses.
- Map subprocessors (cloud, database, email, payment, malware scanning, monitoring) and regions, including support access.

## User rights and lifecycle

- Approve a clear privacy notice and terms, including non-diagnostic limitations.
- Publish retention periods for live objects, S3 versions, database backups, audit logs, email tokens, and payment records.
- Explain that report deletion queues live-object removal, S3 historical versions expire under a lifecycle rule, and database backups may retain deleted data for up to the documented backup period.
- Define and test access/correction/export/deletion request handling, identity verification, exceptions, deadlines, and evidence of completion.
- Define account closure, subscription cancellation, disputes, tax/accounting retention, and data-subject request workflows.

## Security and contracts

- Execute provider agreements/DPAs and required health-data addenda before uploading real data.
- Approve data residency, encryption/key ownership, access logging, breach notification, subcontractor changes, service termination, return/export, and deletion terms.
- Approve incident-response, breach assessment/notification, regulator contact, and customer communication procedures.
- Review transfer mechanisms for cross-border processing, analytics/telemetry, and email content.
- Review IP ownership, third-party licenses, data/source provenance, and product marketing claims.

## Product and regulatory scope

- Determine whether the intended use triggers medical-device/clinical decision-support, health-product, professional-practice, or other regulatory requirements in each target market.
- Review marketing, UI language, disclaimers, accessibility, consent, age eligibility, and complaint handling.
- Confirm that synthetic extraction scores are not presented as real-world or clinical accuracy.
- Sign and date a written opinion/decision record, list assumptions, required changes, and re-review triggers.

Do not mark this checklist complete until a qualified reviewer has assessed the actual deployed system and signed off.
