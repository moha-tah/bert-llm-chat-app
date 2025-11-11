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

variable "allowed_origins" {
  description = "Allowed origins for CORS"
  type        = string
  default     = "http://localhost:3000"
}

variable "groq_api_key" {
  description = "Groq API key for LLM access"
  type        = string
  sensitive   = true
}

# App Runner Configuration
variable "app_runner_cpu" {
  description = "CPU units for App Runner instance (256, 512, 1024, 2048, 4096)"
  type        = string
  default     = "1024"
}

variable "app_runner_memory" {
  description = "Memory for App Runner instance (512, 1024, 2048, 3072, 4096, 6144, 8192, 10240, 12288)"
  type        = string
  default     = "2048"
}

# Application Configuration
variable "groq_model" {
  description = "Groq model to use"
  type        = string
  default     = "llama-3.3-70b-versatile"
}

variable "groq_temperature" {
  description = "Temperature for Groq model"
  type        = string
  default     = "0.7"
}

variable "groq_max_tokens" {
  description = "Max tokens for Groq model"
  type        = string
  default     = "1024"
}

variable "embedding_model" {
  description = "Sentence transformer model for embeddings"
  type        = string
  default     = "sentence-transformers/all-MiniLM-L6-v2"
}

variable "k_neighbors" {
  description = "Number of nearest neighbors for FAISS search"
  type        = string
  default     = "5"
}
