# Skills Catalog

[https://github.com/niparis/agent-skills.git](https://github.com/niparis/agent-skills.git)

A personal catalog of [Agent Skills](https://skills.sh) for Claude Code and other coding agents. It mixes reusable engineering disciplines (architecture patterns, code review, CI/CD design) with standalone workflows (documentation generation, knowledge-graph building, skill creation). Install what you need, or browse the reference below for what each skill does and when it applies.

## Installation

```bash
npx skills add niparis/agent-skills
```

Pick the skills you want from the interactive prompt, and which coding agents to install them on.

## Reference

Skills split on one axis: who invokes them. **User-invoked** skills are reachable only when you type them (e.g. `/graphify`); their job is to run a full, deliberate task end-to-end. **Model-invoked** skills hold a reusable discipline the agent reaches for automatically when a task fits, but you can also invoke them directly.

### Engineering

Backend architecture, code quality, and delivery. Reference disciplines the agent applies mid-task.

**Model-invoked**

- **[architecture-patterns](./skills/architecture-patterns/SKILL.md)**: Implements Clean Architecture, Hexagonal Architecture, and DDD for backend systems — inward dependencies, framework-free domain code, thin controllers.
- **[boundary-validation](./skills/boundary-validation/SKILL.md)**: Enforces the Two-Layer Boundary policy for API payloads, keeping DTO contract checks separate from domain business rules.
- **[clean-architecture-python](./skills/implementing-clean-architecture/SKILL.md)**: Implements Clean Architecture in advanced Python codebases — use cases, ports, adapters, and composition roots kept framework-free.
- **[event-store-design](./skills/event-store-design/SKILL.md)**: Designs append-only event stores for event-sourced systems — ordering, optimistic concurrency, idempotency, replay.
- **[modular-monolith-fastapi](./skills/modular-monolith/SKILL.md)**: Designs FastAPI modular monoliths with strict module boundaries, composition-root wiring, and DTO-based contracts.
- **[mastering-postgresql-appdev](./skills/mastering-postgresql/SKILL.md)**: Treats PostgreSQL as an application-facing service — DB API layering, constraints, set-based logic, versioned SQL.
- **[litestar-expert](./skills/litestar-expert/SKILL.md)**: Expert guidance for Litestar ASGI apps — routing, DTOs, dependency injection, middleware, auth, OpenAPI.
- **[pydantic-models-py](./skills/pydantic-models-py/SKILL.md)**: Defines Pydantic v2 models with the Base/Create/Update/Response/InDB pattern for clean API schemas.
- **[vercel-react-best-practices](./skills/react-best-practices/SKILL.md)**: Vercel's React/Next.js performance rules — waterfall elimination, bundle control, fetch strategy, rerender efficiency.
- **[web-design-guidelines](./skills/web-design-guidelines/SKILL.md)**: Reviews UI implementations against current web interface and accessibility guidelines, reporting only materially impactful issues.
- **[code-review](./skills/code-review/SKILL.md)**: Structured, checklist- and guideline-driven code review with severity-ranked findings.
- **[docs-review](./skills/docs-review/SKILL.md)**: Reviews documentation changes against Metabase-style writing quality standards.
- **[deployment-pipeline-design](./skills/deployment-pipeline-design/SKILL.md)**: Designs multi-stage CI/CD pipelines — approval gates, rollout strategy, explicit rollback triggers.
- **[github-actions-templates](./skills/github-actions-templates/SKILL.md)**: Builds production-grade GitHub Actions workflows with pinned actions, least-privilege permissions, secret-safe config.
- **[git-master](./skills/git-master/SKILL.md)**: Advanced Git workflows — atomic commit splitting, rebases, blame/bisect history search, PR prep.

### Writing

Documentation and prose, from one-off setup to ongoing editorial discipline.

**User-invoked**

- **[comprehensive-documenter](./skills/comprehensive-documenter/SKILL.md)**: Generates accurate, maintainable, why-first documentation for an entire codebase, module, or API.
- **[apply-project-agent-template](./skills/apply-project-agent-template/SKILL.md)**: Creates or updates a lean `AGENTS.md`/`CLAUDE.md` from a standard template.
- **[specs-arch-modules](./skills/specs-arch-modules/SKILL.md)**: Keeps architecture docs (product vision, system/functional architecture, component ownership, ADRs) in a fixed `docs/` layout, filing new information in the right file and auditing existing docs against it.

**Model-invoked**

- **[ste-writing](./skills/cure-ai-slop/SKILL.md)**: Rewrites prose into ASD-STE100 Simplified Technical English to strip "AI slop" from docs, PRs, and release notes.
- **[editorial-inquisition](./skills/editorial-inquisition/SKILL.md)**: Ruthlessly tightens long-form prose, cutting anything — sentence, example, digression — that doesn't earn its place.

### AI & Agent Tooling

Working with skills, knowledge graphs, LLM evals, and other agent-facing artifacts.

**User-invoked**

- **[skill-creator](./skills/skill-creator/SKILL.md)**: Creates or updates AgentSkills — naming, frontmatter, progressive disclosure, validation, packaging.
- **[find-skills](./skills/find-skills/SKILL.md)**: Discovers and installs skills from the open agent skills ecosystem via the `npx skills` CLI.
- **[graphify](./skills/graphify/SKILL.md)**: Turns any folder of files into a navigable knowledge graph — interactive HTML, GraphRAG-ready JSON, and an audit report.
- **[agentic-architecture-design](./skills/arch-decks/SKILL.md)**: Generates on-brand slide decks and prototype assets for the Standard Chartered "Agentic Architecture" system.
- **[extract-factbank](./skills/extract-factbank/SKILL.md)**: Extracts a validated, examinable fact bank from a textbook chapter, then optionally builds study sheets.
- **[process-inbox](./skills/process-inbox/SKILL.md)**: Ingests a raw source file into a structured wiki knowledge base, enriching existing pages over creating new ones.

**Model-invoked**

- **[phoenix-llm-evals](./skills/llm-evals-standards/SKILL.md)**: Best practices for designing, running, and maintaining LLM evaluations on Arize Phoenix.
