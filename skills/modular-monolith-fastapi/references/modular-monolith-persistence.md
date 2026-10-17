# Persistence and Ownership Rules

Table ownership
	•	Each table is owned by exactly one module.
	•	Use naming conventions:
	•	users_*, billing_*, etc. or separate schemas

Cross-module reads

Allowed:
	•	via module API
	•	via published read model (explicit, documented, ideally read-only)

Disallowed:
	•	ad-hoc joins across modules from outside the owner module
	•	foreign code touching another module’s ORM entities

Migrations
	•	Prefer per-module migrations folders or strict naming conventions.
	•	CI should fail if a module modifies tables it doesn’t own.
