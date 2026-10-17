# Output contracts

What the model is *told* to emit, and what happens to it before anything compares it.

- [Type every output](#type-every-output)
- [Type the skeleton, not the grammar](#type-the-skeleton-not-the-grammar)
- [Coerce before comparing](#coerce-before-comparing)
- [When a coercer is right, and when it is a smell](#when-a-coercer-is-right-and-when-it-is-a-smell)
- [Model settings](#model-settings)

## Type every output

`output_type=dict` / `list[dict]` is **not a contract**. It compiles to an object schema
with no properties, so the only thing describing the shape is prose in the system prompt.
A lenient model infers it and complies. A model doing strict schema-guided decoding
correctly emits nothing, because the schema asks for nothing.

Measured, on an author call asked for two questions:

| model | `output_type=list[dict]` | `output_type=list[QuestionDraft]` |
|---|---|---|
| deepseek-v4-flash | 2 complete questions | 2 complete questions |
| gpt-5.6-luna | **`[{}]`** | 2 complete questions |

The model was never the problem. The prose already specified the shape exactly
(`"Output: list of {qid, stem, options: [4], …}"`); a decoder following the schema was
correctly ignoring it.

The failure mode is nasty because it is **silent and model-specific**. Everything works
until someone swaps a model, and then it returns empty objects rather than erroring.

## Type the skeleton, not the grammar

Typing can become its own failure source if it starts rejecting output the pipeline
currently recovers. Two rules:

- `extra="allow"`, and require only the keys a caller actually reads.
- Where a model legitimately varies **and a coercer already does semantic work**, keep
  the field permissive. `chosen: int | str | None` is correct if `coerce_chosen` exists.

Convert to plain dicts at the boundary (`model_dump()`) so gates and downstream code are
untouched. The typing exists for the schema the model is handed, not to restructure the
code that reads it.

**Make the schema agree with the prompt.** If the prompt says `{situation: str}`, the
model field is `situation` — not `text`. A schema disagreeing with its own instructions
is the exact mismatch typing is supposed to remove.

## Coerce before comparing

Models return the right answer in the wrong shape, constantly. Never compare raw model
output to anything.

The canonical incident: a judge returns `chosen` as `"0"` (string) rather than `0`. The
key comparison is `chosen != correct`, so a **correct** judgment is counted as a mis-key
and a good question is dropped. Silent, and it looks like a quality problem.

```python
def coerce_chosen(v) -> int:
    """Normalize to an int index, -1 when unparseable. Live finding: the model
    returns "0" (string), null, or omits the field — an int/str compare then
    counts a correct judge answer as a MIS-KEY. Coerce before any comparison."""
    if isinstance(v, bool):      # bool is an int subclass — check it first
        return -1
    if isinstance(v, int):
        return v
    if isinstance(v, float) and v.is_integer():
        return int(v)
    if isinstance(v, str):
        m = re.search(r"\d", v)
        if m:
            return int(m.group(0))
    return -1
```

Two things this shows beyond the obvious:

- **`bool` before `int`.** `isinstance(True, int)` is `True` in Python; without the guard,
  `True` coerces to option 1.
- **Unparseable is not a value.** `-1` never flows into the comparison — the caller
  retries, because malformed output is not evidence about the question.

Distinguish the two cases explicitly:

| output | meaning | action |
|---|---|---|
| wrong shape, recoverable | model idiosyncrasy | coerce, continue |
| wrong shape, unrecoverable | malformed | retry (then fall back — see failure-isolation.md) |
| right shape, wrong content | a real judgment | act on it |

## When a coercer is right, and when it is a smell

A coercer earns its place when it does work a schema *cannot* express.

Real example: an author was told to emit `options_provenance` as fact-id strings. Across
72 live options it emitted **28 bare ints, 16 lists, 15 id strings, 13 nulls** — 21% of
spec. But the ints were not noise: `5` meant `…-F005`, and matching `F{n:03d}` against the
allowed set resolved **25 of 28**. The explanations cited the ids correctly all along.

That is recovery no schema can do. Keep it.

Conversely, **after** the outputs are typed, reaching for a new coercer should prompt the
question: *should the schema have said this?* Most coercion helpers in an untyped codebase
are repair work for a missing contract, not for genuine model variance.

## Model settings

**Bind settings to the model, not to each call.** Four call sites in one codebase quietly
omitted `model_settings=`, inherited thinking mode, and failed on the forced `tool_choice`
that structured output requires — while the stages that passed settings worked. Building
them into the model factory means a newly written agent cannot forget.

```python
def _make_model(role):
    model = _resolve_provider(model_name(role))
    model._settings = ModelSettings(**_model_settings(role))
    return model
```

**Do not cache the model factory** if settings carry ambient context (session ids, trace
tags). Caching freezes them at construction time.

**Send the field, do not omit it.** Omitting `reasoning_effort` is not the same as asking
for none: a provider whose default enables thinking will then reject the `tool_choice`
that structured output forces, failing every call. Send `"none"` explicitly, and keep an
escape hatch value (`"provider-default"`) for providers that reject `"none"`.

**`max_tokens` is a circuit breaker, not a budget.** Set it well above any legitimate
response and treat hitting it as a runaway, not a truncation to tune. One codebase raised
it to the documented 384K maximum and found the model still looped three times, taking
108s per attempt — a bigger allowance only bought a slower failure.
