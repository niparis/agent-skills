---
name: docs-review
description: Review documentation changes for compliance with the Metabase writing style guide. Use when reviewing pull requests, files, or diffs containing documentation markdown files.
---

# Documentation Review Skill

## Review intent

Focus on whether the doc helps a reader decide and succeed. Prioritize the why (purpose, context, consequences) before the how (steps and mechanics). Only flag issues that materially improve comprehension, trust, or decision-making.

## Metabase style summary (short)

- Use plain, direct language.
- Prefer "people" or "companies" over "users" when possible.
- Avoid marketing fluff and "just/easy/simple" qualifiers.
- Show value with specifics instead of hype.
- Use descriptive links (avoid "here").

## Review process

1. Read once for intent and audience.
2. Map what the reader needs to know: goal, when to use, prerequisites, steps, success criteria.
3. Identify gaps in purpose or decision guidance before editing wording.
4. Flag only issues that improve reader outcomes.
5. Number every issue sequentially starting at Issue 1.

## What to prioritize (why-first)

**Purpose and outcomes**
- The doc doesn’t state what problem it solves or the expected outcome.
- The reader cannot tell when to use this process or when not to.

**Decision guidance**
- No tradeoffs, prerequisites, or constraints where they affect success.
- Missing success criteria or "what good looks like".

**Step rationale**
- Non-obvious steps lack a reason or risk explanation.
- Instructions are pure mechanics with no context.

**Structure and clarity**
- Key information is buried or headings don’t answer reader questions.
- Verbose text that doesn’t change meaning or reduce risk.

**Tone and trust**
- Corporate language, hype, or claims without evidence.
- "Users" when "people/companies" fits better.

**Links and formatting**
- "Click here" links or links inside headings.
- Inconsistent lists or unclear ordering.

## Feedback format

Every issue must be numbered sequentially starting from Issue 1.

### Local review mode

```markdown
## Issues

**Issue 1: [Brief title]**
Line X: Description of the issue
Impact: Why this matters for the reader
Suggestion: Concrete fix
```

### PR review mode

If reviewing a GitHub PR, add each issue as a review comment using pending review tools when available. Start each comment with `**Issue N: [Brief title]**`, include Impact and Suggestion, and submit one cohesive review.

## Final check

1. Remove issues that would not materially improve the doc.
2. Verify sequential numbering (Issue 1, Issue 2, ...).
3. Ensure each issue explains reader impact.
