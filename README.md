# Skills Catalog


npx skills add ni.paris/skills

### architecture-patterns
- Implements Clean Architecture, Hexagonal Architecture, and DDD for backend systems.
- Use it when designing or refactoring service boundaries, ports/adapters, and domain models.
- Enforces inward dependencies, framework-free domain code, and thin controllers.

### apply-project-agent-template
- Creates or updates a lean `AGENTS.md` or `CLAUDE.md` using a standard template.
- Use it to establish consistent repo-specific agent instructions and workflow defaults.
- Focuses on minimal, practical guidance with placeholders for unknown project details.

### boundary-validation
- Enforces strict two-layer validation: DTO contract checks vs domain business rules.
- Use it when reviewing API payload validation, especially Pydantic-heavy endpoints.
- Prevents validator bloat by moving policy, IO, and semantic checks out of request models.

### code-review
- Runs structured code reviews with checklist-driven and guideline-driven feedback.
- Use it for pull request reviews requiring security and performance-aware evaluation.
- Applies companion files and reports findings by severity.

### comprehensive-documenter
- Generates accurate, maintainable documentation for whole repositories, modules, and APIs.
- Use it when asked to document architecture, modules, or project usage comprehensively.
- Prioritizes why-first docs, evidence-backed claims, and explicit unknowns.

### deployment-pipeline-design
- Designs multi-stage CI/CD pipelines with gates, rollout strategy, and rollback design.
- Use it for release workflows balancing speed, safety, and production confidence.
- Enforces artifact promotion, explicit verification, and predefined rollback triggers.

### docs-review
- Reviews markdown documentation against Metabase-style writing quality standards.
- Use it for documentation reviews that need clear, actionable editorial feedback.
- Emphasizes reader outcomes, decision clarity, tone trust, and numbered issues.

### event-store-design
- Designs append-only event stores for event-sourced architectures.
- Use it when selecting event store tech and implementing streams, subscriptions, and checkpoints.
- Requires ordering, optimistic concurrency, idempotency, and durable replay positioning.

### git-master
- Provides advanced Git workflows for commits, rebases, history search, and pull request prep.
- Use it for Git-heavy tasks including split commits, blame or bisect, and history cleanup.
- Enforces atomic commit splitting, style detection, and branch context analysis.

### github-actions-templates
- Builds production-grade GitHub Actions workflows for test, build, and deploy automation.
- Use it when creating CI/CD pipelines, reusable workflows, and deployment gates.
- Enforces pinned actions, least-privilege permissions, and secret-safe configuration.

### clean-architecture-python
- Applies Clean Architecture patterns in Python codebases with clear layer boundaries.
- Use it when defining use cases, ports, adapters, and composition roots.
- Keeps domain logic framework-free and routes persistence through interfaces.

### litestar-expert
- Provides expert guidance for Litestar-based ASGI apps and APIs.
- Use it for routing, DTOs, dependency injection, middleware, auth, and OpenAPI setup.
- Promotes layered configuration, DTO-safe responses, and policy outside handlers.

### mastering-postgresql-appdev
- Treats PostgreSQL as an application-facing service, not only a storage backend.
- Use it for SQL-centric app design, DB API layering, and schema or query strategy.
- Emphasizes constraints, set-based logic, explicit result shaping, and versioned SQL.

### modular-monolith-fastapi
- Designs FastAPI modular monoliths with strict module boundaries and public APIs.
- Use it when you want monolith simplicity with microservice-like internal modularity.
- Enforces no cross-module leakage, composition-root wiring, and DTO-based contracts.

### pydantic-models-py
- Defines Pydantic v2 models using Base, Create, Update, Response, and Persistence variants.
- Use it for clean request and response schema design in Python APIs.
- Keeps DTOs mechanical and lightweight while deferring business logic elsewhere.

### vercel-react-best-practices
- Curates Vercel React and Next.js performance rules across eight optimization categories.
- Use it when writing, reviewing, or refactoring frontend code for runtime and bundle gains.
- Prioritizes waterfall elimination, bundle control, fetch strategy, and rerender efficiency.

### skill-creator
- Provides a framework for creating, structuring, and packaging high-quality AgentSkills.
- Use it when building or iterating skills with scripts, references, and assets.
- Covers naming, frontmatter quality, progressive disclosure, validation, and packaging.

### web-design-guidelines
- Reviews UI implementations against current web interface and accessibility guidelines.
- Use it for UX or UI audits and design-quality checks against explicit standards.
- Requires fetching the latest guidelines and reporting only materially impactful issues.

### agentic-architecture-design
- Generates on-brand slide decks and prototype assets for the Standard Chartered "Agentic Architecture" design system.
- Use it when building software-architecture or platform-strategy slides, or throwaway prototypes/mocks.
- Ships color/type tokens, reusable slide components, and strict brand voice and layout rules.

### ste-writing
- Rewrites prose into ASD-STE100 Simplified Technical English to strip "AI slop" from docs and writing.
- Use it for READMEs, PR descriptions, error messages, release notes, and comments that need to read plain and human.
- Enforces one-word-one-meaning, active voice, short sentences, and a strict/STE-flavored mode split.

### editorial-inquisition
- Ruthlessly tightens essays, white papers, specs, and memos by cutting anything that doesn't earn its place.
- Use it when editing long-form prose that's grown bloated, repetitive, or unfocused.
- Treats every sentence as guilty until proven necessary; skip it when the user wants brainstorming or expansion instead.

### extract-factbank
- Extracts an examinable fact bank (validated JSONL + clusters) from a textbook or source chapter, then optionally builds study sheets.
- Use it to turn regulatory, medical, technical, or exam-prep material into structured, testable facts.
- Requires every fact to cite a chapter page; subject-agnostic via per-subject profile.json conventions.

### find-skills
- Helps discover and install skills from the open agent skills ecosystem via the `npx skills` CLI.
- Use it when the user asks "is there a skill for X" or wants to extend agent capabilities.
- Points to `npx skills find/add/check/update` and skills.sh for browsing.

### graphify
- Turns any folder of files (code, docs, papers, images) into a navigable knowledge graph with community detection.
- Use it via `/graphify` to build interactive HTML, GraphRAG-ready JSON, and a plain-language audit report.
- Supports incremental updates, BFS/DFS querying, Neo4j export, and MCP server access.

### phoenix-llm-evals
- Best practices for designing, running, and maintaining LLM evaluations on Arize Phoenix.
- Use it when evaluating RAG pipelines, chatbots, tool-calling agents, extraction, summarization, or codegen.
- Routes to use-case-specific playbooks plus core principles, Phoenix mechanics, and judge-validation references.

### process-inbox
- Ingests raw sources (articles, papers, books, notes, transcripts) into a structured wiki knowledge base.
- Use it when asked to process an inbox file, summarize a source, or add a document to the knowledge base.
- Identifies key concepts and decisions, prefers enriching existing wiki pages over creating new ones, and logs history.
