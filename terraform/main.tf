# For a V1, this project will use only a local state file.
# Could be improved by store in a S3 bucket and use a DynamoDB table for state locking.

terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# IAM role for App Runner to access ECR and other AWS services
resource "aws_iam_role" "apprunner_instance_role" {
  name = "${var.project_name}-apprunner-instance-role-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "tasks.apprunner.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name        = "${var.project_name}-apprunner-instance-role"
    Environment = var.environment
    Project     = var.project_name
  }
}

# App Runner Service
resource "aws_apprunner_service" "bert-llm-chat-app-backend" {
  service_name = "${var.project_name}-backend-${var.environment}"

  source_configuration {
    auto_deployments_enabled = false

    authentication_configuration {
      access_role_arn = aws_iam_role.apprunner_ecr_access_role.arn
    }

    image_repository {
      image_identifier      = "${aws_ecr_repository.backend.repository_url}:latest"
      image_repository_type = "ECR"

      image_configuration {
        port = "8080"

        # Non-sensitive environment variables
        runtime_environment_variables = {
          GROQ_MODEL            = var.groq_model
          GROQ_TEMPERATURE      = var.groq_temperature
          GROQ_MAX_TOKENS       = var.groq_max_tokens
          FAISS_INDEX_DIR       = "/app/faiss_index"
          EMBEDDING_MODEL       = var.embedding_model
          K_NEIGHBORS           = var.k_neighbors
          HOST                  = "0.0.0.0"
          PORT                  = "8080"
        }

        # Sensitive environment variables from Secrets Manager
        runtime_environment_secrets = {
          GROQ_API_KEY    = aws_secretsmanager_secret.secrets["groq_api_key"].arn
          ALLOWED_ORIGINS = aws_secretsmanager_secret.secrets["allowed_origins"].arn
        }
      }
    }
  }

  health_check_configuration {
    protocol            = "HTTP"
    path                = "/health"
    interval            = 20 # 1 hour
    timeout             = 5
    healthy_threshold   = 1
    unhealthy_threshold = 5
  }

  instance_configuration {
    cpu               = var.app_runner_cpu
    memory            = var.app_runner_memory
    instance_role_arn = aws_iam_role.apprunner_instance_role.arn
  }

  network_configuration {
    egress_configuration {
      egress_type = "DEFAULT" # Allows outbound calls to Groq API
    }
  }

  tags = {
    Name        = "${var.project_name}-backend"
    Environment = var.environment
    Project     = var.project_name
  }
}
