---
name: apply-project-agent-template
metadata:
  author: niparis
  version: "1.0.0"
description: Create or update a lean AGENTS.md (or CLAUDE.md) using our standard template, plus lightweight guidance on how to fill each section.
inputs:
  - project_name (optional)
  - one_sentence_description (optional)
  - tech_stack (optional)
  - north_star_preferences (optional)
  - anti_patterns (optional)
  - workflow_commands (optional)
  - docs_location (optional)
  - requirements_file (optional)
outputs:
  - AGENTS.md (preferred) or CLAUDE.md content, or a minimal diff if the file already exists
---

 Skill: Apply Project Agent Template (Lean)

## Role
You are an autonomous repo-bootstrapping agent. Your job is to produce a **single, minimal “agent guidance” file** (prefer `AGENTS.md`; fallback `CLAUDE.md`) that makes future coding agents faster and more consistent.

## Core Rules
- Keep the final file **lean**. Aim for **~1200 tokens or less**.
- Prefer **project-specific truths** over generic advice.
- If something is unknown, either:
  - infer it from the repo (package.json, pyproject, README, docker-compose, etc.), or
  - leave a clear placeholder (`[TODO: ...]`) rather than asking questions.
- Output:
  - If no existing file: output the **complete markdown file**.
  - If the file exists: output **diff-style changes only** (clear additions/removals).

## How to Execute
1. Check whether `AGENTS.md` or `CLAUDE.md` exists.
2. Read project signals (README, package manager files, build scripts, CI configs).
3. Fill the template below with repo-grounded details.
4. Keep optional sections only if relevant.

---


## Template to Produce (fill it in; remove the helper notes)

> **Filling guidance:** The comments in parentheses are instructions to you. They should NOT appear in the final file.

```markdown
# Project: [Project Name]
A [one-sentence description of what it is and why it exists].
(How to fill: Use the repo context/README. If unclear, write a neutral best-effort statement like “Internal tool for X” and add [TODO] if needed.)

Built with: [concise tech stack list, e.g., Next.js 15 (app router), Supabase, Tailwind, Shadcn/ui, TypeScript, pnpm].
(How to fill: Prefer exact versions if obvious (package.json, lockfile). Keep it a single line.)

## North Star Preferences
- [Your key style rules, e.g., Prioritize React Server Components...]
- [Anti-patterns, e.g., Named exports only; no barrel files...]
(How to fill: Use “house rules” that prevent churn: architecture choices, code style, patterns to avoid. Keep 3–8 bullets total.)

## Documentation & Resources
- Main project docs live in `/docs/` folder (Markdown files).
- Requirements and roadmap: See `REQUIREMENTS.md` at project root.
- For any unclear specs, check `/docs/` first before asking.
(How to fill: Point to the real places in THIS repo. If `/docs/` doesn’t exist, either remove it or set the correct path. If there is no requirements file, keep one line that says where requirements SHOULD live, e.g. `REQUIREMENTS.md`.)

## Requirements Roadmap Maintenance
- All features/user stories live in `REQUIREMENTS.md` (use sections: Planned, In Progress, Completed).
- When a new requirement emerges (e.g., during implementation or clarification):
  - Add it under **Planned** with a brief description and priority.
  - Tag with `[ ]` checkbox if it's a task.
- When implementing a feature:
  - Move it to **In Progress** at start.
  - On completion: Move to **Completed**, add a short note on implementation (e.g., "Implemented via X component"), and check `[x]`.
- Always update `REQUIREMENTS.md` in the same PR as the code changes.
(How to fill: Keep this section if the project is evolving. If there’s no requirements file yet, keep the protocol and ensure it encourages creating one, but don’t over-explain.)

## Git Workflow
- Work on feature branches: `git checkout -b feat/short-description` or `fix/short-description`.
- Commit often using Conventional Commits (`feat:`, `fix:`, `refactor:`, etc.).
- Keep branches small and focused (one feature/fix per branch).
- After changes: Commit, push branch, and open a PR for review.
- Main branch is protected—never push directly to main.
- Rebase interactively before PR if history is messy.


## Workflow Commands
- Dev server: `pnpm dev`
- Build: `pnpm build`
- Lint & fix: `pnpm lint --fix`
- Type check: `pnpm check`
- Tests: `pnpm test`
- Always run `pnpm check` before opening PR.
(How to fill: Replace with real commands from package.json/scripts, Makefile, or task runner. If none exist, remove everything keep the header onlu)

## Commits & Communication
- Be concise and direct. No apologies.
- If uncertain, ask clarifying questions.
- Use available skills for complex tasks (git operations, testing, refactoring).
(How to fill: Keep it short. This is about interaction style and autonomy.)
