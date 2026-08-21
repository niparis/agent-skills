# UI kit — the visual grammar and its mechanics

Contents:
- [The four-tag vocabulary](#the-four-tag-vocabulary)
- [Shared CSS: one file, linked](#shared-css-one-file-linked)
- [Core blocks and when each applies](#core-blocks-and-when-each-applies)
- [Page-local blocks](#page-local-blocks)
- [The diagram block](#the-diagram-block)
- [Progressive disclosure mechanics](#progressive-disclosure-mechanics)
- [Theming](#theming)
- [The file:// constraint](#the-file-constraint)

## The four-tag vocabulary

Four classifications, used identically on every page and in every legend:

| Tag | Class | Means |
|---|---|---|
| ■ deterministic | `tag t-det` | Zero model calls. Same input, same output. |
| ◆ agentic | `tag t-agt` | Makes a model call. |
| ▲ gate | `tag t-gate` | Can stop the run. |
| ▸ artifact | `tag t-file` | A file or record, not an action. |
| ◇ decision | `tag t-adr` | A decision record's own status badge. Only on a rendered record page. |

Rules:
- **Never overload a tag.** A stage that is deterministic *and* has a gate carries both tags.
- **Extend by adding**, not by redefining. A new classification means a new `--var` pair and a new `t-*` class, added to the shared CSS with the legend updated on every page.
- The legend is repeated on every page verbatim. It costs four lines and removes the need to remember.

## Shared CSS: one file, linked

One `_pages.css` beside the pages; every page links it relatively:

```html
<link rel="stylesheet" href="_pages.css">
```

Do **not** inline the shared block per page. At two pages the duplication is annoying; at ten it means a tag colour change is a ten-file edit. Copy `assets/_pages.css` into the docs directory unchanged.

## Core blocks and when each applies

Everything below lives in `_pages.css` and is available on every page.

**`.wrap`** — the page container. `max-width:1120px`, centred.

**`.stage` + `.rail` + `.num` + `.card`** — the numbered rail. The spine of both levels. On the map, one per pipeline stage; on a drill-down, one per *decision*. Omit `<div class="bar">` on the last item so the connecting line stops.

```html
<div class="stage">
  <div class="rail"><div class="num">3</div><div class="bar"></div></div>
  <div class="card">
    <h3>name <span class="tag t-det">■ deterministic</span></h3>
    <div class="cmd">the exact command</div>
    <p class="note">prose</p>
  </div>
</div>
```

Sub-steps use a superscript in `.num` — `0ᵇ`, `1ᵇ`. Use these for a **parallel branch or a same-level variant**, not for a new sequential step. A branch that gets its own integer reads as "happens after", which is wrong.

**`.goal`** — the purpose line, first thing inside a stage card, above `.cmd`. Full-strength text so it reads before the muted `.note` under it; no border or background, because it repeats on every card. Required on every stage card — the rule and the failure modes are in [level-1-map.md](level-1-map.md#goal-first-mechanism-second).

```html
<h3>stage-name <span class="tag t-det">■ deterministic</span></h3>
<p class="goal"><strong>Goal:</strong> what it is for, and why the pipeline needs it.</p>
<div class="cmd">the exact command</div>
```

**`.cmd`** — a copy-pasteable command. Monospace, `white-space:pre`, scrolls rather than wraps. Multi-line for a stage that is two commands.

**`.io` + `.chips` + `.chip`** — the flow. `.chip.new` (outlined, bold) marks an artifact this stage *creates*; a plain chip is one it consumes or amends. This is the whole data-flow story at level 1, so get the `new` marking right.

Three verbs, three chip variants: a plain chip under `reads`, `.chip.persist` (green, solid) under `persists`, `.chip.emit` (purple, dashed) under `emits`. The dashed border is doing real work — it is the visual claim that nothing landed on disk. Only `persists` is treated as a claim about the data directory by `check_docs.py`.

**`.inv`** — the invariants block: the claims that must hold for a stage to be correct. Quiet by design, with a gate-coloured left border because a violated invariant is a correctness failure. Earns its place by being complete, not by being loud.

**`.dec` + `.decs`** — decision-record links. Always a link to a rendered page under `decisions/pages/`, never inline rationale. See [decisions.md](decisions.md#the-link-dont-restate-rule).

**`details.more`** — the mid level between a card and a page. `<summary>` collapsed by default so the map still skims as a list of goal lines. Zero JavaScript on purpose, which is what makes it safe over `file://` where an external script can fetch `200 OK` and never run.

**`.viewbar` + `.viewbtn`** — the view filter. The bar only *styles* the buttons; the matching is done by the map's inline script setting `hidden` on non-matching stages, because CSS cannot ask whether one attribute's value appears inside another's. `.stage[hidden]{display:none}` is needed because `.stage` sets `display:grid`, which outranks the UA rule for `[hidden]`.

**`.panel`** — a contract block. Purple/agentic by default; add `class="det"` for green/deterministic. Use for the *rules* a model is held to, or a deterministic rule set (a weight formula, a derivation). Put field names in `<b>` — they render monospace inside a panel. Quote the rules, never paraphrase the prompt's prose.

**`.refs` + `.ref`** — the code-reference chips. Dashed border, muted, monospace. Content is always `file · symbol` (see [level-2-drilldown.md](level-2-drilldown.md)).

**`table` inside `.scroll`** — every table is wrapped in `<div class="scroll">` so a wide table scrolls inside its own box and the page body never scrolls horizontally.

**`.muted`** — a greyed table row for an absent-but-expected key. Often the most useful row on the page: *what this stage does not write, and what the default is until someone does.*

## Page-local blocks

Keep a block in the page's own `<style>` until a **third** page needs it, then promote it to `_pages.css`. Two pages sharing a block is a coincidence; three is a pattern.

Two blocks that have earned their place, shipped in `assets/drilldown-template.html`:

**`.ladder` + `.rung`** — the failure-isolation ladder. Two columns: what fails, how far the damage goes. `.rung.fatal` tints the one rung that stops the run. Order rungs smallest blast radius first, fatal last.

**`.phases` + `.ph` + `.arrow`** — a one-line phase strip for a non-linear stage. `→` for sequence, `+` for a parallel branch. Colour each `.ph` by classification (`det`/`agt`). Skip it entirely for a linear stage — the rail already says it.

## The diagram block

`.dg` — inline SVG, shipped in `assets/component-template.html` and used by the component map. The one place in the doc set where a picture beats a table, because the subject is a shape rather than a sequence.

**Inline, never an image.** A rendered PNG or an external `.svg` needs regenerating, cannot inherit the page's theme, and is one more artifact to keep in sync. Inline SVG that fills with `var(--card)` and strokes with `var(--line)` follows the reader's light/dark toggle for free.

```html
<div class="scroll">
<svg class="dg" viewBox="0 0 1000 460" role="img" aria-labelledby="dgt dgd">
  <title id="dgt">…</title>
  <desc id="dgd">one sentence naming the structure, for a screen reader</desc>
  <defs>
    <marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7"
            orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="var(--muted)"></path>
    </marker>
  </defs>
  <rect class="box det" x="300" y="80" width="380" height="76" rx="10"></rect>
  <text class="t" x="490" y="110">component</text>
  <text class="s" x="490" y="130">one line on what it owns</text>
  <path class="link" d="M430,156 L430,196" marker-end="url(#ah)"></path>
  <text class="l lend" x="420" y="172">what travels</text>
</svg>
</div>
```

Classes: `.box` plus `.det` / `.agt` / `.file` / `.gate` for the four-tag palette, `.bound` for the dashed boundary, `.link` for an arrow and `.link.dash` for a hosting or supervision relationship, and `.t` / `.s` / `.l` for box title, box subtitle and edge label. `.lend` and `.lstart` re-anchor a label away from its arrow.

Four constraints that are not obvious until a label lands on a line:

- **`min-width` on `.dg` plus the `.scroll` wrapper.** Without it a narrow viewport scales the whole diagram down until the 9.5px labels are unreadable. With it, the diagram scrolls inside its own box and the page body still never scrolls horizontally.
- **A vertical routing lane and a horizontal label in the same channel collide.** The line runs through the text and reads as a rendering bug. Keep labels clear of the lane's x, or drop the label where the target box's subtitle already carries the verb.
- **Custom properties resolve inside `<defs>`.** The marker is a child of the same `<svg>`, so `fill="var(--muted)"` in the arrowhead follows the theme like everything else.
- **`font-family:inherit` on `.dg`.** SVG text does not inherit the body font otherwise, and a diagram in the default serif next to sans-serif prose looks like a pasted foreign object.

Verify in **both themes and at a narrow width** before finishing. A collision that is invisible in dark mode at 1280px is not fixed, only hidden.

## Progressive disclosure mechanics

Four levels, and the boundaries are strict:

| Level | Says |
|---|---|
| Index | Which page answers which question. Nothing else |
| System context | What is inside the boundary and what is outside |
| Component map | Which components exist, what each owns, what travels between them |
| Map | What the stages are and in what order |
| `<details>` in a card | That stage's or component's boundary, invariants and decisions |
| Drill-down page | How it works and why it is shaped that way |
| Decision record | Why this, and not the obvious alternative |

If a sentence explains an internal, it belongs one level down. If it restates a stage's order or artifacts, it belongs one level up and should not be repeated. If it argues for a choice against an alternative, it belongs in a record and the page links it.

A stage with a drill-down gets three things:

```html
<div class="card" data-href="stage-08-questions.html">
  <h3><a href="stage-08-questions.html">questions</a><span class="caret">↗</span>
    <span class="tag t-det">■ blueprint</span></h3>
```

1. `data-href` on the **card** — the whole box is the click target.
2. A real `<a>` on the **title** — keyboard-reachable, right-clickable, and it degrades correctly with JS off.
3. `<span class="caret">↗</span>` — the affordance.

The caret sits at `opacity:.45` and rises to `1` on card hover; the card lifts 1px and takes the accent border. **Do not** put a button or pill on every card — repeated down a long page it is visually exhausting, which is the whole reason the affordance is this quiet.

The click handler goes **inline at the bottom of the map page**:

```html
<script>
document.addEventListener("click", function (e) {
  var card = e.target.closest && e.target.closest(".card[data-href]");
  if (!card) return;
  if (e.target.closest("a")) return;              // a real link wins
  var sel = window.getSelection();                 // reading, not navigating
  if (sel && String(sel).length > 0) return;
  window.location.href = card.getAttribute("data-href");
});
</script>
```

The selection check is not optional. These pages are dense with paths and symbols that readers copy; navigating away mid-selection is infuriating. The `closest("a")` check keeps real links working.

### Navigation: one shape on every page

Links that only run downhill strand whoever arrived from a search result or a bookmark. Two elements, on **every** page except the index:

**`.crumb` at the top — the path.** Root → current, ancestors linked, the current page as plain text, `/` between segments.

```html
<p class="crumb"><a href="index.html">Architecture index</a> <span>/</span>
  <a href="pipeline-map.html">The pipeline map</a> <span>/</span>
  <span>Stage 2 — dispatch</span></p>
```

No arrow in the crumb. An `←` in the middle of a path reads as a direction rather than a location, and the reader who wants to go back is at the bottom of the page by then, not the top.

**A footer that starts with the back link, then goes sideways.** `← <parent>`, the index if it is not the parent, then siblings, then the companion document:

```html
<footer>
  <a href="pipeline-map.html">← The pipeline map</a> ·
  <a href="index.html">Architecture index</a> ·
  Siblings: <a href="stage-04-execute.html">stage 4 — execute</a> ·
  Companion document: <code>../architecture.md</code>
</footer>
```

`check_docs.py` fails the run when a page the manifest names does not link the index, so "you can always get home" is mechanical rather than a habit. Decision pages get theirs generated — the renderer points them at the index, because a record is cited from several pages and there is no single page it came from.

Paths are relative to the page, which matters once the HTML lives in a subdirectory and the records or the prose do not: `../decisions/pages/007-x.html`, `../architecture.md`.

## Theming

The palette is defined three times over: `@media (prefers-color-scheme:dark)` for the OS signal, then `:root[data-theme="dark"]` and `:root[data-theme="light"]` so an explicit toggle wins in both directions. Keep all three in sync when adding a colour. Every colour is a `--var` — never hardcode a hex outside the `:root` blocks, or dark mode breaks silently on one page.

## The file:// constraint

These pages are read straight off disk, with no build step and no server.

- **External CSS over `file://` works.** Verified: the stylesheet loads and applies.
- **External JS over `file://` is not reliably executed.** It fetches `200 OK` and never runs in some viewers, while inline scripts run fine. So any script a page needs stays **inline**. This is why the click handler is not in a shared `.js` file next to the shared `.css`.
- No `fetch`, no ES modules, no CDN. Nothing that needs an origin.

Consequence for verification: a rendered-in-browser check may show a **stale** page — force a fresh load with a cache-busting query (`?v=2`) rather than trusting a reload, and confirm what is on disk with `grep` before concluding a change did not work.
