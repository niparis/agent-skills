# Agentic Architecture — Design System

A design language for **software-architecture and platform-strategy slide decks**, originally
extracted for **Standard Chartered**. The system codifies the look of a single source deck
(`agentic-architecture 5.html`, slides 1–9) into reusable tokens, components, and slide
templates so future architecture decks render consistently.

This is **not a product UI** — the "product" is the *deck itself*. The deliverables here are
a typographic + color foundation, a component vocabulary (pills, badges, decision tables,
architecture-layer rows, process cards), and a set of ready-to-use 16:9 slide templates.

---

## What this system is for

The source material is a technical strategy narrative: how to run **agentic AI systems** in a
large regulated enterprise. Its central idea — *"Govern centrally, execute where the data
lives"* — drives the entire visual language:

- **Green = execution / federated / local / edge**
- **Navy = governance / central / immutable / control-plane**
- **Red = a rejected alternative / negation** (used sparingly, never decoratively)

The signature **dual underline bar** (navy left, green right) at the foot of every slide is a
literal visual encoding of this central/federated split. Wherever the two-hue logic appears,
it is *semantic*, not aesthetic — pick the color by what the thing *means*.

### Audience & register
Senior engineers, architects, and risk/governance stakeholders at a global bank. The tone is
precise, declarative, and decision-oriented — closer to an architecture decision record (ADR)
than a marketing deck.

---

## Sources

- **`uploads/agentic-architecture-design-system.html`** — the canonical design-system export
  this project was built from. Contains the full token set, every component, and a complete
  example slide. Treat it as the source of truth if anything here conflicts.
- Originating deck: `agentic-architecture 5.html` (slides 1–9) — *not included in this
  project*; referenced only.

> ⚠️ **No brand logo was provided.** Standard Chartered's official wordmark / brandmark is not
> in this project, so slide templates use a neutral text lockup placeholder. **If you want the
> real logo on title and footer slides, please upload the Standard Chartered logo (SVG
> preferred).** See [Iconography](#iconography).

---

## CONTENT FUNDAMENTALS

How copy is written in this system. Match this voice when authoring new slides.

**Voice: declarative, architectural, decisive.** Slides assert a position and defend it. The
register is that of a senior architect writing a decision record — confident, terse, allergic
to fluff.

**Person.** Largely **impersonal / third-person**. The subject is the system, not the speaker:
*"A central gateway governs every agent."* "The gateway **decides**; the app boundary
**enforces and runs**." Almost never "we" or "you."

**Sentence shape.** Short, parallel, often three-part. Verb-forward. Emphasis carried by
**bold** on the load-bearing word (`fixed`, `tuned`, `built locally`, `decides`, `executes`),
not by adjectives. Example: *"What stays **fixed**, what is **tuned**, and what is **built
locally** is decided once."*

**Two-tone statements.** Big statement lines run dark, then resolve to a single **green**
summary line — the thesis. e.g. *"Control is centralised; data and tools are not."* The green
line is always the takeaway.

**Negation pattern.** Rejected alternatives are stated bluntly, in **red**, as consequences:
*"Decentralised policy only. Unenforceable; kill switch becomes theatre."* / *"Central
tool-broker. Honeypot, breaks app identity, residency bleed."* Note the rhythm: name the
alternative → fragment listing why it fails.

**Casing.**
- Slide titles & statements: **sentence case** ("Govern centrally, execute where the data lives").
- Labels, badges, table headers, legends, section labels: **UPPERCASE** with wide letter-spacing
  (`+0.1–0.14em`).
- Section labels carry a leading green dash: `— THE GOVERNANCE MODEL`.

**Spelling.** **British English** (centralis**e**d, summaris**e**rs, optimis**e**). Keep it.

**Technical density is welcome.** Real product/tool names appear as mono tags and are not
diluted: *Postgres + pgvector, LangGraph, Pydantic AI, MCP, A2A, Temporal, Azure AI Foundry,
Bedrock, Databricks, SKE / ServiceBench / AKS*. Use the actual names; don't generalise to
"a database" or "a framework."

**No emoji.** None. (One typographic `✦` glyph appears as a "preferred / starred" marker on a
tag — that is the only decorative mark, and it is optional.) No exclamation marks. No hype words
("revolutionary", "seamless", "powerful"). Numbers are concrete or absent — no invented stats.

**Vibe:** an immutable core, calmly defended. Engineering seriousness on warm paper.

---

## VISUAL FOUNDATIONS

**Palette.** A disciplined two-hue brand on a warm-paper neutral family.
- **Forest green** `#2D6A2D` (primary), `#3B7A3B` (accent/bold), `#4A8F3F` (light/hover).
- **Deep navy** `#1B2A6B` (primary), `#0F1B4C` (high-contrast dark).
- **Red** `#C0392B` — negation only.
- **Neutrals:** warm paper `#F5F3EC` background, `#EDEAE0` surface, `#F0EEE7` card,
  `#D0CCC0` border, `#E0DDD4` subtle divider.
- **Text:** `#111111` primary, `#444444` body, `#888880` muted.
The neutrals are intentionally *warm* (paper, not white/grey). Never put content on pure white.

**Typography.** Two Google fonts, tight scale.
- **DM Sans** for everything structural — display 700, headings 600, **body at weight 300**
  (light body is a defining trait), bold emphasis 600.
- **DM Mono** for tags, technical names, slide numbers, captions, code-like metadata.
- Display tracking is negative (`-0.01 to -0.02em`); label tracking is wide positive
  (`+0.08 to +0.14em`, uppercase). Scale: 48 hero / 26 h1 / 22 statement / 17 col-title /
  14 body / 13 card-title / 9–11 mono+labels.

**Backgrounds.** Flat warm paper. **No images, no gradients, no textures, no patterns.** The
page is calm and matte; all energy comes from type, the two hues, and the dual bar. Section
slides may invert to a navy or green field, but the default is paper.

**Borders & hairlines.** The signature detail: **0.5px borders** everywhere (`--border`).
Hairline-thin, never 1px+. Dividers use the even-subtler `--border-subtle`. This thinness is
load-bearing to the "precise/technical" feel — keep it.

**Corner radii.** Small and restrained. `4px` (badges/tags), `6px` (arch rows), `8px` (cards),
`12px` (slide frame), `100px` (concept pills only). Filled navy badges are *squared* (4px) to
read as "hard constraint"; outlined concept pills are *fully rounded* to read as "idea."

**Shadows / elevation.** **None.** There is no drop-shadow system. Elevation is communicated by
**fill + 0.5px border**, never by shadow. Cards are flat planes on paper. Do not add shadows.

**The dual bar.** A 2px-tall split bar (navy | green) at the bottom of every slide. It is the
brand's one persistent motif. Always full-width, always navy-then-green, always 2px.

**Pills, badges & tags — the vocabulary.**
- `.pill` — mono, outlined, fully rounded → a *concept / principle*.
- `.pill-filled` — navy fill, white, squared, uppercase → a *non-negotiable constraint*.
- `.pill-ghost` — outlined, uppercase, muted → a *metadata marker*.
- `.badge-label` — mono, light surface fill, tiny caps → an *inline annotation*.
- `.arch-badge-center` (navy) / `.arch-badge-fed` (green) → *layer role* on architecture rows.

**Cards.** Flat `--surface-card` fill, 0.5px border, 8px radius, no shadow. Variants:
process-card (numbered step, mono number top-right, footer badge), col-card (uppercase header
→ title → body, header underlined with subtle hairline), arch-row (label | layer name |
mono tag cluster | role badge).

**Tables.** `.ds-table` — navy header band, white uppercase header text, 0.5px row dividers,
first column emphasized, a dedicated **red "Alternative Rejected"** column. This three-column
decision table (Decision / Why / Alternative Rejected) is the system's argument structure.

**Layout rules.** Slides are built on a vertical stack: section-label → h1 → body lede →
content (3-col grid, arch stack, or table) → optional pill row → slide number (mono, right
aligned) → dual bar. Generous left/top padding (~40px), content max-width ~580–600px for lede
text. Three-column grids and `auto-fit` card grids are the workhorses.

**Hover / press / animation.** The source is a static deck — there is **no defined motion or
interaction system**. For interactive recreations, keep it minimal and in-character: hover =
slight darken toward `--g-light` / `--navy-dark` or a border-color shift to the brand hue;
press = subtle opacity (~0.9), no bounce. **No large transitions, no parallax, no easing
flourishes.** If in doubt, animate nothing.

**Transparency & blur.** Not used. Everything is opaque on paper.

**Imagery mood.** N/A — the system is text-and-token driven. If imagery is ever introduced,
it should be restrained and matte to match the paper feel; ask before adding any.

---

## ICONOGRAPHY

**There is effectively no icon system.** This is a deliberate, near-iconless visual language —
meaning is carried by *color, type, and small geometric marks*, not pictograms.

- **No icon font, no SVG icon set, no PNG icons** appear in the source. Do not introduce a
  pictographic icon set (Lucide, Heroicons, Font Awesome, etc.) — it would be off-brand.
- **Geometric marks only:**
  - **Legend dots** — 12px navy/green rounded squares (`.dot`), the only recurring "icon."
  - **Green dash** — the 20×1.5px rule prefixing every section label.
  - **Dual bar** — the 2px navy|green footer split.
- **One glyph:** `✦` (U+2726) used optionally as a "preferred / starred" marker on a tag
  (e.g. *Pydantic AI ✦*). This is the only decorative character. Unicode `→` and `·` (middot)
  are used as inline connectors in tags (*"Azure AI Foundry → candidate control-plane impl."*,
  *"Runtime · AI Platform"*). These are typographic, not icons.
- **No emoji**, ever.

**If you need a logo:** none is bundled (see [Sources](#sources)). Upload the Standard
Chartered wordmark/brandmark as SVG and place it in `assets/`; title and footer templates have
a placeholder lockup ready to swap.

**Guidance:** when extending the system, resist adding icons. If a concept needs marking, reach
for a colored dot, a badge, a mono tag, or the dash — not a glyph.

---

## INDEX — what's in this folder

**Foundations**
- `README.md` — this file (context, content + visual foundations, iconography, manifest).
- `colors_and_type.css` — all design tokens (color, type, spacing, radii) + semantic type roles.
- `components.css` — the reusable component vocabulary (pills, badges, cards, tables, dual bar).
- `SKILL.md` — agent-skill front-matter so this system can be used as a Claude/Claude Code skill.

**Previews** (populate the Design System tab)
- `preview/*.html` — small specimen cards: palettes, type scale, pills, badges, cards, table,
  dual bar, spacing/radii.

**Slide templates** (the main deliverable — 16:9, 1280×720)
- `slides/index.html` — interactive deck assembling all templates with prev/next nav.
- `slides/*.jsx` — one component per slide archetype (title, statement, three-column,
  architecture-layer, process, decision-table, section divider).

**Assets**
- `assets/` — logos and any bundled imagery. *(Currently empty pending the brand logo.)*

> Quick start: link `colors_and_type.css` then `components.css`, load DM Sans + DM Mono from
> Google Fonts, and compose slides from the classes documented above. The example slide at the
> bottom of `uploads/agentic-architecture-design-system.html` is the canonical reference layout.
