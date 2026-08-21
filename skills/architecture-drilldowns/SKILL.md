---
name: architecture-drilldowns
description: Create, extend, or audit layered architecture documentation as self-contained HTML plus a checkable manifest — a system-context page, a component map of what owns what and the channels between them, a process map of what actually runs versus what is only linked into something that runs, a zoom-out map of a pipeline's stages, per-stage drill-downs covering the call chain, prompt contracts, gates and failure isolation, an index that routes between them, and decision records for the why. Use when asked to document a pipeline or system architecture, map a data flow, draw a system or component diagram, show how the parts of a system relate, say which component owns a responsibility, say whether something is a process or a library or a table, show the process tree or what crosses a process boundary, add a deeper page for one stage, record an architecture decision or ADR, declare data contracts between stages, make architecture docs clickable or navigable, check whether an existing architecture doc still matches the code, or fix drift between docs and implementation. Also use when asked to document what a multi-step or agentic pipeline actually does, stage by stage.
---

# Architecture drill-downs

Layered documentation for a system, as plain HTML read straight off disk — no build step,
no server — plus a manifest that makes drift from the code fail a check.

| Level | Artifact | Answers | Reference |
|---|---|---|---|
| 0 | `system-map.html` — **only if >1 pipeline or real externals** | What is this system, what is outside it | [level-0-system.md](references/level-0-system.md) |
| 1 | `component-map.html` — **only if >1 long-lived actor** | Which components exist, what each owns, what travels between them | [level-1-components.md](references/level-1-components.md) |
| 1 | `process-map.html` — **only if >1 process kind** | What has a PID, what is only linked into something that does, what crosses a boundary | [level-1-processes.md](references/level-1-processes.md) |
| 1 | `<pipeline>-map.html` — one page | What are the stages, in what order, what does each write | [level-1-map.md](references/level-1-map.md) |
| 2 | `stage-NN-<name>.html` — one per stage that earns one | What happens inside, and why is it shaped this way | [level-2-drilldown.md](references/level-2-drilldown.md) |
| — | `index.html` — **once there are 3+ pages** | Which page answers which question | [level-0-system.md](references/level-0-system.md#the-index-page) |
| — | `decisions/NNN-<slug>.md` | Why this, and not the obvious alternative | [decisions.md](references/decisions.md) |
| — | `architecture.json` | The machine-readable index that makes the rest checkable | [manifest.md](references/manifest.md) |

The level-1 pages are the same system on different axes: the pipeline map reads **along**
(what happens next), the component map reads **across** (who owns this), the process map
reads **down** (what actually runs). None substitutes for another, and a system with one
long-lived process only needs the first.

Visual grammar, CSS blocks, clickable-card and view-filter mechanics:
[ui-kit.md](references/ui-kit.md).

## Two rules that govern everything

**1. Strict level boundaries.** The map says *what and in what order*; a drill-down says
*how and why*; a decision record says *why this and not the alternative*. Never explain
internals on the map, never restate the map's order on a drill-down, never restate a
decision's rationale on either.

**2. Nothing is declared twice.** The HTML owns the narrative — purpose lines, prose,
reads/persists/emits. The manifest owns identity, contracts, invariants, decisions and
views. There are no reads/writes in the manifest and no `purpose` field on a stage,
because both already have a home. Duplication always diverges, and the copy being read is
always the wrong one.

On every level, **every stage leads with its goal** — one or two sentences on what it is
for and why the system needs it, before a word about how it works. Mechanism-first cards
are the default failure mode of this whole skill, because mechanism is what you have just
read in the source and purpose is written down nowhere. See
[goal first, mechanism second](references/level-1-map.md#goal-first-mechanism-second).

## Workflow

### 1. Read the code, never the existing docs

Derive every claim from source. Existing docs are the thing under audit, not the input.

Find the authoritative stage list — an enum, a constant, a registry, the orchestrator's
loop — and use it verbatim. That symbol becomes `stage_source` in the manifest, which is
what turns "the docs are right today" into a check.

**Exception, and declare it:** if the system does not exist yet, there is no code to read
and the document *is* the source. Set `"status": "proposed"` so the code and data checks
are skipped rather than failing on absence. See
[status](references/manifest.md#status--as-built-or-as-designed).

### 2. Write the manifest first

Before any page. It forces the questions that produce a good map — what is the real stage
list, which stages are outside the run, what does each artifact actually contain — and it
makes everything after it verifiable. Start from
[assets/architecture.json](assets/architecture.json) and run the checker on it alone; it
will tell you where the stage list disagrees with the code before you have written a word
of prose.

### 3. If auditing, produce the drift list before editing

When the task is "check this doc is still accurate", audit and report first, then fix.
Run the checker to get the mechanical drift, then read for the rest. Categories and order
in [level-1-map.md](references/level-1-map.md#drift-audit-updating-an-existing-map).

The misses that matter most are **absent sections, not wrong sentences** — a whole mode,
tier, or output format the doc has never heard of. Look for branches on config the doc
never mentions.

Distinguish "the doc is wrong" from "the code has a bug". Both turn up. Document what the
code *does*; report suspected bugs separately rather than encoding either the bug or the
intent as if it were behaviour.

### 4. Build the map, then drill down — simplest and hardest first

**Do not write drill-downs in pipeline order, and do not derive a template from the first
one.**

The simplest stage produces a template that fits nothing else — one model call, no loop,
no gate, no archive. Write the simplest stage *and* the most complex one, then generalize
from both ends. A template validated against the extremes holds for everything between;
one fitted to the easy case has to be fought on every hard page.

If a convention is wanted before the pages exist, write only the invariants already known
to be safe and mark it provisional. Conventions are expensive to unlearn — once written
they get followed, including where wrong.

**Most stages should not get a drill-down.** A stage that does not justify a whole page
still owes the reader its boundary, its invariants and its decisions — put those in the
card's `<details class="more">` block. Coverage is reported by the checker, not required.

### 4b. Map the components when ownership is a question the map cannot answer

A supervisor and a worker, a daemon and the jobs it starts, two writers to one store, a
backstop that must not move: none of that is a step, so none of it is visible on a
stage-ordered page. That is when to add
[the component map](references/level-1-components.md).

Do not derive it from the stage list. Derive it from what owns a process, a store, or an
authority — one component usually spans several stages, and a stage is sometimes run by
two components.

Writing it is also an audit. Forcing every responsibility to have one owner and every
channel two ends surfaces contradictions that reading the spec does not: a relay that
requires a capability its named component does not hold, an atomic write that spans two
writers. **Report those; do not quietly resolve them on the page.**

### 4c. Map the processes when a reader cannot tell what runs

The signal is a person asking several questions in a row that all have one root: *is A the
same as B, is C just a table, is D part of E.* Those are altitude questions, and more prose
never answers them. [The process map](references/level-1-processes.md) does, because
**nesting means "code in this process"** and a box either has a PID or it does not.

Build it before writing code for a system that does not exist yet. It is cheapest then and
it is the pass that finds a missing process, a component that is really two, and a component
that is really a table.

### 5. Cite `file · symbol`, never `file:line`

Line numbers rot silently: a file edited between writing and publishing leaves every
number confidently wrong, pointing at real but unrelated code. A symbol name either exists
or fails a check. Form and details in
[level-2-drilldown.md](references/level-2-drilldown.md#the-file--symbol-rule).

### 6. Use three flow verbs, not two

**reads** — existing durable data or supplied input. **persists** — a durable write that
outlives the run. **emits** — a payload handed to the next stage that nobody stores.

Collapsing the last two into "writes" makes a handoff look like a stored artifact, and
readers then go looking on disk for something that was never there. Only `persists` is
expected to appear in the data directory, and the checker relies on that distinction.

### 7. Mine the comments for incidents, and record decisions as you go

The highest-value content is not derivable from reading the functions: removed approaches
and the case that killed them, measurements from real runs, calibrated thresholds,
defensive coercion and the bug it prevents. This lives in comments, docstrings and commit
messages. How to harvest it:
[level-2-drilldown.md](references/level-2-drilldown.md#mining-incidents--the-highest-value-content).

Where the rationale is load-bearing and non-obvious, it belongs in a
[decision record](references/decisions.md) — and the page then links it rather than
restating it. Mining is archaeology; a record written when the decision is made is the
same content at a tenth of the cost.

**If a sentence is derivable from the function signature, cut it.** Prose that restates
code is pure cost.

### 8. Verify before finishing

```bash
scripts/render_cards.py     <docs-dir>
scripts/render_decisions.py <docs-dir>
scripts/check_docs.py       <docs-dir> --source-root <repo-root>
```

All three default to `<docs-dir>/decisions/`. Where a project keeps its pages in a
subdirectory of their own — `docs/architecture/html/` — and its records beside the prose
they belong to, pass `--decisions <dir>` to each. Every generated href is then computed
relative to the page carrying it, so both layouts produce links that resolve:

```bash
scripts/render_cards.py docs/architecture/html --decisions docs/architecture/decisions
```

Render first — the checker re-renders and compares byte-for-byte, so a record or a
generated card block edited without re-rendering fails. Then check. Run all three even
when the pages were just written: files move, and the checker catches what reading cannot.

A page with a rendered diagram needs one more pass that no script can do: **open it in
both themes and at a narrow width.** A label sitting on top of a routing line is invisible
in the source and obvious on screen.

Also cross-check any number quoted from a live run against the artifact it came from.

### 9. State the cascade rule where it will be read

An architecture change is incomplete until the pages, the manifest, the records and the
code agree. Write that down — in `AGENTS.md`, `CLAUDE.md`, or the docs directory's
`README.md` — as the list of things that must be updated in the same change, with the two
commands above. Documentation that is not part of the change checklist is documentation
that drifts.

## Setting up a docs directory

```bash
cp assets/_pages.css              <docs-dir>/_pages.css
cp assets/architecture.json       <docs-dir>/architecture.json
cp assets/system-template.html    <docs-dir>/system-map.html          # only if needed
cp assets/component-template.html <docs-dir>/component-map.html       # only if needed
cp assets/component-template.html <docs-dir>/process-map.html         # only if needed —
#   start from the component template, then replace its key and diagram per
#   references/level-1-processes.md. There is no separate process template:
#   the page shell, crumb, legend and tables are identical.
cp assets/map-template.html       <docs-dir>/<pipeline>-map.html
cp assets/drilldown-template.html <docs-dir>/stage-NN-<name>.html
cp assets/index-template.html     <docs-dir>/index.html               # once 3+ pages
mkdir -p                          <docs-dir>/decisions
cp assets/decision-template.md    <docs-dir>/decisions/001-<slug>.md
```

Every page links the one shared stylesheet — do not inline it per page. The drill-down
template carries page-local blocks (failure ladder, phase strip) in its own `<style>`;
delete the ones the stage does not use.

Naming: `stage-NN-<name>.html`, with `NN` the stage's number on the map, so the directory
sorts into pipeline order. The checker requires the number to match the manifest.

## Hard-won constraints

- **External CSS over `file://` works; external JS does not reliably execute.** It fetches
  `200 OK` and silently never runs in some viewers. Keep every script a page needs
  **inline**.
- **Generated pages must be byte-comparable.** Nothing varying — no timestamp, no
  filesystem-dependent ordering — in rendered output, or the staleness check that proves a
  page is current becomes a check that always fails.
- **A rendered check may show a stale page.** Force a fresh load with a cache-busting query
  rather than trusting a reload, and confirm what is on disk with `grep` before concluding
  an edit did not take.
- **Do not put a button on every clickable card.** Repeated down a long page it is visually
  exhausting. The whole card is the target; the affordance is a hover lift plus a quiet
  caret.
- **Never navigate on a click that lands inside a text selection.** These pages are dense
  with paths readers copy.
- **Prefer `<details>` to a popover for a mid level.** Zero JavaScript, works over
  `file://`, keyboard-reachable, and findable by in-page search.
- **Promote a page-local CSS block to the shared file on the third page that needs it**,
  not the second.
- **A page may own a colour key the rest of the set does not share** — but only with a
  legend note saying so, and only page-local. Runtime kind and deterministic-versus-agentic
  are orthogonal axes; one palette cannot carry both.
- **A diagram is inline SVG using the shared CSS variables** — never an image file. It
  follows the reader's theme, needs no regeneration, and adds no second artifact to keep
  in sync. A routing lane and a label in the same channel will collide; check on screen.

## Anti-patterns

| Don't | Because |
|---|---|
| Write pages before the manifest | The manifest is what makes them checkable, and writing it first surfaces the real stage list |
| Declare a flow, purpose, or artifact in two places | It diverges, and the copy being read is the wrong one |
| Open a card with mechanism | A reader who does not know why the stage exists cannot use the how. Goal line first, always |
| Trust the existing doc's stage order | It is the single most common drift |
| Use `file:line` | Rots silently into confidently wrong pointers |
| Collapse `persists` and `emits` into "writes" | Sends readers looking on disk for a payload that was never stored |
| Mark a design `built` | A wall of "not implemented" errors is how a checker gets switched off |
| Mark shipped code `proposed` | Silently disables the only checks that can see drift |
| Restate a decision's rationale on a page | The record is the single source; a copy will outlive the reasoning |
| Cite a superseded record | Presents overturned reasoning as current — worse than no citation |
| Delete a superseded record | It is the only place the old reasoning survives, and that question recurs |
| Give every stage a drill-down | Most stages need the `<details>` mid level, not a page |
| Derive the component list from the stage list | They are different shapes — one component usually spans several stages |
| List processes, libraries, tables and wrappers at one altitude | Every item looks equally weighty and the reader cannot tell which ones run |
| Draw a shared library as its own top-level box | It has no PID. Repeat it inside each process that links it |
| Draw a session or cache file as a process | It is long-lived data, not a running thing. There is nothing to supervise |
| Hand-edit a generated region or a manifest id | Dangling references and stale cards. Re-render, then run the checker |
| Let the index explain anything | It becomes a fifth map, and the one nobody updates |
| Ship a page the index does not link | It reads as complete, so the unlisted page is never found |
| Link only downwards | Readers arrive in the middle, from a search result or a bookmark. Every page needs a crumb and a footer back link |
| Write prose that restates the code | Pure token cost; spend it on the why |
| Explain internals on the map | That is what level 2 is for |
| Derive the template from the easiest stage | It will fit nothing else |
| Round a measured number into "often" | The number is the whole value |
| Fill template sections with thin content | Delete unused blocks instead |
| Inline the shared CSS per page | A colour change becomes an N-file edit |
