# Failure isolation

Model calls fail constantly and unrepeatably. The design question is never "will this
fail" but **how far does one failure travel**.

- [The failure ladder](#the-failure-ladder)
- [Degrade the run, do not end it](#degrade-the-run-do-not-end-it)
- [Retry conformance failures on a different model](#retry-conformance-failures-on-a-different-model)
- [New capability must never gate what already works](#new-capability-must-never-gate-what-already-works)
- [Drops are data](#drops-are-data)

## The failure ladder

Write down, for each failure mode, exactly how far the damage travels. This is a design
artifact, not documentation — the act of filling it in is what surfaces the rung that is
wrong.

| what fails | blast radius |
|---|---|
| one output element fails a gate | that item drops with its reason; the rest ship |
| a batch of 10 raises | those 10 become "not authored" drops |
| a call exhausts its output retries | retried once on a different model |
| a sub-stage raises | caught; the stage's earlier output is untouched |
| an entire optional tier raises | caught; the core output ships complete |
| **judgments missing at a rate** | **fatal — but only above a threshold** |

If every rung says "fatal", there is no isolation. If none does, you cannot tell a bad run
from a good one.

## Degrade the run, do not end it

The incident: an invariant said *a question may never ship unjudged*, enforced by aborting
the run if **any** item lacked a judgment. Then three calls out of 154 failed:

```
judge FAILED …S12-F004: UnexpectedModelBehavior: Exceeded maximum output retries (3)
judge FAILED …S19-F002: UnexpectedModelBehavior: Exceeded maximum output retries (3)
FATAL: 2 gating question(s) missing judge results
```

**Three flaky calls destroyed a complete run.** 110 author calls and 154 judge calls had
already been paid for, and the abort fired before anything was written, so none of it was
recoverable or even inspectable.

The invariant was right. The response was wrong. It required the *item* not to ship;
nothing about it required the *run* to die.

Three layers, cheapest first:

1. **Fall back** (see below).
2. **Drop** the item with a first-class reason and continue.
3. **Abort on a rate**, not a count — `max(FLOOR, share)` of the eligible population.

**The floor matters as much as the share.** On a small unit a 5% share rounds down to
zero and silently restores the original cliff. Use both.

Corollary: **write artifacts before the fatal.** A run that did all its work and then
aborted should leave something inspectable behind.

## Retry conformance failures on a different model

A retry that re-sends a byte-identical request re-runs the same sampling accident. The
weak version of this fix is nudging temperature; the strong version is changing model.

**Scope it to the failure class where it helps.** Not all retries are equal:

| failure | fallback? | why |
|---|---|---|
| output-validator exhausted its budget | **yes** | structured-output conformance; models differ idiosyncratically here and feedback helps least |
| content gate rejected (retry carries the violation text) | **no** | not byte-identical — the model has new information; switching discards it |
| transport / rate limit / timeout | **no** | an infrastructure axis, not an idiosyncrasy one |
| content-policy refusal | **no** | a different model rarely helps and may be worse |

```python
try:
    return await call(item, role=role)
except UnexpectedModelBehavior as e:          # validator ran out of retries
    alt = fallback_model(role)
    if alt == model_name(role):
        raise
    result = await call(item, role=role, model_override=alt)
    result["model"] = alt                     # provenance travels with the output
    result["model_fallback"] = True
    return result
```

Two things this must do beyond retrying:

- **Record which model produced the output**, per item, written only when it differs from
  the run's declared model. Where the model is part of the *measurement* — any judge, any
  rating — a silent substitution quietly mixes provenance inside one artifact.
- **Count fallbacks in the run metadata.** A rising rate means the prompt or the output
  schema fits the primary model badly, which is exactly what a silent fallback hides.

Make the alternate **configurable per role**, so a proxy that stops serving your default
does not turn the fallback into a second, slower failure. For a judge the natural
alternate is its counterpart model; for an author, prefer a different *family*, since what
you are routing around is the model's structured-output habits.

## New capability must never gate what already works

When adding a tier, mode, or optional stage, wrap it so that its total failure is a
non-event for everything that already shipped:

```python
scenarios, items, authored = [], [], []
try:
    scenarios, items, authored = await build_optional_tier(...)
except Exception as e:
    print(f"  optional tier FAILED ({type(e).__name__}: {e}) — continuing without it")
    tier_failure = f"{type(e).__name__}: {e}"
```

Put the wrapper around **generation**, not just around consumption of the results, or a
crash while producing them escapes it.

And scope any existing hard invariant so it does not extend to the new thing by default —
an invariant written for gating output should not suddenly let an experimental tier kill
the run.

Make this an explicit acceptance test: **inject an exception into the new tier and assert
the run still produces a complete artifact.** It is the property that quietly stops being
true as code grows.

## Drops are data

Every rejected item is a measurement. Treat the drop log as a first-class output.

- **Reasons are a partition**, declared once as a constant, not free-form strings. Counts
  per reason belong in the run metadata; the per-item detail belongs in the log.
- **Never name a count for one cause when it holds several.** A field called
  `dropped_by_judge` that actually counted every drop made the judge look like the problem
  for as long as it existed. Delete a misleading name rather than aliasing it.
- **The log must survive promotion.** A drop log left behind in a temp or run directory
  cannot answer "was it the judge or the gates?" — the question you will have first.
- **A short output is now a normal outcome.** Anything consuming the artifact must not
  infer failure from a count below the plan; the reason partition is the authority.
