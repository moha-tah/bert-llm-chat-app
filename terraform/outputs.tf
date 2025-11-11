output "aws_region" {
  description = "AWS region being used"
  value       = var.aws_region
}

output "project_name" {
  description = "Project name"
  value       = var.project_name
}

# App Runner Service Outputs
output "app_runner_service_url" {
  description = "Public URL of the App Runner service"
  value       = "https://${aws_apprunner_service.bert-llm-chat-app-backend.service_url}"
}

output "app_runner_service_arn" {
  description = "ARN of the App Runner service"
  value       = aws_apprunner_service.bert-llm-chat-app-backend.arn
}

output "app_runner_service_id" {
  description = "ID of the App Runner service"
  value       = aws_apprunner_service.bert-llm-chat-app-backend.service_id
}

output "app_runner_service_status" {
  description = "Status of the App Runner service"
  value       = aws_apprunner_service.bert-llm-chat-app-backend.status
}
