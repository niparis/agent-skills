# Tooling Baseline (Practical Defaults)

uv
	•	Use uv to create venv, sync deps, and run tools consistently.
	•	Keep tool versions pinned (ruff, pyright, pytest).

ruff
	•	Enable formatting and lint rules.
	•	Add import/order rules to keep modules consistent.
	•	Fail CI on lint.

pyright
	•	Use strict mode for module public APIs at minimum.
	•	Treat DTOs and public interfaces as “contracts”.

FastAPI + Pydantic
	•	Use Pydantic models for:
	•	request/response
	•	module DTOs
	•	Avoid “model reuse” across modules when it leaks ownership.