# MediQuery — Buyer Due Diligence Request Index

## Purpose

This index defines the evidence package to provide to a serious prospective acquirer. It separates verified repository facts from items that require seller-provided or independently verified evidence.

## 1. Corporate / ownership

Buyer may request:

- seller identity and authority to sell;
- ownership of source code and related IP;
- contributor/contractor agreements, if applicable;
- assignment of inventions/IP, if applicable;
- trademark/domain ownership, if included;
- open-source and third-party license inventory;
- known claims or disputes concerning the IP.

**Status:** requires transaction-specific evidence outside the repository.

## 2. Source code

Provide:

- exact repository URL and acquisition branch/tag;
- exact release/commit under consideration;
- complete source tree;
- build/run instructions;
- dependency manifests;
- test suite and CI configuration;
- known limitations and technical debt.

**Status:** repository evidence available; buyer should independently reproduce the release.

## 3. Security

Buyer may review:

- authentication implementation;
- authorization/tenant isolation;
- upload validation;
- secret/configuration handling;
- CORS/security headers;
- logging and audit patterns;
- dependency vulnerabilities;
- infrastructure configuration;
- penetration-test results, if any.

**Status:** repository evidence exists for implemented controls. Independent penetration testing is not represented as completed unless separately evidenced.

## 4. Privacy / healthcare

Buyer may request:

- privacy impact assessment;
- data-flow diagrams;
- retention/deletion policy;
- data residency architecture;
- encryption-at-rest/in-transit evidence;
- access-control policy;
- incident-response process;
- PHI/PII handling assessment;
- legal analysis for the buyer's intended jurisdiction.

**Status:** not represented as completed certification/compliance evidence by the repository.

## 5. AI / ML

Buyer should distinguish implemented software from future extension points.

Request evidence for:

- production model integrations;
- model/provider contracts;
- model versions;
- evaluation datasets;
- labeled benchmark results;
- retrieval corpus ownership/licensing;
- prompt/system-instruction inventory;
- model safety evaluations;
- inference costs and latency.

**Status:** do not infer production AI capability from architecture documents or unused utilities. Any future AI capability must be demonstrated and independently verified.

## 6. Product / traction

Buyer may request:

- hosted-demo details;
- user/customer counts;
- usage analytics;
- revenue records;
- contracts;
- pilots/LOIs;
- retention/engagement metrics;
- product roadmap.

**Status:** no customer, revenue, or production-usage claim should be made without evidence.

## 7. Operations

Buyer may review:

- deployment procedure;
- environment configuration;
- backups/recovery;
- monitoring/alerting;
- incident history;
- uptime history;
- cloud/vendor dependencies;
- operational runbooks.

**Status:** documentation exists; production operational history requires separate evidence.

## 8. Transaction scope

Before signing a definitive agreement, define explicitly:

- source-code rights transferred;
- repository/history transfer;
- domains/brands/assets, if any;
- datasets/models, if any;
- third-party licenses that can/cannot be transferred;
- support/transition period;
- warranties and representations;
- exclusions;
- payment structure;
- confidentiality;
- liability/indemnification terms;
- governing law.

## Evidence rule

Every material buyer-facing claim should have one of these statuses:

- **Verified in repository**
- **Verified by external evidence**
- **Seller representation — requires diligence**
- **Not implemented / not claimed**

Never convert a planned capability into an implemented capability merely because documentation describes it.
