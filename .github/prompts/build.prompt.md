---
description: "Execute a written plan step by step with validation gates and completion reporting."
argument-hint: "path to plan file (e.g. .agent/plans/1.auth-setup.md)"
agent: "agent"
---

Read and execute: $ARGUMENTS

## Process

1. Read the full plan first. Understand all tasks, dependencies, and success criteria.
2. Confirm prerequisites and ordering constraints before writing any code.
3. Execute tasks in order. Do not reorder unless the plan explicitly allows parallel work.
4. After each meaningful change, run the plan's validation checks (tests, lint, type checks, or runtime checks).
5. Fix failures before moving forward. Do not mark tasks complete while validation is failing.
6. Keep implementation aligned with repository rules in [CLAUDE.md](../../CLAUDE.md):
   - Plans are stored in `.agent/plans/`.
   - Each task must include validation.
   - Update [PROGRESS.md](../../PROGRESS.md) when work is completed.
7. Report completion with:
   - Tasks completed
   - Files created or modified
   - Validation/test results
   - Any deviation from plan and justification

If the plan is missing acceptance criteria, validation commands, or sequencing details, ask targeted clarification questions before making risky changes.
