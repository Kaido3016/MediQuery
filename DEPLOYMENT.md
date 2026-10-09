# Deployment

1. Provision managed Postgres and private encrypted object storage in the approved region. Do not use the development SQLite/local-directory defaults for real reports.
2. Set `ENVIRONMENT=production`, a unique 32+ character `JWT_SECRET`, the managed `DATABASE_URL`, approved HTTPS `CORS_ORIGINS`, `RATE_LIMIT_REDIS_URL` for a private Redis service, and a private `UPLOAD_ROOT` through a secret manager.
3. For monetization, configure a real provider-hosted checkout URL and populate `subscriptions` only from verified provider events. Do not mark a user as paid from a browser callback alone. Stripe integration, webhook signature verification, invoices, refunds, tax handling, and provider agreements remain deployment/business work.
4. For telemetry, configure a random 32+ character `METRICS_TOKEN` and keep `/health/metrics` reachable only from the trusted monitoring network. Forward aggregate logs/metrics to a managed system with PHI-safe retention and access controls. Do not send report text, filenames, tokens, or email addresses as metric dimensions.
5. Build and deploy the API behind TLS/WAF controls, a reverse proxy, and provider network restrictions. Do not publicly expose databases, caches, dashboards, or storage buckets.
6. Configure and test backups/restore, object lifecycle policies, malware scanning, alerts, and provider agreements before accepting PHI. A versioned schema-migration workflow remains a release blocker; do not treat `create_all()` as a migration strategy.
7. Run tests, dependency scan, secret scan, and a manual mobile/accessibility pass in CI/release approval.

The included CI workflow verifies formatting without rewriting source, linting, tests, compilation, common credential patterns, a Docker build, and Compose configuration. CI is read-only and does not push commits to `main`. It does not deploy, provision cloud resources, scan container images, or perform a compliance review. Production requires a shared Redis rate-limit backend; if it is unavailable, API requests fail closed with HTTP 503 rather than bypassing the limit.

`docker compose up --build` is a local production-shaped smoke tool, not a complete production deployment. Its API service intentionally requires a real managed database URL and secrets; it does not provision insecure database defaults.
