---
name: mastering-postgresql-appdev
description: Use PostgreSQL as a first-class component of application architecture. Best practices for integrating SQL into codebases, structuring DB-facing APIs, and modeling data for maintainable application development (advanced SQL users).
---

# Mastering PostgreSQL for Application Development

Use PostgreSQL as an application-facing data service, not just storage.

## Quick Workflow

1. Model data with constraints that enforce invariants.
2. Design queries to return the final shape for callers.
3. Decide whether to expose views/functions as a stable DB API.
4. Version and test SQL like application code.
5. Choose normalization vs denormalization deliberately.

## Non-Negotiables

- SQL is production code: review, test, and version it.
- Prefer set-based logic over row-by-row loops.
- Use constraints for correctness; do not rely on app validation alone.
- Do not use `SELECT *` in application queries.

## Decision Guide

- Views + functions: use when you want a stable DB API layer.
- JSONB: use for sparse or external payloads, not core relational data.
- Keyset pagination: default for large datasets; offset only for admin tooling.

## Minimal SQL Header Template

```sql
/*
Purpose: Fetch customer dashboard summary
Inputs: $1 customer_id (uuid)
Output: customer_id, status, balance_minor_units, last_activity_at
Notes: stable shape; add columns only with versioning plan
*/
```

## Read These References When Needed

- DB API layer (views/functions): `references/db-api-views-functions.md`
- SQL idioms and CTEs: `references/sql-idioms-ctes-window-functions.md`
- Normalization and denormalization: `references/normalization-and-denormalization.md`
- Schema anti-patterns: `references/schema-anti-patterns.md`
- Postgres types and extensions: `references/postgresql-types-and-extensions.md`
- JSONB usage: `references/jsonb-in-applications.md`
- Pagination and result shaping: `references/pagination-and-result-shaping.md`
- SQL workflow and testing: `references/sql-workflow-versioning-testing.md`
- Concurrency and transactions: `references/concurrency-and-transactions.md`
- Indexing and query performance: `references/indexing-and-query-performance.md`
- Triggers and NOTIFY: `references/triggers-and-notify.md`
