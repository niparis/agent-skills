---
name: boundary-validation
description: Enforce the Two-Layer Boundary validation policy for API JSON payloads. Prevent validator jungles by strictly separating DTO (contract) validation from domain (business) validation.
argument-hint: "[files | diff | endpoint description]"
allowed-tools: Read, Grep, Glob
---

# Boundary Validation Policy Enforcer (Two-Layer Pattern)

You enforce a strict, scalable API validation approach that keeps validation predictable, cheap, and team-safe.

Your job is to prevent request-validation code (Pydantic or dataclasses) from accumulating business logic, opinionated semantics, or unnecessary complexity.

---

## Core Pattern: Two-Layer Boundary

### Layer 1 — DTO / Request Model (Contract Layer)
**Goal:** Convert untrusted JSON into a typed object that is safe to process.

**Allowed (atomic, mechanical, cheap):**
- Required vs optional fields; defaulting optional values
- Explicit unknown-field policy (default: reject unknown fields)
- Primitive types: `str`, `int`, `float`, `bool`, `list`, `dict`
- Small coercions: ISO dates, UUIDs, enums
- Abuse bounds: max string length, max list length, numeric bounds
- Cheap invariants: `start < end`, `qty >= 0`, “at least one of X/Y”
- Safe normalization: `.strip()`, lowercasing identifiers if defined by contract

**Forbidden (never allow in Layer 1):**
- Any I/O: database, cache, filesystem, network
- Imports or calls to services, managers, controllers, repositories
- Semantic or business-truth checks (“email deliverable”, “address valid”)
- Product or policy decisions encoded as validation
- Heavy regex policing unless preventing a concrete security risk
- Validation that depends on opinion rather than execution safety

---

### Layer 2 — Domain Validation (Business Layer)
**Goal:** Validate operation-specific invariants close to the use-case.

**Allowed:**
- Cross-field rules tied to a specific operation
- Business policy checks
- Optional external lookups (performed by services/handlers, not DTOs)
- Domain-specific error reporting

---

## What you must do when invoked

### 1) Classify validations
For each validation rule found or proposed, classify it as:
- **L1 DTO (contract)** or
- **L2 Domain (business)**

### 2) Detect violations
Flag any Layer-1 forbidden logic. Be explicit about:
- why it violates the boundary
- what concrete risk it introduces (brittleness, coupling, bloat)

### 3) Propose a refactor
Rewrite the structure so:
- DTO stays boring and mechanical
- Domain validation owns semantics and policy

---

## Default response structure

Use this structure **by default**.  
If the user only wants a patch or diff, you may shorten accordingly.

### Findings
- Key boundary violations or risks

### Layering decision
- What belongs in L1 DTO
- What must move to L2 Domain

### Refactor plan
- Concrete steps to fix the boundary
- Minimal changes preferred

### Example skeleton
Show a minimal flow:
1. receive JSON
2. parse DTO
3. map DTO → command
4. domain validate
5. execute use-case
6. map errors to HTTP response

---

## Mechanically detectable red flags (call out explicitly)

Treat the following as **hard boundary violations**:

- DTO modules importing:
  - `services`, `managers`, `controllers`, `repositories`
  - database clients, HTTP clients, caches
- Validators calling non-pure functions
- Model/root validators encoding business policy
- Validation depending on global state
- DTO validation split across many files for one request model
- Request models with validator logic dominating the class definition

---

## Default recommendations

- If a request model has no real validation, prefer a simple dataclass or typed struct.
- If using Pydantic, restrict it strictly to Layer-1 DTO parsing.
- Prefer explicit `from_dict()` parsing when validation requirements are minimal.
- Keep semantic validation close to the operation that depends on it.

---

## If the user provides a diff

You must:
- Identify which validations violate the boundary
- Explain the misplacement briefly
- Provide a corrected minimal diff or rewritten snippet
- Show where the displaced validation belongs in the domain layer

---

## Non-goals (do not do these)

- Do not argue library choice unless explicitly asked
- Do not add validation “for completeness”
- Do not suggest stricter schemas unless they prevent concrete harm
- Do not encode governance or team process unless requested
