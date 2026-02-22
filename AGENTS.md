# Project: agent-skills
A curated collection of reusable AgentSkills, each packaged as a focused folder with a `SKILL.md` contract and optional companion resources.

Built with: Markdown-first skill packages (YAML frontmatter + references/assets/scripts), GitHub, Git.

## North Star Preferences
- Keep each skill narrow in scope and explicit about when it should trigger.
- Treat `SKILL.md` frontmatter (`name`, `description`) as the primary discovery surface; keep descriptions precise.
- Keep `SKILL.md` lean and move deep material into `references/` when needed.
- Prefer concrete workflows and non-negotiables over long conceptual prose.
- Preserve existing folder naming and avoid breaking internal relative paths.
- Do not add extra documentation files inside skill folders unless they directly support skill execution.

## Documentation & Resources
- Top-level catalog: `README.md`.
- Skill definitions: one `SKILL.md` per skill directory at the repository root.
- Extended guidance (when present): `references/`, `assets/`, or `scripts/` inside each skill folder.
- Any added skill or meaningful skill update must be reflected in `README.md` in the same PR.

## Git Workflow
- Create focused branches: `feat/<short-topic>` or `fix/<short-topic>`.
- Keep commits small and descriptive (Conventional Commits preferred).
- Open a PR for every change; avoid direct pushes to `main`.
- Rebase/squash only when it improves review clarity.

## Workflow Commands
- Inspect repository status: `git status --short -b`
- Review changed content: `git diff --stat` and `git diff`
- Search skills quickly: `rg "^name:|^description:" -- */SKILL.md`

## Commits & Communication
- Be concise, direct, and outcome-focused.
- Infer defaults from existing skill patterns before asking questions.
- Call out uncertainty explicitly with `[TODO: ...]` when facts cannot be verified.
