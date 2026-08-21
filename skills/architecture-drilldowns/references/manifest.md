# The manifest — what makes the docs checkable

`architecture.json` beside the pages. Without it the pages are prose that happens to be
true today; with it, drift between the docs and the system fails a check.

Contents:
- [The division of labour](#the-division-of-labour)
- [Why this is the highest-value piece](#why-this-is-the-highest-value-piece)
- [`status` — as-built or as-designed](#status--as-built-or-as-designed)
- [`stage_source` — binding the docs to the code](#stage_source--binding-the-docs-to-the-code)
- [Views](#views)
- [Boundaries and invariants](#boundaries-and-invariants)
- [Data contracts](#data-contracts)
- [Externals and edges](#externals-and-edges)
- [Components and channels](#components-and-channels)
- [The pages the manifest names](#the-pages-the-manifest-names)
- [What the checker actually proves](#what-the-checker-actually-proves)

Annotated template: [assets/architecture.json](../assets/architecture.json).

## The division of labour

One rule governs everything here:

> **The HTML owns the narrative. The manifest owns identity, contracts, invariants,
> decisions and views. Nothing is declared in both.**

So there are deliberately **no reads/writes lists in the manifest**. The checker parses
those out of the map's own chips. Declaring a flow in two places is the duplication that
this skill's own anti-pattern table warns about, and the manifest would win arguments it
should not — the map is where readers look.

Likewise there is no `purpose` field on a stage. Purpose is the map's `.goal` line, in
front of the reader. What the manifest carries is the half the map has no place for: the
**non-responsibilities**, the **invariants**, and the **decisions**.

## Why this is the highest-value piece

The per-page checks — refs resolve, tags balance, links work — only ever prove the
documentation is internally consistent. A doc set can pass all of them while describing
a pipeline that was reordered six months ago.

The manifest is what makes the *other* class of check possible: comparing the docs
against the code and against the real data. That is the class that catches what this
skill names as the most common drift — a renamed stage, a reordered stage, a stage that
exists in code and in no document at all.

## `status` — as-built or as-designed

```json
"status": "built"
```

`built` (the default) means the code exists, so the code and data checks run. `proposed`,
`draft`, `design` and `planned` mean it does not, so those checks are skipped and the run
says so.

This field is load-bearing in both directions:

- `built` on a design produces a wall of errors that all mean *not implemented yet*. That
  is how a checker gets switched off, and once off it catches nothing.
- `proposed` on shipped code silently disables the only checks that can see drift. The
  run looks clean and proves nothing.

It also fixes a hole in this skill's central rule. "Read the code, never the docs"
assumes there is code to read. For a design that has not been built, the document *is*
the source — and saying so explicitly is better than pretending otherwise.

## `stage_source` — binding the docs to the code

```json
"stage_source": "src/pipeline/constants.py · StageName"
```

Same `file · symbol` grammar as a `.ref` chip. The checker reads the real stage list out
of it and compares, in order, against the flattened `code_names` of every stage.

Two shapes are read: an enum whose members carry string values, and a module-level list
or tuple of string literals.

**Point it at the enum, not at something derived from the enum.** A comprehension like
`STAGES = [s.value for s in StageName]` contains no literals to read; the checker will
tell you so rather than guess, but you have lost the check until you fix it.

`code_names` handles the two cases where the map and the enum legitimately differ:

| Case | Declare |
|---|---|
| A setup verb outside the run pipeline (import, split, deploy) | `"code_names": []` |
| One card covering two members that always run together | `"code_names": ["frameworks", "sidecar"]` |
| Everything else | omit — it defaults to `[name]` |

Flattening in manifest order and comparing to the code's list checks naming *and*
ordering in one comparison. Do not "fix" a mismatch by editing the manifest until you
have checked which side is wrong — a stage that moved in code and not in the doc, and a
doc that was always wrong, need different responses.

## Views

```json
"views": [{ "id": "ingest", "title": "Ingestion" }]
```

Named readings of the one model. A stage lists the views it belongs to; the map's view
bar filters to one at a time. This is how you get real zoom levels without a second
hand-maintained page — the alternative is N diagrams that diverge.

Add a view when a real audience keeps needing a subset, not one per phase heading. Three
to five is a healthy number; ten means the views have become a table of contents.

The checker fails a stage naming an undeclared view, and warns on a declared view no
stage is in.

## Boundaries and invariants

Two fields per stage, both reported in aggregate so a doc set in progress does not drown
in per-stage warnings.

**`not`** — the responsibilities the stage explicitly does not take on:

```json
"not": ["does not decide themes — that is a chapter-level judgement made in stage 5"]
```

Write these as the neighbouring concern a reader would *assume* lives here and does not.
Boundary creep is what this field catches, and it is worth more than a second paragraph
of purpose. Set `"no_not": true` to declare there genuinely are none.

**`invariants`** — claims that must hold for the stage to be correct, written so a reader
can check the code against them:

```json
"invariants": ["every fact leaves this stage with cluster set to the reserved sentinel"]
```

An invariant is not a description. "Merges the shards" is a description; "ids are stable
across a re-run of the same input" is a claim that can be false. If a sentence cannot be
false, it is not an invariant. `"no_invariants": true` to declare none deliberately.

## Data contracts

The shape of each durable artifact at a stage boundary — what the next stage is entitled
to assume.

```json
"contracts": {
  "chapter-NN.jsonl": {
    "kind": "jsonl",
    "sample": "data/*/facts/chapter-[0-9][0-9].jsonl",
    "written_by": "4",
    "amended_by": ["5"],
    "required": ["fact_id", "section", "cluster"],
    "optional": ["tags"],
    "invariants": ["cluster is the reserved sentinel until stage 5, never after"]
  }
}
```

`required` means present in **every record of every sample**, not present somewhere.
`optional` may be absent. A key that is present and undeclared warns — that is how a
sidecar which quietly grew a field surfaces.

Three things that are easy to get wrong:

- **Anchor the sample glob.** `chapter-*.sections.json` also matches
  `chapter-05.meta.sections.json` — a different artifact — and the contract then fails
  against the wrong file. Use character classes: `chapter-[0-9][0-9].sections.json`.
- **Several samples, not one.** The checker reads the three most recent matches by
  default. One file passes a contract it only happens to satisfy, and where a glob spans
  subjects or tenants the optional keys differ per file.
- **`invariants` here are prose, not checks.** The run prints "none machine-checked —
  verify by hand" every time, on purpose. A reader who mistakes a stated invariant for a
  verified one is worse off than one who knows it is a claim.

Coverage is checked both ways: a structured artifact some stage writes but no contract
describes, and a contract describing a file no stage writes, both warn.

## Externals and edges

For the level-0 page. `externals` are the systems outside the boundary — they have no
card of their own, so their `purpose` is declared here and required.

`edges` is **only** for relationships the numbered rail cannot express: a side channel
every stage uses (telemetry, a run archive), or a link to an external system. Do not
restate stage N → stage N+1; the order already says it. Endpoints must resolve to a stage
id or an external id.

## Components and channels

For the component map. `stages` is the sequence; `components` is the ownership, and the
two lists are deliberately different shapes — one component usually spans several stages.
Full guidance: [level-1-components.md](level-1-components.md).

```json
"components": [
  { "id": "1", "name": "Operational Policy", "kind": "deterministic",
    "not": ["does not start workflows"],
    "invariants": ["the run row exists before the process does"],
    "adr": ["002"] },
  { "id": "6", "external": "github", "adr": ["001"] }
],
"channels": [
  { "from": "1", "to": "2", "carries": "dispatch trigger" }
]
```

Three things worth knowing:

- **`external` instead of `name`** presents an already-declared external as a component
  card. A system can be an external to the boundary page and a component to a reader
  without being declared twice — the purpose stays on the external, the card position on
  the component. Pass both when the card says it differently (*one* repository here, all
  of them on the boundary page); the external reference is still resolved.
- **`channels` is the model, not the prose** — the same role `edges` plays at level 0.
  `carries` is required, because a channel with no payload named is a line on a diagram.
  What breaks when one goes silent lives in the page's table, where a reader meets it.
- **`not` and `invariants` render into the card**, through `render_cards.py`, from the
  same sentinels a stage card uses. Declared once, in the manifest; visible on the page;
  proved current by a re-render.

There is no `drilldown` field on a component. A component's deeper page is a *stage* page,
on the other axis, and the link belongs in the card's HTML.

## The pages the manifest names

`system`, `component_map`, `map`, `index`, and each stage's `drilldown`. Every one of them
is checked for existence, and every one must be linked from the index if there is one.

`index` is the routing page — see
[level-0-system.md](level-0-system.md#the-index-page). It is the cheapest check in the
file and it catches the most embarrassing failure: a page written, committed, and never
found by anyone.

## What the checker actually proves

Worth being precise about, because a check that is trusted for more than it does is a
liability:

| Proved mechanically | Still a human judgement |
|---|---|
| The documented stage list equals the code's, in order | Whether the stage order makes sense |
| Every declared component has a card, in order | Whether the components are the right cut |
| Every channel endpoint resolves to a component or external | Whether the channel is the one that actually exists |
| Every page the manifest names is linked from the index | Whether the index says anything useful about them |
| Every card's drill-down link resolves | Whether the drill-down is any good |
| Every declared required key is in every sampled record | Whether the contract is the right contract |
| Every cited decision exists and is not superseded | Whether the decision is still right |
| Every rendered page matches a fresh render | Whether the record says anything useful |
| No data file is unclaimed by any stage | Whether a claimed write actually happens |
| A `.goal` line is present | Whether it states purpose or mechanism |

The last row is the one that matters most and the one no checker can do. Mechanism-first
prose passes every mechanical check ever written.
