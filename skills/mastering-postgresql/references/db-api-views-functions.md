# Database API: Views and Functions

## Views (Read APIs)
- stable result shapes
- clear naming and contracts
- avoid hidden expensive logic without tests

## Functions (Write or Multi-Step APIs)
- treat as service endpoints
- inputs are parameters, outputs are explicit
- prefer SQL-language functions when possible
- use procedural logic only when orchestration is required

## Compatibility
- version your function/view contracts when you must change semantics
- prefer additive changes over breaking changes