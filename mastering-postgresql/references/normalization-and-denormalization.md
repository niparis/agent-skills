
# Normalization and Denormalization (Practical)

## Default: Normalize
- Use join tables for many-to-many
- Avoid duplicated facts across tables
- Make invariants enforceable with constraints

## Denormalize Only When
- You have a measured bottleneck
- The read pattern dominates and can’t be fixed with query design
- You accept the maintenance cost

## Denormalization Techniques
- Cached aggregates (summary tables)
- Materialized views (with refresh strategy)
- Stored computed columns (via triggers) only with a drift-repair plan

## Drift Control
- Add tests to detect drift
- Provide periodic reconciliation jobs
- Keep source-of-truth tables authoritative
