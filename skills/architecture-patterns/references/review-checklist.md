# Architecture Review Checklist

## Dependency Direction

- Domain imports no framework or IO packages.
- Application imports domain, not infrastructure.
- Infrastructure imports application, not the reverse.

## Boundaries

- Ports are defined in the core.
- Adapters are thin and replaceable.
- Controllers translate and delegate only.

## Domain Health

- Entities enforce invariants.
- Value objects validate on creation.
- Aggregates define consistency boundaries.

## Testability

- Core logic is testable without external systems.
- Integration tests cover adapters and wiring.
