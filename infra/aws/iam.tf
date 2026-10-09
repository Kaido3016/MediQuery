resource "aws_iam_policy" "api_report_storage" {
  name        = "${var.name_prefix}-api-report-storage"
  description = "Least-privilege S3/KMS permissions for the MediQuery API task role."
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid      = "ReportBucketMetadata"
        Effect   = "Allow"
        Action   = ["s3:ListBucket", "s3:GetBucketLocation"]
        Resource = aws_s3_bucket.reports.arn
      },
      {
        Sid      = "ReportObjects"
        Effect   = "Allow"
        Action   = ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"]
        Resource = "${aws_s3_bucket.reports.arn}/*"
      },
      {
        Sid      = "ReportKms"
        Effect   = "Allow"
        Action   = ["kms:Encrypt", "kms:Decrypt", "kms:GenerateDataKey", "kms:DescribeKey"]
        Resource = aws_kms_key.mediquery.arn
      }
    ]
  })
}

resource "aws_iam_policy" "encrypted_backup_objects" {
  name        = "${var.name_prefix}-encrypted-backup-objects"
  description = "Permissions for a dedicated backup operator to upload/download encrypted PostgreSQL dumps."
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid      = "BackupBucketMetadata"
        Effect   = "Allow"
        Action   = ["s3:ListBucket", "s3:GetBucketLocation"]
        Resource = aws_s3_bucket.backups.arn
      },
      {
        Sid      = "BackupObjects"
        Effect   = "Allow"
        Action   = ["s3:GetObject", "s3:PutObject"]
        Resource = "${aws_s3_bucket.backups.arn}/postgres/*"
      },
      {
        Sid      = "BackupKms"
        Effect   = "Allow"
        Action   = ["kms:Encrypt", "kms:Decrypt", "kms:GenerateDataKey", "kms:DescribeKey"]
        Resource = aws_kms_key.mediquery.arn
      }
    ]
  })
}
