---
description: "Execute a written plan step by step with validation gates and completion reporting."
argument-hint: "path to plan file (e.g. .agent/plans/1.auth-setup.md)"
agent: "agent"
---

Read and execute: $ARGUMENTS

## Process

1. Read the full plan first. Understand all tasks, dependencies, and success criteria.
2. Confirm prerequisites and ordering constraints before writing any code:
   - Required env files exist: `backend/.env`, `frontend/.env`
   - Backend runtime exists at `backend/venv`
   - Frontend dependencies exist at `frontend/node_modules`
   - If touching LLM config, verify `AZURE_OPENAI_ENDPOINT` contains `/api/projects/{project-name}`
3. Execute tasks in order. Do not reorder unless the plan explicitly allows parallel work.
4. After each meaningful change, run the plan's validation checks (tests, lint, type checks, or runtime checks). For app-flow changes, prefer:
   - `scripts/start-services.sh restart`
   - `node e2e/module1.mjs`
   - `TEST_EMAIL="test@test.com" TEST_PASSWORD='$1MhDupRhDqzqGY' node e2e/module1-auth-chat.mjs`
5. Fix failures before moving forward. Do not mark tasks complete while validation is failing.
6. Keep implementation aligned with repository rules in [CLAUDE.md](../../CLAUDE.md):
   - Plans are stored in `.agent/plans/`.
   - Each task must include validation.
   - Update [PROGRESS.md](../../PROGRESS.md) when work is completed.
7. If architecture, dependencies, or workflow changed, update [PRD.md](../../PRD.md) and [CLAUDE.md](../../CLAUDE.md) in the same pass.
8. Report completion with:
   - Tasks completed
   - Files created or modified
   - Validation/test results
   - Any deviation from plan and justification

If the plan is missing acceptance criteria, validation commands, or sequencing details, ask targeted clarification questions before making risky changes.
