# SQL Workflow: Versioning, Review, Testing, Deployment

## Versioning
- Put schema, views, functions in migrations
- Keep query files close to application code with stable contracts

## Review Standards
- Enforce formatting conventions
- Require explicit column lists
- Require “result shape contract” documentation for non-trivial queries
- Prefer query files over inline giant strings in code

## Testing Approaches
Minimal viable:
1) Load fixtures
2) Execute query/function
3) Assert exact rows/columns

Recommended:
- Dedicated test schema
- Transaction rollback per test
- Golden files for complex reporting outputs (with careful maintenance)

## Deployment
- Transactional migrations where possible
- Backward-compatible changes in multi-step deploys:
  - add new columns
  - backfill
  - switch reads/writes
  - drop old columns later