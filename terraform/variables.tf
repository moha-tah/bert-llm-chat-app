# Non-sensitive variables for MRO Copilot infrastructure

variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name used for resource naming"
  type        = string
  default     = "bert-llm-chat-app"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "prod"
}

variable "groq_api_key" {
  description = "Groq API key for LLM access"
  type        = string
  sensitive   = true
}

# App Runner Configuration
variable "github_connection_arn" {
  description = "ARN of the GitHub connection created in AWS Console"
  type        = string
}

variable "github_repository_url" {
  description = "GitHub repository URL (e.g., https://github.com/username/repo)"
  type        = string
}

variable "github_branch_name" {
  description = "GitHub branch name to deploy"
  type        = string
  default     = "main"
}

variable "app_runner_cpu" {
  description = "CPU units for App Runner instance (256, 512, 1024, 2048, 4096)"
  type        = string
  default     = "256"
}

variable "app_runner_memory" {
  description = "Memory for App Runner instance (512, 1024, 2048, 3072, 4096, 6144, 8192, 10240, 12288)"
  type        = string
  default     = "512"
}
