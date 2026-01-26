# SQL Idioms: CTEs and Window Functions (App-Focused)

## When to Use
- You want to replace application loops with set-based computation
- You need “previous row”, ranking, running totals, partitions
- You need multi-stage transformations that remain readable

## CTE Guidance
Use CTEs to name pipeline stages:
- `raw` → `filtered` → `enriched` → `final`
Keep each stage small and purpose-driven.

Avoid:
- 10+ chained CTEs with no explanation
- reusing the same column name with changing semantics

## Window Function Patterns
- LAG/LEAD for “previous/next”
- ROW_NUMBER for stable ordering within partitions
- SUM(...) OVER (...) for running totals
- AVG(...) OVER (...) for moving averages

## App-Shaping Tips
- Prefer window functions over “fetch more rows then compute in code”
- Always define deterministic ORDER BY inside the window
- Partition by your business key (customer_id, product_id, etc.)

## Common Mistakes
- Missing ORDER BY inside OVER()
- Using window functions when a simple GROUP BY is enough
- Returning mixed granularities (row-level + aggregate) without clarity