# MediQuery — Buyer Evidence Matrix

## Purpose

Provide a concise, evidence-first map for buyer diligence. This document prevents acquisition materials from turning planned capabilities into unsupported claims.

| Buyer question | Evidence source | Status | Buyer action |
|---|---|---|---|
| Is the backend implemented? | Repository source + tests | Verified repository evidence | Reproduce locally |
| Is authentication implemented? | Auth/security code + tests | Verified repository evidence | Review implementation |
| Is report ownership isolated? | Data-access code + tests | Verified repository evidence | Attempt tenant-isolation review |
| Are uploaded PDFs validated defensively? | Upload/validation implementation + tests | Verified repository evidence | Review limits and parser threat model |
| Is structured extraction implemented? | Report-analysis implementation + tests | Verified repository evidence | Review supported formats and limitations |
| Is evidence retained with findings? | Finding/report schema and analysis path | Verified repository evidence | Trace sample output to source evidence |
| Is there a production LLM integration? | Repository-wide integration review | Not to be claimed without evidence | Verify separately |
| Is production RAG demonstrated? | Runtime integration + evaluation evidence | Not to be claimed without evidence | Verify separately |
| Is clinical accuracy validated? | Labeled clinical benchmark/study | No evidence in acquisition package | Require independent evidence before claim |
| Is healthcare regulatory compliance certified? | Formal assessment/certification | No certification claim | Buyer/legal team to assess intended use |
| Are there customers/revenue? | Contracts, invoices, analytics | Requires external evidence | Request seller evidence |
| Is production uptime demonstrated? | Monitoring/hosting history | Requires external evidence | Request operational evidence |
| Is IP ownership documented? | Assignment/contributor agreements | Transaction-specific evidence | Complete before definitive agreement |
| Are third-party licenses transferable? | Dependency/license inventory | Requires diligence | Review licenses |

## Evidence hierarchy

1. **Executable/reproducible evidence** — strongest for technical capability.
2. **Repository source and automated tests** — strong for implemented code paths.
3. **Independent security/compliance reports** — required for corresponding assurance claims.
4. **Business records** — required for customer, revenue, usage, or traction claims.
5. **Roadmap/documentation statements** — useful context but not proof of implementation.

## Buyer presentation rule

During diligence, demonstrate the exact release being offered. If a feature is future work, label it future work. If an assurance requires independent certification or legal review, label it as such.

This matrix is intended to increase buyer confidence by making verification easy, not by inflating the perceived maturity of MediQuery.
