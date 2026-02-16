---
name: architecture-patterns
description: Implement proven backend architecture patterns including Clean Architecture, Hexagonal Architecture, and Domain-Driven Design. Use when architecting complex backend systems or refactoring existing applications for better maintainability.
---

# Architecture Patterns

Use Clean Architecture, Hexagonal Architecture, and DDD to keep business rules stable while infrastructure changes around them.

## Quick Start

1. Choose a core: Clean or Hexagonal.
2. Define boundaries: domain, application, infrastructure.
3. Define ports in the core, implement adapters at the edge.
4. Put business rules in entities/use cases, not controllers.
5. Enforce inward dependencies with CI and import rules.

## Non-Negotiables

- Dependencies point inward.
- Domain has no framework or IO imports.
- Ports are defined in the core, adapters implement them at the edge.
- Controllers translate and delegate, they do not contain business rules.

## Pattern Selection Guide

- Clean Architecture: layered structure and explicit use cases.
- Hexagonal: ports and adapters with IO at the edges.
- DDD: model-rich domains with bounded contexts and aggregates.

## Event Sourcing Decision (Quick)

Use event sourcing when you need auditability, temporal queries, or asynchronous projections.
Avoid it if your domain is simple CRUD or your team cannot operate an event store reliably.

Deep dive: `event-store-design`.

## Read These References When Needed

- Clean Architecture layers and directory layout: `references/clean-architecture.md`
- Hexagonal architecture ports and adapters: `references/hexagonal-architecture.md`
- DDD tactical patterns and examples: `references/ddd-patterns.md`
- Common pitfalls and review checklist: `references/review-checklist.md`
