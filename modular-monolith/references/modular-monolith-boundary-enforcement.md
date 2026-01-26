Boundary Enforcement Techniques
# Import rules (recommended)

Goal: allow only modules.<name>.public to be imported cross-module.

Approaches:
	1.	Static checks in CI

	•	Use a dedicated import-linting tool or custom script.
	•	Enforce rules like:
	•	Allowed: app.modules.users.public
	•	Forbidden: app.modules.users.repo, app.modules.users.domain, etc.

	2.	Code review + conventions

	•	All cross-module calls must go through public.py.
	•	Any exception must be documented and time-boxed.

Dependency graph discipline
	•	Maintain a simple “module dependency map” (text file or diagram).
	•	Enforce acyclic dependencies.

Packaging trick (advanced)

Treat each module as a package (even inside a monorepo):
	•	module has its own pyproject.toml section or internal package metadata
	•	module declares which other module public APIs it depends on
This makes accidental imports fail earlier.

“Shared” code policy
	•	Allow only: primitives, error base types, logging wrappers, tracing, small helpers
	•	Disallow: domain logic, repositories, ORM models, business rules
If shared code becomes business-relevant: move it into a real module and expose via public API.