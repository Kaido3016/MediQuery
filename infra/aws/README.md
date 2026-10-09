# AWS production security baseline

This Terraform module provisions private KMS-encrypted S3 report and backup buckets, versioning/lifecycle controls, an AWS Backup plan for an existing managed database ARN, a regional WAF ACL, optional HTTPS and HTTP-redirect listeners on an existing ALB, and CloudWatch/SNS alarms.

## Apply

1. Review with your cloud/security owner and pin a reviewed Terraform/AWS provider version in the deployment pipeline.
2. Supply unique bucket names, the managed database ARN, ALB name/ARN, RDS identifier, and an operations email.
3. Run terraform init, terraform fmt -check, terraform validate, and terraform plan; inspect the plan before applying.
4. Set protected_alb_arn to associate WAF with the ALB. Set acm_certificate_arn and application_target_group_arn as well to provision the HTTPS listener and HTTP-to-HTTPS redirect. If values are omitted, the corresponding edge resources are not attached/provisioned.
5. Configure the ALB security group to accept only intended inbound traffic, normally 443 from the approved edge. Use a trusted ACM certificate, DNS, and private API targets.
6. Configure the API with STORAGE_BACKEND=s3, the reports bucket, the output KMS key ARN, private ClamAV service address, SMTP delivery, Stripe secrets, Redis, managed PostgreSQL, and a unique JWT secret. Give the API task role only required S3 object actions plus s3:ListBucket for readiness checks and KMS encrypt/decrypt permissions for the key.
7. Route API and deletion-worker stdout/stderr to the configured CloudWatch log group so metric filters and alarms can observe their events. Confirm SNS email subscriptions.
8. Restrict database, Redis, ClamAV, and worker to private network paths. Do not expose them publicly.

## Retention and erasure

- Live report objects are deleted through a durable application outbox; schedule python -m ops.process_storage_deletions from a private worker and alert on non-zero exit/backlog.
- S3 report bucket versions are retained for up to 7 days before lifecycle expiration. This is a recovery window, not immediate physical erasure.
- Encrypted database backups are retained for 35 days. User deletions may remain in older backups until backup expiry; do not promise immediate erasure from immutable backups. Disclose the schedule in privacy notices/contracts and obtain legal approval.
- Schedule encrypted backups and isolated restore drills using ops/backup_postgres.sh and ops/verify_restore.sh. Keep revision, integrity, RPO/RTO, operator, and sign-off evidence.
- SNS email subscriptions require recipient confirmation.

## Explicit limits

This module does not create your VPC, RDS instance, DNS, ACM certificate, application target group, ECS/Fargate service, ClamAV fleet, SMTP account, Stripe product/webhook, or staffed on-call team. It does not perform an independent penetration test, privacy/legal review, or clinical validation. Those require operator action and independent reviewers.
