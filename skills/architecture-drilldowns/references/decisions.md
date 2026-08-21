# Decision records — where the *why* lives

Contents:
- [Why this level exists](#why-this-level-exists)
- [Layout and the render step](#layout-and-the-render-step)
- [The link-don't-restate rule](#the-link-dont-restate-rule)
- [Writing one](#writing-one)
- [Status, and never deleting](#status-and-never-deleting)
- [Retro-writing records for an existing system](#retro-writing-records-for-an-existing-system)

Template: [assets/decision-template.md](../assets/decision-template.md).

## Why this level exists

This skill already prizes the *why* — [mining incidents](level-2-drilldown.md#mining-incidents--the-highest-value-content)
is where the highest-value content on a drill-down comes from. But mining is retrospective
archaeology: it recovers rationale from comments and commit messages *years after* the
decision, and only what someone happened to write down survives.

A decision record is the same content captured when it is cheap — at the moment of
deciding, when the alternatives are still in someone's head. It is the difference between
reconstructing why a threshold is 2.5 and reading the note that says so.

The second reason is structural. Without a home for rationale, it goes into prose inside a
drill-down, where it drifts silently: the code changes, the page gets updated, and the
paragraph explaining a constraint that no longer applies stays exactly where it was.

## Layout and the render step

```
<docs-dir>/
├── architecture.json
├── <pipeline>-map.html
├── stage-NN-<name>.html
└── decisions/
    ├── 001-<slug>.md          ← canonical, hand-written, the source of truth
    ├── 002-<slug>.md
    └── pages/
        ├── 001-<slug>.html    ← generated, never hand-edited
        └── 002-<slug>.html
```

```bash
scripts/render_decisions.py <docs-dir>
```

The Markdown is the editable record; the pages are build output. Both are committed.

**Why render at all**, given that Markdown is perfectly readable? Because these pages are
read off disk over `file://`, and a browser handed a `.md` link downloads it or shows raw
source. A card cannot usefully link a decision unless the decision has an HTML face.

The renderer's output is deterministic — no timestamps, no filesystem-dependent ordering —
which is what lets `check_docs.py` **re-render and compare byte-for-byte**. That check is
the entire reason to generate rather than hand-write: a generated page provably cannot
rot. It also detects the two adjacent failures: a page whose record was deleted (orphan),
and a record that was never rendered.

After changing any record, re-render. The checker will tell you if you forget.

## The link-don't-restate rule

**A page links a decision. It does not restate it.**

Same strictness as the map/drill-down boundary, and for the same reason: duplicated prose
diverges, and the copy that is wrong is always the one being read. A card gets a chip:

```html
<div class="decs">
  <a class="dec" href="decisions/pages/002-cluster-sentinel.html">◇ 002 — the cluster sentinel</a>
</div>
```

What belongs on the page instead of the rationale is the **consequence** — stated as an
invariant, in the place that has to honour it. The record explains why `cluster` carries a
sentinel; the stage's invariant says *this stage must set it*. A reader of stage 5 needs
the obligation, not the debate.

Declare the citation in the manifest too (`"adr": ["002"]`), which is what lets the
checker verify the record exists, is not superseded, and is rendered.

## Writing one

Five sections, in this order: **Status · Context · Decision · Alternatives considered ·
Consequences.** The full template with per-section guidance is in
[assets/decision-template.md](../assets/decision-template.md).

The two sections that carry the value:

**Alternatives considered.** The option that was *nearly* chosen is the highest-value
entry in the whole record — it is what a future reader will propose, and this is where
they find out it was already weighed. Say what it would have cost, not that it was "less
clean". An approach that was tried and removed is worth more still: name what it shipped
that was wrong, with the example that killed it.

**Consequences.** What this makes easy, what it makes hard, and what now has to be true
forever. Where a consequence is load-bearing, also declare it as an `invariant` on the
stage that must uphold it — the record is where it is justified, the stage is where it is
enforced, and a reader of the stage should not have to find the record to know the rule.

Two rules carried over from the rest of the skill:

- **Never round a measurement.** "Only 21% of responses arrived in the specified shape" is
  the reason the decision went the way it did. "Often malformed" is not.
- **If a sentence is derivable from the code, cut it.** A record that describes what the
  code does is a worse version of the code. Spend the space on what the code cannot say.

## Status, and never deleting

One word under `## Status`: `Proposed`, `Accepted`, `Superseded by NNN`, `Deprecated`, or
`Rejected`. The renderer reads it into a badge and the checker reads it too.

**Never delete a superseded record.** Link forward to the one that replaced it. The
superseded record is the only place the old reasoning survives, and the question it answers
— "why did we ever do it that way?" — comes up precisely when someone is about to do it
that way again.

But do **stop citing it from cards.** The checker errors when a card cites a superseded
record as if it were live, because a stale citation is worse than no citation: it presents
overturned reasoning as current.

A `Rejected` record is worth writing for an option that keeps being proposed. It costs ten
minutes once and settles the argument permanently.

## Retro-writing records for an existing system

For a system that already exists, the rationale is not lost — it is scattered. Harvest in
this order, because it runs cheapest-first:

1. **Long code comments.** Length signals a hard-won lesson. A comment explaining why
   something is *not* done the obvious way is a decision record waiting to be extracted.
2. **The existing drill-downs.** Rationale already mined into prose should move into a
   record, with the page reduced to a chip plus the invariant.
3. **Commit messages** on the commits that introduced the constant, the threshold, or the
   boundary. `git log -S` on the value finds them.
4. **Design and sprint docs.** Highest yield per word, but treat them as claims about
   intent rather than fact — they record what was planned, and the code records what
   shipped. Where they disagree, the code wins and the disagreement is itself worth a note.

Write records for the decisions that are **load-bearing and non-obvious** — a boundary, a
schema, a calibrated threshold, a technology choice with a real alternative. Five to ten
good records beat thirty that restate the obvious. A record nobody would ever question is
a record nobody will ever read.
