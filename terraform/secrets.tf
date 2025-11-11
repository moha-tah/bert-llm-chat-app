# ============================================================================
# Secrets Management for App Runner
# ============================================================================
# This file centralizes all secrets configuration to avoid code duplication.
#
# To add a new secret:
# 1. Add it to the locals.secrets map below
# 2. Add the corresponding variable in variables.tf
# 3. Reference it in main.tf's runtime_environment_secrets block
# 4. Update terraform.tfvars with the actual value
# ============================================================================

# Define all secrets in a single map
locals {
  secrets = {
    groq_api_key = {
      description = "Groq API key for LLM access"
      value       = var.groq_api_key
    }
    allowed_origins = {
      description = "Allowed origins for CORS"
      value       = var.allowed_origins
    }
  }
}

# Create all secrets in AWS Secrets Manager
resource "aws_secretsmanager_secret" "secrets" {
  for_each = local.secrets

  name        = "${var.project_name}-${each.key}-${var.environment}"
  description = each.value.description

  tags = {
    Name        = "${var.project_name}-${each.key}"
    Environment = var.environment
    Project     = var.project_name
  }
}

# Store secret values
resource "aws_secretsmanager_secret_version" "secrets" {
  for_each = local.secrets

  secret_id     = aws_secretsmanager_secret.secrets[each.key].id
  secret_string = each.value.value
}

# IAM policy to allow App Runner to read all secrets
resource "aws_iam_role_policy" "apprunner_secrets_policy" {
  name = "${var.project_name}-apprunner-secrets-policy-${var.environment}"
  role = aws_iam_role.apprunner_instance_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = [
          for secret in aws_secretsmanager_secret.secrets : secret.arn
        ]
      }
    ]
  })
}

# Output all secret ARNs for reference
output "secret_arns" {
  description = "ARNs of all secrets in Secrets Manager"
  value = {
    for key, secret in aws_secretsmanager_secret.secrets : key => secret.arn
  }
  sensitive = true
}
