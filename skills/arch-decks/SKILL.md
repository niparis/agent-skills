---
name: agentic-architecture-design
description: Use this skill to generate well-branded interfaces and assets for the Standard Chartered "Agentic Architecture" deck system — software-architecture and platform-strategy slides — for production or throwaway prototypes/mocks. Contains essential design guidelines, colors, type, fonts, and reusable slide + component templates for prototyping.
user-invocable: true
---

Read the `README.md` file within this skill, and explore the other available files.

This is a **slide-deck design language** (not a product UI). The brand encodes a single idea
visually: **green = execution / federated**, **navy = governance / central**, **red = a rejected
alternative**. The signature dual underline bar (navy | green) at the foot of every slide is a
literal encoding of that split — keep it.

**Foundations**
- `colors_and_type.css` — all tokens (color, type, spacing, radii) + semantic type roles.
- `components.css` — reusable component vocabulary (pills, badges, cards, decision table, dual bar).
- Fonts: **DM Sans** (body at weight 300) + **DM Mono**, both from Google Fonts (CDN link in the CSS header).

**Slide templates** (`slides/`)
- `index.html` assembles a 7-slide reference deck via `deck-stage.js`.
- One JSX component per archetype: `TitleSlide`, `SectionDividerSlide`, `StatementSlide`,
  `ThreeColumnSlide`, `ArchitectureSlide`, `ProcessSlide`, `DecisionTableSlide`, plus shared
  primitives in `SlideKit.jsx`. Compose new decks from these.

**Previews** (`preview/`) — small specimen cards documenting palette, type, and each component.

If creating visual artifacts (slides, mocks, throwaway prototypes), copy assets out and create
static HTML files for the user to view. If working on production code, copy the CSS and read the
rules here to design fluently in this brand.

If the user invokes this skill without other guidance, ask what they want to build, ask a few
questions, then act as an expert designer who outputs HTML artifacts _or_ production code as needed.

**Voice & rules to honor** (full detail in README):
- Impersonal, declarative, architectural register. British English. Sentence-case titles,
  UPPERCASE wide-tracked labels with a leading green dash.
- Emphasis via **bold** on the load-bearing word; two-tone statements resolve to a green thesis line.
- Negation stated bluntly in red. **No emoji, no icons, no shadows, no gradients, no images.**
- Warm-paper neutrals only (never pure white); hairline 0.5px borders; small radii.
- No bundled logo yet — ask the user for the Standard Chartered wordmark (SVG) if a title/footer needs it.
