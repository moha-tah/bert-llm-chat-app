# MRO Copilot V-Final - Project Plan

## Overview

This document outlines the plan for building a RAG (Retrieval Augmented Generation) application called "MRO Copilot V-Final" as a simplified Proof of Concept (PoC).

## Objective

Build a read-only RAG web application with minimal infrastructure. There will be NO traditional database (RDS, pgvector).

Document ingestion is performed via a local script that generates a vector index (FAISS file). This index file is treated as a static asset and included directly in the Git repository to be deployed with the backend.

Deployment will be fully automated via `git push`.

## Technology Stack

- **Infrastructure as Code (IaC)**: Terraform
- **Cloud Provider**: AWS
- **Vector Database**: FAISS files (stored in Git repository)
- **Backend API**: FastAPI (Python)
- **Frontend**: Next.js (App Router, TypeScript)
- **Backend Hosting**: AWS App Runner (connected directly to GitHub)
- **Frontend Hosting**: Vercel
- **LLM Provider**: Groq (Model: llama-3.3-70b-versatile)
- **LLM Response**: Streaming (Server-Sent Events)

## Production Principles

- **Secrets Management**: `.env` files locally, environment variables in production (managed by App Runner / Vercel)
- **Remote Terraform State**: `.tfstate` stored in local state file
- **Monorepo Structure**: Clean organization (`backend/`, `frontend/`, `scripts/`)

## Project Plan - Step by Step

### Phase 0: Project Initialization and Git Configuration

**Actions:**

1. Initialize a Git repository (e.g., on GitHub)

2. Create the monorepo structure:

   ```
   /
   ├── backend/              # FastAPI
   │   ├── .env.example
   │   ├── faiss_index/      # Folder where the index will be generated
   │   │   └── .gitkeep
   │   └── .gitignore
   ├── frontend/             # Next.js
   │   ├── .env.example
   │   └── .gitignore
   ├── terraform/            # All .tf files
   │   └── .gitignore
   ├── scripts/              # One-shot ingestion script
   │   ├── .env.example
   │   └── .gitignore
   ├── .gitignore            # Root
   └── README.md
   ```

3. Create `.env.example` files in each folder

4. DO NOT ignore the `backend/faiss_index/` folder

**Validation (Manual Tests):**

- Clone the repository and verify the folder structure is correct

### Phase 1: Infrastructure (Terraform) - Local State Only

**Note:** This project will use only a local `.tfstate` file. There is no need to configure a remote backend (e.g., S3/DynamoDB).

**Actions:**

1. **Terraform**: Create `terraform/main.tf` and define your infrastructure resources as needed.
2. Terraform will save state in `terraform/terraform.tfstate` by default.

**Validation (Manual Tests):**

- Run `terraform init`
- Verify that `terraform/terraform.tfstate` is created locally

### Phase 2: AWS Infrastructure Provisioning (Terraform)

**Actions:**

1. **AWS Console (One-time setup)**:

   - Go to AWS App Runner > Connections and create a new connection to your GitHub repository
   - Note: Terraform cannot create the connection, but it can use it
   - Save the ARN of this connection

2. **Terraform**: In the `terraform/` folder, define the infrastructure:

   - `data "aws_apprunner_connection"`: Retrieve the ARN of the GitHub connection created in step 1

   - `aws_apprunner_service`: Main resource with the following configuration:
     - **source_configuration**: Points to your GitHub repository (`connection_arn`, `repository_url`, `branch_name`)
       - `source_code_version.type = "BRANCH"`
       - `auto_deployments_enabled = true` (This enables CI/CD!)
       - `code_configuration.configuration_source = "REPOSITORY"` (looks for `apprunner.yaml` or Dockerfile)
     - **health_check_configuration**: Point to `/health` endpoint of your API
     - **instance_configuration**: Define CPU/Memory
     - **network_configuration**: Set `egress_type = "DEFAULT"` (to allow calls to Groq)
     - **service_name**: `"mro-copilot-backend"`
     - **Environment Variables**: Define secrets (environment variables) for the service, including `GROQ_API_KEY`

3. **Terraform**: Create `outputs.tf` to expose the App Runner service URL (`aws_apprunner_service.mro_copilot.service_url`)

**Validation (Manual Tests):**

- Run `terraform apply`
- Verify in AWS Console that an App Runner service is "running"
- Note the public URL (`.awsapprunner.com`)

### Phase 3: One-Shot Ingestion Script (Local)

**Actions:**

1. Create `scripts/ingest.py`

2. The script must:

   - Read from `scripts/source_pdfs/` folder (where manuals are placed)
   - Load text content (e.g., using `pypdf`)
   - Split text into chunks (e.g., using `RecursiveCharacterTextSplitter`)
   - Load the embedding model (e.g., `sentence-transformers/all-MiniLM-L6-v2`)
   - Create a FAISS index from these embeddings
   - Save the FAISS index and a mapping file (for chunks) to `backend/faiss_index/`

3. Create `scripts/requirements.txt` with dependencies: `pypdf`, `sentence-transformers`, `langchain`, `faiss-cpu`

**Validation (Manual Tests):**

- Place a PDF manual (e.g., `manuel_A320.pdf`) in `scripts/source_pdfs/`
- Run `pip install -r scripts/requirements.txt`
- Run `python scripts/ingest.py`
- **Key Test**: The `backend/faiss_index/` folder contains new files (e.g., `index.faiss`, `index.json`)

### Phase 4: Backend Development (FastAPI)

**Actions:**

1. Initialize a FastAPI project in `backend/`

2. Create a multi-stage `Dockerfile`:

   - `COPY requirements.txt .` and `pip install ...`
   - `COPY . /app` (This will include the `faiss_index/` folder in the build context)

3. **app/main.py**:

   - **On startup**: Load the FAISS index (`faiss.read_index(...)`) and chunks (`json.load(...)`) from the `faiss_index/` folder into memory
   - Create a `/health` endpoint that returns `{"status": "ok"}` for App Runner health checks

4. **app/api/endpoints/chat.py**:

   - Create a `POST /ask-stream` endpoint
   - The endpoint must:
     - Vectorize the user question
     - Query the in-memory FAISS index to find the N most relevant chunks
     - Retrieve the chunk text (via the JSON mapping)
     - Build the prompt and call Groq in streaming mode
     - Return a `StreamingResponse`

5. **app/main.py**: Configure CORS to allow requests from the Vercel frontend URL

**Validation (Manual Tests):**

- Successfully `docker build` the image without errors
- Successfully `docker run` the image locally (with a `.env` file)
- API starts and logs "FAISS index loaded"
- Test `http://localhost:8080/ask-stream` from Postman/Swagger and receive a streamed response

### Phase 5: Frontend Development (Next.js)

**Actions:**

1. Initialize a Next.js project in `frontend/` (with TypeScript and Tailwind CSS)

2. **app/page.tsx**: Create a simple chat UI

3. **components/ChatWindow.tsx**: Implement streaming logic (via `fetch` POST)

**Validation (Manual Tests):**

- Run `npm run dev`
- Ensure the API (Phase 4) is running locally
- Configure the frontend to connect to `http://localhost:8080`
- Ask a question and verify the response displays word by word (streaming)

### Phase 6: CI/CD Deployment and E2E Testing

**Actions:**

1. **Backend Deployment**:

   - `git add .`
   - `git commit -m "feat: initial MRO copilot"`
   - `git push`
   - **Magic happens**: Go to AWS App Runner console and observe the service enter "Operation in progress" mode. It automatically builds and deploys.

2. **Frontend Deployment**:
   - Connect the Git repository to a new Vercel project
   - In Vercel settings, add the environment variable `NEXT_PUBLIC_API_URL` with the `.awsapprunner.com` URL (obtained from Terraform output or AWS Console)
   - Vercel automatically deploys

**Validation (Manual Tests) - THE FINAL E2E TEST:**

- Open the Vercel URL in a browser
- Ask a technical question
- The frontend calls the App Runner API (HTTPS)
- The App Runner API queries its local FAISS index, calls Groq, and streams the response
- The response displays word by word

---

## Summary

This plan provides a complete roadmap for building and deploying the MRO Copilot RAG application with minimal infrastructure, automated CI/CD, and streaming LLM responses. Each phase includes clear actions and validation steps to ensure successful implementation.
