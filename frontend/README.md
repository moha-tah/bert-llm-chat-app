# Ask Barfield AI - Support Intake Widget

> Intelligent document assistant and support intake system for Air France / Barfield.

## ⚡ Features

- **RAG Chat**: Interactive document retrieval with real-time streaming and source citations.
- **Support Widget**: Global floating widget for structured support intake and smart team routing.
- **AI Powered**: OpenAI GPT-4o integration with Vercel AI SDK.
- **Modern UI**: Next.js 16, Tailwind CSS v4, and dark/light mode.

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| **Framework** | Next.js 16 (App Router), React 19 |
| **Language** | TypeScript (Strict) |
| **Styling** | Tailwind CSS v4 |
| **AI/ML** | Vercel AI SDK, OpenAI GPT-4o |
| **Validation** | Zod |

## 🚀 Getting Started

### Prerequisites
- Node.js 18+
- OpenAI API Key
- Backend API running on port 8080 (for RAG chat)

### Installation

1. **Install dependencies**:
   ```bash
   pnpm install
   ```

2. **Configure Environment**:
   Create `.env.local`:
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8080
   OPENAI_API_KEY=sk-your-key
   ```

3. **Run Development Server**:
   ```bash
   pnpm dev
   ```
   Visit `http://localhost:3000`.

## 🏗️ Architecture

### Support Widget Flow
1. **User Interaction**: Floating widget collects issue details.
2. **AI Processing**: `useSupportChat` sends history to `/api/support`.
3. **Extraction**: GPT-4o extracts structured data (schema in `lib/intake-schema.ts`) and validates via Zod.
4. **Routing**: AI routes to appropriate internal teams based on embedded knowledge base.

### Project Structure
```
frontend/
├── app/
│   ├── api/support/       # Streaming chat API
│   ├── ask/               # Main RAG chat page
│   └── layout.tsx         # Global layout with Widget
├── components/
│   ├── support-widget/    # Widget UI components
│   └── chat/              # Shared chat UI
├── hooks/                 # Custom hooks (useChat, useSupportChat)
└── lib/                   # Schemas (Zod) and utils
```

## 📦 Deployment

Standard Next.js deployment (Vercel recommended).
Ensure `OPENAI_API_KEY` and `NEXT_PUBLIC_API_URL` are set in your deployment environment.

---
**License**: Proprietary - Air France / Barfield
