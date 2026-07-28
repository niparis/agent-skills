---
name: extract-factbank
description: >-
  Extract an examinable fact bank from a textbook/source chapter into validated
  JSONL + a clusters sidecar, then optionally build study sheets. Use whenever
  the task is turning a professional/study textbook (regulatory, medical,
  technical, exam-prep) into structured, testable facts — e.g. "extract facts
  from chapter N", "build the fact bank for a subject", "add chapter N as we did
  before", "split this study PDF into chapters", or generating cram/cheat sheets
  or question banks from a source. Subject-agnostic: per-subject conventions live
  in profile.json, so it works for any new textbook, not just an existing one.
---

# Extract fact bank

Turn a source chapter into a **validated, examinable fact bank**: one JSONL of
atomic facts + a clusters sidecar, mechanically checked, ready to drive cheat
sheets and question banks.

**Golden rule — the source chapter is the ONLY source of truth.** Every fact
cites a page in the chapter. Never import facts from outside knowledge, mock
exams, or web searches. (Mock exams, if any, are a *coverage lens* applied
after extraction — never a source of facts.)

**Where things live.** This skill orchestrates; the canonical spec and scripts
live **once**, in the textbooks workspace (run the skill from there). Paths
below are relative to that workspace root. Do not copy these files per subject —
reuse the single canonical copy so the methodology cannot drift.

## The spec lives in two workspace files — read them first

These are normative. Read both before extracting; do not restate or fork them.

- **`pipeline/src/factbank/specs/fact-schema.md`** — the record schema (every field, enums), the
  `numeric` discipline, the two sidecars, the verification checklist. This is the
  contract `validate.py` enforces.
- **`pipeline/src/factbank/specs/facts-extraction-methodology.md`** — the workflow and
  extraction/verification principles (atomicity, provenance, fact taxonomy,
  dedup).

## Layout (per subject)

```
<subject>/
  chapters/                 # per-chapter source PDFs
  facts/
    profile.json            # per-subject conventions (EDIT this per subject)
    chapter-NN.jsonl        # the facts — one JSON object per line
    chapter-NN.clusters.json# thematic clusters + icons + confusion-pairs
```

`profile.json` is the only file that is subject-specific by design. To start a
new subject, copy an existing `profile.json` and edit `source`, `id_pattern`,
`chapters`, `tag_vocabulary`, and the difficulty scales.

## Workflow

Run these in order. Do not skip the validation gate.

### 1. Split the source PDF into chapters (once per book)

Bookmarks are often broken; detect chapters from running-header text instead.

```bash
# Review boundaries first — writes nothing:
python3 split_textbook.py "<book>.pdf" --out <subject>/chapters \
    --skip-pages N --strategy headers --dry-run
# When the chapter table looks right, drop --dry-run.
```

Tune `--skip-pages` (front-matter/TOC to ignore) and add `--pattern '<regex>'`
if the header wording differs (capture the chapter number in group 1). Use
`--strategy headers` when bookmarks resolve to the wrong pages (e.g. the TOC).

### 2. Read the chapter and map its numbered sections

Extract the chapter text and identify the numbered top-level sections/topics
(1, 2, 3, …) and their sub-paragraphs. These numbered topics become the `S`
grouping in fact ids (see conventions below). Work one section at a time; never
split a table, list, definition, or example across facts.

### 3. Build the fact bank via a generator script (do NOT hand-write JSONL)

Write a short Python builder in a scratch dir that defines the records with one
helper `F(...)` and emits `chapter-NN.jsonl` + `chapter-NN.clusters.json`. This
keeps common fields consistent and makes edits/re-runs cheap. Follow the schema
in `pipeline/src/factbank/specs/fact-schema.md` exactly.

### 4. Validate — HARD GATE (Definition of Done)

```bash
# One canonical validator (currently tools/validate.py — the reference
# instance) serves any subject via --facts-dir:
python3 tools/validate.py --facts-dir <subject>/facts --chapter NN
```

Extraction is **not done** until this exits `0 error(s)`. It enforces: required
fields, enums, `numeric` discipline, cluster/confusion-pair/`confused_with`
integrity, fact_id shape + source/chapter consistency, contiguous `F` sequences,
the exam_difficulty policy, and a skipped-section tripwire. Then do the
editorial review in `pipeline/src/factbank/specs/fact-schema.md` (atomicity, no over-generalised
examples, no recommendation upgraded to a requirement, accurate distractors).

### 5. Register the chapter + generate study material (optional/downstream)

Add the chapter's title to `profile.json` `chapters`, then run the subject's
`generate_study.py` (lives in `<subject>/facts/`) to build the cheat sheet.
Question generation is a **separate later pass** that consumes the *approved*
facts — not part of extraction.

## Conventions that are easy to get wrong (make them explicit)

- **fact_id** `= <SOURCE>-C<NN>-S<gg>-F<nnn>`. The `S` number is the **numbered
  top-level topic** (S02 = topic 2), zero-padded — *not* the sub-paragraph. `F`
  is a contiguous 001-based sequence **within that topic**. The record's
  `section` field still holds the fine sub-paragraph label (e.g. "9.2").
- **`confused_with` must reference ids in the SAME chapter file.** Cross-chapter
  references fail validation. Capture cross-chapter links via `tags`/prose, not
  `confused_with`.
- **Penalty/threshold facts go in their TOPICAL cluster**, not a "numbers"
  cluster. The cheat sheet's key-figures/key-dates tables are driven purely by
  the `numeric` block (`kind` threshold/deadline/penalty/date), so no dedicated
  numbers cluster is needed.
- **Every cluster used by a fact needs an entry in `icons`** (validator warns).
- **`numeric` only for figures a candidate must recall & apply.** Counts of an
  enumeration ("the four principles"), rule-embedded numbers ("one-principal
  rule"), and "all N conditions" get **no** `numeric` block — the number lives
  in the `fact` text. See the numeric-discipline table in the schema.
- **Extract principles/named enumerations as a COMPLETE, `framework`-tagged
  set.** Check the source chapter for a dedicated principles section (e.g. RES5
  Ch.1 §3 "Principles of the FAA and FAR") before settling the tag set. Extract
  the enumerating fact (the members) *plus* one fact per member's meaning —
  including counter-intuitive rationale ("independence not borne out →
  reasonable basis prioritised instead"), which summaries drop and exams test.
  Tag them all `framework`; they drive the cheat sheet's "Principles &
  frameworks" section (the complement of the numeric discipline — enumeration
  counts have no `numeric`, the tag is their hook onto the digest). Mirror rule
  + inclusion test: `pipeline/src/factbank/specs/fact-schema.md` → "Reserved tag: `framework`".
- **`pages` stores the label exactly as printed in the source.** Some sources
  paginate per chapter (RES5's folio `1-5` = chapter 1, page 5 — not a range).
  Keep the raw folio in the data for look-up fidelity; the display layer
  (`fmt_pages` in `generate_study.py`) renders it unambiguously as
  `Ch. 1, p. 5`. Never render the raw `p.1-5` form in study output.

## Recorded decisions (apply consistently across chapters)

- **Mock-exam calibration is OFF by default.** Only calibrate against a *real*
  exam/question bank the user supplies. Do not generate mock questions to
  calibrate against — that is circular and risks contaminating facts.
- **`exam_difficulty`**: set it on every fact only when a real calibration exam
  exists; otherwise `null` on every fact. A mix of null and set is a validation
  ERROR (drift signal).
