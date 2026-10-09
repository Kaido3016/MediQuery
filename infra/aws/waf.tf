resource "aws_wafv2_web_acl" "mediquery" {
  name        = "${var.name_prefix}-regional-waf"
  description = "Managed baseline protection for the MediQuery public API."
  scope       = "REGIONAL"

  default_action {
    allow {}
  }

  rule {
    name     = "AWSManagedCommonRuleSet"
    priority = 10
    override_action {
      none {}
    }
    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesCommonRuleSet"
        vendor_name = "AWS"
      }
    }
    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "MediQueryCommonRules"
      sampled_requests_enabled   = false
    }
  }

  rule {
    name     = "AWSManagedKnownBadInputs"
    priority = 20
    override_action {
      none {}
    }
    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesKnownBadInputsRuleSet"
        vendor_name = "AWS"
      }
    }
    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "MediQueryKnownBadInputs"
      sampled_requests_enabled   = false
    }
  }

  rule {
    name     = "IPRateLimit"
    priority = 30
    action {
      block {}
    }
    statement {
      rate_based_statement {
        limit              = 2000
        aggregate_key_type = "IP"
      }
    }
    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "MediQueryEdgeRateLimit"
      sampled_requests_enabled   = false
    }
  }

  visibility_config {
    cloudwatch_metrics_enabled = true
    metric_name                = "MediQueryWAF"
    sampled_requests_enabled   = false
  }
}

resource "aws_wafv2_web_acl_association" "alb" {
  count        = var.protected_alb_arn == "" ? 0 : 1
  resource_arn = var.protected_alb_arn
  web_acl_arn  = aws_wafv2_web_acl.mediquery.arn
}
