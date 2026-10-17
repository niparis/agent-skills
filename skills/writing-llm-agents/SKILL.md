---
name: writing-llm-agents
description: Design, review and debug LLM agent call sites — output schemas, prompts, deterministic gates and verifiers, LLM-as-judge, retries, model fallbacks and failure isolation. Use when writing a new agent call or pipeline stage that calls a model; when reviewing or refactoring existing agent code; when a pipeline drops or rejects more model output than expected; when a model returns empty objects, wrong-shaped fields or unparseable values; when designing an LLM-as-judge or a rubric; when deciding retry, fallback or abort policy for flaky model calls; when a prompt and a validator seem to disagree; or when making agent code portable across models and providers.
---

# Writing LLM agents

An agent call site is three things: a **contract** (what the model is told to emit), a
**gate** (what you check before trusting it), and a **failure policy** (what happens when
it goes wrong). Almost every expensive bug lives in the seams between them, not inside any
one of them.

Everything here comes from production incidents with the numbers attached. Prefer the
measured example to the general principle when writing code.

## The checklist

Run this before shipping any agent call, and when reviewing one.

**Contract**
- [ ] Output is a **typed schema**, never `dict` / `list[dict]` / `Any`. An untyped
      contract compiles to an object schema with no properties — a strict-schema model
      correctly returns `{}` and you will blame the model.
- [ ] Required fields are only what a caller reads; everything else permissive
      (`extra="allow"`). Type the skeleton, not the grammar.
- [ ] The schema's field names **match what the prompt asks for**.
- [ ] Every model value is **coerced before it is compared** to anything.
- [ ] Model settings are bound to the model, not passed per call.

**Gate**
- [ ] No semantic property is enforced by lexical/token matching.
- [ ] **Could output that perfectly obeys the prompt fail this gate?** Construct the ideal
      output by hand and run the gate on it.
- [ ] Where provenance matters, the model **declares** it and the gate checks the
      declaration — never infer it from wording.
- [ ] Variant-specific rules live in one table keyed by variant, not an `if` cascade.
- [ ] Every rule the spec states is enforced somewhere; no computed-and-never-read
      validation.

**Failure policy**
- [ ] Written down: for each failure mode, how far the damage travels.
- [ ] A flaky call **degrades** the run; only a *rate* aborts it — with a floor as well as
      a share.
- [ ] Output-conformance failures retry on a **different model**; content retries and
      transport errors do not.
- [ ] New or optional capability cannot gate what already works, and a test injects a
      failure into it to prove that.
- [ ] Drops are recorded as a **partition of typed reasons**, and the log survives
      promotion.

**Judge** (if there is one)
- [ ] Gets the source material, enforced by raising when it is missing.
- [ ] Key-blind, and **never shown your prior** — expectations are checked in aggregate.
- [ ] Every rubric key rates something the judge can actually see.
- [ ] A second judge is a different model, not a second sample.
- [ ] You have checked whether the judge is even the bottleneck.

## Reference material

Read the file that matches the task. Each is self-contained.

| File | Read when |
|---|---|
| [references/output-contracts.md](references/output-contracts.md) | Declaring output types, writing coercers, setting model params (`reasoning_effort`, `max_tokens`) |
| [references/gates.md](references/gates.md) | Writing or debugging deterministic verification; a gate rejects output that looks fine |
| [references/judges.md](references/judges.md) | Building an LLM-as-judge, a rubric, or a second-opinion pass |
| [references/failure-isolation.md](references/failure-isolation.md) | Retry, fallback and abort policy; optional stages; drop logging |
| [references/debugging-agents.md](references/debugging-agents.md) | A pipeline is dropping too much and the cause is not yet known |

## The static check

`scripts/check_agent_contracts.py` finds the cheap-to-detect smells — untyped output
contracts, comparisons against un-coerced model fields, silent `except Exception`.

```bash
python3 scripts/check_agent_contracts.py <src-dir>            # errors + warnings
python3 scripts/check_agent_contracts.py <src-dir> --quiet    # errors only; exit 1 gates CI
```

Untyped contracts are ERROR (exit 1); the rest are WARN. Wire the `--quiet` invocation
into CI once a codebase is clean — the rule is only worth having if a new agent cannot
quietly reintroduce it.

## Three habits that matter more than any rule

**Measure before fixing.** Plausible causal stories about model behaviour are cheap and
usually wrong, and every one is testable offline against artifacts already on disk. In one
investigation two confidently-argued hypotheses — "extraction regressed to over-long
inputs" and "the model cannot see enough of the text" — were each killed by a single
query, and both would have shipped a fix aimed at the wrong thing. State the hypothesis as
a number, check it, then put the number in the commit message.

**Read the actual outputs.** Drop reasons say which gate fired, not whether it was right.
A tier shipping 0 of 16 looked like a broken generator; reading the items showed
well-formed work that the judges had all passed, and four wrong gates.

**Capture and replay.** Persist real model outputs once, then replay them against changed
gates offline. It turns a paid, non-deterministic run into an instant deterministic test,
produces the before/after number that makes a fix reviewable (`2/18 → 16/18`), and shows
when to stop — the items that *should* still fail, still fail.

## When the model looks like the problem

It usually is not. Walk the seams first: prompt vs gate, prompt vs schema, compare before
coerce, an invariant scoped too wide, post-processing that invalidates a check. In one
full investigation every finding was in a seam and none was the model. The single time a
model genuinely looked incapable — returning `[{}]` where another returned complete output
— the cause was an untyped schema on our side, and the same model produced perfect output
the moment the contract was declared.
