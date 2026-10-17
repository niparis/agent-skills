# LLM-as-judge

A second model rating the first one's output. Cheap and useful, and easy to build so that
it measures nothing.

- [Give the judge the material, and enforce it](#give-the-judge-the-material-and-enforce-it)
- [Never show the judge your prior](#never-show-the-judge-your-prior)
- [Every rubric key must rate something](#every-rubric-key-must-rate-something)
- [Judge diversity is not two samples](#judge-diversity-is-not-two-samples)
- [Thresholds are a function of the scale](#thresholds-are-a-function-of-the-scale)
- [Check whether the judge is even the bottleneck](#check-whether-the-judge-is-even-the-bottleneck)

## Give the judge the material, and enforce it

An open-book judge without the book silently becomes a **world-knowledge judge** — it
still answers, still sounds confident, and now disagrees with your source. Observed live:
with the cited material accidentally omitted, a judge "disagreed" with the bank from
general knowledge and gutted every numeric item.

Make it structurally impossible rather than hoping:

```python
cited = [f for f in facts if f["fact_id"] in item.get("fact_ids", [])]
if not cited:
    raise RuntimeError(
        f"judge called with no cited material for {item.get('qid','?')} — "
        f"the open-book judge requires it")
```

Keep the judge **key-blind**: it answers the question itself, and its answer is compared
to the key afterwards. A judge shown the key rates the key.

## Never show the judge your prior

If you have a deterministic expectation (a tier, a difficulty prior, a predicted label),
**do not put it in the prompt**. Models comply with framing. The rating stops being an
independent measurement, and it stops being able to detect the thing the prior exists to
detect.

The trap in full: a tier-derived difficulty prior (`scenario→Hard`) was going to be shown
to the judge so it could "confirm or move it". But the anomaly worth catching is *a
scenario item that is not actually hard* — and a judge told "this should be Hard" says
Hard. The mechanism destroys its own measurement.

Instead:

- Judge blind.
- Keep the expectation as an **aggregate** check: record a per-variant distribution in the
  run metadata and compare after the fact.
- Aggregate is also more actionable. A skew points at a prompt or a predicate; a per-item
  mismatch points at nothing you can fix.

Worked example of the diagnostic that replaces the prior:

| observation | what it means | where the fix is |
|---|---|---|
| scenario tier skews Easy | the tier is not producing what it was built for | the scenario/authoring prompts |
| composite tier skews Easy | composed keys are resolvable from a single input | the composition predicates |
| recall tier skews Hard | the judge's scale is miscalibrated for this corpus | the rubric wording |

Also: **the rubric wording is the only calibration the judge gets.** It must describe the
output's demands, never name the variant it came from — a judge that can infer the tier
from the prompt is anchored just as effectively as one handed the prior.

## Every rubric key must rate something

A live rubric contained `difficulty_sane: "does the difficulty match the content?"` — but
the judge was never shown a difficulty, and the field it referred to was a hardcoded
constant. **The key rated nothing** and had done so since it was written.

When adding a rubric key, check that the judge can actually see what it is being asked to
rate. Then check that something downstream reads the answer.

## Judge diversity is not two samples

Two calls to the same model with the same prompt is close to a duplicate sample, not a
second opinion. If you want a second judge, use a **different model** — ideally a
different family.

The corollary matters for reconciliation: different models drift systematically. Two
judges one step apart on a scale is a property of the model pair, not of the item.

## Thresholds are a function of the scale

On a 3-point scale (Easy/Medium/Hard), distances are 0, 1, 2 only:

- **1 step is the resolution limit of the instrument.** Adjacent-category disagreement is
  the normal condition even between careful human raters, and two different models will
  produce it systematically.
- **2 steps is maximal disagreement** — the judges did not read the same thing.

So drop on 2, not on 1. If you want a finer trigger, **widen the scale to 5 points** —
do not tighten the threshold on a 3-point one.

Same reasoning applies to a prior-vs-judge distance if you ever compare them offline.

## Check whether the judge is even the bottleneck

Before investing in judge quality, find out what is actually rejecting output. Structured
drop reasons made this answerable in one run:

| cause | share of drops |
|---|---|
| deterministic verify | **82%** |
| judge — wrong key | 10% |
| judge — rubric | 8% |

The judge was not the problem; the verifier was. Without the partition, months of judge
tuning would have been aimed at 18% of the failures.

**Do not gate a question on an unvalidated judge signal.** If nothing downstream reads a
rating yet, a rating that disagrees with expectation should be *recorded*, not turned into
a drop. Dropping output that passed every other gate, on the basis of a scale you have not
validated, destroys work to enforce a preference.
