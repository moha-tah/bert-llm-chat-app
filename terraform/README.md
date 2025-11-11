# Terraform Configuration - BERT LLM Chat App

This directory contains Terraform configuration for deploying the backend to AWS App Runner.

## Structure

- `main.tf` - Main infrastructure resources (App Runner, IAM roles)
- `secrets.tf` - Secrets management (AWS Secrets Manager configuration)
- `variables.tf` - Input variables
- `outputs.tf` - Output values
- `terraform.tfvars` - Your local variables (not committed to git)
- `terraform.tfvars.example` - Example variables file

## Getting Started

1. Copy the example variables file:
```bash
cp terraform.tfvars.example terraform.tfvars
```

2. Edit `terraform.tfvars` with your values:
```bash
# Required values
groq_api_key = "your-actual-groq-api-key"
github_connection_arn = "arn:aws:apprunner:..."
github_repository_url = "https://github.com/your-username/your-repo"

# Add more secrets as needed
```

3. Initialize Terraform:
```bash
terraform init
```

4. Plan and apply:
```bash
terraform plan
terraform apply
```

## Adding New Secrets

To add a new secret to the application:

### Step 1: Add the secret to `secrets.tf`

Edit the `locals.secrets` block in `secrets.tf`:

```hcl
locals {
  secrets = {
    groq_api_key = {
      description = "Groq API key for LLM access"
      value       = var.groq_api_key
    }
    # Add your new secret here
    new_secret_name = {
      description = "Description of your secret"
      value       = var.new_secret_name
    }
  }
}
```

### Step 2: Add the variable to `variables.tf`

```hcl
variable "new_secret_name" {
  description = "Description of your secret"
  type        = string
  sensitive   = true
}
```

### Step 3: Add the secret to `main.tf`

In the `runtime_environment_secrets` block of the App Runner service:

```hcl
runtime_environment_secrets = {
  GROQ_API_KEY = aws_secretsmanager_secret.secrets["groq_api_key"].arn
  NEW_SECRET   = aws_secretsmanager_secret.secrets["new_secret_name"].arn
}
```

### Step 4: Update `terraform.tfvars`

Add your secret value:

```hcl
new_secret_name = "your-secret-value"
```

### Step 5: Update `terraform.tfvars.example`

Add a placeholder for documentation:

```hcl
new_secret_name = "your-new-secret-here"
```

That's it! Run `terraform apply` to deploy your changes.

## Environment Variables

### Non-sensitive variables
Defined in `main.tf` under `runtime_environment_variables`:
- `APP_PORT` - Application port (8080)
- `ENVIRONMENT` - Environment name (prod/dev/staging)

### Sensitive variables
Defined in `main.tf` under `runtime_environment_secrets` and stored in AWS Secrets Manager:
- `GROQ_API_KEY` - API key for Groq LLM service

## Security Best Practices

- Never commit `terraform.tfvars` to git (already in .gitignore)
- Always use `runtime_environment_secrets` for sensitive data
- Use `runtime_environment_variables` only for non-sensitive configuration
- Secrets are encrypted at rest in AWS Secrets Manager
- IAM policies follow least privilege principle

## Important Notes

- The `PORT` environment variable is reserved by AWS App Runner and cannot be manually set
- After rotating secrets in AWS Secrets Manager, you must redeploy the App Runner service
- Secrets Manager and the App Runner service must be in the same AWS account

## Troubleshooting

### Secret not accessible
If your application can't access a secret, check:
1. The IAM role has permissions to read the secret (check `secrets.tf`)
2. The secret ARN is correctly referenced in `main.tf`
3. The App Runner service has been redeployed after adding the secret

### State file issues
This setup uses local state files. For production, consider:
- Storing state in S3
- Using DynamoDB for state locking
- Enabling state encryption
