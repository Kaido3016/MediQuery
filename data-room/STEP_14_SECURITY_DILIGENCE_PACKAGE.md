# Step 14 — Security Diligence Package

## Objective

Present MediQuery's security posture accurately and define the remaining buyer verification work.

## Evidence to demonstrate

- Authentication and password protection.
- JWT expiration/claims handling.
- Owner-scoped report access.
- Defensive PDF validation.
- Generated storage keys rather than user-controlled filesystem paths.
- Parameterized ORM access.
- Security headers/CORS configuration.
- Fail-closed production configuration where implemented.
- Audit-oriented logging that avoids placing report content in audit metadata.
- Automated security-related tests and CI checks.

## Required independent diligence

- Dependency vulnerability scan.
- Static analysis review.
- Dynamic application security testing.
- PDF parser/fuzz testing appropriate to the deployment.
- Cloud/infrastructure review.
- Secret-management review.
- Penetration testing where required by buyer policy.

## Claim policy

Do not call MediQuery secure, compliant, or production-ready solely because these controls exist. They are evidence of engineering practices and must be evaluated in the buyer's intended environment.

## Exit criterion

A security reviewer receives a clear map of implemented controls and outstanding verification tasks.
