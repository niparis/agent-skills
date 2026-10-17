# Debugging an agent pipeline

The failure is usually not where the error message points, and it is usually not the
model.

- [Measure before fixing](#measure-before-fixing)
- [Read the actual outputs](#read-the-actual-outputs)
- [Is the gate wrong, or the model?](#is-the-gate-wrong-or-the-model)
- [Capture and replay](#capture-and-replay)
- [Suspect the seams](#suspect-the-seams)

## Measure before fixing

Plausible causal stories about model behaviour are cheap and usually wrong. Every one is
testable offline against artifacts you already have. Test it.

Two hypotheses from a single investigation, both confidently argued, both **disproven by
one query each**:

**"Extraction regressed — the source entries are too long."** The dropped items did have
longer source entries than the shipped ones. But checking every corpus that had ever run:

| corpus | entries ≥10 tokens | drop rate |
|---|---|---|
| A | 79% | **15%** |
| B | 91% | **15%** |
| C | 85% | **20%** |
| D (the one under investigation) | 86% | **53%** |

Long entries were the norm everywhere and three of four corpora were fine. Length did not
drive the drop rate. A schema constraint built on that reading would have been a fix aimed
at a misattribution.

**"The model can only see 47% of the text it's matched against, so it can't reproduce
it."** True about the truncation, and the arithmetic still killed it: if the model echoed
*verbatim* the 60 characters it could see, **92%** of those options would have passed the
gate anyway. Truncation was a minor contributor, not the cause.

Both took one script. Both would have shipped the wrong fix.

**The habit:** before writing a fix, state the hypothesis as a number you can check
against existing artifacts, and check it. If it survives, the fix is grounded and the
number belongs in the commit message.

## Read the actual outputs

Drop *reasons* tell you which gate fired. They do not tell you whether the gate was right.
For that you have to look at the item.

A tier shipping 0 of 16 looked like a broken generator. Reading the questions showed
well-formed, genuinely multi-fact items that any examiner would recognise — and the
judges had passed **every one** on the rubric. The generator was fine; four gates were
wrong.

If the artifacts of failed items are not persisted (they usually aren't — only successes
get written), re-run the sub-stage in isolation and dump them. A few dollars of model
calls to see the actual text is always worth it.

## Is the gate wrong, or the model?

Fastest discriminators, in order:

1. **Do the judges pass it?** If a semantic judge reading the source material says the
   output is sound while a deterministic gate rejects it, suspect the gate.
2. **Does the failure rate correlate with something structural** — the length of the text
   being matched, the variant, the presence of a field? A gate that fails in proportion to
   an incidental property is measuring that property, not the thing you care about.
3. **Could output that perfectly obeys the prompt fail this gate?** Construct the ideal
   output by hand and run the gate on it. If it fails, the gate contradicts the prompt.
4. **Is the "wrong" output actually right in the wrong shape?** Run the coercion question:
   does the content resolve if you interpret the format differently? (`5` → `…-F005`
   resolved 25 of 28.)

## Capture and replay

The highest-leverage tool in this domain: **capture real model outputs once, then replay
them against changed gates offline.**

It converts a 5-minute, paid, non-deterministic run into an instant, free, deterministic
test — and it lets you quantify a fix before shipping it:

```
scenario tier: 2/18 pass verify   (before)
scenario tier: 16/18 pass verify  (after; the 2 remaining are legitimate)
```

That number is what makes a fix defensible in review, and it is what tells you when to
*stop* — the 2 that still fail should still fail.

Keep the captured outputs. They become regression fixtures for exactly the failures that
actually occurred.

## Suspect the seams

In a pipeline of deterministic → agentic → deterministic stages, most real bugs are in the
joins, not in any component:

- **Prompt says one thing, gate enforces another.** See gates.md.
- **Prompt asks for key `X`, schema declares field `Y`.**
- **A field is computed and never read** — dead validation that the docs claim as a
  guarantee.
- **An invariant scoped too widely** — a rule written for one tier silently applying to a
  new one.
- **A value compared before coercion** — the shape mismatch that reads as a content
  disagreement.
- **Post-processing that invalidates a check.** If output is shuffled or reordered after
  verification, re-running the verifier on the stored artifact will produce failures that
  never existed at generation time. Know which of your checks are order-dependent before
  concluding you have found a regression.

When something looks like a model quality problem, walk the seams first. In one
investigation, every single finding — four gate defects, a contradictory prompt, an
untyped output contract, an abort-on-first-flake — was in a seam. None was the model.
