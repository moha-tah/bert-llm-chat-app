# MRO Copilot V-Final

A RAG (Retrieval Augmented Generation) application for MRO (Maintenance, Repair, and Operations) documentation with streaming LLM responses.

## Overview

This is a read-only RAG web application with minimal infrastructure. Document ingestion is performed via a local script that generates a FAISS vector index, which is committed to the repository and deployed with the backend.

## Technology Stack

- **Infrastructure as Code**: Terraform
- **Cloud Provider**: AWS
- **Vector Database**: FAISS (static files in repository)
- **Backend**: FastAPI (Python)
- **Frontend**: Next.js (App Router, TypeScript)
- **Backend Hosting**: AWS App Runner
- **Frontend Hosting**: Vercel
- **LLM Provider**: Groq (llama-3.3-70b-versatile)
- **LLM Response**: Streaming (Server-Sent Events)

## Project Structure

```
/
├── backend/              # FastAPI backend
│   ├── faiss_index/      # FAISS vector index (committed to repo)
│   ├── .env.example      # Backend environment variables template
│   └── .gitignore
├── frontend/             # Next.js frontend
│   ├── .env.example      # Frontend environment variables template
│   └── .gitignore
├── terraform/            # Infrastructure as Code
│   └── .gitignore
├── scripts/              # One-shot ingestion script
│   ├── .env.example      # Scripts environment variables template
│   └── .gitignore
├── .gitignore            # Root gitignore
├── PLAN.md               # Detailed project plan
└── README.md             # This file
```

## Getting Started

### Prerequisites

- Python 3.9+
- Node.js 18+
- AWS Account
- Groq API Key
- Git & GitHub Account

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd bert-llm-chat-app
   ```

2. **Configure environment variables**
   - Copy `.env.example` to `.env` in each module (backend, frontend, scripts)
   - Fill in your API keys and configuration values

3. **Backend Setup**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

4. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   ```

5. **Document Ingestion**
   ```bash
   cd scripts
   pip install -r requirements.txt
   # Place your PDF manuals in scripts/source_pdfs/
   python ingest.py
   ```

## Development

### Running Locally

**Backend:**
```bash
cd backend
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm run dev
```

## Deployment

### Backend (AWS App Runner)
- Push to GitHub main branch
- AWS App Runner automatically builds and deploys

### Frontend (Vercel)
- Connect repository to Vercel
- Configure `NEXT_PUBLIC_API_URL` environment variable
- Automatic deployment on push

## Features

- **Read-Only RAG**: Query MRO documentation with natural language
- **Streaming Responses**: Real-time word-by-word LLM responses
- **Auto-Deploy**: Push to deploy via GitHub integration
- **Minimal Infrastructure**: No database setup required
- **Static Vector Index**: FAISS index committed with code

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]
