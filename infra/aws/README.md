# AWS production security baseline

This Terraform is an infrastructure module, not a turnkey full environment. It provisions private KMS-encrypted S3 report/backup buckets, versioning and lifecycle controls, an AWS Backup plan for an existing managed database ARN, a regional WAF ACL, and CloudWatch/SNS alarms.

## Apply

1. Review with your cloud/security owner and pin a reviewed Terraform/AWS provider version in your deployment pipeline.
2. Supply unique bucket names, the managed database ARN, ALB name/ARN, RDS identifier, and an operations email.
3. Run `terraform init`, `terraform fmt -check`, `terraform validate`, and `terraform plan`; inspect the plan before applying.
4. If an ALB already exists, set `protected_alb_arn` to associate the WAF. If omitted, WAF is provisioned but not attached.
5. Configure an HTTPS listener on the ALB with an ACM certificate, redirect HTTP to HTTPS, allow inbound traffic only on 443, and forward to the API target group. The ALB certificate/listener and network topology are deliberately deployment-specific and must be configured separately.
6. Configure the API with `STORAGE_BACKEND=s3`, the reports bucket, the output KMS key ARN, private ClamAV service address, SMTP delivery, Stripe secrets, Redis, managed PostgreSQL, and a unique JWT secret. Give the API task role only the required object actions on the reports bucket and KMS encrypt/decrypt permissions for that key.
7. Restrict the database, Redis, ClamAV, and worker to private network paths. Do not expose them publicly.

## Retention and erasure

- Live report objects are deleted through a durable application outbox; schedule `python -m ops.process_storage_deletions` from a private worker and alert on non-zero exit/backlog.
- S3 report bucket versions are retained for up to 7 days before lifecycle expiration. This is a recovery window, not immediate physical erasure.
- Encrypted database backups are retained for 35 days. User deletions may remain in older backups until backup expiry; do not promise immediate erasure from immutable backups. Document this retention in the privacy notice and contract, and have privacy/legal counsel approve the policy.
- Every backup must be followed by restore verification in an isolated database. Keep drill evidence and monitor missed backups/failed restores.
- SNS email subscriptions require recipient confirmation.

## Explicit limits

The code does not create an SMTP account, Stripe account/price/webhook, managed PostgreSQL instance, private VPC, ClamAV fleet, ACM certificate, DNS record, staffed on-call team, or legal/clinical approval. These require operator action and validation.
