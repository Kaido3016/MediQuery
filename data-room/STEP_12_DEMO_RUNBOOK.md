# Step 12 — Buyer Technical Demo Runbook

## Objective

Give a prospective buyer a reproducible demonstration of the exact MediQuery release being evaluated.

## Demo principles

- Use a clean environment.
- Use synthetic/non-production medical-report data only.
- Never use real patient data for an informal acquisition demo.
- Show implemented behavior, not roadmap slides.
- Record the exact commit/release demonstrated.

## Demonstration flow

1. Start the documented application stack.
2. Create a demo account.
3. Authenticate.
4. Upload a valid synthetic PDF.
5. Show upload validation behavior.
6. Run the implemented report-analysis workflow.
7. Show extracted findings and their source evidence/page information where available.
8. Demonstrate that report access is owner-scoped.
9. Demonstrate deletion.
10. Run the automated test suite and show the resulting status.
11. Walk through architecture/security documentation.
12. Clearly identify features that are future work rather than implemented capabilities.

## Buyer questions to anticipate

- How is tenant isolation enforced?
- How are uploads validated?
- What evidence is retained with a finding?
- What happens when a report is malformed or encrypted?
- What is deterministic versus model-driven?
- Where would the buyer integrate its AI stack?
- What security review remains?
- What healthcare/privacy controls require additional implementation?

## Closing message

MediQuery should be presented as a coherent healthcare software foundation. The buyer is acquiring an existing implementation and the option to accelerate a product roadmap, not a claim of clinical validation or regulatory certification.

## Exit criterion

A technical buyer can reproduce the core demo and distinguish verified capabilities from future extensions.
