# Level 0 — the system context page

One page. Only when the repo holds **more than one pipeline**, or depends on external
systems whose failure a reader needs to understand.

Template: [assets/system-template.html](../assets/system-template.html).

Contents:
- [When to build this at all](#when-to-build-this-at-all)
- [What belongs here](#what-belongs-here)
- [Externals: the honest blast radius](#externals-the-honest-blast-radius)
- [Pinned configuration](#pinned-configuration)
- [Open questions](#open-questions)
- [Keeping it one page](#keeping-it-one-page)
- [The index page](#the-index-page)

## When to build this at all

Skip it for a single pipeline with no external dependencies — the map is already the top
level, and a context page above it would say nothing the map's title does not.

Build it when one of these is true:

- **There is more than one pipeline.** Two maps with no index means a reader has to know
  which one to open before they can find out what either does.
- **External systems can fail, cost money, or change under you.** A model API, a hosting
  platform, a telemetry backend. These are invisible in a stage-ordered map and they are
  the things that break in production.
- **There are calibrated constants that several pipelines share.** They need one home.

## What belongs here

Three questions, and then stop: **what is inside the boundary, what is outside it, and
where do I go next.**

| Belongs | Does not |
|---|---|
| What the system delivers, and to whom | How any stage works |
| An index of pipelines, each with a goal line | A stage list — that is the map |
| External systems and what breaks without them | Retry behaviour against those systems |
| Pinned configuration and why each value | Where each value is read in the code |
| The decision index and open questions | The decisions themselves |

The test: if a reader asks "what is this system and what does it depend on?", this page
answers alone. Anything past that is one level down.

## Externals: the honest blast radius

The column that earns this page its place is **what breaks if it is gone**. Answer it
concretely, per system:

- *"Nothing until the next run — cached artifacts serve the whole site."*
- *"Every agentic stage stops; deterministic stages still run."*
- *"The site keeps serving; only new deploys fail."*

These are wildly different answers and they are exactly what nobody knows during an
incident. Derive them by reading what actually happens on failure — the `except` around
the call, whether there is a cache, whether the artifact is already on disk — not from
what the dependency is *for*.

Also name what the system sends **out**, and to whom. A telemetry backend receiving trace
data is a data-egress boundary; it belongs on the one page that claims to draw the
boundary.

## Pinned configuration

Values that were **calibrated rather than chosen**, and that other things now depend on.

For each, say where the number came from. This is the whole value of the section: the next
reader's instinct is to round 2.5 to 3, and the only defence is a note saying what was
measured. Where a value *was* a guess, say so — a guess labelled as a guess is safe to
change, while a guess that looks calibrated is load-bearing by accident.

Declare the same values in the manifest's `configuration` block so they have a
machine-readable home.

## Open questions

Decisions not yet made, and decisions **deliberately deferred**. Distinguish them, because
they are different states and only one is a problem:

- *"Chunk size and overlap: deferred until retrieval is evaluated."* — a decision waiting
  on evidence. Correct, and worth recording so nobody re-opens it prematurely.
- *"Nobody has decided how access scope propagates to generated notes."* — a gap.

A deferred decision with the evidence it waits on named is one of the most useful lines in
a doc set. It tells a reader why the obvious question has no answer, which stops them
assuming there is one they failed to find.

## Keeping it one page

The pressure on this page is always to grow, because every pipeline wants its concerns
represented at the top. Resist it: a context page that grows into a second map is a page
nobody reads, and the pipelines' own maps get neglected in favour of it.

Two rules hold the line:

- **A pipeline gets a card with a goal line and a link. Never a stage list.** If the card
  needs stages to make sense, the goal line is not doing its job.
- **A row on this page is one line.** The moment an external system needs a paragraph, that
  paragraph belongs on the stage that talks to it.

## The index page

Once the directory holds three or more pages — context, components, one or more maps,
drill-downs — a reader opening it cold has to guess which file answers their question, and
the filenames do not tell them. `index.html` is the answer, and its job is exactly one
thing: **route**.

Template: [assets/index-template.html](../assets/index-template.html). Declare it as
`"index": "index.html"` in the manifest.

Each entry is a card with an **Answers:** line — the question the page settles — and one
sentence on when to open it. That is the whole page, plus the generated decision index.

Two rules, and the first is the one that decays:

- **The index links; it does not explain.** The moment a paragraph starts describing the
  system, the index has become another map, and it is the map nobody remembers to update
  because it is not the one they were editing.
- **It cannot be allowed to miss a page.** An incomplete index is worse than none, because
  it reads as complete and the unlisted page is simply never found. `check_docs.py` fails
  the run when a page the manifest names is not linked from the index, and reports any
  other page in the directory that nothing links.

And the return trip, which is the half that gets forgotten: **every page links back to the
index**, through the crumb at its top and the footer at its bottom
([ui-kit.md](ui-kit.md#navigation-one-shape-on-every-page)). The checker fails the run
otherwise. Readers do not arrive at the index and work downwards — they arrive in the
middle, from a search result, a bookmark or a link someone pasted, and a page with no way
up is where they stop.

The index is not the place for the cascade rule's detail, the status of the docs, or a
changelog. One line in the footer naming what must be updated together is enough; the rule
itself belongs where the change is made — `AGENTS.md`, `CLAUDE.md`, or the directory's
`README.md`.
