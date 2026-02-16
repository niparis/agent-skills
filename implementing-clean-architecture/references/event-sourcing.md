## Event Sourcing in Clean Architecture (Python)

### Goal
Persist state changes as an **append-only stream of events**, rebuild state by replay, and power projections.

### Core Concepts
- **Aggregate**: consistency boundary; produces events
- **Event Store**: append-only persistence with optimistic concurrency
- **Projection**: read model built from events
- **Snapshot** (optional): speed up rebuild for large streams

### Where Things Live
- Domain: event definitions (data), aggregate methods that decide events
- Application: command handlers/use cases, transaction boundaries, publishing
- Infrastructure: event store adapter, projection writers, subscriptions

### Rules
- Events are immutable facts; never update/delete.
- Use optimistic concurrency per stream (expected version).
- Keep events small; store IDs and essential fields.
- Include metadata (correlation/causation IDs, actor, timestamp).

### Implementation Pattern
1. Use case loads aggregate by replaying events (or snapshot + tail).
2. Domain method returns new events (or records them internally).
3. Application appends events to store in a transaction.
4. Infrastructure updates projections (sync or async).

### Projections
- Design projections for query needs (not for domain purity).
- Idempotent handlers: safe to re-run events.
- Store checkpoint positions for subscribers.

### When Event Sourcing Pays Off
- Strong audit requirements
- Complex workflows and state history matters
- You need multiple read projections over time

### When Not to Use Event Sourcing (Yet)
- Simple CRUD domains
- Team unfamiliarity and low tolerance for operational complexity