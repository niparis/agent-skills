# Level 1 — the map

The zoom-out page. One per pipeline. Answers: *what are the stages, in what order, and which file does each one produce?*

Contents:
- [What belongs here and what does not](#what-belongs-here-and-what-does-not)
- [Deriving the stage order](#deriving-the-stage-order)
- [The stage card](#the-stage-card)
- [Goal first, mechanism second](#goal-first-mechanism-second)
- [The mid level: `<details>` instead of a page](#the-mid-level-details-instead-of-a-page)
- [Views](#views)
- [The three tables](#the-three-tables)
- [Drift audit: updating an existing map](#drift-audit-updating-an-existing-map)

## What belongs here and what does not

**Belongs:** each stage's *purpose*, the stage sequence, the exact command per stage, what each stage reads and writes, which artifacts are new, terms with a local meaning, every file the pipeline touches and whether it is committed, and cross-stage side effects.

**Does not belong:** internals. Retry budgets, prompt rules, gate lists, per-variant behaviour. One or two sentences of "the non-obvious thing about this stage" is right; a paragraph on how it works means the stage needs a drill-down.

The test: if a reader asks "in what order does this run and what do I get?", the map answers alone. If they ask "why did it drop half my items?", they need level 2.

## Deriving the stage order

**Read the code, not the runbook.** Order is the single most common drift, because the docs get written when the pipeline is designed and the code gets reordered later.

Find the actual list — an enum, a constant, a registry, the loop body of the orchestrator — and use it verbatim. Then check three things:

1. **Does a stage run where the docs claim?** A validation step that reads as "right after consolidation" may in fact run several stages later, with the earlier stages gating their own output internally. Both facts are worth stating.
2. **Do the standalone commands share the orchestrator's path?** If `run --from X --until X` is how each single-stage verb executes, say so — it means a verb cannot drift from the pipeline.
3. **What does each stage skip on?** The idempotency condition is per stage and often surprising (an existing output file, a flag in a metadata blob, a signoff string in a report).

State the order explicitly in prose under the phase heading, and call out anything counter-intuitive. A reader who has the wrong mental model of the order will misread every card.

## The stage card

```html
<div class="stage" data-views="ingest">
  <div class="rail"><div class="num">4</div><div class="bar"></div></div>
  <div class="card">
    <h3>stage-name <span class="tag t-det">■ deterministic</span></h3>
    <p class="goal"><strong>Goal:</strong> what this stage is for, and why the pipeline needs it.</p>
    <div class="cmd">the exact command, copy-pasteable</div>
    <p class="note">How it works, plus the thing a reader would get wrong.</p>
    <div class="io">
      <div><h4>reads</h4><div class="chips">
        <span class="chip">input.ext</span></div></div>
      <div><h4>persists</h4><div class="chips">
        <span class="chip new persist">created.ext</span>
        <span class="chip persist">amended.ext <span class="muted">(what changed)</span></span></div></div>
      <div><h4>emits</h4><div class="chips">
        <span class="chip emit">payload → next stage</span></div></div>
    </div>
  </div>
</div>
```

- **Title** = the stage's real name in the codebase, not a prettified one. A reader greps it.
- **Tags** = every applicable classification. Multiple is normal.
- **Goal** = required, one or two sentences, always first. See below.
- **Command** = exactly what you would type, including the flag that makes it safe or required.
- **Note** = the non-obvious behaviour. Prefer stating a surprise over describing the happy path.
- **Chips** = `.chip.new` for created, plain for consumed or amended. Annotate an amendment with what changed: `chapter-NN.jsonl (tags)`.
- **`data-views`** = which views this stage belongs to. Omit entirely if the map has no views.

**Three verbs, not two.** `reads` is existing durable data or supplied input; `persists` is
a durable write that outlives the run; `emits` is a payload handed onward that nobody
stores. The distinction is not cosmetic — collapsing `emits` into `persists` sends readers
to the filesystem looking for something that was never there, and the checker treats only
`persists` as a claim about the data directory. Drop any of the three sections that is
empty rather than writing "none".

The older two-verb form (`<h4>writes</h4>`) still passes every check, so an existing map
does not have to be rewritten to gain the manifest checks — but new pages should split it.

Cards that merge two commands into one stage are fine when the two always run together and share a role — but not when a third stage runs between them. Check the order first.

## Goal first, mechanism second

**Every card opens with `.goal`: one or two sentences on what the stage is for and why the pipeline needs it. Only then how it works.** A reader who skims nothing but the goal lines, top to bottom, should come away with the pipeline.

This is the easiest section of a map to get wrong, because mechanism is what you have just finished reading in the source and purpose is not written down anywhere. The failure looks like a card that opens `"S-pad → content-key dedupe → renumber → resolve @topic refs"` — every word true, and useless to anyone who does not already know why the stage exists.

A goal line earns its place by answering at least one of:

- **What would be broken or missing without this stage?** *"Merge the per-section shards into one chapter bank with stable ids and no duplicates. Sections were extracted independently and know nothing of each other, so this is the first point at which the chapter exists as a single object."*
- **What is the unit of work, and why that unit?** *"Make the chapter the unit of work. Everything after this point is per chapter, and nothing ever opens the whole book again."*
- **What is the hard part?** — the constraint that explains the stage's whole shape. *"Writing questions is the easy part; the hard part is guaranteeing the keyed answer is actually right."*
- **What is this stage deliberately not for?** Cheap and high-value where the name misleads. *"It is not a quality gate on this chapter — it is the record you read across chapters."*

Rules:

- **Never restate the command or the artifacts.** `.cmd` and the chips are directly below; "writes `chapter-NN.jsonl`" in a goal line is wasted.
- **Never open with a step list, a tool name, or a call count.** Those are mechanism — they belong in `.note` or one level down.
- **Name the consequence, not the activity.** "Extracts facts from the section text" says nothing the title did not. "The only stage that reads the book's actual content, so a fact it misses is missing from the cheat sheet, the questions and the audit alike" says why it matters.
- **Two sentences maximum.** A third sentence is always mechanism that drifted upward. If purpose genuinely needs a paragraph, the stage needs a drill-down and its framing paragraph is where the paragraph goes.
- **Derive it from the code like everything else.** Purpose is inferred from what breaks without the stage, what the comments say it prevents, and what the next stage assumes — not from what would sound good.

Non-stage cards on the map (a shared side-effect block, for instance) take a goal line too, on the same terms.

## The mid level: `<details>` instead of a page

Most stages should not get a drill-down. A stage with one model call, no loop and no gate
produces a thin page that costs more to maintain than it returns — but it still owes the
reader three things a card has no room for: its **boundary**, its **invariants**, and the
**decisions** that shaped it.

That is what `<details class="more">` inside the card is for:

```html
<details class="more">
  <summary>Boundary, invariants and decisions</summary>
  <p class="note"><strong>Does not:</strong> decide themes — that is a chapter-level
    judgement made in stage 5.</p>
  <div class="inv"><h4>invariants</h4><ul>
    <li>ids are stable across a re-run of the same input</li>
  </ul></div>
  <div class="decs">
    <a class="dec" href="decisions/pages/002-cluster-sentinel.html">◇ 002 — the cluster sentinel</a>
  </div>
</details>
```

Collapsed by default, so the map still skims as a list of goal lines. `<details>` rather
than a popover because it needs no JavaScript — which matters over `file://`, where an
external script fetches `200 OK` and then silently never runs — and because it is
keyboard-reachable and findable by in-page search.

**The `Does not:` line is the highest-value part.** Write it as the neighbouring concern a
reader would *assume* lives in this stage and does not. That is where scope creep gets
caught, and it is the one thing neither the goal line nor a drill-down naturally states.
Declare the same content in the manifest's `not` field, which is what makes its absence
visible.

A stage that has a drill-down does not need this block — the page carries all three, in
more depth. Do not write both.

## Views

A map with more than about eight stages usually serves several audiences who each need a
subset. Rather than a second diagram that will diverge, declare **views** in the manifest
and let one page filter itself:

```html
<div class="viewbar" role="group" aria-label="Filter stages by view">
  <button class="viewbtn" type="button" data-view="all" aria-pressed="true">All stages</button>
  <button class="viewbtn" type="button" data-view="ingest" aria-pressed="false">Ingestion</button>
</div>
```

Each `.stage` carries `data-views="ingest query"`; the inline script sets `hidden` on the
rest. The filtering is done in JavaScript rather than CSS because a selector cannot ask
whether one attribute's value appears inside another's — and with JavaScript off nothing is
hidden and every stage shows, which is the right fallback for a document.

Add a view when a real audience keeps needing a subset, not one per phase heading. Three to
five is healthy; ten means the views have become a table of contents. Every view a stage
names must be declared in the manifest, and a declared view no stage is in warns.

## The three tables

**Vocabulary.** Every term the codebase uses in a non-standard sense. For each, say what it is *and what it is not* — "a shard only in the loose sense of one piece of the chapter; not a database shard: no partition key, no routing, nothing queries them." This table prevents the most expensive kind of misreading. Include any pair of similar-sounding terms that are actually different things, and say what conflating them once caused.

**File index.** Every file, with: layer (source / pipeline state / canonical / generated / evidence / telemetry), which stage writes it, whether a **contract** declares its shape, and whether it is committed. Verify the committed column against the VCS rather than the gitignore — a file that is neither cleaned up nor ignored *is* committed in practice, whatever the intent was. Check with the equivalent of `git ls-files`, not by reading `.gitignore`.

A greyed `none` in the contract column is a useful row, not an omission to hide: it says the
next stage's assumptions about that file are undocumented. The checker warns on every
structured artifact with no contract, so the column and the warning agree.

**Side effects.** Anything that happens on every stage regardless of what the stage does: run archives, telemetry, eval rows, promotion semantics. Name the flags that change it.

## Drift audit: updating an existing map

When updating rather than creating, audit before editing. Produce the drift list first, then fix.

**Run the checker before reading anything.** It resolves items 1, 3, 4 and 6 below
mechanically and in seconds, which leaves your attention for the ones no script can do:

```bash
scripts/check_docs.py <docs-dir> --source-root <repo-root>
```

If there is no `architecture.json` yet, writing one *is* the audit — declaring the stage
list against `stage_source` surfaces the order drift immediately. See
[manifest.md](manifest.md).

Check, in this order:

1. **Stage order** against the code's stage list.
2. **Command names and flags** — run the CLI's help, or read the command decorators. Renamed verbs are common.
3. **Every artifact filename** — glob the real data directory. Files get added (a new sidecar, a log) and the doc never hears about it.
4. **Every "written by"** claim — grep for the writer. A file the doc credits to stage A may now be written by B, or by nobody (hand-written).
5. **Every gate claim** — "only X can stop the run" is the claim most likely to have quietly become false.
6. **Committed status** for each file, against the VCS.
7. **New concepts with no row at all** — a mode, a tier, a second output format. These are the real misses: not a wrong sentence but an absent one. Look for branches on config the doc never mentions.

Report the drift as a list before changing anything, so the human can tell you which of it is intended.
