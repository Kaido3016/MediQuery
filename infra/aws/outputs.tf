output "reports_bucket_name" {
  value = aws_s3_bucket.reports.bucket
}

output "backups_bucket_name" {
  value = aws_s3_bucket.backups.bucket
}

output "kms_key_arn" {
  value = aws_kms_key.mediquery.arn
}

output "waf_web_acl_arn" {
  value = aws_wafv2_web_acl.mediquery.arn
}

output "operations_topic_arn" {
  value = aws_sns_topic.operations.arn
}
