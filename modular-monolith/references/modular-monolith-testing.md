# Testing Strategy by Module

Module tests
	•	import only module.public
	•	stub infra via fake repos/adapters
	•	verify invariants and core use-cases

Contract tests
	•	validate DTO schemas (Pydantic models) match expectations
	•	pin versions of DTOs if needed

Integration tests (FastAPI)
	•	TestClient / async client
	•	cover critical multi-module flows
	•	include DB migrations + transaction rollback strategy

Anti-patterns
	•	tests importing other modules’ internals
	•	“unit tests” that actually require the whole app to run for simple logic