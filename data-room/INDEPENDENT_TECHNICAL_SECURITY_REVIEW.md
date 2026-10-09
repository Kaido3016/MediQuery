# MediQuery — Independent Technical & Security Review

**Review type:** repository-level technical/security due-diligence review
**Candidate:** `release/v1.0.0`
**Repository:** Akumo961/MediQuery
**Reviewer:** OpenAI code-review analysis
**Scope:** source-tree architecture, security controls, CI, tests, deployment configuration, dependencies, and documented limitations
**Status:** preliminary desk/code review — **not** a penetration test, certification, clinical validation, or legal opinion

## 1. Executive assessment

MediQuery presents a credible, security-conscious healthcare-document application foundation. The repository demonstrates meaningful controls around authentication, authorization, tenant isolation, PDF validation, generated storage keys, deletion workflows, safe logging, configuration fail-closed behavior, rate limiting, and automated quality checks.

The strongest acquisition-relevant engineering asset is the combination of **owner-scoped data access + evidence-preserving report processing + explicit medical-safety boundaries**. The principal diligence limitation is that several controls required for real PHI production are explicitly outside the repository and remain deployment/provider/operational responsibilities.

**Overall technical readiness for acquisition diligence: PASS WITH MATERIAL LIMITATIONS.**

This review does not establish that MediQuery is production-authorized for real medical records. The repository itself correctly identifies managed Postgres, private encrypted object storage, backups/restore testing, TLS/WAF, malware scanning, asynchronous resource isolation, secret management, dependency/SBOM controls, penetration testing, threat modeling, incident response, privacy/legal review, and OCR evaluation as remaining work. fileciteturn22file0

## 2. Controls observed

### Authentication & authorization — PASS

The documented implementation includes bearer-token authentication, password hashing, owner-scoped report queries, account/report deletion, and safe error handling. The test strategy states that authentication/authorization boundaries, owner isolation, account deletion, and authenticated report lifecycle are covered. fileciteturn22file0 fileciteturn24file0

### Tenant isolation — PASS

The acquisition data-room documentation identifies tenant isolation as repository evidence, while the testing documentation explicitly includes owner-isolation and authenticated upload/history/detail/delete flows. This is an important control for a multi-user healthcare application. fileciteturn18file0 fileciteturn24file0

### PDF/file security — PASS WITH LIMITATIONS

The repository documents server-side checks for extension, advisory MIME, magic bytes, byte size, page count, encryption, and malformed content. This is materially stronger than trusting a browser-provided MIME type alone. The remaining gap is deeper parser fuzzing, malware scanning, content-disarm/reconstruction policy, and sandboxing for production workloads. fileciteturn22file0

### Secrets/configuration — PASS WITH LIMITATIONS

The security documentation states that production configuration fails on default/short JWT secrets, SQLite, or HTTP CORS origins, and that local `.env` and report/database paths are ignored. This is a strong fail-closed design choice. A production deployment still requires managed secret storage, rotation, and environment-level access controls. fileciteturn22file0

### CORS/security headers/logging — PASS

The repository documents an explicit CORS allowlist, restrictive API methods/headers, baseline security headers, safe error messages, request IDs, aggregate counters, and audit metadata designed to exclude PHI. fileciteturn22file0

### Rate limiting — PASS WITH SCALING LIMITATION

Rate limiting is implemented at the API-process level according to the security documentation. For horizontally scaled production deployments, the repository itself identifies cross-replica usage/rate enforcement as additional required work. fileciteturn22file0

### CI and automated quality — PASS

The CI workflow runs Black, Flake8, pytest, compileall, and a credential-pattern scan. fileciteturn25file0 The testing documentation identifies synthetic-only test data and explicitly separates provider-bound tests from local unit/API tests. fileciteturn24file0

### Dependency posture — REVIEW REQUIRED

The runtime dependency manifest contains a broad AI/ML, image-processing, document-processing, database, and development stack. fileciteturn23file0 Before a production acquisition handoff, the buyer should generate a current SBOM, run vulnerability scanning, verify direct/transitive dependency necessity, and establish an update policy. This review does not independently certify that every pinned version is currently vulnerability-free.

### Healthcare privacy/compliance — NOT ESTABLISHED

The repository explicitly states that it does not establish HIPAA, PIPEDA, PHIPA, GDPR, SOC 2, or other certification/compliance status. fileciteturn22file0 This is a limitation, not a defect in disclosure. A buyer must evaluate the deployed system, contracts, policies, people, providers, and jurisdiction-specific obligations.

## 3. Critical acquisition findings

| ID | Finding | Severity | Acquisition implication |
|---|---|---|---|
| SEC-01 | No independent penetration test evidenced | High | Buyer should conduct or commission one before PHI production |
| SEC-02 | Managed DB/object storage/backup controls are not established by source code | High | Deployment diligence required |
| SEC-03 | No compliance certification evidenced | High | Cannot market as HIPAA/PIPEDA/PHIPA/GDPR/SOC 2 compliant |
| SEC-04 | OCR/parser hardening and malware scanning remain deployment/release work | Medium-High | Important for arbitrary uploaded medical PDFs |
| SEC-05 | Secret rotation/managed secret infrastructure not established | Medium | Required for production operations |
| SEC-06 | Dependency/SBOM process should be independently run at handoff | Medium | Supply-chain diligence item |
| SEC-07 | Clinical accuracy is not established by this review | High | No clinical-performance claims should be made |

## 4. Positive acquisition signals

1. Security limitations are documented instead of hidden.
2. Synthetic test data is explicitly required and real patient data is excluded from repository/CI artifacts. fileciteturn24file0
3. The release data room separates implemented evidence from external evidence requirements. fileciteturn18file0
4. Production configuration is designed to fail closed on several unsafe configurations. fileciteturn22file0
5. The test strategy covers security-sensitive workflows rather than only happy-path unit tests. fileciteturn24file0

## 5. Buyer verification checklist

Before closing, a buyer should independently verify:

- [ ] Exact acquisition commit and repository integrity
- [ ] Dependency/SBOM scan and license inventory
- [ ] Secret history scan
- [ ] Authentication/authorization tests
- [ ] Tenant-isolation tests including negative/IDOR cases
- [ ] PDF parser fuzzing and malformed-file handling
- [ ] Malware-scanning architecture
- [ ] Production database configuration
- [ ] Object-storage encryption/access policies
- [ ] Backup/restore and deletion behavior
- [ ] TLS/WAF/network configuration
- [ ] Centralized immutable audit logging where required
- [ ] Monitoring and incident response
- [ ] Privacy/retention/consent workflows
- [ ] Legal/regulatory assessment
- [ ] Clinical validation methodology if AI/medical interpretation is commercialized

## 6. Acquisition conclusion

**Recommendation: TECHNICAL DILIGENCE CAN PROCEED.**

The repository is sufficiently coherent to justify a buyer's deeper technical review and is not merely documentation around an unstructured prototype. However, the buyer should value it as a **security-conscious healthcare software foundation**, not as evidence of certified compliance, clinical validation, or production-grade PHI operations.

The most credible commercial claim is therefore:

> **MediQuery provides a documented, tested foundation for secure medical-document workflows, with clear controls and clearly disclosed production gaps.**

Any stronger claim requires independent evidence outside this repository.
