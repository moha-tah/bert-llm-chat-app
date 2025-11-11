# BERT LLM Chat App

> A production-ready RAG (Retrieval-Augmented Generation) system with containerized microservices, CI/CD automation, and cloud-native deployment

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-16.0-black.svg)](https://nextjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-blue.svg)](https://www.typescriptlang.org/)
[![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED.svg)](https://www.docker.com/)
[![AWS ECR](https://img.shields.io/badge/AWS-ECR-FF9900.svg)](https://aws.amazon.com/ecr/)
[![AWS App Runner](https://img.shields.io/badge/AWS-App_Runner-FF9900.svg)](https://aws.amazon.com/apprunner/)
[![GitHub Actions](https://img.shields.io/badge/CI%2FCD-GitHub_Actions-2088FF.svg)](https://github.com/features/actions)
[![Terraform](https://img.shields.io/badge/Terraform-IaC-7B42BC.svg)](https://www.terraform.io/)

---

## 🎯 Overview

This project demonstrates a **cloud-native AI application** combining advanced machine learning techniques with modern DevOps practices. Built for enterprise-scale document Q&A, it showcases deep expertise in:

- **🤖 AI/ML Engineering**: RAG pipelines, vector embeddings, semantic search, LLM orchestration
- **☁️ Cloud Architecture**: AWS services (ECR, App Runner, Secrets Manager), containerization, auto-scaling
- **🚀 DevOps**: CI/CD with GitHub Actions, Docker multi-stage builds, Infrastructure as Code

### What It Does

An intelligent document Q&A system that combines machine learning with production-grade cloud infrastructure. Users ask questions in natural language and receive real-time AI-generated responses grounded in document sources.

**AI/ML Pipeline:**
- **Semantic Understanding**: Transformer-based embeddings (sentence-transformers/all-MiniLM-L6-v2, 384-dim)
- **Vector Search**: FAISS-powered similarity search with cosine distance
- **LLM Generation**: LLaMA 3.3 70B via Groq for natural language synthesis
- **RAG Architecture**: Retrieval-Augmented Generation for factual, grounded responses
- **Streaming Inference**: Server-Sent Events for real-time token delivery

**Cloud Infrastructure:**
- **Containerization**: Multi-stage Docker builds optimized for production
- **Container Registry**: AWS ECR with automated image management
- **Serverless Compute**: AWS App Runner with auto-scaling (0-100 instances)
- **CI/CD Pipeline**: GitHub Actions for automated build, test, and deployment
- **Secrets Management**: AWS Secrets Manager for secure credential injection
- **Infrastructure as Code**: Terraform for reproducible cloud provisioning

### Key Features

🤖 **Production ML Pipeline**: End-to-end RAG system with embedding generation, vector retrieval, and LLM synthesis

🐳 **Containerized Architecture**: Docker-based microservices with multi-stage builds for minimal image size

☁️ **Cloud-Native Design**: Fully managed AWS services with auto-scaling and zero-downtime deployments

🔄 **Automated CI/CD**: GitHub Actions pipeline for continuous integration and deployment to ECR/App Runner

⚡ **Real-Time Streaming**: SSE-based token streaming for responsive user experience

🔒 **Security Best Practices**: Non-root containers, secrets management, IAM least-privilege policies

📊 **Observability**: Health checks, structured logging, container monitoring

---

## 🏗️ Technical Architecture

### System Overview

Cloud-native architecture with containerized microservices and automated CI/CD:

```
                    ┌──────────────────────┐
                    │  GitHub Repository   │
                    │  (Source Code)       │
                    └──────────┬───────────┘
                               │ git push
                               ▼
                    ┌──────────────────────┐
                    │  GitHub Actions      │
                    │  (CI/CD Pipeline)    │
                    └──────────┬───────────┘
                               │ docker build & push
                               ▼
┌──────────────┐    ┌──────────────────────┐    ┌──────────────────┐
│   Frontend   │    │   AWS ECR            │    │ AWS Secrets Mgr  │
│   (Vercel)   │    │   (Container Reg.)   │    │ (API Keys)       │
└──────┬───────┘    └──────────┬───────────┘    └────────┬─────────┘
       │                       │ pull image             │
       │ HTTP/SSE              ▼                        ▼
       │            ┌──────────────────────┐    ┌──────────────┐
       └───────────►│  AWS App Runner      │◄───│ IAM Role     │
                    │  (Docker Container)  │    │              │
                    └──────────┬───────────┘    └──────────────┘
                               │
                               ▼
                    ┌─────────────────────────────┐
                    │      RAG Pipeline           │
                    │                             │
                    │  1. Embedding Model         │
                    │     (MiniLM-L6-v2, 384-dim) │
                    │                             │
                    │  2. FAISS Vector Search     │
                    │     (Inner Product)         │
                    │                             │
                    │  3. LLM Generation          │
                    │     (LLaMA 3.3 70B / Groq)  │
                    └─────────────────────────────┘
```

### RAG Pipeline Flow

1. **User Query** → Question submitted via Next.js frontend (Vercel-hosted)
2. **API Gateway** → Request routed to containerized FastAPI backend on App Runner
3. **Query Embedding** → Vectorization using `all-MiniLM-L6-v2` (384-dim transformer model)
4. **Vector Search** → FAISS IndexFlatIP performs K-NN search (K=5) with inner product similarity
5. **Context Retrieval** → Top-5 document chunks retrieved with relevance scores
6. **Prompt Engineering** → Context + history assembled into structured LLM prompt
7. **LLM Inference** → Groq API streams LLaMA 3.3 70B tokens at 300+ tokens/sec
8. **SSE Streaming** → Async generator streams tokens via Server-Sent Events
9. **Real-Time Rendering** → Frontend displays word-by-word response with source citations

### Core Components

#### 🧠 AI/ML Layer

- **Embedding Model**: `sentence-transformers/all-MiniLM-L6-v2`

  - 384-dimensional dense vectors (efficient, fast inference)
  - Trained on 1B+ sentence pairs for semantic similarity
  - L2-normalized for cosine similarity via inner product
  - ~120MB model size, optimized for production deployment

- **Vector Database**: FAISS (Facebook AI Similarity Search)

  - `IndexFlatIP` (Inner Product) for exact nearest-neighbor search
  - Pre-built static index (276 chunks) versioned in repository
  - Sub-millisecond query latency (<1ms for K=5 retrieval)
  - In-memory index for zero-latency startup

- **LLM**: LLaMA 3.3 70B Versatile via Groq API
  - Ultra-fast inference: 300+ tokens/sec (LPU architecture)
  - Native streaming support with Server-Sent Events
  - 128K token context window
  - Configurable temperature (0.7) and max tokens (1024)

#### 🔧 Backend (FastAPI + Docker)

- **Framework**: FastAPI with async/await and Pydantic V2
- **Containerization**: Multi-stage Dockerfile for optimized builds
  - Stage 1: Poetry dependency installation
  - Stage 2: Minimal production image (Python 3.11-slim)
  - Non-root user for security
  - Final image size: ~500MB (optimized)
- **API Endpoints**:
  - `POST /ask-stream`: RAG endpoint with SSE streaming
  - `GET /health`: Container health check with FAISS status
  - `GET /`: API documentation and metadata
- **Document Processing**: LangChain recursive text splitters (1000 chars, 200 overlap)
- **Configuration**: Environment-based config with Pydantic Settings
- **CORS**: Configurable origins for frontend communication

#### 🎨 Frontend (Next.js)

- **Framework**: Next.js 16 with App Router (React 19)
- **Language**: TypeScript 5 for type safety
- **Styling**: Tailwind CSS 4 with custom design system
- **Streaming**: `eventsource-parser` for SSE handling
- **State Management**: Custom `useChat` hook with optimistic updates
- **Features**: Chat interface, message history, sources sidebar, dark mode
- **Deployment**: Vercel with edge functions and global CDN

#### ☁️ Cloud Infrastructure (AWS + GitHub Actions)

- **Container Registry**: AWS ECR (Elastic Container Registry)
  - Private registry for Docker images
  - Image scanning for vulnerabilities
  - Lifecycle policies for automated cleanup
  - SHA-tagged images for immutability

- **Compute**: AWS App Runner
  - Managed container orchestration
  - Auto-scaling: 0-100 instances
  - Health checks via `/health` endpoint
  - Pull from ECR with IAM authentication

- **CI/CD**: GitHub Actions workflow (`cd.yml`)
  - Trigger: Push to `main` branch
  - Build: Multi-stage Docker build
  - Push: Tagged images to ECR (latest + SHA)
  - Deploy: Automatic App Runner service update

- **Secrets**: AWS Secrets Manager
  - Encrypted API keys (GROQ_API_KEY)
  - Runtime injection into containers
  - IAM-based access control

- **IaC**: Terraform for infrastructure provisioning
  - ECR repositories
  - App Runner services
  - IAM roles and policies
  - Secrets Manager resources

### Technical Decisions & Rationale

| Component           | Choice                      | Why?                                                                               |
| ------------------- | --------------------------- | ---------------------------------------------------------------------------------- |
| **Embedding**       | all-MiniLM-L6-v2            | Fast inference, small size (120MB), 384-dim optimal for speed/accuracy tradeoff    |
| **Vector DB**       | FAISS                       | Sub-ms latency, no external DB, static index versioned in git, zero cold-start     |
| **LLM Provider**    | Groq                        | Fastest inference (300+ tok/s), LPU architecture, native streaming, low latency    |
| **LLM Model**       | LLaMA 3.3 70B Versatile     | SOTA quality, 128K context, excellent instruction-following, fast on Groq          |
| **Backend**         | FastAPI                     | Async/await, OpenAPI docs, Python ML ecosystem, SSE support                        |
| **Containerization**| Docker (multi-stage)        | Reproducible builds, minimal image size, security (non-root), platform-agnostic    |
| **Registry**        | AWS ECR                     | Native AWS integration, IAM auth, vulnerability scanning, lifecycle management     |
| **Compute**         | AWS App Runner              | Managed containers, auto-scaling, zero-config deploys, cost-effective serverless   |
| **CI/CD**           | GitHub Actions              | Native GitHub integration, matrix builds, secrets management, free for public repos|
| **Frontend**        | Next.js 16                  | App Router, React 19, Server Components, excellent DX, TypeScript, Vercel-optimized|
| **IaC**             | Terraform                   | Declarative, version-controlled, AWS provider maturity, reproducible infrastructure|

---

## 🛠️ Technology Stack

### Backend Stack

- **Python 3.11+** with Poetry for dependency management
- **Docker** with multi-stage builds (Python 3.11-slim base)
- **FastAPI** + Uvicorn ASGI server for async API
- **FAISS** (`faiss-cpu`) for vector similarity search
- **Sentence Transformers** (`all-MiniLM-L6-v2`) for embeddings
- **Groq SDK** for LLM API streaming
- **LangChain** text splitters for document chunking
- **pypdf** for PDF parsing
- **Pydantic V2** for settings and validation

### Frontend Stack

- **Next.js 16.0** (App Router) with React 19
- **TypeScript 5** for type safety
- **Tailwind CSS 4** for styling
- **eventsource-parser** for SSE handling
- **Lucide React** for icons
- **next-themes** for dark/light mode
- **pnpm** for fast package management

### Infrastructure Stack

- **Docker** for containerization with multi-stage builds
- **AWS ECR** (Elastic Container Registry) for private image registry
- **AWS App Runner** for managed container hosting
- **AWS Secrets Manager** for encrypted credential storage
- **AWS IAM** for least-privilege access control
- **GitHub Actions** for automated CI/CD pipeline
- **Terraform** for Infrastructure as Code (IaC)
- **Vercel** for frontend hosting with edge CDN

### AI/ML Stack

- **Embedding Model**: sentence-transformers/all-MiniLM-L6-v2 (384-dim)
- **LLM**: LLaMA 3.3 70B Versatile via Groq API
- **Vector Database**: FAISS IndexFlatIP (inner product similarity)
- **Text Processing**: LangChain RecursiveCharacterTextSplitter
- **PDF Parser**: pypdf library
- **Inference**: Groq LPU (300+ tokens/sec streaming)

---

## 🚀 Deployment Architecture

### Backend Deployment (Containerized)

The backend uses a **modern containerized deployment** with automated CI/CD:

```
GitHub Push → GitHub Actions → Docker Build → ECR Push → App Runner Deploy → Live
```

#### CI/CD Pipeline (GitHub Actions)

**Workflow File**: `.github/workflows/cd.yml`

**Pipeline Stages:**

1. **Trigger**: Push to `main` branch or changes to `backend/**`
2. **Checkout**: Clone repository code
3. **AWS Auth**: Configure credentials via OIDC or access keys
4. **ECR Login**: Authenticate with Elastic Container Registry
5. **Docker Build**: Multi-stage build with BuildKit
6. **Image Tag**: SHA-based tags for immutability (`main-{sha}`)
7. **ECR Push**: Upload image to private registry
8. **App Runner Update**: Deploy new image with zero-downtime

**Key Features:**
- Automated builds on every push to `main`
- Multi-platform support (linux/amd64)
- Image vulnerability scanning
- Disk space optimization for GitHub runners

#### Docker Configuration

**Multi-Stage Dockerfile**:

```dockerfile
# Stage 1: Builder
FROM python:3.11-slim as builder
RUN pip install poetry
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-dev

# Stage 2: Production
FROM python:3.11-slim
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY . .
RUN useradd -m appuser
USER appuser
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
```

**Optimizations:**
- Multi-stage build reduces final image size (~500MB)
- Non-root user for security
- Layer caching for faster builds
- Health checks with Python HTTP requests

#### AWS Infrastructure

**ECR (Container Registry):**
- Private registry: `bert-llm-chat-app-backend`
- Image scanning enabled
- Lifecycle policies for cleanup
- IAM-based authentication

**App Runner Service:**
- Pulls images from ECR automatically
- Auto-scaling: 0-100 instances
- Health checks via `/health` endpoint
- Environment variables from Secrets Manager
- Runtime configuration:
  - `GROQ_API_KEY`, `ALLOWED_ORIGINS` (from Secrets)
  - `FAISS_INDEX_DIR`, `EMBEDDING_MODEL`, `K_NEIGHBORS` (environment)

**Secrets Manager:**
- Encrypted API keys injection at runtime
- No secrets in Docker images
- IAM role-based access control

#### Local Development

**Docker Compose** (`backend/docker-compose.yml`):

```bash
cd backend
docker-compose up --build
```

Features:
- Hot-reload with volume mounts
- Environment variable configuration
- Health checks
- Port mapping (8080:8080)

### Frontend Deployment (Vercel)

Automated deployment with edge optimization:

```
GitHub Push → Vercel Build → Next.js Build → Edge Deploy → Global CDN → Live
```

**Configuration:**

- Environment: `NEXT_PUBLIC_API_URL` → App Runner URL
- Automatic HTTPS with Let's Encrypt
- Edge Functions for API routes
- Global CDN (300+ locations)
- Preview deployments for branches

### Infrastructure Provisioning

**Terraform Setup:**

```bash
cd terraform
terraform init
terraform plan
terraform apply
```

**Resources Created:**
- ECR repository
- App Runner service
- IAM roles and policies
- Secrets Manager secrets
- Security groups and VPC config

---

## 📁 Project Structure

```
/
├── .github/
│   └── workflows/
│       └── cd.yml                  # CI/CD pipeline (GitHub Actions)
│
├── backend/                        # FastAPI backend
│   ├── app/                        # Application code
│   │   ├── main.py                 # FastAPI app initialization
│   │   ├── config.py               # Settings with Pydantic
│   │   ├── dependencies.py         # FAISS manager singleton
│   │   └── api/endpoints/          # API route handlers
│   ├── faiss_index/                # Vector database (versioned)
│   │   ├── index.faiss             # Binary FAISS index
│   │   └── index.json              # Document chunks metadata
│   ├── Dockerfile                  # Multi-stage container build
│   ├── docker-compose.yml          # Local development setup
│   ├── main.py                     # Uvicorn entry point
│   ├── pyproject.toml              # Poetry dependencies
│   └── poetry.lock                 # Locked dependencies
│
├── frontend/                       # Next.js frontend
│   ├── app/                        # Next.js App Router
│   │   ├── page.tsx                # Landing page
│   │   └── ask/                    # Chat interface
│   ├── components/                 # React components
│   ├── hooks/                      # Custom hooks (useChat)
│   ├── lib/                        # Utilities
│   └── package.json                # pnpm dependencies
│
├── terraform/                      # Infrastructure as Code
│   ├── main.tf                     # ECR, App Runner, IAM
│   ├── secrets.tf                  # AWS Secrets Manager
│   ├── variables.tf                # Input variables
│   └── outputs.tf                  # Output values (URLs)
│
└── scripts/                        # ML utilities
    ├── ingest.py                   # PDF → embeddings → FAISS
    └── source_pdfs/                # Source documents
```

---

## 🎓 Key Technical Highlights

### 1. Advanced RAG Implementation

- **Semantic chunking** with overlap for context preservation (1000 chars, 200 overlap)
- **Vector normalization** (L2) for accurate cosine similarity via inner product
- **Relevance scoring** returned with each retrieved chunk
- **Top-K retrieval** (K=5) with score thresholding
- **Conversation history** injection for context-aware responses

### 2. Containerization & DevOps

- **Multi-stage Docker builds** for minimal image footprint (~500MB)
- **Non-root containers** for security hardening
- **Health checks** with HTTP probes for liveness/readiness
- **Layer caching** for fast iterative builds
- **Docker Compose** for local development with hot-reload

### 3. CI/CD Pipeline

- **GitHub Actions** for automated build-test-deploy
- **ECR integration** with automatic image push
- **SHA-based tagging** for immutable deployments
- **Zero-downtime deployments** with App Runner rolling updates
- **Automated rollback** on health check failures
- **Secrets injection** at runtime (no secrets in images)

### 4. Cloud-Native Architecture

- **Infrastructure as Code** with Terraform (reproducible, version-controlled)
- **Managed container orchestration** with AWS App Runner
- **Auto-scaling** (0-100 instances) based on CPU/memory
- **Private container registry** with ECR vulnerability scanning
- **Secrets management** with AWS Secrets Manager
- **IAM least-privilege** access control

### 5. Real-Time AI Streaming

- **Server-Sent Events (SSE)** for efficient HTTP streaming
- **Async generators** for token-by-token delivery
- **Backpressure handling** in streaming pipeline
- **Groq LPU** for ultra-fast inference (300+ tok/s)
- **Error recovery** with graceful degradation

### 6. Performance Optimizations

- **Singleton embedding model** (loaded once, reused)
- **In-memory FAISS index** for sub-millisecond retrieval
- **Async/await** throughout backend (FastAPI + httpx)
- **Static index** versioned in git (zero cold-start)
- **Efficient embeddings** (384-dim vs 1024-dim) for faster inference

---

## 🔧 Quick Start

### Prerequisites

- **Docker** and Docker Compose
- **Python 3.11+** (for local development without Docker)
- **Node.js 18+** with pnpm
- **AWS Account** + CLI configured (for deployment)
- **Groq API Key** ([get one here](https://console.groq.com))

### Local Development

#### Option 1: Docker (Recommended)

**Backend:**
```bash
cd backend
docker-compose up --build
# Backend runs on http://localhost:8080
```

**Frontend:**
```bash
cd frontend
pnpm install
pnpm dev
# Frontend runs on http://localhost:3000
```

#### Option 2: Native Python

**Backend:**
```bash
cd backend
poetry install
poetry run uvicorn main:app --reload --host 0.0.0.0 --port 8080
```

**Frontend:**
```bash
cd frontend
pnpm install
pnpm dev
```

### Document Ingestion

**Ingest PDFs into FAISS index:**

```bash
cd scripts
poetry install
# Place PDFs in source_pdfs/
poetry run python ingest.py
# Creates backend/faiss_index/index.faiss and index.json
```

### Environment Variables

**Backend** (`.env` or `docker-compose.yml`):

```env
GROQ_API_KEY=gsk_...
GROQ_MODEL=llama-3.3-70b-versatile
GROQ_TEMPERATURE=0.7
GROQ_MAX_TOKENS=1024

ALLOWED_ORIGINS=http://localhost:3000

FAISS_INDEX_DIR=./faiss_index
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
K_NEIGHBORS=5
```

**Frontend** (`.env.local`):

```env
NEXT_PUBLIC_API_URL=http://localhost:8080
```

### Production Deployment

**1. Build and test Docker image locally:**
```bash
cd backend
docker build -t bert-llm-chat-app-backend .
docker run -p 8080:8080 --env-file .env bert-llm-chat-app-backend
```

**2. Deploy infrastructure with Terraform:**
```bash
cd terraform
terraform init
terraform plan
terraform apply
```

**3. Push to GitHub to trigger CI/CD:**
```bash
git push origin main
# GitHub Actions automatically builds, pushes to ECR, and deploys to App Runner
```

---

## 📊 Current Status

**Deployment**: ✅ Production-ready on AWS (containerized)
**Dataset**: 276 document chunks from technical documentation
**Response Latency**: ~100-200ms to first token (Groq LPU)
**Throughput**: 300+ tokens/sec streaming
**Scalability**: Auto-scaling 0-100 instances (App Runner)
**Availability**: Health checks + zero-downtime rolling deployments

---

## 🔮 Skills Demonstrated

This project showcases expertise across AI/ML and Cloud Engineering:

### 🤖 AI/ML Engineering
✅ **Deep Learning**: Transformer-based embeddings (sentence-transformers), semantic similarity
✅ **RAG Pipelines**: Document chunking, vector retrieval, context injection, LLM synthesis
✅ **Vector Databases**: FAISS indexing, K-NN search, cosine similarity optimization
✅ **LLM Engineering**: Prompt engineering, streaming inference, context window management
✅ **Model Deployment**: Efficient model serving, singleton patterns, inference optimization

### ☁️ Cloud & DevOps
✅ **Containerization**: Docker multi-stage builds, image optimization, security hardening
✅ **Container Orchestration**: AWS ECR, App Runner managed containers, auto-scaling
✅ **CI/CD**: GitHub Actions pipelines, automated build-test-deploy, rollback strategies
✅ **Infrastructure as Code**: Terraform for AWS resources (ECR, App Runner, IAM, Secrets)
✅ **Cloud Architecture**: Serverless compute, managed services, cost optimization
✅ **Security**: IAM least-privilege, Secrets Manager, non-root containers, vulnerability scanning
✅ **Observability**: Health checks, structured logging, container monitoring

### 💻 Software Engineering
✅ **Backend**: FastAPI async/await, Pydantic validation, SSE streaming, API design
✅ **Frontend**: Next.js 16 App Router, TypeScript, React hooks, real-time UI
✅ **Performance**: Async I/O, caching strategies, connection pooling, backpressure handling

---

## 💡 Key Architectural Decisions for Production

### Why This Stack?

**AI/ML Choices:**
- **all-MiniLM-L6-v2**: Balanced speed/accuracy, 3x smaller than alternatives (120MB vs 500MB)
- **FAISS**: Zero external dependencies, sub-millisecond retrieval, version-controlled index
- **Groq**: 10x faster than OpenAI (300 tok/s vs 30), native streaming, lower latency

**Cloud/DevOps Choices:**
- **Docker**: Reproducible deployments, platform-agnostic, local-prod parity
- **ECR + App Runner**: Fully managed, auto-scaling, no Kubernetes complexity
- **GitHub Actions**: Native integration, free tier, matrix builds, secrets management
- **Terraform**: Declarative IaC, version-controlled infrastructure, reproducible across environments

**Trade-offs Made:**
- **Static FAISS index** (in git) vs dynamic database → Faster startup, simpler ops, acceptable for <1M docs
- **App Runner** vs ECS/EKS → Lower operational complexity, faster iteration, cost-effective at scale
- **Smaller embedding model** (384-dim) vs larger (1024-dim) → 3x faster, 60% smaller, acceptable quality drop

---

## 📝 License

MIT License - See LICENSE file for details

---

**Built with Python, Docker, TypeScript, and AWS** | **Designed for AI + Cloud Engineering roles**
