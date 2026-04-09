# Agentic RAG Masterclass App

This repository contains a full-stack RAG chat application built during Module 1 of the Agentic RAG Masterclass.

Current implementation includes:
- FastAPI backend with auth-protected thread and message routes
- React + Vite frontend with Supabase auth flow and protected routes
- Supabase-backed threads and messages schema with Row-Level Security policies
- Azure OpenAI integration with streaming responses over SSE
- LangSmith tracing hooks in the backend OpenAI service
- Playwright-based end-to-end smoke validation script

## Tech Stack

| Layer | Tech |
|---|---|
| Frontend | React, TypeScript, Vite, Tailwind, shadcn/ui |
| Backend | Python, FastAPI, Uvicorn |
| Database/Auth | Supabase |
| LLM | Azure OpenAI |
| Observability | LangSmith |
| E2E Testing | Playwright |

## Project Structure

```
backend/
	app/
		auth/
		db/
		models/
		routers/
		services/
frontend/
	src/
		components/
		contexts/
		lib/
		pages/
supabase/
	migrations/
e2e/
```

## Prerequisites

- Python 3.11+
- Node.js 20+
- npm
- [Supabase CLI](https://supabase.com/docs/guides/cli) (`brew install supabase/tap/supabase` or download binary from [GitHub releases](https://github.com/supabase/cli/releases))
- Supabase project
- Azure OpenAI deployment
- LangSmith project (optional but recommended)

## Environment Configuration

Use `.env.example` as your reference. This project expects:

- Backend env file: `backend/.env`
- Frontend env file: `frontend/.env`

Required variables:
- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`
- `SUPABASE_SERVICE_ROLE_KEY`
- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_API_KEY`
- `AZURE_OPENAI_DEPLOYMENT_NAME`
- `LANGCHAIN_API_KEY` (optional if tracing disabled)
- `LANGCHAIN_PROJECT`
- `LANGCHAIN_TRACING_V2`
- `VITE_SUPABASE_URL`
- `VITE_SUPABASE_ANON_KEY`
- `VITE_API_URL`

## Setup

### 1) Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2) Frontend

```bash
cd frontend
npm install
```

### 3) Supabase SQL migrations

Apply migrations using the Supabase CLI:

```bash
supabase login
supabase link --project-ref <your-project-ref>
supabase db push
```

Or apply manually via the Supabase SQL editor:
- `supabase/migrations/001_create_threads.sql`
- `supabase/migrations/002_create_messages.sql`

## Run Locally

Start backend:

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

Start frontend:

```bash
cd frontend
npm run dev
```

App URLs:
- Frontend: http://localhost:5173
- Backend: http://127.0.0.1:8000
- Backend health: http://127.0.0.1:8000/health

## Validation and Testing

### Frontend static checks

```bash
cd frontend
npm run build
npm run lint
```

### End-to-end smoke test

```bash
node e2e/module1.mjs
```

The smoke test validates:
- unauthenticated redirect to `/login`
- login page render
- protected route guard behavior
- callback page mount
- backend health endpoint response
- unauthenticated API access rejection

## Playwright MCP (VS Code)

This repo includes VS Code MCP server config at `.vscode/mcp.json`:
- server name: `playwright`
- command: `playwright-mcp`
- browser: `chromium`

Install globally:

```bash
npm install -g @playwright/mcp
$(npm root -g)/@playwright/mcp/node_modules/.bin/playwright install chromium
```

## Useful Docs

- `PRD.md` for module requirements
- `CLAUDE.md` for project rules and architecture constraints
- `PROGRESS.md` for implementation and validation status
