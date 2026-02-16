# Best Practices

## Do

- Use stream IDs that include aggregate type.
- Include correlation and causation IDs.
- Version events from day one.
- Implement idempotency for writes.
- Index for your query patterns.

## Do Not

- Update or delete events.
- Store large payloads in events.
- Skip optimistic concurrency checks.
- Ignore slow consumers and backpressure.
