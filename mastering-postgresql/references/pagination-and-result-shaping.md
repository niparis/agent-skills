# Pagination and Result Shaping

## Keyset Pagination
Use when:
- large datasets
- stable ordering possible
Pattern:
- ORDER BY (created_at, id)
- WHERE (created_at, id) > ($cursor_created_at, $cursor_id)

## Offset Pagination
Use when:
- small datasets
- admin tooling
- accept potential inconsistency under concurrent writes

## Always Define Deterministic Order
If pagination exists, ORDER BY must be deterministic.