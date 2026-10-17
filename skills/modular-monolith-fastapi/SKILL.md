---
name: modular-monolith-fastapi
description: Design and implement a Modular Monolith in Python using FastAPI, Pydantic, and modern tooling (uv, ruff, pyright). Use when you want microservice-grade modularity with monolith simplicity.
---

# Modular Monolith for FastAPI

Build a single deployable FastAPI application split into modules with strong boundaries, explicit APIs, and minimal coupling. Keep the option to extract services later without starting distributed.

## Quick Start

1. Create modules as top-level packages under `app/modules/`.
2. Put module public API in `public.py` and treat everything else as private.
3. Expose only DTOs from module APIs (never ORM entities).
4. Route handlers call module public APIs, not repositories.
5. Wire all dependencies in the composition root (main app factory).
6. Enforce boundaries with CI checks and import rules.

## Non-Negotiable Boundary Rules

- No cross-module imports except `modules.<name>.public`.
- No shared tables or shared ORM models across modules.
- No circular module dependencies.
- Composition root is the only place that wires modules together.

## Communication Patterns (Choose One per Interaction)

- Synchronous call: use for immediate invariants and validations.
- Events: use for async side effects and decoupling.
- Ports: use for inversion of control and testability.

Use the details and tradeoffs in `references/modular-monolith-communication.md`.

## Minimal Skeleton

```python
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
```

```python
# app/modules/users/api.py
from fastapi import APIRouter, Depends
from app.modules.users import public
from app.modules.users.wiring import get_users_repo

router = APIRouter()

@router.post("/", response_model=public.UserDTO)
async def create_user(data: public.CreateUserIn, repo = Depends(get_users_repo)):
    return await public.create_user(data, repo=repo)
```

## Read These References When Needed

- Project layout and composition root wiring: `references/layout.md`
- Boundary enforcement checklist: `references/modular-monolith-boundary-enforcement.md`
- Module communication patterns: `references/modular-monolith-communication.md`
- Persistence ownership rules: `references/modular-monolith-persistence.md`
- Testing strategy: `references/modular-monolith-testing.md`
- Tooling baseline: `references/python-tooling-uv-fastapi.md`
