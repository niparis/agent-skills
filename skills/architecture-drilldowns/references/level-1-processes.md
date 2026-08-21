# Level 1, runtime axis — the process map

One page. The same system as the other two level-1 pages, read **down** instead of along or
across: what actually runs, what is only code inside something that runs, and how the
running things reach each other.

The component map answers *who is responsible*. This page answers the question you have to
settle before writing a line of code: **what has a PID, what does not, and what crosses a
process boundary.**

Contents:
- [When to build this at all](#when-to-build-this-at-all)
- [The altitude rule](#the-altitude-rule)
- [The four kinds, plus the one that is not a box](#the-four-kinds-plus-the-one-that-is-not-a-box)
- [Nesting is what does the work](#nesting-is-what-does-the-work)
- [Channels are the content](#channels-are-the-content)
- [Long-lived data is not a long-running process](#long-lived-data-is-not-a-long-running-process)
- [The colour key is page-local — say so](#the-colour-key-is-page-local--say-so)
- [Drawing it](#drawing-it)
- [Writing it is an audit, and it finds different faults](#writing-it-is-an-audit-and-it-finds-different-faults)
- [Manifest](#manifest)
- [Anti-patterns](#anti-patterns)

## When to build this at all

Skip it when the system is one process. There is nothing to distinguish.

Build it when any of these hold:

- **A reader cannot tell, from the component map, which components are processes.** This is
  the common trigger, and it usually arrives as a person asking four questions in a row that
  all have the same root: *is A the same thing as B? is C just a table? is D part of E?*
  Those are altitude questions. Answer them with a picture, not more prose.
- **The same code is linked into more than one process.** A shared package looks exactly
  like a service in a component list, and the difference decides whether there is a channel
  between them or nothing at all.
- **Ordering across a process boundary is load-bearing.** *Durable before spawn. Registered
  before the first turn.* Those rules only make sense once you can see where the boundary
  is.
- **Nothing is built yet.** A design that has never run is exactly when the process
  inventory is cheapest to get right and most expensive to get wrong. Set
  `"status": "proposed"` and the code checks stand down.

## The altitude rule

**One box, one runtime kind.** The failure this page exists to prevent is a flat list that
mixes kinds at one altitude:

| The list said | It actually was |
|---|---|
| Operational Policy | a daemon |
| Factory application service | a library linked into four processes |
| Project registry | two tables and four functions |
| Trace writer and query | a writer in one process, a reader in three others |
| Quota adapter | one function wrapping one binary |

Presented as five peers with identical headings, every one of them looks equally weighty,
and no reader can tell that the second has no process, the third has no code, and the fifth
is four lines. That list is unusable, and no amount of better prose fixes it — the defect is
that the list has no altitude rule at all.

**The test, applied to every box: does this have a PID?** Three answers, and each one puts
the box somewhere different. *Always* is a service. *Sometimes* is a one-shot process.
*Never* is a library or a store, and it is never a top-level box.

## The four kinds, plus the one that is not a box

**1. Long-running service.** Started once, outlives every individual unit of work. Give it a
badge line saying what it holds, because that is the real sub-kind and it carries an
invariant: `LISTENS ON 127.0.0.1`, `STDIO · NO SOCKET`, `HEADLESS`.

**2. One-shot process.** Spawned per unit of work, then exits. A CLI invocation, one agent
turn, a workflow run, a wrapped third-party binary. Lifetime is not the discriminator —
"one-shot" can run for an hour. The discriminator is whether it outlives the work item.

**3. Database.** Draw its key tables inside it. That is what its nesting means.

**4. File storage.** Draw the kinds of file inside it. Keep it visibly distinct from the
database: they have different writers, different durability, and one often mirrors the other
in a fixed order that the page should show.

**And the one that is not a box: the shared library.** It has no process, so it never
appears at top level. It appears *inside* every process that links it, with a distinct edge,
and the legend explains why it repeats. Drawing it once with four "links into" arrows
reintroduces the exact confusion the page removes — it makes a library look like a service.
Four copies is noisier and true.

## Nesting is what does the work

Colour is a convenience. **Nesting is the load-bearing device**: a box drawn inside another
box is code in that process, not a peer of it.

This is what makes the page answer questions prose could not settle:

- *Is the application service the same thing as the supervisor?* It is drawn inside it. And
  inside three other processes. Both facts land at once.
- *Is the project registry a component?* There is no box. There are two chips inside the
  database.
- *Is the review delegate a child process?* It is inside the turn that runs it, because a
  subagent shares its parent's process.

The rule has to be strict to be useful. A spawned child is **not** nested — it is a sibling
box with a spawn arrow. The moment you nest a child process "because it belongs to" its
parent, nesting stops meaning one thing and the page loses its only unambiguous notation.

## Channels are the content

Arrows carry more here than colour does, and **weight carries the split that matters**: a
heavy arrow creates a process; everything thinner only talks to one that already exists.
Read the heavy arrows alone and you have the process tree. Say that in the caption.

| Kind | Notation | Example |
|---|---|---|
| in-process call | no arrow — this is what nesting means | supervisor → its own linked package |
| **spawn** | heavy solid | CLI → the workflow process group it starts |
| pipe / stdio | medium, distinct hue, labelled with the protocol | named pipe; JSON Lines on stdin/stdout |
| store read/write | thin, muted | trace writer → file, then → database |
| network | dotted | loopback HTTP; a wrapped binary → its remote API |

Five is the ceiling. If a sixth is wanted, one of the five is doing two jobs.

## Long-lived data is not a long-running process

The reliable objection to this page is *"but X is really long-running — it is just idle
between uses."* Usually X is a **session**, and the objection is half right in a way worth
drawing rather than arguing:

- The session is long-lived. It is durable, it has an ID, it survives restarts.
- The process is not. Between turns there is no PID, no memory, and nothing to supervise.

So the session is a **file store**, and the disposable process gets a read/write arrow to
it. Drawn that way, the objection answers itself and the page gains a fact it was missing.
Drawn as a process, the page hides that there is nothing there to kill, and hides why every
volatile fact has to be re-read at the start of each turn instead of remembered.

Generalise it: **if it feels long-lived but has no PID between uses, it is a store.**

## The colour key is page-local — say so

The component map's colours usually encode a *semantic* axis — deterministic versus agentic,
gate versus artifact. This page's colours encode *runtime kind*. Those are orthogonal, and
reusing one palette for both gives the doc set two meanings for one swatch.

Resolve it deliberately, in this order:

1. This page owns its own key, defined page-local, not promoted to the shared stylesheet.
2. A loud note under the legend saying the key differs here and what it means elsewhere.
3. The other axis moves to a **glyph**, not a second colour — a `◆` in the corner for
   agent-bearing, a `▤` for file storage. A glyph coexists with any fill.

Four hues is the working set: service, one-shot, database, file storage. Check them against
each other, not just against the background — warm tan against amber, or teal against sky
blue, reads as one category in a screenshot even when the hex values differ. Verify on
screen in both themes before believing the palette.

## Drawing it

Inline SVG using page-local variables layered over the shared ones. `file://` constraints and
the base diagram CSS: [ui-kit.md](ui-kit.md#the-diagram-block).

Four columns, wider than the rest of the set, with a page-local `.wrap{max-width:...}`
override — this is the one page that earns the extra width, and forcing it into the shared
measure buys a permanent horizontal scrollbar.

```
col 1              col 2            col 3                col 4
human surfaces     durable state    the engine           outside the boundary
and local CLIs     (db + files)     (services, then      (externals, and the
                                     the processes        binaries you spawn,
                                     they spawn)          at the edge)
```

Numbers that survived contact with real labels:

- **Gutters of 50–60px between columns**, and even then three routing lanes in one gutter
  will cross. Accept crossings between a thin store line and a heavy spawn line — the weight
  difference makes them read as a crossing rather than a junction. Do not accept a crossing
  between two heavy lines: hop one with a small arc.
- **Reserve horizontal lanes below the last store box** for the long left-to-right spawn
  arrows. Place that box's bottom edge and the lane's `y` deliberately, then re-check after
  any vertical resize.
- **Label placement is where this page actually breaks.** Two labels 4px apart render as one
  unreadable line and it is invisible in the source. Budget a screenshot pass per label
  cluster.
- **Modules inside a process: 22–28px tall, one line each.** Two lines only for the largest
  container, where a four-word role earns its space.
- **Ours versus third-party.** A binary you shell out to and a CLI you wrote get the same
  runtime kind and therefore the same colour. Distinguish them by content: yours gets its
  full component list and a naming line under the title; theirs gets a title and a badge.

## Writing it is an audit, and it finds different faults

The component map audit finds ownership contradictions. This one finds altitude and boundary
faults, and they are a different list. Real examples from one page:

- **A component that is two processes.** The Web UI was described alongside a headless
  daemon as though it might be a thread inside it. It is neither — it is a second service
  with its own socket.
- **A component that is zero processes.** A "project registry" that turned out to be two
  tables and four functions.
- **A seam built for an implementation the scope excludes.** A "runner" and an "adapter"
  split that only pays off with a second harness, in a project whose MVP explicitly excludes
  a second harness.
- **A second, unwrapped path to an external.** One component reaches a service through a
  wrapper that guarantees an invariant; an agent reaches the same service directly through
  its shell, and the invariant is now prompt-enforced.
- **An operation that straddles a proposed boundary.** A command that interleaves durable
  writes with a spawn inside one postcondition cannot be split across two surfaces, which
  kills any "data here, process there" boundary before it is proposed.
- **A whole missing process.** A workflow described as if it ran no model, whose declared
  extension turned out to name a runtime.

**Report these; do not quietly resolve them on the page.** Each is somebody's decision. The
page's job is to make them unavoidable.

One further outcome to expect: **this page can obsolete prose.** A per-component document of
Responsibility / Does not own / Interface / Dependencies / Patterns headings, applied
uniformly to every item regardless of kind, is the document this page replaces. Before
deleting it, check each of its cross-component invariants against the specs — they are
usually already stated there — and rehome any open question that exists nowhere else.

## Manifest

```json
"process_map": "process-map.html",
"processes": [
  { "id": "1", "name": "Operational Policy", "kind": "service",
    "holds": "nothing — headless", "started_by": "the engineer",
    "links": ["core-operations", "store-access"], "invariants": ["..."], "adr": ["002"] },
  { "id": "4", "name": "pf", "kind": "one-shot", "ours": true,
    "started_by": ["2", "engineer"], "spawns": ["6"] },
  { "id": "9", "name": "Factory SQLite", "kind": "database", "tables": ["runs", "events"] }
],
"process_channels": [
  { "from": "4", "to": "6", "kind": "spawn", "carries": "run id, workflow, model" },
  { "from": "4", "to": "6", "kind": "pipe",  "carries": "steer message, verbatim" }
]
```

`kind` is one of `service`, `one-shot`, `database`, `file-storage`. A library is not a
process and does not get an entry — it appears in the `links` array of every process that
links it, which is what makes "linked into three processes" a checkable claim rather than a
drawing.

**These keys are not yet validated by `check_docs.py`**, which warns on keys nothing reads.
Either extend the checker alongside them or leave the page out of the manifest and say so —
do not add keys that produce a permanent warning, because a checker that always warns is a
checker people stop reading.

## Anti-patterns

| Don't | Because |
|---|---|
| List processes, libraries, tables and wrappers at one altitude | Every item then looks equally weighty, and the reader cannot tell which ones run |
| Nest a spawned child inside its parent | Nesting means "same process". One exception and the notation means nothing |
| Draw a shared library once with arrows into its callers | That is exactly how a library gets mistaken for a service |
| Give a library a top-level box "for visibility" | It has no PID. Visibility is what the repeated inner box is for |
| Draw a session, cache, or queue file as a process | It has no PID between uses. It is a store, and drawing it as one answers the objection |
| Reuse the doc set's palette for runtime kind | Two meanings for one swatch. Own the key here and say it in the legend |
| Use a second colour for agent-bearing | A glyph coexists with any fill; a second colour axis fights the first |
| Name a box with just its executable name | `pf` reads as a pipe utility. A one-word name needs a description line |
| Ship it without a screenshot pass in both themes | Colliding labels and merged palettes are invisible in source and obvious on screen |
| Resolve a boundary fault you found while drawing | Report it. Each one is a decision somebody owns |
| Hand-edit the manifest or a generated region afterwards | Dangling ids and stale cards. Re-render, then run the checker |
