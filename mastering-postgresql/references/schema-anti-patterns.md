# Schema Anti-Patterns to Avoid

## EAV
Why it fails:
- weak constraints
- hard indexing
- hard query readability and evolution

Alternatives:
- explicit columns for important fields
- JSONB for optional/sparse metadata
- separate tables for extensible subdomains

## Multi-value strings
- comma-separated lists are not queryable safely
- no constraints and poor index usage

Alternatives:
- join tables
- arrays (only when semantics fit)
- JSONB arrays for document payloads
