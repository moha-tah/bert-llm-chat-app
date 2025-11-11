# BERT LLM Chat App

> A production-ready RAG (Retrieval-Augmented Generation) system for intelligent document Q&A with real-time streaming responses

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-16.0-black.svg)](https://nextjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-blue.svg)](https://www.typescriptlang.org/)
[![AWS](https://img.shields.io/badge/AWS-App_Runner-orange.svg)](https://aws.amazon.com/apprunner/)
[![Terraform](https://img.shields.io/badge/Terraform-IaC-purple.svg)](https://www.terraform.io/)

---

## 🎯 Overview

This project demonstrates a **modern AI-powered question-answering system** that combines state-of-the-art natural language processing techniques with cloud-native architecture. Built for document-based knowledge retrieval, it showcases expertise in **Deep Learning**, **RAG pipelines**, and **Cloud Infrastructure**.

### What It Does

The application allows users to ask questions about technical documents in natural language and receive intelligent, contextual answers in real-time. It leverages:

- **Vector embeddings** to understand semantic meaning
- **FAISS vector database** for efficient similarity search
- **Large Language Models** (LLaMA 3.3 70B) for natural language generation
- **Retrieval-Augmented Generation (RAG)** to ground responses in source documents
- **Streaming responses** for real-time user experience

### Key Features

✨ **Intelligent Document Understanding**: Converts documents into semantic vectors using transformer-based embeddings
🔍 **Semantic Search**: FAISS-powered vector similarity search finds relevant context
🤖 **LLM-Powered Responses**: LLaMA 3.3 generates accurate, context-aware answers
⚡ **Real-Time Streaming**: Server-Sent Events (SSE) for word-by-word response generation
📚 **Source Attribution**: Cites specific document sections with relevance scores
💬 **Conversational Context**: Maintains chat history for multi-turn conversations
☁️ **Cloud-Native**: Fully deployed on AWS with Infrastructure as Code

---

## 🏗️ Technical Architecture

### System Overview

The application follows a modern three-tier architecture with AI/ML capabilities integrated throughout:

```
┌─────────────────┐
│   User Browser  │
│   (Next.js UI)  │
└────────┬────────┘
         │ HTTP/SSE
         ▼
┌─────────────────┐      ┌──────────────────┐
│  AWS App Runner │◄────►│ AWS Secrets Mgr  │
│  FastAPI Backend│      │ (API Keys)       │
└────────┬────────┘      └──────────────────┘
         │
         ▼
    ┌────────────────────────────────┐
    │      RAG Pipeline              │
    │                                │
    │  1. Embedding Model            │
    │     (BAAI/bge-large-en-v1.5)   │
    │                                │
    │  2. FAISS Vector Search        │
    │     (Cosine Similarity)        │
    │                                │
    │  3. LLM Generation             │
    │     (LLaMA 3.3 70B via Groq)   │
    └────────────────────────────────┘
```

### RAG Pipeline Flow

1. **User Query** → User asks a question via the Next.js frontend
2. **Query Embedding** → Question is vectorized using `BAAI/bge-large-en-v1.5` (1024-dim)
3. **Vector Search** → FAISS performs K-nearest neighbor search (K=5) with cosine similarity
4. **Context Retrieval** → Top 5 most relevant document chunks are retrieved with scores
5. **Prompt Construction** → Builds context-aware prompt with retrieved chunks + conversation history
6. **LLM Generation** → Groq API streams tokens from LLaMA 3.3 70B model
7. **SSE Streaming** → Backend formats and streams tokens to frontend in real-time
8. **Real-Time Display** → User sees response appear word-by-word with source citations

### Core Components

#### 🧠 AI/ML Layer

- **Embedding Model**: `BAAI/bge-large-en-v1.5` via Sentence Transformers
  - 1024-dimensional dense vectors
  - Optimized for semantic similarity tasks
  - L2 normalization for cosine similarity via inner product

- **Vector Database**: FAISS (Facebook AI Similarity Search)
  - `IndexFlatIP` (Inner Product) for exact search
  - Static index committed to repository (276 chunks)
  - Sub-millisecond search latency

- **LLM**: LLaMA 3.3 70B via Groq API
  - Streaming token generation
  - Context window: 128K tokens
  - Temperature: 0.7 (configurable)
  - Max output tokens: 1024

#### 🔧 Backend (FastAPI)

- **Framework**: FastAPI with async/await support
- **Document Processing**: LangChain text splitters (1000 chars, 200 overlap)
- **Ingestion Script**: Converts PDFs → embeddings → FAISS index
- **Endpoints**:
  - `POST /ask-stream`: Main RAG endpoint with SSE streaming
  - `GET /health`: Health check for AWS App Runner
- **Configuration**: Pydantic Settings with environment variables
- **CORS**: Configurable allowed origins for frontend

#### 🎨 Frontend (Next.js)

- **Framework**: Next.js 16 with App Router (React 19)
- **Language**: TypeScript for type safety
- **Styling**: Tailwind CSS 4 with custom components
- **Streaming**: `eventsource-parser` for SSE handling
- **State Management**: Custom `useChat` hook with real-time updates
- **Features**: Chat interface, message history, sources sidebar, theme toggle

#### ☁️ Infrastructure (AWS + Terraform)

- **IaC**: Terraform for reproducible infrastructure
- **Backend Hosting**: AWS App Runner
  - Auto-scaling managed container service
  - Direct GitHub integration for CI/CD
  - Health checks on `/health` endpoint
- **Secrets**: AWS Secrets Manager for API keys
- **IAM**: Least-privilege roles for App Runner
- **Frontend Hosting**: Vercel with automatic deployments

### Technical Decisions & Rationale

| Component | Choice | Why? |
|-----------|--------|------|
| **Embedding** | BAAI/bge-large-en-v1.5 | Top performance on MTEB benchmark, excellent for retrieval tasks |
| **Vector DB** | FAISS | Extremely fast, no external database needed, perfect for read-only RAG |
| **LLM Provider** | Groq | Fastest inference available (300+ tokens/sec), native streaming support |
| **LLM Model** | LLaMA 3.3 70B | High quality, large context window, excellent instruction following |
| **Backend** | FastAPI | Async support, automatic OpenAPI docs, Python ML ecosystem |
| **Frontend** | Next.js 16 | App Router, Server Components, excellent DX, TypeScript support |
| **Hosting** | AWS App Runner | Managed service, auto-scaling, GitHub integration, cost-effective |
| **IaC** | Terraform | Industry standard, reproducible, version-controlled infrastructure |

---

## 🛠️ Technology Stack

### Backend Stack
- **Python 3.11+** with Poetry dependency management
- **FastAPI** + Uvicorn for high-performance async API
- **FAISS** (`faiss-cpu`) for vector similarity search
- **Sentence Transformers** for embedding generation
- **Groq SDK** for LLM API access
- **LangChain** text splitters for document processing
- **pypdf** for PDF text extraction
- **Pydantic** for configuration and validation

### Frontend Stack
- **Next.js 16.0** (App Router) with React 19
- **TypeScript 5** for type safety
- **Tailwind CSS 4** for styling
- **eventsource-parser** for SSE handling
- **Lucide React** for icons
- **next-themes** for dark/light mode
- **pnpm** for fast package management

### Infrastructure Stack
- **Terraform** for Infrastructure as Code
- **AWS App Runner** for backend hosting
- **AWS Secrets Manager** for secure credential storage
- **AWS IAM** for access control
- **Vercel** for frontend hosting and CDN
- **GitHub Actions** for CI linting

### AI/ML Stack
- **Embedding Model**: BAAI/bge-large-en-v1.5 (1024-dim)
- **LLM**: LLaMA 3.3 70B Versatile (Groq)
- **Vector Database**: FAISS IndexFlatIP
- **Text Processing**: LangChain RecursiveCharacterTextSplitter
- **PDF Parser**: pypdf library

---

## 🚀 Deployment Architecture

### Backend Deployment (AWS)

The backend is deployed on **AWS App Runner** with fully automated CI/CD:

```
GitHub Push → App Runner Build Trigger → Poetry Install → Uvicorn Start → Health Check → Live
```

**Infrastructure Components:**
- **App Runner Service**: Managed container with auto-scaling
- **Secrets Manager**: Stores `GROQ_API_KEY` and `ALLOWED_ORIGINS`
- **IAM Role**: Grants App Runner read access to secrets
- **Health Endpoint**: `/health` returns FAISS index status

**Configuration** (`backend/apprunner.yaml`):
```yaml
runtime: python311
build:
  commands:
    - pip3 install poetry
    - poetry config virtualenvs.create false
    - poetry install
run:
  command: poetry run uvicorn main:app --host 0.0.0.0 --port 8080
  network:
    port: 8080
```

**Terraform Deployment:**
```bash
cd terraform
terraform init
terraform plan
terraform apply
```

### Frontend Deployment (Vercel)

The frontend is deployed on **Vercel** with automatic deployments:

```
GitHub Push → Vercel Build → Next.js Build → Deploy to CDN → Live
```

**Configuration:**
- Environment variable: `NEXT_PUBLIC_API_URL` → App Runner URL
- Automatic HTTPS with Vercel SSL
- Global CDN for fast worldwide access
- Edge Functions support

---

## 📁 Project Structure

```
/
├── backend/                 # FastAPI backend
│   ├── faiss_index/         # FAISS vector index (committed)
│   │   ├── index.faiss      # Binary vector database
│   │   └── index.json       # Text chunks metadata
│   ├── main.py              # FastAPI application
│   ├── apprunner.yaml       # App Runner configuration
│   ├── pyproject.toml       # Poetry dependencies
│   └── poetry.lock          # Locked dependencies
│
├── frontend/                # Next.js frontend
│   ├── app/                 # Next.js App Router
│   │   ├── page.tsx         # Landing page
│   │   └── ask/             # Chat interface
│   ├── components/          # React components
│   ├── hooks/               # Custom hooks (useChat)
│   └── package.json         # npm dependencies
│
├── terraform/               # Infrastructure as Code
│   ├── main.tf              # App Runner, IAM resources
│   ├── secrets.tf           # AWS Secrets Manager
│   ├── variables.tf         # Terraform variables
│   └── outputs.tf           # Output values (URLs)
│
└── scripts/                 # Document ingestion
    ├── ingest.py            # PDF → FAISS pipeline
    └── source_pdfs/         # Source documents
```

---

## 🎓 Key Technical Highlights

### 1. Advanced RAG Implementation
- **Semantic chunking** with overlap for context preservation
- **Vector normalization** for accurate cosine similarity
- **Relevance scoring** returned with each retrieved chunk
- **Context window optimization** with top-K selection

### 2. Real-Time Streaming
- **Server-Sent Events (SSE)** for efficient streaming
- **Token-by-token** generation with async generators
- **Backpressure handling** in the streaming pipeline
- **Error recovery** with graceful degradation

### 3. Production-Ready Features
- **Health monitoring** for cloud service availability
- **Secrets management** with AWS Secrets Manager
- **CORS configuration** for secure frontend access
- **Environment-based config** for multi-stage deployment

### 4. Cloud-Native Architecture
- **Infrastructure as Code** with Terraform
- **Auto-scaling** with AWS App Runner
- **CI/CD automation** via GitHub integration
- **Zero-downtime deployments** with health checks

### 5. Performance Optimizations
- **Singleton pattern** for embedding model (loaded once)
- **FAISS CPU optimization** for fast vector search
- **Async/await** throughout the backend
- **Static index** for instant startup

---

## 🔧 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+ (with pnpm)
- AWS Account + CLI configured
- Groq API Key

### Local Development

**Backend:**
```bash
cd backend
poetry install
poetry run uvicorn main:app --reload
```

**Frontend:**
```bash
cd frontend
pnpm install
pnpm dev
```

**Document Ingestion:**
```bash
cd scripts
poetry install
# Place PDFs in source_pdfs/
poetry run python ingest.py
```

### Environment Variables

**Backend** (`.env`):
```env
GROQ_API_KEY=your_groq_api_key
ALLOWED_ORIGINS=http://localhost:3000
```

**Frontend** (`.env.local`):
```env
NEXT_PUBLIC_API_URL=http://localhost:8080
```

---

## 📊 Current Status

**Deployment Status**: ✅ Production-ready MVP
**Dataset**: 276 chunks from technical documentation
**Response Time**: ~100-200ms to first token (via Groq)
**Scalability**: Auto-scaling enabled on App Runner

---

## 🔮 Technical Showcase

This project demonstrates proficiency in:

✅ **Deep Learning**: Transformer embeddings, semantic similarity, RAG pipelines
✅ **LLM Engineering**: Prompt engineering, streaming, context management
✅ **Vector Databases**: FAISS indexing, similarity search, optimization
✅ **Cloud Architecture**: AWS services, IaC with Terraform, managed services
✅ **Backend Development**: FastAPI, async Python, API design, SSE streaming
✅ **Frontend Development**: Next.js, TypeScript, React hooks, real-time UI
✅ **DevOps**: CI/CD, GitHub integration, secrets management, monitoring

---

## 📝 License

MIT License - See LICENSE file for details

---

**Built with ❤️ using Python, TypeScript, and AWS**
