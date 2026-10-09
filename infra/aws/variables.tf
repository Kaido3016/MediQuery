variable "aws_region" {
  description = "AWS region for the private health-document infrastructure."
  type        = string
  default     = "ca-central-1"
}

variable "name_prefix" {
  type    = string
  default = "mediquery"
}

variable "reports_bucket_name" {
  description = "Globally unique name for the private report-object bucket."
  type        = string
}

variable "backups_bucket_name" {
  description = "Globally unique name for the encrypted database-backup bucket."
  type        = string
}

variable "protected_alb_arn" {
  description = "Optional ARN of the regional Application Load Balancer to associate with WAF."
  type        = string
  default     = ""
}

variable "database_resource_arn" {
  description = "ARN of the managed RDS database protected by AWS Backup."
  type        = string
}

variable "alarm_email" {
  description = "Operations address subscribed to alarm notifications. Subscription confirmation is required."
  type        = string
}

variable "alb_name" {
  description = "CloudWatch dimension name for the Application Load Balancer."
  type        = string
}

variable "rds_instance_identifier" {
  description = "CloudWatch dimension name for the RDS instance."
  type        = string
}
