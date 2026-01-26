---
name: mastering-postgresql-appdev
description: Use PostgreSQL as a first-class component of application architecture. Best practices for integrating SQL into codebases, structuring DB-facing APIs, and modeling data for maintainable application development (advanced SQL users).
license: MIT
metadata:
  author: niparis
  version: "1.0.0"
---

# Mastering PostgreSQL for Application Development

This skill is for developers who already know SQL well but struggle to use it effectively in application development. The focus is maintainability, correctness, and architectural leverage—treating PostgreSQL as a data access *service* and SQL as production code.

## When to Use This Skill

- Designing a backend where PostgreSQL is more than “storage”
- Refactoring ORM-heavy or chatty database access into fewer, stronger queries
- Establishing team conventions for SQL readability, review, testing, and deployment
- Designing schemas (normalization/denormalization) for long-term maintainability
- Creating stable database-facing APIs (views/functions) for application code

## Core Principles

### 1) PostgreSQL is a Stateful Data Access Service
Treat PostgreSQL as a service that:
- Hosts the authoritative dataset
- Enforces integrity (constraints)
- Executes data-centric business logic safely and close to the data
- Provides an API surface (SQL, views, functions) to the application

**Architectural consequence:** application code becomes thinner: orchestrate inputs/outputs; let SQL compute result sets and enforce invariants.

### 2) SQL is Code
Apply the same engineering rigor as application code:
- Formatting and readability standards
- Version control
- Code review
- Automated tests
- Repeatable deployments

### 3) Prefer Set-Based Logic Over Row-by-Row Logic
If you can express logic as:
- joins
- aggregates
- window functions
- CTEs
- set-returning functions
…then you usually get simpler, faster, and more correct code than loops in application code.

(Deep dive: `references/sql-idioms-ctes-window-functions.md`)

### 4) Correctness First, Performance Second
Use the database to guarantee correctness:
- constraints beat “application validation”
- transactions beat ad-hoc multi-query sequences
- a single statement is often safer than multiple queries with implicit assumptions

Performance work (indexing, EXPLAIN, plans) is important but is a separate skill.
(Deep dive: `references/indexing-and-query-performance.md`)

---

## Architecture Patterns for Application SQL

### Pattern A: Database API Layer (Views + Functions)
Create a deliberate boundary between application code and raw tables.

**Use views for read APIs**
- `reporting_*` views: stable read models
- `app_*` views: canonical query shapes used by the app
- Keep views small and composable when possible

**Use functions for write / multi-step APIs**
- Encapsulate multi-step state changes into a single callable operation
- Let the function be the “unit of work” for the app

**Benefits**
- Centralizes invariants and logic near data
- Easier refactors: change tables behind stable API
- Easier testing: test view/function behavior with fixtures

**Guideline**
- A function should be:
  - explicit inputs/outputs
  - stable semantics
  - transaction-friendly
  - deterministic unless it’s intentionally stateful

(Deep dive: `references/db-api-views-functions.md`)

### Pattern B: Thin Application, Strong Queries
Prefer:
- one query returning the exact result set shape needed
over:
- N queries + client-side stitching + hydration

**Symptoms you should refactor**
- “N+1” behavior
- repeated queries in loops
- SELECT * everywhere
- building big in-memory structures only to filter/aggregate later

**Refactor approach**
1. Define the exact output shape (columns, types, ordering)
2. Build a query that returns it directly
3. Wrap it as a view or a named SQL file (depending on your deployment style)
4. Add tests for edge cases

### Pattern C: Database-Enforced Invariants
Use schema features to prevent bad states.

**Prefer database constraints for:**
- uniqueness
- referential integrity
- required fields
- domain checks (ranges, enums, format constraints)
- exclusion constraints for “no overlap” rules (when appropriate)

**Avoid relying solely on application code for invariants.**
Apps are replicated, concurrency exists, and multiple code paths appear over time.

(Deep dive: `references/constraints-and-invariants.md`)

---

## Data Modeling Best Practices

### 1) Start Normalized, Denormalize Deliberately
Start with a normalized model to preserve integrity and reduce anomalies.
Denormalize only when:
- you have a measured bottleneck
- you can state exactly what query or workflow benefits
- you have a maintenance plan for duplicated data

**Denormalization checklist**
- What invariant becomes harder to enforce?
- How will duplicated data remain consistent?
- How will you backfill/repair if drift happens?
- What tests catch drift?

(Deep dive: `references/normalization-and-denormalization.md`)

### 2) Avoid Common Modeling Anti-Patterns

**Avoid EAV (Entity-Attribute-Value) for core domain data**
- Hard to constrain
- Hard to index meaningfully
- Hard to query and evolve safely

If you need flexible attributes, prefer:
- explicit columns for important attributes
- JSONB for truly flexible/rare attributes, with a plan for indexing and validation

**Avoid multi-value strings**
Do not store lists as comma-separated strings or ad-hoc encodings.
Prefer:
- join tables (default)
- arrays (when semantics truly fit)
- JSONB arrays (when payload is inherently document-like)

(Deep dive: `references/schema-anti-patterns.md`)

### 3) Use PostgreSQL Types Intentionally
Use native types to reduce parsing/bugs and simplify code.

**General rule**
- If Postgres has a type that matches your domain, use it.
- Avoid storing structured data in text unless you must.

Examples:
- `timestamptz` for real timestamps
- `numeric` for money-like values (or a strict integer of minor units if your domain prefers it)
- `uuid` for identifiers
- `jsonb` for semi-structured attributes
- arrays for compact list semantics

(Deep dive: `references/postgresql-types-and-extensions.md`)

### 4) JSONB is a Tool, Not a Default
Use JSONB when:
- attributes are sparse or vary across records
- you need to store event payloads, external documents, or flexible metadata
- you can tolerate weaker relational guarantees on that subset of data

Avoid JSONB when:
- fields are frequently queried and need constraints
- you need strong relational integrity and joins across those attributes

Plan for:
- migrations from JSONB to columns when fields become important
- indexing strategy for JSONB query patterns (in the performance skill)

(Deep dive: `references/jsonb-in-applications.md`)

---

## Query Design Best Practices

### 1) Make Queries Return the Final Shape
Design SQL so the result set is directly usable by application code:
- correct filtering
- correct ordering
- correct aggregation
- correct pagination shape
- correct data types (cast intentionally)

Avoid “fetch raw then fix in code” patterns.

### 2) Prefer Explicit Column Lists
Avoid `SELECT *` in application queries.
- prevents accidental payload growth
- avoids breaking changes when schema evolves
- improves readability and review

### 3) Use CTEs and Window Functions to Express Intent
- Use CTEs for readability and staged transformations
- Use window functions for analytics-like computations without client-side loops

Keep CTE usage intentional:
- don’t create long chains without documenting the pipeline steps

(Deep dive: `references/sql-idioms-ctes-window-functions.md`)

### 4) Safe Parameters Always
Never build query strings by concatenating user inputs.
Always use parameter binding offered by your driver.

### 5) Pagination Rules of Thumb
Prefer keyset pagination where possible (stable ordering + “seek” predicate).
Offset-based pagination is acceptable for small datasets or admin tooling but becomes costly and inconsistent under changes.

(Deep dive: `references/pagination-and-result-shaping.md`)

---

## Workflow: How to Integrate SQL Into a Codebase

### Recommended Repository Layout

db/
migrations/
views/
functions/
seeds/
tests/
sql/
queries/
reporting/
app/
…

### Conventions
- One query per file for complex queries
- Header comment with:
  - purpose
  - inputs
  - output columns and semantics
  - stability expectations

Example header:
```sql
/*
Purpose: Fetch customer dashboard summary
Inputs: $1 customer_id (uuid)
Output: customer_id, status, balance_minor_units, last_activity_at
Notes: stable shape; add columns only with versioning plan
*/

Deployment
	•	Schema changes are migrations, always
	•	Views/functions are deployed via migrations too
	•	Use transactional migrations where possible

Testing

At minimum:
	•	fixture setup
	•	run the query/function
	•	assert outputs for edge cases

(Deep dive: references/sql-workflow-versioning-testing.md)

⸻

What This Skill Intentionally Does NOT Cover

These are important, but belong in specialized skills:
	•	Concurrency, isolation levels, locking, race conditions
See: references/concurrency-and-transactions.md
	•	Indexing strategy, EXPLAIN, query plans, performance tuning
See: references/indexing-and-query-performance.md
	•	Triggers and LISTEN/NOTIFY design trade-offs
See: references/triggers-and-notify.md

⸻

Quick Checklist for PR Review (SQL + DB Changes)

Schema
	•	Constraints enforce key invariants
	•	No EAV or multi-value strings added as “shortcuts”
	•	Types are appropriate (avoid text-by-default)

Queries
	•	No SELECT *
	•	Query returns the final shape needed by callers
	•	Uses parameters safely (no concatenation)
	•	CTEs/window functions used to reduce app-side loops
	•	Pagination approach is appropriate

Workflow
	•	Changes are in migrations
	•	Query/view/function has tests for edge cases
	•	Backfill/repair plan exists when denormalizing

End.

---


File: references/



File: references/normalization-and-denormalization.md

File: references/



File: references/



File: references/



File: references/



File: references/

# Concurrency and Transactions (Deep Dive)

Covers:
- isolation levels and anomalies
- transaction scoping in application code
- locking patterns and deadlocks
- safe multi-step writes
- idempotency and retries

(Kept separate from the main skill by design.)

File: references/indexing-and-query-performance.md

# Indexing and Query Performance (Deep Dive)

Covers:
- indexing strategy
- EXPLAIN / EXPLAIN ANALYZE
- query plan reading
- common slow-query patterns
- designing indexes for query shapes
- JSONB/array indexing considerations

(Kept separate from the main skill by design.)

File: references/triggers-and-notify.md

# Triggers and LISTEN/NOTIFY (Deep Dive)

Covers:
- when triggers are appropriate vs dangerous
- trigger testing and debugging
- using NOTIFY for event signaling
- reliability constraints and recovery patterns

(Kept separate from the main skill by design.)

