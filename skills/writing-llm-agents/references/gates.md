# Gates and verification

Deterministic checks on model output. The most expensive bugs in an agent pipeline live
here — not in the prompt, and not in the model.

- [Never gate a semantic property with lexical matching](#never-gate-a-semantic-property-with-lexical-matching)
- [The prompt and the gate must not contradict](#the-prompt-and-the-gate-must-not-contradict)
- [Declared provenance beats inferred provenance](#declared-provenance-beats-inferred-provenance)
- [Gate profiles per variant](#gate-profiles-per-variant)
- [Enforce the rules you already wrote down](#enforce-the-rules-you-already-wrote-down)
- [Dead validation is worse than none](#dead-validation-is-worse-than-none)

## Never gate a semantic property with lexical matching

The property you want is usually semantic — *this wrong answer came from the approved
list*, *this claim is grounded in the source*. Token overlap is the obvious deterministic
proxy, and it is the wrong instrument. It cannot express "came from" across a
compression, a paraphrase, or a synonym.

Two independent failures of the same root, both measured:

**Case 1 — options that *assess* rather than restate.** The gate required an option to
token-contain the fact it declared. Of 15 options with a valid declared fact, containment
against the full fact text passed **0**. Against the fact's short `topic`, only **40%**.
A recall option restates a fact; a scenario option judges one ("It violates the standard
because an opinion must be unambiguously stated…"). A long proposition cannot be contained
in a short judgment. No threshold fixes this — it is structural.

**Case 2 — options that *compress*.** The same gate on another tier accounted for **55 of
67 drops**. The signature was unmistakable:

| | median source-text length |
|---|---|
| items that dropped | **14 tokens** |
| items that shipped | **7 tokens** |

and exactly **1 of the 55** was a numeric item — because numeric sources are bare figures
("S$50,000") that survive trimming and match on shared digits.

**The tell:** the gate fails in proportion to how much shared framing the source text
carries. If a failure rate correlates with the *length* of the thing being matched, the
matching is the bug.

The fix is not a lower threshold. It is to stop matching (see declared provenance below)
and move the semantic judgment to a judge.

## The prompt and the gate must not contradict

This is the highest-value review question for any agent call site:

> **Can output that perfectly obeys the prompt fail the gate?**

If yes, one of them is wrong, and you are penalising the model for compliance.

The canonical incident. The prompt said:

> SHARED CONTEXT GOES IN THE STEM … let each option carry ONLY the distinguishing part.
> Options should read as tight parallel phrases, not restated sentences.

The gate required each option to contain ≥50% of its source entry's tokens — and the
source entries were full propositions carrying exactly that shared framing. An option that
obeyed the prompt kept only the distinguishing clause and scored 25%.

Concretely:

- source: *"Where a licensed financial adviser has not reported a suspicious activity or
  incident of fraud to MAS, it shall **notify MAS of the reasons orally**."*
- author wrote: *"It shall **notify the Authority of the reasons** for non-reporting."*

Correct use of the source, compressed as instructed, synonym substituted. Dropped.

Both instructions were individually reasonable. Nobody read them together.

## Declared provenance beats inferred provenance

When you need to know where an output element came from, **have the model say so**, and
check the declaration mechanically. Do not try to recover it from the wording.

- Give the source material **stable identifiers** and show it enumerated and in full. An
  author cannot cite an entry it has no name for. (One codebase truncated the list to 6
  entries of 60 chars, so the model saw 47% of the text it was matched against.)
- Require an identifier per output element, with an explicit null for "invented".
- The gate becomes: **is the identifier in range / in the allowed set?** Plus any
  structural rule you care about — e.g. no two elements may claim the same source, which
  catches duplicates that are otherwise invisible.
- Semantic plausibility moves to the judge, which is already running.

What you give up is the *illusion* of a deterministic guarantee: a model could always
paraphrase past a token test anyway. What you gain is a check that does not punish
compliant work.

## Gate profiles per variant

When output has variants (tiers, modes, intents) with genuinely different rules, declare
the rules in **one table keyed by variant** rather than an `if` cascade, so variants
cannot drift into each other's gates by accident:

```python
VERIFY_PROFILES = {
    "recall":    {"accidental_truth": "all_facts",  "distractors": "declared_index",
                  "min_cited": 1, "key_substance": "blueprint"},
    "composite": {"accidental_truth": "non_cited",  "distractors": "declared_index",
                  "min_cited": 2, "key_substance": "blueprint"},
    "scenario":  {"accidental_truth": "cited_only", "distractors": "declared",
                  "min_cited": 2, "key_substance": "cited_union"},
}
```

The table is also the documentation. When a gate changes, the diff shows which variants
were affected.

## Enforce the rules you already wrote down

Specs accumulate rules that nothing checks. In one codebase the schema said *"distractors
do not overlap"* — and no code tested it, for the life of the project. Adding the check
caught 4 real violations on the first run, each one quietly shrinking a 4-way question to
a 3-way one.

When writing a gate, re-read the spec it implements and ask which stated rules are
currently unenforced. That list is usually short and high-value.

## Dead validation is worse than none

Watch for validation that is computed and never used:

```python
refs_in_stem = set(re.findall(r"[A-Z]{2,}\(?\d+\)?", stem))   # never read again
```

The docs claimed *"numbers **and section references** must exist in the cited facts"*.
Only the numbers half was ever wired. For a regulatory subject where "Section 45" versus
"Section 43" *is* the question, that is a real hole hiding behind a documented guarantee.

Either wire it up or correct the claim. Do not leave the decoy.
