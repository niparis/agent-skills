# Triggers and LISTEN/NOTIFY

## When to Use Triggers

- Enforce invariants close to the data
- Maintain derived tables or audit records

## When to Avoid

- Complex business logic that is hard to test
- Cross-module coupling via hidden side effects

## NOTIFY Guidance

- Use for lightweight event signaling.
- Ensure consumers handle retries and idempotency.
