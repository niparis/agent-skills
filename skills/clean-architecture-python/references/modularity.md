## Modularity for Large Python Clean Architecture Codebases

### Goal
Scale a single deployment (modular monolith) with **strong boundaries** so teams can move independently.

### Start: Layered + Feature Folders
- Keep `domain/application/infrastructure` top-level
- Create feature folders inside each layer as needed

### Scale: Vertical Slices (Modules)
A module is a mini-application:
- `modules/billing/domain/...`
- `modules/billing/application/...`
- `modules/billing/infrastructure/...`

Rules:
- Modules expose a small public API (facade) in application layer:
  - `modules/billing/api.py` (functions/classes)
- Cross-module calls use:
  - module API, or
  - events, or
  - ports (interfaces), not internal imports

### Boundaries Enforcement
- Lint rules / import boundaries (recommended)
- Keep shared code in:
  - `shared_kernel/` only if stable and small
  - otherwise duplicate small utilities and refactor later

### Facades: Use Carefully
Use a module facade if:
- You want one entry point for a module
- The methods are cohesive and stable

Avoid:
- A single facade for the entire system
- Facades that become “god objects”

### Signals You Need Module Split
- Frequent merge conflicts across unrelated features
- People can’t reason about ownership
- Shared models become “everything types”
- Testing becomes slow due to coupling

### Integration Styles
- In-process calls (module API)
- Domain events (preferred for loose coupling)
- Async messaging (only when operationally justified)