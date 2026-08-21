---
name: clean-architecture-python
description: Implement Clean Architecture in advanced Python codebases. Use when designing or refactoring service boundaries, use cases, domain models, adapters, and tests for long-term maintainability.
---

# Clean Architecture in Python

Design Python systems where business rules stay stable while frameworks and infrastructure evolve.

## Quick Workflow

1. Identify domain entities and invariants.
2. Define use cases as orchestration, not logic containers.
3. Define ports in application; implement adapters in infrastructure.
4. Wire dependencies in a single composition root.
5. Add tests at domain and application layers first.

## Non-Negotiables

- Domain has no framework, ORM, or IO imports.
- Dependencies point inward; infrastructure depends on application.
- Controllers translate input/output only.
- Use cases do not access DBs directly; they call ports.

## Minimal Skeleton

```python
# application/ports.py
class UserRepositoryPort:
    async def get(self, user_id: str):
        raise NotImplementedError

# application/use_cases.py
class GetUser:
    def __init__(self, users: UserRepositoryPort):
        self.users = users

    async def execute(self, user_id: str):
        return await self.users.get(user_id)
```

```python
# infrastructure/repositories.py
class SqlUserRepository(UserRepositoryPort):
    async def get(self, user_id: str):
        return await self._query(user_id)
```

## Decision Guide

- CQRS: use when read complexity outgrows writes.
- Event sourcing: use for auditability or temporal queries.
- Modularity: split into modules when teams or domains diverge.

## Read These References When Needed

- CQRS guidance: `references/cqrs.md`
- Modularity and module boundaries: `references/modularity.md`
- Event sourcing basics: `references/event-sourcing.md`
- Testing strategy: `references/testing-strategies.md`
