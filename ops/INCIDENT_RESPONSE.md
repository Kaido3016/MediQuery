# MediQuery production incident response

This runbook is a starting control, not proof that a staffed response function exists. Assign named on-call owners, test contact paths, and approve it with privacy/legal counsel before production.

## Severity and first response

- **P1 — suspected health-data disclosure, credential compromise, unauthorized access, or malware bypass:** page the security incident lead immediately; preserve evidence; isolate affected services and credentials; do not delete logs or backups.
- **P2 — prolonged outage, backup failure, storage deletion backlog, or authentication/billing integrity incident:** page the service owner; fail closed for upload and sensitive operations if required controls are unavailable.
- **P3 — non-sensitive degradation:** track, mitigate, and review in the normal operations queue.

## First 60 minutes

1. Open an incident record with UTC start time, incident commander, scope, and an internal random incident ID. Do not put report text, filenames, patient identifiers, or tokens in tickets or chat.
2. Preserve access, WAF, database, object-store, CI, and identity-provider logs with retention controls. Record hashes and who accessed evidence.
3. Contain: revoke affected sessions by incrementing user token versions; rotate credentials through the provider; disable affected integrations; restrict public ingress; quarantine suspicious uploads.
4. Determine which systems, records, jurisdictions, and time windows may be involved using metadata only where possible.
5. Notify privacy/legal leadership promptly to determine statutory, contractual, regulator, and individual-notification duties. Do not make public or legal conclusions from engineering alone.
6. Recover from a known-good image and verified backup only after integrity checks. Run smoke tests and monitor for recurrence.

## Required drills and evidence

- Quarterly restore drill with duration, data-integrity checks, migration revision, RPO/RTO results, operator, and sign-off.
- Quarterly access-key rotation and session-revocation test.
- Monthly storage-deletion outbox reconciliation; alert on oldest pending deletion and repeated provider failures.
- Tabletop exercise for exposed credentials, malicious PDF, data exfiltration, failed backup, and payment webhook replay.
- Post-incident review with root cause, blast radius, customer impact, corrective owners, and deadlines.
