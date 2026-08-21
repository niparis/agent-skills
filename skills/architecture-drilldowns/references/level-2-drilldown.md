# Level 2 — the drill-down

One page per stage. Answers: *what happens inside, in what order, which function does it, and why is it shaped this way?*

**Only for a stage that earns one.** A stage with one model call, no loop and no gate should
carry its boundary, invariants and decisions in the map card's
[`<details>` block](level-1-map.md#the-mid-level-details-instead-of-a-page) instead. A thin
drill-down costs more to maintain than it returns, and the checker reports drill-down
coverage rather than requiring it.

Contents:
- [Section contract](#section-contract)
- [What lands on disk: state the contract](#what-lands-on-disk-state-the-contract)
- [The `file · symbol` rule](#the-file--symbol-rule)
- [Mining incidents — the highest-value content](#mining-incidents--the-highest-value-content)
- [Writing the call chain](#writing-the-call-chain)
- [The failure-isolation ladder](#the-failure-isolation-ladder)
- [Which sections a given stage needs](#which-sections-a-given-stage-needs)

## Section contract

In this order. Required unless marked.

| # | Section | Notes |
|---|---|---|
| 1 | Breadcrumb | `← map / Stage NN — name` |
| 2 | `Inside <command>` + framing paragraph | Frame *why the stage is shaped this way*, not what it does. This is the drill-down's goal line — same rule as the map's `.goal`, one paragraph instead of two sentences |
| 3 | Legend | The same four tags, verbatim |
| 4 | Phase strip | **Only if non-linear.** A linear stage has the rail |
| 5 | At a glance | Fixed rows — see below |
| 6 | The idea worth holding onto | **Optional, high value.** The one load-bearing invariant |
| 7 | Failure isolation | **Required if >1 failure mode.** Goes *before* the call chain |
| 8 | The call chain | Numbered rail, one decision per step |
| 9 | Variant comparison | **Only if** the stage has tiers / modes / shapes with different rules |
| 10 | Enumerated failure vocabulary | Exit codes, or drop/skip reasons |
| 11 | What lands on disk | Include greyed rows for absent-but-expected keys. State the **contract** — see below |
| 12 | What this stage deliberately does not do | Bound the stage against wrong assumptions. Mirror the manifest's `not` |
| 13 | Decisions | `.dec` chips only. Link, never restate — see [decisions.md](decisions.md#the-link-dont-restate-rule) |
| 14 | Footer | Zoom-out link + siblings |

**At a glance** has a fixed row set so pages are comparable at a glance across stages:

Command · Skipped when · Model calls · Agent roles · Reads · Writes · Archived? · Idempotent?

Give **Model calls** as a count or a formula (`⌈items/10⌉ batches + 1 per item judged`), never "several". Say what makes it vary. For **Idempotent?** answer what a re-run actually does: skip, refuse, or redo — "refuses rather than overwrites" is a different contract from "skips when complete".

Split **Writes** into **Persists** and **Emits** where both apply, on the same terms as the
[map's chips](level-1-map.md#the-stage-card): a durable write is a different promise from a
payload handed onward.

## What lands on disk: state the contract

Section 11 is where a stage's output shape gets pinned down, and it is the section most
often written as a shrug — "writes the results". The next stage's correctness depends on
this shape, so name it: the required keys, the ones that are optional and until when, and
the invariant that no key list can express.

Then declare the same shape in the manifest's `contracts` block, which is what gets it
checked against real files. The two are not duplication: the table is prose a reader
understands, the manifest is a machine-checkable key list, and the manifest's `sample` glob
proves the table is still true. See [manifest.md](manifest.md#data-contracts).

The greyed rows earn their place here. *What this stage does not write, and what the
default is until someone does* is usually the most useful information on the page — it is
the difference between a reader concluding "the field is missing, something failed" and
"the field arrives at stage 7".

## The `file · symbol` rule

Every code reference is `file · symbol` in a `.ref` chip. **Never `file:line`.**

Line numbers rot silently and invisibly. A file edited between writing and publishing leaves every number confidently wrong, pointing at real but unrelated code — worse than no reference. A symbol name fails loudly: it either exists or `check_docs.py` catches it.

- `questions.py · build_blueprint`
- `tools/library.py · scan_books`
- `cli.py · import_ → write gate` — the arrow tail is a human annotation for a region inside a function that has no symbol of its own. The checker verifies the part before the arrow.

Use the bare basename when it is unambiguous in the repo; add a path when it is not.

**Verify before publishing, every time:**

```bash
scripts/check_docs.py <docs-dir> --source-root <repo-root>
```

Do this even when you just wrote the page. Files move under you.

## Mining incidents — the highest-value content

This is what makes a drill-down worth more than the source it describes.

The best content is **not** derivable from reading the functions. It is the recorded history of what went wrong, which lives in code comments, commit messages, and the docstrings explaining why a thing is *not* done the obvious way. Harvest:

- **Removed approaches and why.** A shape deleted because it "shipped nonsense" — with the concrete example that killed it — teaches more than three working shapes.
- **Measurements.** "Only 21% of responses arrived in the specified shape." "Containment passed 0 of 15." "A blanket threshold dropped 15 legitimate items." Numbers from real runs are irreplaceable; never round them into "often" or "many".
- **Calibration stories.** A threshold that is 2.5 for one case and 3.5 for another, because a blanket value was measured to be wrong.
- **Defensive coercion and the bug it prevents.** "The model returns `"0"` as a string, and an int/str comparison then counted a *correct* answer as a mis-key."
- **Named failure modes with a live example**, including the identifier of the case if the comment has it.

Grep the stage's source for `because`, `used to`, `REMOVED`, `live`, `measured`, `finding`, `why`, `NOT`, `never`. Read every long comment — length signals a hard-won lesson.

Rule: **if a sentence is derivable from the function signature, cut it.** Prose that restates code is pure cost. Spend the space on the why.

**Where the why is a decision rather than an incident, write a record and link it.** Mining
recovers rationale years later from whatever someone happened to write down; a
[decision record](decisions.md) captures it while the alternatives are still known. The
test for which applies: an *incident* is something that happened once and left a scar — a
shape that shipped nonsense, a threshold that had to be recalibrated. A *decision* is a
choice with a live alternative that a future reader will propose again. Incidents belong in
the call-chain prose; decisions belong in a record, cited by a `.dec` chip.

## Writing the call chain

One rail step = **one decision**, not one function. A step may cite several symbols; a large function may split across several steps.

Each step: a title with its classification tags, prose on what is decided and what happens when it fails, the `.refs` chips, and — for a model call — a `.panel` with the prompt contract and an `.io` block for in/out.

**A step's first sentence says what the step is for; the mechanism follows.** Same discipline as the map's [goal line](level-1-map.md#goal-first-mechanism-second), scaled down — one clause is usually enough, because the step title and the stage's framing paragraph have already done most of the work. Where a step exists *only* because of a past failure, that is the purpose: lead with it. A step whose prose opens on a regex, a threshold, or a function name has buried the reason it is on the page.

For the **prompt contract**, quote the *rules*, not the prompt's prose. Turn each rule into a list item with the field name in `<b>`. Flag any rule that exists because of a past failure — "publisher only from the copyright page, never from a PDF producer string" is a rule with a story.

For a stage with structured model output, say what the **output type** buys: a typed schema with extra fields forbidden means malformed output is retried with the error rather than accepted and cleaned up. Note what the schema deliberately *omits* and why.

## The failure-isolation ladder

For any stage with more than one failure mode, this is the most useful section on the page — and it belongs *before* the call chain, because it is the frame that makes the detail legible.

Two columns: what fails, how far the damage travels. Order by blast radius, smallest first, fatal last with `.rung.fatal`.

Derive it by reading every `try`/`except`, every `return None`, and every `raise` in the stage, then asking of each: *what still ships when this fires?* A well-built stage has a deliberate ladder — one item, one batch, one branch, one whole tier — with exactly one rung that stops the run. Say which, and why that one is not survivable when the others are.

If a stage has exactly one failure mode, skip the section and state it in the relevant call-chain step instead.

## Which sections a given stage needs

Stages vary enormously. Three rough shapes:

**Command-shaped** (a setup or one-shot verb: import, split, deploy). Linear, so no phase strip. Failure vocabulary renders as **exit codes**. Usually one model call or none, so the ladder may collapse to a single fallback rung — state it in the call chain instead. Strong candidates for a "what lands in the config file" table with greyed absent-key rows.

**Loop-shaped** (per-unit work: extract, per-section passes). Add the per-unit budget (retries, supplements) prominently. The ladder matters: per-unit failure vs whole-run failure. A variant table is usually unnecessary.

**Multi-phase** (author + verify + judge + assemble). Needs everything: phase strip, ladder, variant table, enumerated drop reasons. Expect the longest page. Lead with the load-bearing invariant — without it the phases look arbitrary.

Do not force a stage into sections it does not need. Delete unused blocks from the template rather than filling them with thin content.
