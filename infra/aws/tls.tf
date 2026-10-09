locals {
  configure_https_listener = var.protected_alb_arn != "" && var.acm_certificate_arn != "" && var.application_target_group_arn != ""
}

resource "aws_lb_listener" "https" {
  count             = local.configure_https_listener ? 1 : 0
  load_balancer_arn = var.protected_alb_arn
  port              = 443
  protocol          = "HTTPS"
  certificate_arn   = var.acm_certificate_arn
  ssl_policy        = "ELBSecurityPolicy-TLS13-1-2-2021-06"

  default_action {
    type             = "forward"
    target_group_arn = var.application_target_group_arn
  }
}

resource "aws_lb_listener" "http_redirect" {
  count             = local.configure_https_listener ? 1 : 0
  load_balancer_arn = var.protected_alb_arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type = "redirect"
    redirect {
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }
  }
}
