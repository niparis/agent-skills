## Testing Strategies for Clean Architecture (Python)

### Goals
- Fast feedback
- High confidence without over-testing infrastructure
- Clear separation: domain correctness vs integration correctness

### Test Levels

#### 1) Domain Unit Tests (Most)
Test:
- Entity methods and invariants
- Value object validation
- Domain services (pure)

Rules:
- No DB, no network, no framework
- Pure python objects only
- Assert on behavior and invariants

#### 2) Application Unit Tests (Many)
Test:
- Use cases orchestration
- Error mapping and result types
- Transaction semantics (via fake UoW)

Technique:
- Use fake ports (in-memory repo, stub email sender)
- Validate correct calls and order of operations

#### 3) Integration Tests (Few but Real)
Test:
- Repository mappings (domain <-> storage)
- Transactions/UnitOfWork with real DB
- External API adapters (contract tests if possible)

Rules:
- Use dockerized DB
- Keep tests narrow and deterministic
- Avoid testing business invariants here (domain tests cover those)

#### 4) Thin API Tests (Selective)
Test:
- Controller translation (request -> input DTO)
- Response mapping (output DTO -> response)
- Wiring correctness (container config)

Keep these small:
- 1–2 tests per endpoint style, not exhaustive

### Common Anti-Patterns
- “Everything is an integration test”
- Controller tests asserting business rules
- Mocking ORM internals instead of using adapter tests

### Practical Toolkit
- Pytest fixtures for fakes and test containers
- Factory helpers for domain objects (not ORM factories)
- Use `freezegun` or a ClockPort for time-dependent logic