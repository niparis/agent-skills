---
name: comprehensive-documenter
description: Create documentation for the whole project.. Use when getting started on a new project
allowed-tools: Read, Grep, Bash, Glob
---

## Purpose

Generate accurate, maintainable, production-grade documentation for real codebases using standardized templates.

This skill prioritizes **truth over completeness**:  
if something cannot be verified, it is explicitly marked as such.

Do not create one documentation per code file, it's too exhaustive. Create one file for each python module (one folder). If a module contains a single file, combine it's documentation with the parent directory

---

## Core Principles

1. **Template-Driven**
   - Use predefined templates to ensure consistency and coverage.
   - Do not invent new sections unless explicitly requested.

2. **Accuracy First**
   - Never guess behavior.
   - If information cannot be derived from code or provided context, mark it as **Unknown / Unverified**.

3. **Evidence-Aware**
   - Clearly indicate how information was derived (e.g. code inspection, tests, assumptions).

4. **Layered Information**
   - Support deep understanding (Architecture, Design Decisions).
   - Allow precise lookup (Module & API documentation).

5. **Maintainability**
   - Include verification metadata.
   - Make documentation safe to update incrementally.

---

## When to Use

Use this skill when the user asks to:
- “Document this project / repo / codebase”
- “Write developer documentation / README”
- “Explain the architecture”
- “Generate API or module documentation”

---

## Documentation Standards (Global)

All generated documents must include, where applicable:
- **Last Verified:** date or commit hash
- **Evidence Sources:** how information was obtained
- **Unknown / Unverified:** section if any assumptions exist

## Templates Reference

This skill uses the following documentation templates:
- **Module Documentation** → `templates/stamndard.md`
- **Architecture Documentation** → `templates/architecture.md`
- **API Reference** → `templates/api.md`

These templates define the structure that this skill will populate. If any template changes, update this skill accordingly.    