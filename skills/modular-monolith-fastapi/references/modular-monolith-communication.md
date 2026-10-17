# Communication Patterns

## 1) Direct call (sync)

Use when:
	•	operation must succeed/fail immediately
	•	invariants are enforced synchronously

Rules:
	•	call other_module.public.* only
	•	keep call chains shallow (avoid 4+ modules deep)

## 2) Events (async / decoupled)

Use when:
	•	you can accept eventual consistency
	•	consumer modules are optional

Rules:
	•	define event DTOs (Pydantic/dataclass)
	•	publisher should not import consumers
	•	handlers must be idempotent

In-process event bus:
	•	good default for monolith
	•	easy to test
	•	minimal operational overhead

External broker:
	•	use only if required (throughput, cross-process, auditing, multiple consumers at scale)

## 3) Ports (interfaces)

Use when:
	•	you want the caller module to be stable even if implementation changes
	•	you want easy test doubles

Rule of thumb:
	•	define the port next to the caller
	•	bind implementation in composition root