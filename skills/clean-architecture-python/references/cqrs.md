## CQRS in a Clean Architecture Codebase (Python)

### Goal
Separate **writes** (commands) from **reads** (queries) to simplify use cases and optimize read performance.

### Command Side (Writes)
Rules:
- Commands go through **Application use cases** and **Domain entities**.
- Use case returns:
  - either `None` + raises on failure, or
  - a small `CommandResult` (ids, status), not a full view model.
- Writes should not depend on read-model shape.

Patterns:
- `PlaceOrderUseCase.execute(InputDTO) -> CommandResult`
- Emit domain events after state changes (application/infrastructure publishes).

### Query Side (Reads)
Rules:
- Queries do not mutate state.
- Queries can bypass domain entities (read DTOs) for performance.
- Use a dedicated read repository or query service:
  - `OrderReadRepository.get_order_view(order_id) -> OrderViewDTO`

Read model options:
- Same database, separate tables/views
- Materialized views / denormalized read tables
- Search index for text-heavy queries

Guardrails:
- Keep read model strictly read-only in code review.
- Avoid ORM session reuse from command side to query side unless well understood.
- Don’t embed business invariants in queries (domain owns rules).

### When CQRS Pays Off
- High read/write asymmetry
- Complex UI/dashboard requirements
- Performance or scaling pressure on reads
- You need multiple read shapes per aggregate

### When Not to Use CQRS (Yet)
- CRUD-only with minimal read complexity
- Small codebase where extra moving parts add overhead

### Practical “Lite CQRS”
- Keep commands as normal use cases.
- Implement queries as simple functions/classes in `application/queries/`.
- Use explicit `ReadDTO` types.