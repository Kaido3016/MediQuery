resource "aws_backup_vault" "mediquery" {
  name        = "${var.name_prefix}-database-backups"
  kms_key_arn = aws_kms_key.mediquery.arn
}

resource "aws_iam_role" "backup" {
  name = "${var.name_prefix}-aws-backup-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = { Service = "backup.amazonaws.com" }
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "backup" {
  role       = aws_iam_role.backup.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSBackupServiceRolePolicyForBackup"
}

resource "aws_iam_role_policy_attachment" "restore" {
  role       = aws_iam_role.backup.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSBackupServiceRolePolicyForRestores"
}

resource "aws_backup_plan" "mediquery" {
  name = "${var.name_prefix}-daily-rds"

  rule {
    rule_name         = "daily-encrypted-rds-backup"
    target_vault_name = aws_backup_vault.mediquery.name
    schedule          = "cron(0 5 * * ? *)"
    lifecycle { delete_after = 35 }
    recovery_point_tags = {
      Application = "MediQuery"
      DataClass   = "SensitiveHealthData"
    }
  }
}

resource "aws_backup_selection" "database" {
  name         = "${var.name_prefix}-managed-database"
  plan_id      = aws_backup_plan.mediquery.id
  iam_role_arn = aws_iam_role.backup.arn
  resources    = [var.database_resource_arn]
}

resource "aws_sns_topic" "operations" {
  name = "${var.name_prefix}-operations-alerts"
}

resource "aws_sns_topic_subscription" "operations_email" {
  topic_arn = aws_sns_topic.operations.arn
  protocol  = "email"
  endpoint  = var.alarm_email
}

resource "aws_cloudwatch_metric_alarm" "alb_5xx" {
  alarm_name          = "${var.name_prefix}-alb-5xx"
  namespace           = "AWS/ApplicationELB"
  metric_name         = "HTTPCode_ELB_5XX_Count"
  statistic           = "Sum"
  period              = 300
  evaluation_periods  = 2
  threshold           = 5
  comparison_operator = "GreaterThanOrEqualToThreshold"
  dimensions          = { LoadBalancer = var.alb_name }
  alarm_actions       = [aws_sns_topic.operations.arn]
  treat_missing_data  = "notBreaching"
}

resource "aws_cloudwatch_metric_alarm" "rds_cpu" {
  alarm_name          = "${var.name_prefix}-rds-high-cpu"
  namespace           = "AWS/RDS"
  metric_name         = "CPUUtilization"
  statistic           = "Average"
  period              = 300
  evaluation_periods  = 3
  threshold           = 85
  comparison_operator = "GreaterThanOrEqualToThreshold"
  dimensions          = { DBInstanceIdentifier = var.rds_instance_identifier }
  alarm_actions       = [aws_sns_topic.operations.arn]
  treat_missing_data  = "notBreaching"
}
