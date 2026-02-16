# Subscriptions and Checkpoints

## Subscription Rules

- Read globally by `global_position`.
- Store a durable checkpoint per subscriber.
- Handle backpressure with batching and retries.

## Minimal Flow

1. Load checkpoint for subscription.
2. Read events from last position in batches.
3. Process events in order.
4. Persist checkpoint after successful batch.

## Failure Handling

- If handler fails, do not advance checkpoint.
- Use exponential backoff or retry queues.
- Keep handlers idempotent.
