resource "aws_cloudwatch_log_group" "api" {
  name              = var.api_log_group_name
  retention_in_days = 90
}

resource "aws_cloudwatch_log_metric_filter" "scanner_unavailable" {
  name           = "${var.name_prefix}-scanner-unavailable"
  log_group_name = aws_cloudwatch_log_group.api.name
  pattern        = "\"reports.scanner_unavailable\""

  metric_transformation {
    name      = "ScannerUnavailable"
    namespace = "MediQuery/Operations"
    value     = "1"
  }
}

resource "aws_cloudwatch_log_metric_filter" "storage_deletion_failed" {
  name           = "${var.name_prefix}-storage-deletion-failed"
  log_group_name = aws_cloudwatch_log_group.api.name
  pattern        = "\"storage_deletion_failed\""

  metric_transformation {
    name      = "StorageDeletionFailed"
    namespace = "MediQuery/Operations"
    value     = "1"
  }
}

resource "aws_cloudwatch_log_metric_filter" "email_delivery_failed" {
  name           = "${var.name_prefix}-email-delivery-failed"
  log_group_name = aws_cloudwatch_log_group.api.name
  pattern        = "\"account_email_delivery_failed\""

  metric_transformation {
    name      = "AccountEmailDeliveryFailed"
    namespace = "MediQuery/Operations"
    value     = "1"
  }
}

resource "aws_cloudwatch_metric_alarm" "scanner_unavailable" {
  alarm_name          = "${var.name_prefix}-scanner-unavailable"
  namespace           = "MediQuery/Operations"
  metric_name         = "ScannerUnavailable"
  statistic           = "Sum"
  period              = 300
  evaluation_periods  = 1
  threshold           = 1
  comparison_operator = "GreaterThanOrEqualToThreshold"
  alarm_actions       = [aws_sns_topic.operations.arn]
  treat_missing_data  = "notBreaching"
}

resource "aws_cloudwatch_metric_alarm" "storage_deletion_failed" {
  alarm_name          = "${var.name_prefix}-storage-deletion-failed"
  namespace           = "MediQuery/Operations"
  metric_name         = "StorageDeletionFailed"
  statistic           = "Sum"
  period              = 300
  evaluation_periods  = 1
  threshold           = 1
  comparison_operator = "GreaterThanOrEqualToThreshold"
  alarm_actions       = [aws_sns_topic.operations.arn]
  treat_missing_data  = "notBreaching"
}

resource "aws_cloudwatch_metric_alarm" "email_delivery_failed" {
  alarm_name          = "${var.name_prefix}-account-email-delivery-failed"
  namespace           = "MediQuery/Operations"
  metric_name         = "AccountEmailDeliveryFailed"
  statistic           = "Sum"
  period              = 300
  evaluation_periods  = 1
  threshold           = 1
  comparison_operator = "GreaterThanOrEqualToThreshold"
  alarm_actions       = [aws_sns_topic.operations.arn]
  treat_missing_data  = "notBreaching"
}

resource "aws_cloudwatch_metric_alarm" "restore_verification_missing" {
  alarm_name          = "${var.name_prefix}-restore-verification-missing"
  namespace           = "MediQuery/Backup"
  metric_name         = "RestoreVerification"
  statistic           = "Sum"
  period              = 86400
  evaluation_periods  = 90
  threshold           = 1
  comparison_operator = "LessThanThreshold"
  alarm_actions       = [aws_sns_topic.operations.arn]
  treat_missing_data  = "breaching"
}
