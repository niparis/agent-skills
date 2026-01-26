---
name: modular-monolith-fastapi
description: Design and implement a Modular Monolith in Python using FastAPI, Pydantic, and modern tooling (uv, ruff, pyright). Use when you want microservice-grade modularity with monolith simplicity.
license: MIT
metadata:
  author: niparis
  version: "1.0.0"
---

# Modular Monolith for FastAPI

Build a single deployable FastAPI application that is split into modules with strong boundaries, explicit APIs, and minimal coupling. This keeps development fast today and keeps the option to extract services later.

## When to Use This Skill
	•	You need a single deployment unit (simpler ops) but your codebase is growing.
	•	Multiple domains/features should evolve independently (teams or streams of work).
	•	You want to avoid the “shared everything” monolith and keep a clean architecture.
	•	You want a credible path to microservices without starting distributed.

## Core Principles

1) Module boundaries are the architecture

A “module” is a top-level package that contains everything for one business capability.

Rules:
	•	No cross-module imports except via a module’s public API.
	•	No shared database writes/reads across modules except via the module API.
	•	No sharing ORM models across modules (expose DTOs instead).
	•	No circular module dependencies.

2) Each module owns its data + logic

A module can have its own internal architecture:
	•	Simple “service + repository” for CRUD-heavy modules
	•	Clean/Hex patterns for complex business logic

But the boundary rules must stay consistent.

3) A module exposes a narrow public API

Expose operations as:
	•	facade.py functions/classes, or
	•	application/ use-cases, or
	•	a minimal set of “ports” (interfaces) for inversion-of-control

Return types should be DTOs (Pydantic models or dataclasses), not ORM entities.

4) Composition root wires everything

FastAPI entrypoint is the composition root:
	•	creates app
	•	configures infrastructure (db, event bus)
	•	includes routers
	•	wires dependencies (FastAPI Depends)

Avoid global singleton sprawl; keep wiring in one place.

### Recommended Project Layout

src/
  app/
    main.py                 # composition root
    settings.py             # config (pydantic-settings)
    infra/
      db.py                 # engine/session factory
      logging.py
      events.py             # event bus abstraction + implementation
    modules/
      users/
        api.py              # APIRouter (HTTP layer)
        public.py           # module public API (facade/use-cases)
        domain.py           # entities/value objects (optional)
        application.py      # use-cases (optional)
        repo.py             # persistence adapters
        schemas.py          # DTOs (Pydantic)
        __init__.py
      billing/
        api.py
        public.py
        ...
      inventory/
        api.py
        public.py
        ...
  tests/
    integration/
    contract/

Guideline: modules/<name>/public.py is the only file other modules may import.

### FastAPI Integration Pattern

Module router
	•	Each module defines an APIRouter.
	•	The router should call module public API (not repo/ORM directly).

Dependency injection
	•	Use FastAPI Depends to inject:
	•	db session
	•	module services/facades
	•	cross-cutting concerns (auth, tracing)
	•	Keep “wiring functions” close to the composition root, not scattered.

### Data and DTO Rules (Pydantic)

Use Pydantic for:
	•	HTTP request/response models
	•	module DTOs for inter-module communication
	•	validation at the boundary (incoming/outgoing)

Avoid:
	•	returning ORM models from module APIs
	•	accepting ORM models as inputs to module APIs

Communication Between Modules

Choose one of these patterns per interaction:

A) Synchronous call (default)

Use when:
	•	you need immediate result (validation, permission checks, invariants)
	•	the coupling is acceptable and stable

Rule:
	•	calls go only through other_module.public.*

B) Events (decoupling)

Use when:
	•	side effects can be async or eventual (emails, projections, audit)
	•	you want to reduce call chains

Rule:
	•	event payload is a DTO
	•	publisher does not depend on consumers

C) Ports (inversion)

Use when:
	•	you want module A to depend on an interface, not module B
	•	you need high testability or alternate implementations

Rule:
	•	define the interface near the caller
	•	bind implementation in composition root

(Deep dive: references/modular-monolith-communication.md)

### Persistence Strategy

Minimum viable approach:
	•	One physical DB, but each module has:
	•	its own tables (namespace/prefix strongly recommended)
	•	its own repository layer
	•	its own migrations folder (or namespaced migrations)

Hard rule:
	•	no “shared tables” owned by multiple modules

If you must share:
	•	treat it as a published read model (read-only outside owner)
	•	plan migration to proper ownership

(Deep dive: references/modular-monolith-persistence.md)

### Testing Strategy

Levels:
	•	Module tests: call module.public.* directly (no HTTP).
	•	Contract tests: verify DTO schema compatibility across modules.
	•	Integration tests: start app + hit endpoints (FastAPI TestClient).

Rules:
	•	Unit tests should not import another module’s internals.
	•	Prefer “public API tests” over deep internal tests.
	•	Integration tests should cover critical cross-module flows.

(Deep dive: references/modular-monolith-testing.md)

Tooling Baseline (Python 3.12+ recommended)
	•	uv for env + dependency management
	•	ruff for lint + format
	•	pyright for type checking
	•	pytest for tests
	•	alembic for migrations (or your chosen migration tool)
	•	pydantic + pydantic-settings for config

(Deep dive: references/python-tooling-uv-fastapi.md)

### Implementation Template (Minimal)

main.py composition root (sketch)

from fastapi import FastAPI
from app.infra.db import init_db
from app.modules.users.api import router as users_router
from app.modules.billing.api import router as billing_router

def create_app() -> FastAPI:
    app = FastAPI()
    init_db(app)

    app.include_router(users_router, prefix="/users", tags=["users"])
    app.include_router(billing_router, prefix="/billing", tags=["billing"])
    return app

app = create_app()

Module public API pattern (sketch)

# app/modules/users/public.py
from pydantic import BaseModel

class UserDTO(BaseModel):
    id: str
    email: str

class CreateUserIn(BaseModel):
    email: str

async def create_user(data: CreateUserIn, *, repo) -> UserDTO:
    user = await repo.create(email=data.email)
    return UserDTO(id=user.id, email=user.email)

Router uses public API only (sketch)

# app/modules/users/api.py
from fastapi import APIRouter, Depends
from app.modules.users import public
from app.modules.users.wiring import get_users_repo  # wiring is allowed within module

router = APIRouter()

@router.post("/", response_model=public.UserDTO)
async def create_user(
    data: public.CreateUserIn,
    repo = Depends(get_users_repo),
):
    return await public.create_user(data, repo=repo)

### Boundary Enforcement Checklist

Apply these consistently:
	•	Each module has public.py (or equivalent) and everything else is private.
	•	No cross-module imports except modules.<x>.public.
	•	No shared ORM entities across modules.
	•	Each module owns its tables + migrations.
	•	Routers only call the module public API.
	•	Composition root is the only place where modules are wired together.
	•	CI checks boundaries (import rules) + types + tests.

(Deep dive: references/modular-monolith-boundary-enforcement.md)

### Best Practices
	•	Keep module APIs small and stable; change internals freely.
	•	Prefer DTOs and typed interfaces over “sharing objects”.
	•	Use events for side effects to avoid cascading synchronous calls.
	•	Maintain a clear dependency direction (no circular module graphs).
	•	Keep shared code minimal; prefer duplication over coupling for small helpers.
	•	Use type checking as a “contract” between modules.
	•	Make migrations and DB ownership explicit (table prefixes, schema separation).
	•	Keep “wiring” explicit and local (composition root + module wiring files).
	•	Add “extraction readiness” only at the boundary: APIs/events, not everywhere.

### Common Pitfalls
	•	“Module” folders that still import each other’s internals.
	•	Shared common/ becoming a dumping ground.
	•	ORM models leaking outside module boundaries.
	•	One global service layer used by all modules (coupling via “god services”).
	•	Cross-module DB joins and queries outside the owning module.
	•	Events with huge payloads or vague semantics.
	•	Too many tiny modules (over-fragmentation) or one giant module (fake modularity).
	•	Skipping integration tests for critical cross-module flows.



