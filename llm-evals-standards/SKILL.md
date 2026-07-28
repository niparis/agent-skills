---
name: phoenix-llm-evals
description: >
  Best practices for designing, running, and maintaining LLM evaluations on Arize Phoenix
  (open-source). Use this skill whenever the user wants to evaluate an LLM application —
  RAG pipelines, support/conversational chatbots, agents with tool calling, document/data
  extraction, summarization, text-to-SQL, or code generation — or mentions Phoenix, evals,
  LLM-as-a-judge, eval datasets, experiments, hallucination detection, retrieval relevance,
  trajectory evaluation, or CI quality gates for LLM apps. Also use it when the user asks
  "how do I know if my LLM app is good" even if they don't say "eval".
---

# LLM Evals on Arize Phoenix

This skill encodes a repeatable evaluation workflow plus use-case-specific playbooks.
Read this file fully, then load ONLY the reference file(s) matching the user's use case.

## Step 0 — Identify the use case, then load the right reference

| Use case | Signals | Load |
|---|---|---|
| RAG / knowledge assistant | retrieval, chunks, vector DB, "answers from our docs" | `references/rag.md` |
| Support / conversational chatbot | multi-turn, sessions, personas, escalation, CSAT | `references/chatbot.md` |
| Agent (tool calling, multi-step) | tools, function calling, planning, routers, MCP | `references/agents.md` |
| Document / data extraction | structured output, JSON, fields, OCR'd docs, forms | `references/extraction.md` |
| Summarization | condensing docs, meeting notes, report generation | `references/summarization.md` |
| Text-to-SQL / code generation | NL2SQL, generated code, queries | `references/codegen-sql.md` |

Cross-cutting files (load as needed, regardless of use case):

- `references/core-principles.md` — evaluation philosophy and lifecycle; ALWAYS load
  for a new eval program or when the user asks "where do I start".
- `references/phoenix-mechanics.md` — Phoenix APIs: `llm_classify`, evaluators, rails,
  datasets, experiments, span/document evaluations, CI gating. Load whenever writing code.
- `references/judge-validation.md` — building and validating LLM-as-a-judge evaluators
  against human labels. Load whenever creating a custom judge.

Hybrid apps are common (an agent that does RAG; a chatbot that extracts data). Load
each relevant file and evaluate each component with its own playbook — evals attach at
the span level, so one trace can carry RAG evals on retriever spans and trajectory
evals on the root span simultaneously.

## The universal workflow (applies to every use case)

1. **Instrument first.** You cannot evaluate what you cannot observe. Trace the app with
   OpenInference/OpenTelemetry so every LLM call, retrieval, and tool call is a span in
   Phoenix. Evals are computed against trace data or curated datasets, then logged back
   onto spans.
2. **Error analysis before evaluators.** Manually read 50–100+ real (or realistic) traces
   and take open-ended notes. Cluster the notes into a taxonomy of binary failure modes
   specific to THIS app. Do not start from a generic metric menu; start from observed
   failures. Expect 60–80% of total eval effort to be looking at data, not writing code.
3. **Pick the cheapest evaluator that catches each failure.** Code-based assertions
   (format, schema, regex, exact match, latency, contains-required-data) before
   LLM-as-a-judge. Reserve judges for genuinely subjective criteria (hallucination,
   tone, relevance).
4. **Binary or small categorical labels, never 1–10 scores.** LLM judges are unstable on
   continuous scales; scores fluctuate across prompts and models. Use pass/fail or a
   small fixed label set enforced with Phoenix `rails`, and always request explanations.
5. **Build a golden dataset.** Curate real traces (especially failures) into a versioned
   Phoenix Dataset; synthesize additional cases to cover edge conditions. Grow it every
   time production surfaces a new failure.
6. **Run experiments on every change.** Prompt, model, retrieval, or tool changes run as
   Phoenix Experiments against the golden dataset with the same evaluators, so you can
   compare runs and catch regressions.
7. **Validate the judge itself** before trusting it (see `references/judge-validation.md`).
8. **Close the loop in production.** Run the same evaluators as online evals on sampled
   production traffic; route flagged traces back into the golden dataset.

## Non-negotiable defaults

- Judge model at `temperature=0.0`; constrain output with `rails`; set
  `provide_explanation=True`.
- Evaluate components separately before end-to-end (retriever vs generator; router vs
  tools vs final answer). Component evals localize failures; end-to-end evals confirm
  user-visible quality.
- A 100% pass rate usually means the dataset is too easy, not that the app is done.
- Don't optimize a metric you haven't validated against human judgment.
- Uninstrument the judge's own LLM client (or use a separate project) so judge calls
  don't pollute application traces.
