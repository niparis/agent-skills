---
name: clean-architecture-python
description: Implement Clean Architecture in advanced Python codebases. Use when designing or refactoring service boundaries, use cases, domain models, adapters, and tests for long-term maintainability.
license: MIT
metadata:
  author: niparis
  version: "1.0.0"
---

# Clean Architecture in Python

Build Python systems where business rules stay stable while frameworks, databases, and delivery mechanisms can change.

## When to Use This Skill

- Designing a new backend with non-trivial business rules
- Refactoring a framework-centric codebase into testable core logic
- Introducing clear boundaries between domain/application/infrastructure
- Creating modular monoliths with strong internal APIs
- Establishing a testing strategy with fast unit tests + focused integration tests
- Evaluating CQRS / event sourcing / modularization as complexity grows

## Outcomes You Should Aim For

- **Domain rules are framework-agnostic** (no HTTP, ORM, CLI, queues in domain)
- **Use cases are orchestration** (coordinate domain + ports; no IO details)
- **Infrastructure is replaceable** (DB/email/queue/framework behind interfaces)
- **Tests are layered** (domain unit tests are fast; infra tests are few and meaningful)
- **Boundaries are explicit** (DTOs, ports, adapters, composition root)

---

## Core Structure

### Layers

1. **Domain**
   - Entities, value objects, domain services (pure business rules)
   - Domain exceptions / invariants
2. **Application**
   - Use cases (interactors / command handlers)
   - Ports (interfaces) owned by application
   - DTOs (input/output), result objects
   - Transaction boundaries
3. **Infrastructure**
   - Adapters implementing ports (DB repos, external APIs, message bus, filesystem)
   - Controllers/handlers for web/cli/jobs
   - Serialization, ORM mapping, framework glue
4. **External**
   - The actual frameworks/services (FastAPI, SQLAlchemy engine, Redis, etc.)

### Dependency Rule (Enforce This)

- Dependencies point **inward**.
- Domain imports **nothing** from application/infrastructure/framework.
- Application imports **domain**, and defines **ports**.
- Infrastructure imports **application** (to implement ports) and frameworks.

---

## Directory Layout (Practical Default)

project_root/
├── app/
│   ├── domain/
│   │   ├── entities/
│   │   │   └── order.py
│   │   ├── value_objects/
│   │   │   └── money.py
│   │   ├── services/
│   │   │   └── pricing.py
│   │   ├── events/
│   │   │   └── order_events.py
│   │   └── errors.py
│   │
│   ├── application/
│   │   ├── dto/
│   │   │   └── order_dto.py
│   │   ├── ports/
│   │   │   ├── repositories.py
│   │   │   ├── unit_of_work.py
│   │   │   └── clock.py
│   │   ├── use_cases/
│   │   │   ├── create_order.py
│   │   │   └── submit_order.py
│   │   └── errors.py
│   │
│   ├── infrastructure/
│   │   ├── persistence/
│   │   │   ├── orm_models.py
│   │   │   ├── unit_of_work_sqlalchemy.py
│   │   │   └── repositories_sqlalchemy.py
│   │   ├── web/
│   │   │   ├── controllers/
│   │   │   │   └── orders.py
│   │   │   └── presenters/
│   │   │       └── orders_presenter.py
│   │   ├── integrations/
│   │   │   ├── email/
│   │   │   │   └── smtp_email_sender.py
│   │   │   └── messaging/
│   │   │       └── event_bus.py
│   │
│   ├── main/
│   │   ├── settings.py
│   │   ├── container.py
│   │   └── entrypoints/
│   │       ├── api.py
│   │       ├── cli.py
│   │       └── worker.py
│
├── tests/
│   ├── unit/
│   │   ├── domain/
│   │   │   ├── test_order.py
│   │   │   └── test_money.py
│   │   └── application/
│   │       ├── test_create_order.py
│   │       └── test_submit_order.py
│   ├── integration/
│   │   ├── test_repositories_sqlalchemy.py
│   │   └── test_uow_sqlalchemy.py
│
├── scripts/
│   ├── run_api.sh
│   ├── run_worker.sh
│   └── lint.sh
│
├── pyproject.toml
├── README.md
└── .gitignore

**Rule:** If a folder depends on another, it should be “outside” it (domain deepest).



## Domain Best Practices (Python)

### Entities: Put Rules With State

- Entities should contain methods that enforce invariants.
- Avoid “anemic domain”: data-only classes + logic in use cases.
- Prefer explicit domain errors (`DomainError`, `InvariantViolation`) over returning magic values.

**Good:**
- `Order.add_item(...)` validates quantity, stock rules, etc.
- `Auction.place_bid(...)` enforces minimum increment, closed auction rule.

**Avoid:**
- `if order.status == ...` repeated across multiple use cases.
- Domain methods that accept web requests, ORM models, or dicts.

### Value Objects: Validate at Construction

- Use `@dataclass(frozen=True)` for immutability (good enough in Python).
- Validate in `__post_init__`.
- Use VOs for IDs, money, time ranges, email, etc., especially at boundaries.

### Domain Events (Optional, Not Default)

- Use events when you need decoupling between domain actions and side effects.
- Keep domain events as plain data objects.
- Publishing/dispatching happens outside the domain (application/infrastructure).

---

## Application Best Practices

### Use Cases Are Orchestrators

A use case typically:
1. Validates input (lightweight; heavy validation in domain/VOs)
2. Loads aggregates via ports
3. Calls domain methods
4. Persists changes via ports
5. Emits events / calls secondary ports
6. Returns a result DTO (or raises application errors)

**Keep use cases free of:**
- ORM/session objects
- framework request/response types
- serialization concerns
- “smart queries” that belong to read models

### Define Ports in Application (Not Infrastructure)

- Ports are owned by the application layer.
- Infrastructure implements them.

Examples:
- `UserRepositoryPort`
- `PaymentGatewayPort`
- `UnitOfWorkPort` (optional)
- `ClockPort` (for time)
- `IdGeneratorPort` (optional)

### DTO Strategy (Python-Friendly)

- Use `dataclasses` or pydantic *inside controllers only*.
- Convert controller input -> `InputDTO` (application).
- Use case returns `OutputDTO` or `Result`.

Recommended patterns:
- `Result` type: `Ok(value)` / `Err(code, message)` OR raise typed exceptions.
- For advanced codebases, prefer explicit error types over string errors.

### Transactions: Put the Boundary in Application

Options:
- `UnitOfWork` injected into use case, with `with uow:` semantics.
- Transaction decorator at the application boundary (careful with testability).
- Framework-managed transactions are acceptable if hidden behind an adapter.

**Rule:** Domain must not manage transactions.

---

## Infrastructure Best Practices

### Controllers: Thin Translators

A controller/handler should:
- Parse/validate external input (HTTP, CLI, message)
- Build `InputDTO` (and VOs if needed)
- Call use case
- Map `OutputDTO`/errors to a response

Do not:
- Implement business rules
- Call repositories directly (except read models if you intentionally do CQRS)

### Repositories: Translate Between Domain and Storage

Repositories should:
- Return domain entities (or aggregates)
- Hide ORM models and query mechanics
- Keep mapping code localized (assembler/mapper functions)

Avoid:
- Leaking ORM objects into application/domain
- “Active Record” models used as domain entities in complex domains

### Dependency Injection and Composition Root

- All wiring happens in `main/container.py`.
- Use cases depend on ports; container binds ports -> adapters.
- For Python, choose one approach and standardize:
  - Manual wiring (simple, explicit)
  - DI container (Injector/Dependency Injector/etc.)

**Rule:** No importing the container inside domain/application (avoid service locator).

---

## Packaging and Modularity

### Start Simple, Scale to Modules

- Early: organize by layers + feature folders inside.
- Later: vertical slices (modules) that each contain domain/application/infra subpackages.

Signals you need modules:
- Many teams working independently
- Many features with separate domain models
- Integration boundaries become unstable

**Rule:** Modules communicate via explicit APIs (facades/ports/events), not internal imports.

---

## CQRS and Read Models (Pragmatic Guidance)

Use CQRS when:
- Read complexity outgrows write complexity
- Different performance/scaling requirements for reads vs writes
- You want to keep use cases “write-focused” and read models optimized

Practical approach:
- Commands go through use cases + domain.
- Queries use dedicated query services/read repositories and return read DTOs.
- Keep read side strictly read-only.

(See deeper dive: `references/cqrs.md`)

---

## Testing Strategy (Non-Negotiable)

### Test Pyramid (Recommended)

1. **Domain unit tests** (fast, pure)
   - Entities, VOs, domain services
2. **Application unit tests** (fast, with fakes)
   - Use cases + fake ports
3. **Integration tests** (fewer, slower)
   - Repository against real DB (docker)
   - HTTP endpoints + wiring (thin)
4. **End-to-end** (minimal)
   - Only for critical flows

Rules:
- Most coverage comes from domain/application tests.
- Integration tests validate adapters + mapping + transactions.

(See deeper dive: `references/testing-strategies.md`)

---

## Common Failure Modes (And Fixes)

- **Framework leakage into core**
  - Fix: move request/response/ORM types to infrastructure; use DTOs + ports
- **Repositories too smart**
  - Fix: domain rules in entities; repositories do persistence and mapping only
- **Anemic domain**
  - Fix: migrate rules into entity methods; reduce conditional logic in use cases
- **Over-abstracted early**
  - Fix: start with minimal ports; add interfaces where change is expected
- **Too many tiny use cases**
  - Fix: group by module facade *only if cohesive*; avoid “god facade”
- **Testing relies on DB for everything**
  - Fix: fake ports for most tests; keep DB tests focused

---

## Implementation Checklist (Use This When Reviewing PRs)

### Layering
- [ ] Domain imports no framework/ORM/app/infrastructure modules
- [ ] Application defines ports; infrastructure implements them
- [ ] Controllers only translate; do not contain business rules

### Domain
- [ ] Entities enforce invariants via methods
- [ ] Value objects validate on creation and are immutable-ish
- [ ] Domain errors are explicit types

### Application
- [ ] Use cases orchestrate; no IO or framework types
- [ ] Transaction boundary is explicit
- [ ] Outputs are stable DTOs or result types

### Infrastructure
- [ ] Repositories map cleanly (no ORM leakage)
- [ ] External integrations behind ports
- [ ] Composition root owns wiring; no service locator usage

### Tests
- [ ] Domain/application tests dominate
- [ ] Integration tests exist for adapters + mapping + transactions
- [ ] Very few E2E tests; only critical flows

---

## Deeper Dives

- `references/cqrs.md`
- `references/modularity.md`
- `references/event-sourcing.md`
- `references/testing-strategies.md`