# CLAUDE.md

RAG app with chat (default) and document ingestion interfaces. Config via env vars, no admin UI.

## Stack
- Frontend: React + Vite + Tailwind + shadcn/ui
- Backend: Python + FastAPI
- Database: Supabase (Postgres, pgvector, Auth, Storage, Realtime)
- LLM: Azure AI Projects + OpenAI Responses API (Module 1), OpenAI-compatible Chat Completions providers (Module 2+)
- Observability: LangSmith

## Rules
- Python backend must use a `venv` virtual environment
- No LangChain, no LangGraph - raw SDK calls only
- Use Pydantic for structured LLM outputs
- All tables need Row-Level Security - users only see their own data
- Stream chat responses via SSE
- Use Supabase Realtime for ingestion status updates
- Module 2+ uses stateless completions - store and send chat history yourself
- Ingestion is manual file upload only - no connectors or automated pipelines
- Login UX supports both password and magic-link sign in; keep both paths working unless explicitly changed
- Validation maintenance is mandatory: every feature/behavior change must include a test-suite update in at least one applicable layer (`backend/tests/unit`, `backend/tests/integration`, `e2e`) and must keep `validation/manifest.json` acceptance mapping current

## Critical Build Dependencies
- Service launcher expects backend env at `backend/.env` and frontend env at `frontend/.env`
- Service launcher expects backend virtualenv at `backend/venv` (not repo-root `.venv`)
- Service launcher expects frontend dependencies installed in `frontend/node_modules`
- `AZURE_OPENAI_ENDPOINT` must be an Azure AI Project endpoint containing `/api/projects/{project-name}`
- `OPENAI_VECTOR_STORE_ID` is optional; when invalid/missing, backend falls back to Responses API without `file_search`

## Planning
- Save all plans to `.agent/plans/` folder
- Naming convention: `{sequence}.{plan-name}.md` (e.g., `1.auth-setup.md`, `2.document-ingestion.md`)
- Plans should be detailed enough to execute without ambiguity
- Each task in the plan must include at least one validation test to verify it works
- Assess complexity and single-pass feasibility - can an agent realistically complete this in one go?
- Include a complexity indicator at the top of each plan:
  - ✅ **Simple** - Single-pass executable, low risk
  - ⚠️ **Medium** - May need iteration, some complexity
  - 🔴 **Complex** - Break into sub-plans before executing

## Development Flow
1. **Plan** - Create a detailed plan and save it to `.agent/plans/`
2. **Build** - Execute the plan to implement the feature
3. **Validate** - Test and verify the implementation works correctly. Use browser testing where applicable via an appropriate MCP
4. **Iterate** - Fix any issues found during validation

## Validation Policy (For Future Agents)
- Any behavior change is incomplete unless the validation suite grows with it.
- Required after code changes:
  - Update or add tests in at least one matching layer (smoke, unit, integration, e2e)
  - Update `validation/manifest.json` when feature coverage or acceptance criteria changes
  - Run `./scripts/validate.sh fast` during development
  - Run `./scripts/validate.sh full` before handoff/release
- Do not silently skip deferred scope. Keep pending tests explicit (for example xfail with a clear reason).

## Service Spin-Up (For Future Agents)
- Start both backend and frontend from repo root with:
  - `scripts/start-services.sh start`
- Check service state with:
  - `scripts/start-services.sh status`
- Restart cleanly with:
  - `scripts/start-services.sh restart`
- Stop both services with:
  - `scripts/start-services.sh stop`
- View recent logs with:
  - `scripts/start-services.sh logs`

### Agent Guidance
- Always run service commands from repository root.
- Do not manually run separate long-lived `uvicorn` and `npm run dev` commands unless debugging startup issues.
- The startup script enforces expected ports and health checks:
  - Backend health: `http://127.0.0.1:8000/health`
  - Frontend dev server: `http://localhost:5173`
- For validation-heavy changes, prefer:
  - `scripts/start-services.sh restart`
  - `node e2e/module1.mjs`
  - `TEST_EMAIL="test@test.com" TEST_PASSWORD='$1MhDupRhDqzqGY' node e2e/module1-auth-chat.mjs`

## Test Credentials
The following account exists in the Supabase project for automated E2E testing:

- **Email:** test@test.com
- **Password:** $1MhDupRhDqzqGY

Use these with the password sign-in flow (not magic link). Pass them via env vars when running e2e scripts:
```bash
TEST_EMAIL="test@test.com" TEST_PASSWORD='$1MhDupRhDqzqGY' node e2e/module1-auth-chat.mjs
```

## Progress
Check PROGRESS.md for current module status. Update it as you complete tasks.