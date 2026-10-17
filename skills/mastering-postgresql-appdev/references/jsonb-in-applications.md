# JSONB in Applications

## When to Use

- Sparse or highly variable attributes
- External payloads and metadata
- Event payload storage

## When to Avoid

- Core relational data with strict invariants
- Fields frequently queried and constrained

## Rules of Thumb

- Treat JSONB as a boundary, not a default.
- Add indexes for known query paths.
- Plan for migration to columns when fields become critical.
