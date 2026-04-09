# Progress

Track your progress through the masterclass. Update this file as you complete modules - Claude Code reads this to understand where you are in the project.

## Convention
- `[ ]` = Not started
- `[-]` = In progress
- `[x]` = Completed

## Modules

### Module 1: App Shell + Observability
- [x] Phase 1: Project Scaffolding
  - [x] Backend setup (FastAPI + venv)
  - [x] Frontend setup (Vite + React + Tailwind + shadcn)
- [x] Phase 2: Supabase Setup
  - [x] Database schema (threads, messages)
  - [x] Row-Level Security policies
- [x] Phase 3: Authentication
  - [x] Backend auth middleware
  - [x] Frontend auth flow (magic link)
- [x] Phase 4: Chat UI
  - [x] Thread list sidebar
  - [x] Chat interface with messages
- [x] Phase 5: OpenAI Responses API
  - [x] Backend service + streaming
  - [x] Frontend SSE handling
- [x] Phase 6: LangSmith Observability

### Module 1: Validation (completed 2026-04-08)
- [x] Backend starts cleanly (`uvicorn app.main:app --reload`)
- [x] `GET /health` returns `{"status":"ok"}`
- [x] Protected routes reject unauthenticated requests (403)
- [x] Frontend build passes (`tsc -b && vite build`)
- [x] Frontend lint passes (`eslint .`)
- [x] Frontend dev server starts on http://localhost:5173
- [x] Fixed TS 6 `baseUrl` deprecation error in `tsconfig.app.json`
- [x] Fixed `react-refresh` lint violations (split `useAuth` hook and `AuthContext` into separate files)
- [x] Supabase URL corrected to `https://jfkijgjwytnivlthppcr.supabase.co` in both `backend/.env` and `frontend/.env`
- [x] Supabase migrations applied — `001_create_threads.sql` and `002_create_messages.sql` pushed via `supabase db push`
- [x] End-to-end auth flow tested (redirect to login, protected route guard, login page renders, /auth/callback mounts) — automated via `e2e/module1.mjs`
- [x] Added authenticated Playwright script `e2e/module1-auth-chat.mjs` covering OTP request, magic-link completion hook, and chat create/send assertions
- [x] End-to-end chat flow tested (thread create → message → SSE stream) — automated via `e2e/module1-auth-chat.mjs`
- [x] LangSmith trace verification confirmed — `create_openai_thread` and `stream_assistant_response` runs visible in `agentic-rag-masterclass` project with `success` status

### Releases
- [x] `0.0.1` cut on 2026-04-09 for completed Module 1 scope

### Module 2: BYO Retrieval + Memory (In Progress)

**Module 2 Status Summary:**
- ✅ Phases 1-2: Chat completions refactoring complete + OpenRouter testing passing
- ✅ Phase 3: Frontend/Auth validation passing
- ✅ Phase 5: Documentation complete
- ✅ Phase 6: Ingestion foundation complete (DB tables, Storage bucket, upload API, frontend component)
- ⏹️ Phase 7-8: Embeddings & retrieval (next up)

**Key Completed Work (Phases 1-5):**
- Backend successfully migrated from Azure Responses API → stateless Chat Completions
- Provider-agnostic LLM configuration (OpenRouter working, tested)
- All backend services + auth flows working
- Frontend/auth unchanged and passing all tests
- Comprehensive provider setup documentation complete

**Dependencies for Agents:**
- OpenRouter API key: Configured in `backend/.env` (`LLM_API_KEY=sk-or-v1-...`)
- Supabase project: `https://jfkijgjwytnivlthppcr.supabase.co`
- Services command: `scripts/start-services.sh {start|stop|restart|status|logs}`

---

#### Phase 1-2: Chat Completions Refactoring ✅ COMPLETED
- [x] Step 1.1: Updated `backend/app/config.py` 
  - [x] Removed Azure OpenAI vars (endpoint, API key, deployment, API version, vector store ID)
  - [x] Added generic LLM provider vars (provider, endpoint, API key, model name)
- [x] Step 1.2: Replaced `services/openai_service.py` with `completions_service.py`
  - [x] Removed all Azure Responses API code (client creation, thread management, response tools)
  - [x] Implemented stateless Chat Completions streaming via `stream_chat_completion()`
  - [x] Configured to work with any OpenAI-compatible provider
- [x] Step 1.3: Updated `routers/threads.py`
  - [x] Changed import to use `completions_service` instead of `openai_service`
  - [x] Updated `create_thread()` to generate local UUID (was Azure Responses API call)
  - [x] Updated `send_message()` to use new `stream_chat_completion()` function
- [x] Step 2.1: Configured `backend/.env` for testing
  - [x] Set up OpenRouter provider configuration
  - [x] Created `.env.example` with clear setup instructions for all providers
- [x] Step 2.2: Backend service validation
  - [x] Services start successfully via `scripts/start-services.sh restart`
  - [x] Backend health endpoint working: `GET /health` → `{"status":"ok"}`
  - [x] Config loads correctly with new LLM provider settings
  - [x] Imports verified: `completions_service` loads, old `openai_service` removed
- [x] Documentation
  - [x] Created `PROVIDER_SETUP.md` with setup guides (OpenRouter, Ollama, LM Studio, Azure)
  - [x] Updated `backend/.env.example` with all configurable variables

#### Phase 2: End-to-End Testing with OpenRouter ✅ COMPLETED
- [x] Configured OpenRouter API key
- [x] Backend streams via OpenRouter (openai/gpt-3.5-turbo)
- [x] E2E authenticated chat flow works (16/16 test assertions pass)
  - [x] Password sign-in redirects away from /login
  - [x] Authenticated app shell renders
  - [x] Thread creation works
  - [x] Chat send + assistant stream produces output
  - [x] Login UI tabs present

#### Phase 3: Frontend & Auth Validation ✅ COMPLETED
- [x] Verified existing chat UI unchanged (no refactoring needed)
- [x] Existing e2e smoke tests pass: `node e2e/module1.mjs`
- [x] SSE stream format identical (client sees `data: {token: "..."}`)
- [x] Auth flow, RLS queries, thread/message operations work as before

#### Phase 4: Ollama Compatibility Testing ⏳ OPTIONAL (Requires local Ollama install)
- [ ] Install Ollama locally (https://ollama.ai) - optional alternative to OpenRouter
- [ ] If installed: Configure `backend/.env` for Ollama provider
- [ ] Run same e2e test to verify local inference works

Note: Phase 4 is optional. OpenRouter (Phase 2) provides cloud-based testing without local setup.

#### Phase 5: Documentation & Examples ✅ COMPLETED
- [x] Updated `backend/.env.example` with all configurable variables
- [x] Created `PROVIDER_SETUP.md` with setup guides (OpenRouter, Ollama, LM Studio, Azure)
- [x] Updated `README.md`:
  - [x] Updated tech stack (provider-agnostic)
  - [x] Updated environment variables section
  - [x] Added link to PROVIDER_SETUP.md
  - [x] Updated service startup instructions
  - [x] Added authenticated e2e test documentation

### Module 2: Ingestion Pipeline (In Progress)

#### Phase 6: Ingestion Foundation ✅ COMPLETED (2026-04-09)

**Implementation Status:**
- Files Created:
  - `backend/app/routers/documents.py` - Upload/list/delete endpoints
  - `backend/app/db/migrations.py` - Schema initialization on startup
  - `frontend/src/components/chat/DocumentUpload.tsx` - Upload UI component
  - `supabase/migrations/003_create_ingestion_schema.sql` - DB schema
  - `.agent/plans/6.ingestion-foundation.md` - Detailed implementation plan
  
- Files Modified:
  - `backend/app/main.py` - Registered documents router + startup schema init
  - `backend/app/db/supabase.py` - Fixed `get_supabase_for_token()` to pass auth to Storage API
  - `backend/requirements.txt` - Added python-multipart
  - `frontend/src/components/layout/Sidebar.tsx` - Added DocumentUpload component

**Completed Tasks:**
- [x] Fixed TypeScript compilation errors in DocumentUpload.tsx (extra `</div>`, header type mismatch)
- [x] Frontend build passes: `npm run build` ✅
- [x] Applied Supabase schema migration via `supabase db push`
  - Tables: documents, chunks, embeddings (with pgvector extension)
  - RLS policies on all three tables
  - Indexes on user_id and document_id
- [x] Created Supabase Storage bucket: `user-documents` (private, 10MB limit, PDF/TXT/MD)
- [x] Applied Storage RLS policies (users can only access their own folder)
- [x] Fixed `SUPABASE_SERVICE_ROLE_KEY` in backend/.env (was using anon key)
- [x] Fixed documents router to use `get_supabase_for_token()` instead of `get_client()`
- [x] Fixed Storage auth: `get_supabase_for_token()` now sets auth header for Storage API
- [x] Document upload API tested: upload → list → delete lifecycle works
- [x] All existing e2e tests pass (8/8 smoke + 16/16 auth-chat)

**Fixes Applied:**
1. `DocumentUpload.tsx` - Removed extra `</div>` tag causing JSX parse error
2. `DocumentUpload.tsx` - Changed `getAuthHeaders()` return type to `HeadersInit | undefined`
3. `documents.py` - Changed import from `app.db.supabase` module to `get_supabase_for_token`
4. `supabase.py` - Added `client.storage._client.headers["Authorization"]` to pass user token to Storage
5. `backend/.env` - Updated `SUPABASE_SERVICE_ROLE_KEY` to actual service_role JWT

#### Phase 7: Embeddings & Vector Search (Deferred)
- [ ] Chunking strategy (recursive split, overlap)
- [ ] Embedding service integration (OpenAI or open-source)
- [ ] pgvector storage and indexing
- [ ] Similarity search query

#### Phase 8: Retrieval Tool & Tool Calling (Deferred)
- [ ] Define retrieval tool schema (query, top_k, threshold)
- [ ] Implement tool execution in Chat Completions flow
- [ ] Tool result injection into conversation
- [ ] Multi-turn tool calling (chat can call retrieval multiple times)

---

## Testing & Validation Info

### Test Credentials
- Email: `test@test.com`
- Password: `$1MhDupRhDqzqGY`
- Status: Exists in Supabase project

### Key URLs & Endpoints
- Frontend: http://localhost:5173
- Backend health: http://127.0.0.1:8000/health
- Supabase project: https://jfkijgjwytnivlthppcr.supabase.co
- OpenRouter: https://openrouter.ai

### E2E Testing Commands
```bash
# Smoke tests (auth + basic endpoints)
node e2e/module1.mjs

# Full chat flow with OpenRouter streaming
TEST_EMAIL="test@test.com" TEST_PASSWORD='$1MhDupRhDqzqGY' node e2e/module1-auth-chat.mjs

# Service management
scripts/start-services.sh {start|stop|restart|status|logs}

# Frontend build check
cd frontend && npm run build

# Backend import check
cd backend && source venv/bin/activate && python3 -c "from app.routers import documents; print('✅ OK')"
```

### Important Notes
- All Supabase tables require RLS enabled - users see only own data
- Document status field: 'uploading' → 'processing' → 'complete' or 'error'
- Duplicate detection by content_hash prevents re-uploading same file
- Phase 6 uses Supabase Storage bucket: `user-documents`
- python-multipart required for FastAPI file upload (added to requirements.txt)