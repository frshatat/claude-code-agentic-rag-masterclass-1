# Copilot Instructions

Agentic RAG app — chat + document ingestion. Config via env vars only.

## Stack
- Frontend: React + Vite + Tailwind + shadcn/ui
- Backend: Python + FastAPI
- Database: Supabase (Postgres + pgvector + Auth + Storage + Realtime)
- LLM: Azure AI Projects + OpenAI Responses API (Module 1); OpenAI-compatible Chat Completions (Module 2+)
- Observability: LangSmith

## Hard Rules
- No LangChain, no LangGraph — raw SDK calls only
- No new dependencies without clear justification
- Pydantic for all structured LLM outputs
- All DB tables must have Row-Level Security — users see only their own data
- Stream chat responses via SSE; never buffer the full response
- Backend virtualenv at `backend/venv`, not `.venv` at repo root
- Both password and magic-link login flows must stay working unless explicitly changed
- No hardcoded secrets — use env vars

## Critical Build Dependencies
- `backend/.env` and `frontend/.env` must exist before running services
- `AZURE_OPENAI_ENDPOINT` must contain `/api/projects/{project-name}`
- `OPENAI_VECTOR_STORE_ID` is optional; missing/invalid value → Responses API runs without `file_search`

## Service Commands (always run from repo root)
```bash
scripts/start-services.sh start    # start backend + frontend
scripts/start-services.sh restart  # clean restart
scripts/start-services.sh status   # check ports + health
scripts/start-services.sh logs     # tail recent logs
```
- Backend health: `http://127.0.0.1:8000/health`
- Frontend: `http://localhost:5173`
- Do not run `uvicorn` or `npm run dev` manually unless debugging startup

## Validation (run after any meaningful change)
```bash
node e2e/module1.mjs
TEST_EMAIL="test@test.com" TEST_PASSWORD='$1MhDupRhDqzqGY' node e2e/module1-auth-chat.mjs
```

## Planning
- Plans go in `.agent/plans/{sequence}.{name}.md`
- Every task needs at least one validation step
- Mark complexity: ✅ Simple / ⚠️ Medium / 🔴 Complex
- Update `PROGRESS.md` when work completes

## Code Style
- Minimalism: write the least code that solves the problem correctly
- DRY: extract helpers only when it reduces total code and improves clarity
- Guard clauses over deep nesting
- Fail fast at boundaries (inputs, external calls, deserialization)
- Prefer streaming/pagination — never load full datasets into memory
