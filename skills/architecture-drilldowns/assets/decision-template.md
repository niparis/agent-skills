# NNN: <the decision, as a claim not a topic>

## Status

Accepted.

<!-- One word, first: Proposed / Accepted / Superseded by NNN / Deprecated /
     Rejected. `check_docs.py` reads this line, and refuses to let a card cite a
     superseded record as if it were live. Never delete a superseded record —
     link forward to the one that replaced it. -->

## Context

What was true when this was decided, and what forced a decision. Constraints,
the measurement that started it, the thing that broke. A reader who disagrees
with the decision should still agree with this section.

Keep it to what bears on the choice. Background that does not constrain the
outcome belongs in the architecture pages, not here.

## Decision

The choice, stated so it can be checked against the code. Name the thing:
the threshold, the schema, the boundary, the library, the ordering.

## Alternatives considered

- **<the option>** — why not. Say what it would have cost, not that it was
  "less clean".
- **<the option>** — why not.

The alternative that was *nearly* chosen is the highest-value entry here. So is
one that was tried and removed: say what it shipped that was wrong, with the
example that killed it.

## Consequences

What this makes easy, what it makes hard, and what now has to be true forever.
State the follow-on obligations plainly — an invariant that some later stage
must uphold is exactly what a reader of that stage needs to find here.

Where the consequence is load-bearing, declare it as an `invariant` on the
relevant node in `architecture.json` too, so it appears on the page that has to
honour it.
