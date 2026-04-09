---
description: Build from the plan
argument-hint: [link-to-plan]
---

# Build

Read and execute: `$ARGUMENTS`

## Process

1. **Read the entire plan** - Understand all tasks, dependencies, and success criteria

2. **Confirm prerequisites before edits**
   - Required env files exist: `backend/.env`, `frontend/.env`
   - Backend runtime exists at `backend/venv`
   - Frontend dependencies exist at `frontend/node_modules`
   - If touching LLM config, verify `AZURE_OPENAI_ENDPOINT` is an Azure AI Project endpoint containing `/api/projects/{project-name}`

3. **Execute tasks in order** - Implement each task following project conventions. Verify syntax and imports after each change.

4. **Run validation gates** - If the plan includes tests or validation commands, run them. For app flow changes, prefer:
   - `scripts/start-services.sh restart`
   - `node e2e/module1.mjs`
   - `TEST_EMAIL="test@test.com" TEST_PASSWORD='$1MhDupRhDqzqGY' node e2e/module1-auth-chat.mjs`
   Fix issues before proceeding.

5. **Report completion** - Summarise what was done:
   - Tasks completed
   - Files created/modified  
   - Test results (if applicable)
   - Any deviations from plan and why
   - Any required updates to `PRD.md`, `CLAUDE.md`, or `PROGRESS.md`