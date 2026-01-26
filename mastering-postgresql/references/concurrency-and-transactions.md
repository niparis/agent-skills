# Concurrency and Transactions (Deep Dive)

When to Consult

Consult this deep dive when:
	•	You observe race conditions, duplicate rows, or inconsistent state under load.
	•	You are implementing multi-step writes that must be correct with concurrent users.
	•	You are unsure whether correctness belongs in application logic or database transactions.
	•	You need to reason about retries, idempotency, or safe failure handling.
	•	You are seeing deadlocks or blocking and don’t understand why.

## What This Deep Dive Covers

This document explains how PostgreSQL enforces correctness under concurrency and how application code must align with it.

You will learn:
	•	How transactions, isolation levels, and row-level locks actually behave in PostgreSQL.
	•	Which anomalies can occur at each isolation level and which ones PostgreSQL prevents by default.
	•	How to structure application workflows so correctness is guaranteed by the database, not by timing assumptions.
	•	How to design idempotent writes and safe retries.
	•	How to reason about and debug deadlocks and lock contention.

Outcome: you can design write paths that remain correct under concurrency, not just in tests.