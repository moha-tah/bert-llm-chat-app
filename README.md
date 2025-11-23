# BERT LLM Chat App

> A production-ready RAG system featuring LLaMA 3.3, containerized microservices, and cloud-native AWS deployment.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-16.0-black.svg)](https://nextjs.org/)
[![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED.svg)](https://www.docker.com/)
[![AWS](https://img.shields.io/badge/AWS-App_Runner-FF9900.svg)](https://aws.amazon.com/)
[![Terraform](https://img.shields.io/badge/Terraform-IaC-7B42BC.svg)](https://www.terraform.io/)

---

## 🎯 Overview

This project demonstrates a **cloud-native AI application** designed for document Q&A. It combines a high-performance RAG (Retrieval-Augmented Generation) pipeline with modern DevOps practices, featuring:

- **Real-time AI**: LLaMA 3.3 70B via Groq (300+ tokens/sec) with SSE streaming.
- **Efficient Retrieval**: FAISS vector search with `all-MiniLM-L6-v2` embeddings.
- **Robust Ops**: Docker multi-stage builds, AWS App Runner auto-scaling, and Terraform IaC.

## 🏗️ Architecture

```mermaid
graph LR
    User[User] -->|Query| FE[Next.js Frontend]
    FE -->|HTTP/SSE| BE[FastAPI Backend]
    BE -->|1. Embed| Model[MiniLM-L6-v2]
    BE -->|2. Search| FAISS[Vector DB]
    BE -->|3. Generate| LLM[LLaMA 3.3 (Groq)]

    subgraph AWS Cloud
    BE
    end
```

### RAG Pipeline Flow

1. **Input**: User asks a question via the Next.js interface.
2. **Embedding**: Query is converted to a 384-dim vector using `sentence-transformers/all-MiniLM-L6-v2`.
3. **Retrieval**: FAISS performs a similarity search (inner product) to find the top-5 relevant document chunks.
4. **Generation**: Context and query are sent to LLaMA 3.3 70B (via Groq API).
5. **Streaming**: Response tokens are streamed back to the user in real-time.

## 🛠️ Technology Stack

| Component          | Technology                           | Key Choice Rationale                              |
| ------------------ | ------------------------------------ | ------------------------------------------------- |
| **AI/ML**          | LLaMA 3.3, FAISS, LangChain          | Groq LPU for speed; FAISS for sub-ms retrieval.   |
| **Backend**        | FastAPI, Python 3.11                 | Async/await support; robust ML ecosystem.         |
| **Frontend**       | Next.js 16, Tailwind, TypeScript     | Server Components; modern React 19 features.      |
| **Infrastructure** | AWS App Runner, ECR, Secrets Manager | Fully managed; auto-scaling; secure secrets.      |
| **DevOps**         | Docker, GitHub Actions, Terraform    | Immutable artifacts; reproducible infrastructure. |

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- [Groq API Key](https://console.groq.com)

### Local Development

**1. Backend**

```bash
cd backend
# Create .env file
echo "GROQ_API_KEY=your_key_here" > .env
# Start service
docker-compose up --build
```

**2. Frontend**

```bash
cd frontend
pnpm install && pnpm dev
```

Access the app at `http://localhost:3000`.

### Document Ingestion

To add new PDFs to the knowledge base:

```bash
cd scripts
poetry install
# Place PDFs in source_pdfs/
poetry run python ingest.py
```

## ☁️ Deployment

The project uses a GitOps workflow with **GitHub Actions**:

1. **Push to Main**: Triggers CI/CD pipeline.
2. **Build**: Creates optimized multi-stage Docker image.
3. **Push**: Uploads image to AWS ECR with SHA tagging.
4. **Deploy**: Updates AWS App Runner service (Zero-downtime).

Infrastructure is provisioned via **Terraform** in the `/terraform` directory.

## 📊 Evaluation

Includes a comprehensive evaluation framework (`/evaluation`) measuring:

- **RAG Quality**: Context precision/recall (RAGAS).
- **Retrieval**: Recall@K, MRR, NDCG.
- **Latency**: End-to-end response times.

## 📂 Project Structure

```
/
├── backend/            # FastAPI app, Dockerfile, FAISS index
├── frontend/           # Next.js App Router, React components
├── terraform/          # AWS Infrastructure as Code
├── scripts/            # Ingestion and utility scripts
├── evaluation/         # RAG performance metrics and benchmarks
└── .github/workflows/  # CI/CD pipelines
```

---

**License**: MIT
