# Phoenix Mechanics: APIs, Data Flow, and Patterns

## Architecture in one paragraph

Phoenix is open-source, self-hostable (`pip install arize-phoenix`, or
`docker run -p 6006:6006 arizephoenix/phoenix`), and OpenTelemetry-native via the
OpenInference semantic conventions. The loop: instrument the app → traces land in
Phoenix → export the relevant spans as a dataframe (or query them) → run evaluators
over the dataframe → log the results back as annotations on the spans → filter/inspect
in the trace viewer. Datasets and Experiments layer on top for offline iteration.
Evals themselves are OTel-instrumented, so judge runs are traceable too. Verify current
APIs against the docs at arize.com/docs/phoenix — the evals package has both a classic
API (`llm_classify`, `run_evals`) and a newer one (`create_classifier`, `evaluate_dataframe`).

## Classic evals API (arize-phoenix-evals)

`llm_classify` is the workhorse: dataframe in, one label per row out.

```python
from phoenix.evals import (
    HALLUCINATION_PROMPT_TEMPLATE, HALLUCINATION_PROMPT_RAILS_MAP,
    OpenAIModel, llm_classify,
)

model = OpenAIModel(model="gpt-4o", temperature=0.0)
rails = list(HALLUCINATION_PROMPT_RAILS_MAP.values())  # e.g. ["hallucinated", "factual"]

results = llm_classify(
    dataframe=df,                      # columns must match template variables
    template=HALLUCINATION_PROMPT_TEMPLATE,
    model=model,
    rails=rails,                       # constrain judge output to fixed labels
    provide_explanation=True,          # always: free-text rationale per row
)
```

Key behaviors to rely on:

- **rails** force the judge into an aggregatable label set and strip stray text.
- **provide_explanation** returns a rationale column — Phoenix's judges are designed to
  return explanations by default because they both improve results and aid debugging.
- Batching/concurrency is built in (use `nest_asyncio.apply()` in notebooks or eval
  submission is much slower).
- Structured judgments are extracted via function/tool calling rather than parsing free
  text, which is why rails stay clean.

Convenience evaluators wrap common templates: `HallucinationEvaluator`, `QAEvaluator`,
`RelevanceEvaluator`, run together via `run_evals(dataframe, evaluators=[...])`.

## Pre-tested templates (use as starting points, then customize)

Hallucination; Q&A on retrieved data (QA correctness); Retrieval (RAG) relevance;
Summarization; Code generation (correctness/readability); Toxicity; AI vs human
ground truth; Reference/citation link; User frustration; SQL generation; Agent function
calling; Agent path convergence; Agent planning; Agent reflection; Audio emotion.

Each ships with benchmark datasets and published performance so you know the
template+model combo's precision/recall before trusting it. Treat these as calibrated
defaults — still spot-check on YOUR data, and expect to customize wording to your
domain (see judge-validation.md).

## Getting data in and results back

Export QA triads or retrieval data from traces:

```python
from phoenix.session.evaluation import get_qa_with_reference, get_retrieved_documents
qa_df = get_qa_with_reference(px.Client())            # input, output, reference
docs_df = get_retrieved_documents(px.Client())        # one row per retrieved doc
```

Log evals back onto spans/documents:

```python
from phoenix.trace import SpanEvaluations, DocumentEvaluations
px.Client().log_evaluations(
    SpanEvaluations(dataframe=qa_correctness_df, eval_name="Q&A Correctness"),
    SpanEvaluations(dataframe=hallucination_df, eval_name="Hallucination"),
    DocumentEvaluations(dataframe=doc_relevance_df, eval_name="relevance"),
)
```

- **SpanEvaluations**: one label per span (LLM call, retriever call, root span).
- **DocumentEvaluations**: one label per retrieved document within a span — required
  for ranking metrics (precision@k, NDCG).
- Trace-level judgments (e.g., trajectory accuracy) are logged against the root span
  so you can filter whole traces by them.

Once logged, the UI shows aggregate stats, lets you filter to failing spans, and shows
each explanation inline — this filter-to-failures loop is the main debugging workflow.

## Datasets and Experiments

- **Datasets**: versioned example collections (inputs + optional expected outputs).
  Build from curated traces, uploaded dataframes, or synthetic generation
  (`llm_generate` can, e.g., produce question–context pairs from your document chunks).
- **Experiments**: `run_experiment(dataset, task, evaluators=[...])` runs your app
  (the task) over every example and scores outputs. Custom code evaluators via
  `@create_evaluator`; custom judges via `llm_classify` inside an evaluator function.
  Evaluators can return a label, a float, or a full `EvaluationResult(score, label,
  explanation)`.
- Experiments are the unit of comparison: same dataset + same evaluators across two
  prompt versions = a regression report.

## CI/CD gating pattern

Run Phoenix as a service in CI, execute `run_experiment` over the regression dataset,
and assert on aggregate scores — e.g., fail the PR if QA correctness drops below your
threshold. Keep thresholds per-slice where slices matter. This is the same evaluator
code as offline and online runs, which is the point: one evaluator library, three
execution contexts.

## Operational gotchas

- **Uninstrument the judge client** (e.g., `OpenAIInstrumentor().uninstrument()`)
  or point judge calls at a separate project, so evaluation traffic doesn't appear as
  application traces.
- Pin judge model versions; a silent model upgrade shifts all your metrics.
- Watch client/server version skew warnings; mismatches cause compatibility issues.
- Phoenix stores data locally by default — for anything durable, run it as a service
  with a real database and backups, not an ephemeral notebook session.
- For continuous production evals with alerting/thresholds, that's where the managed
  Arize AX product picks up; Phoenix covers the dev/CI loop and self-hosted online
  evals you orchestrate yourself.
