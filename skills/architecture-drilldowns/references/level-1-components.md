# Level 1, structural axis — the component map

One page. The same system as the pipeline map, read **across** instead of **along**:
who owns what, and what travels between them.

Template: [assets/component-template.html](../assets/component-template.html).

Contents:
- [When to build this at all](#when-to-build-this-at-all)
- [Components are not stages](#components-are-not-stages)
- [What belongs here](#what-belongs-here)
- [The four sections that earn the page](#the-four-sections-that-earn-the-page)
- [Drawing the diagram](#drawing-the-diagram)
- [Writing it is an audit](#writing-it-is-an-audit)
- [Manifest](#manifest)
- [Anti-patterns](#anti-patterns)

## When to build this at all

Skip it when the pipeline is one process doing one thing after another. The map already
says everything true about ownership, because there is one owner.

If the question a reader actually has is *which of these things runs*, that is the
[process map](level-1-processes.md), not this page. This one answers who owns a
responsibility; that one answers what has a PID.

Build it when any of these hold:

- **More than one long-lived actor.** A supervisor and a worker, a daemon and a CLI, a
  scheduler and the jobs it starts. Their relationship is invisible on a stage-ordered
  page, because it is not a step.
- **A supervision or authority structure.** Something may kill, restart, gate, or approve
  something else. Who is allowed to do what to whom is the page's whole subject.
- **Several writers to one store.** The moment two components write one database, the
  rule that keeps them from disagreeing is load-bearing and lives nowhere on a map.
- **A responsibility that must not move.** A backstop, a credential boundary, a human
  approval. The page states what each component is *prevented* from owning, which is the
  only durable form that rule takes in a document.

## Components are not stages

The most common way to get this page wrong is to derive the component list from the stage
list. They are different shapes:

| | Pipeline map | Component map |
|---|---|---|
| A card is | a step in a sequence | a thing that owns a responsibility |
| Ordering means | happens after | nothing — the numbers are just rail positions |
| One card may | be run by two components | span half the stages on the map |
| Reader arrives asking | what happens next | who is responsible for this |

Derive components from **what owns a process, a store, or an authority**, not from what
happens. A useful test: if two cards would always be the same process with the same
lifetime and the same permissions, they are one component.

An external system may need a card here even though the boundary page already lists it —
a work-state store a reader thinks of as part of the system, an object store, a queue.
Declare it **once**, as an external with its purpose, and have the component entry present
it (`"external": "github"`). Two declarations diverge; one declaration presented twice
does not.

## What belongs here

| Belongs | Does not |
|---|---|
| What each component owns, and what it may not own | The order work flows through them |
| The channels between them, and what each carries | Retry behaviour on a channel — that is a drill-down |
| Which component writes which store | The schema of that store — that is a contract |
| A layering rule (*nothing spans two levels*) | The rationale for that rule — that is a record |
| What is deliberately not a component | An apology for its absence |

## The four sections that earn the page

**1. The diagram.** The only diagram in the doc set. See below.

**2. Component cards.** Goal line first, then the non-obvious constraint, then
reads/persists/emits, then the generated mid-level block. The field that earns the card is
**what it does not own** — a responsibility a reader would reasonably assume lives here.
Boundary creep is invisible on a pipeline map and obvious here.

**3. Channels, with a "what breaks when it is silent" column.** This is the column that
justifies the table. A channel rarely fails loudly: it goes quiet, and the component on
the other end decides on missing evidence while looking healthy. Answer concretely —
*"nothing starts and nothing reports an error"*, *"the supervisor kill is misread as a
worker fault"*. Never *"it breaks"*.

**4. Who writes what.** One row per store: the writer, the readers, and the rule that
keeps two writers from disagreeing. If the answer is "one writer per table", say which
table belongs to whom, because that is the claim someone will violate first.

## Drawing the diagram

Inline SVG, not an image and not a build step. It uses the shared CSS variables, so it
follows the reader's theme with no second asset to keep in sync. Full CSS block and the
`file://` constraints: [ui-kit.md](ui-kit.md#the-diagram-block).

Layout that survives contact with real labels:

- **Components down a centre spine, stores on the left, externals on the right.** The
  routing channels between the columns are 70–90px, and every label has to fit in one.
- **Two arrows per spine gap** — down on the left, up on the right — each label anchored
  away from its arrow (`.lend` to the left of it, `.lstart` to the right). One arrow with
  a two-way label hides which direction carries what.
- **A vertical routing lane and a horizontal label in the same channel will collide.** The
  lane cuts through the text and it looks like a rendering fault. Either keep labels clear
  of the lane's x, or drop the label: if the target box's own subtitle already says
  *"worktree provisioning"*, the arrow does not need the word *provision* on it.
- **Order the right-hand column so each external sits level with the component that uses
  it.** That is what buys short, straight, unlabelled arrows instead of a bundle of bends.
- **Solid carries data or control; dashed is hosting and supervision.** Keep the
  distinction — it is doing real explanatory work, and it is what makes "supervises the
  process" visibly different from "sends it a message".
- **Check both themes and a narrow viewport** before calling it done. `min-width` on the
  SVG plus the `.scroll` wrapper makes it scroll rather than shrink to unreadable.

Ten boxes is a lot. If the diagram needs more, the page is describing internals that
belong one level down.

## Writing it is an audit

Building this page over an existing specification finds contradictions that reading the
specification does not, because it forces every responsibility to have exactly one owner
and every channel exactly two ends. Two classes turn up reliably:

- **A relay that requires a capability its named component does not hold.** *A says
  control travels A → B → C; elsewhere the document says B does not own C's process.*
- **An atomic write that spans two writers.** *These three facts must settle together;
  elsewhere two of them belong to different components joined by a message channel.*

Report those separately rather than encoding a guess. The page should state only what the
specification states — a page that quietly resolves a contradiction hides it, and the
resolution is a decision somebody has to make.

## Manifest

```json
"component_map": "component-map.html",
"components": [
  { "id": "1", "name": "Operational Policy", "kind": "deterministic",
    "not": ["does not start workflows"], "invariants": ["..."], "adr": ["002"] },
  { "id": "6", "external": "github", "invariants": ["..."], "adr": ["001"] }
],
"channels": [
  { "from": "1", "to": "2", "carries": "dispatch trigger" }
]
```

`channels` is the model, not the prose — the same role `edges` plays at level 0. What
breaks when a channel goes silent lives in the page's table, where a reader meets it.

Checked like the pipeline map: every component needs a card, numbered and in order; every
channel endpoint must resolve to a component or an external; `carries` is required. The
`not`, `invariants` and `adr` fields render into the card's `<details>` block through
`render_cards.py`, exactly as they do for a stage — so they are declared once, in the
manifest, and provably current on the page.

## Anti-patterns

| Don't | Because |
|---|---|
| Number the cards to imply an order | This axis has no order; a reader will follow it as one anyway |
| Give a component a card per stage it participates in | That is the map, drawn twice, and it will drift from the map |
| Draw every channel and label every arrow | The table carries detail; the diagram carries shape |
| Write "what it does" and stop | Without "what it must not own", the page is a component list, not a boundary |
| Answer "what breaks" with "it breaks" | The whole value of the column is that the answers differ wildly per channel |
| Declare a system as both a component and an external | One declaration, presented twice — use `"external": "<id>"` |
| Resolve a contradiction you found while drawing | Report it; the resolution is somebody's decision, not a documentation edit |
