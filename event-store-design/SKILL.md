---
name: event-store-design
description: Design and implement event stores for event-sourced systems. Use when building event sourcing infrastructure, choosing event store technologies, or implementing event persistence patterns.
---

# Event Store Design

Use this skill to design an event store for an event-sourced system.

## Quick Start

1. Define stream naming and event schemas (versioned from day one).
2. Choose your storage technology (EventStoreDB, Postgres, DynamoDB).
3. Implement append-only writes with optimistic concurrency.
4. Design global reads and per-stream reads.
5. Add subscriptions with checkpoints and backpressure handling.

## Non-Negotiables

- Append-only storage (no event updates or deletes).
- Per-stream ordering and optimistic concurrency.
- Idempotent writes (event IDs or expected version).
- Durable checkpoints for subscriptions.

## Decision Guide (Use or Avoid)

- Use when you need auditability, temporal queries, or async projections.
- Avoid when your domain is simple CRUD or you cannot operate a stream store reliably.

## Read These References When Needed

- Event store schema (Postgres): `references/postgres-schema.md`
- Subscription design and checkpoints: `references/subscriptions.md`
- Implementation sketches (Python, EventStoreDB, DynamoDB): `references/implementations.md`
- Technology comparison and tradeoffs: `references/tech-comparison.md`
- Do and don't list for reviews: `references/best-practices.md`
