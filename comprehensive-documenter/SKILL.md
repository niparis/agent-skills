---
name: comprehensive-documenter
description: Create accurate, maintainable documentation for an entire codebase. Use when asked to document a repo, explain architecture, or generate module/API docs from existing code.
---

# Comprehensive Documenter

## Intent (Why this exists)

Produce documentation that helps readers **decide and succeed**:

- Decide: what the system/module does, why it exists, when to use it, and what trade-offs it implies.
- Succeed: how to use it safely, what to expect, and how to verify behavior.

This skill prioritizes **truth over completeness**. If something cannot be verified, mark it as **Unknown / Unverified** and explain what evidence is missing.

Avoid per-file documentation. Prefer one document per module or folder so readers can understand a coherent unit of responsibility.

---

## Core Principles (Why-first)

1. **Reader outcomes first**
   - Lead with purpose, context, and consequences before steps.
   - Explain non-obvious decisions and trade-offs.

2. **Accuracy over completeness**
   - Never guess behavior.
   - Mark unverifiable claims explicitly.

3. **Evidence-aware**
   - State how each claim was derived (code inspection, tests, runtime observation, assumption).

4. **Layered explanation**
   - Architecture docs explain system intent and decisions.
   - Module/API docs explain boundaries, contracts, and usage.

5. **Maintainability**
   - Include verification metadata so updates are safe and incremental.

---

## When to Use

Use this skill when the user asks to:
- "Document this project / repo / codebase"
- "Write developer documentation / README"
- "Explain the architecture"
- "Generate API or module documentation"

---

## Documentation Standards (Global)

All generated documents must include, where applicable:
- **Last Verified:** date or commit hash
- **Evidence Sources:** how information was obtained
- **Unknown / Unverified:** section if any assumptions exist

## What every doc should answer

- What problem does this solve and for whom?
- When should it be used and when should it not?
- What decisions or constraints matter for success?
- How can a reader verify the behavior?

## Templates Reference

Use these templates to keep structure consistent:
- **Module Documentation** → `templates/standard.md`
- **Architecture Documentation** → `templates/architecture.md`
- **API Reference** → `templates/api.md`

Do not invent new sections unless explicitly requested. If a template changes, update this skill accordingly.
