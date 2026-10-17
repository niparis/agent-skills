# Document / Structured Data Extraction Evaluation Playbook

## Why extraction evals are different

Extraction is the use case where LLM-as-a-judge matters LEAST. Outputs are structured
and ground truth is knowable, so the eval stack inverts: code-based evaluation
dominates, judges fill narrow gaps. If you're reaching for a judge to grade a JSON
field, first ask why you can't compare it to a label.

## The evaluation stack (in order)

### 1. Schema validity (code, gate everything on this)

Valid JSON / parses at all; conforms to the schema (required fields present, types
correct, enums in range). Run as an assertion on 100% of outputs — offline and as a
cheap production guardrail. Track the parse-failure rate as its own metric; it moves
with model/prompt changes.

### 2. Field-level accuracy vs ground truth (code)

Build a labeled dataset (documents + hand-verified extractions) and score per field:

- **Exact match** for IDs, enums, booleans.
- **Normalized match** for dates, currency, numbers (compare parsed values, not
  strings — "1,000.00" vs "1000" must not count as an error).
- **Fuzzy/similarity match** with a threshold for free-text fields (names, addresses),
  or a narrow judge for semantic equivalence ("Intl. Business Machines" = "IBM").
- **Per-field precision/recall/F1**, plus:
  - **Recall on present fields** (did we extract what's there — misses)
  - **Precision on extracted fields** (is what we extracted right — errors)
  - **Hallucinated-field rate**: values emitted for fields NOT present in the source
    document. This is the extraction-specific hallucination metric and the most
    dangerous failure in financial/legal/medical pipelines — a model that fabricates
    a plausible invoice number is worse than one that returns null.
  - **Null discipline**: correct use of null/absent for genuinely missing data.

Aggregate two ways: per-field metrics (which fields are weak) and per-document
all-fields-correct rate (the number the business feels).

### 3. Judges, only for what code can't check

- Semantic equivalence of free-text values (as above).
- **Faithfulness spot-check on unlabeled data**: given source document + extraction,
  does every value appear in / follow from the document? This is the hallucination
  template repurposed with the document as reference; it lets you run online evals on
  production traffic where no labels exist.
- Ambiguity adjudication: whether a disputed extraction is defensible given messy
  source text.

## Dataset design

- Stratify by document TYPE and by document QUALITY (clean digital PDFs vs scanned/OCR
  vs photographed) — extraction accuracy is dominated by input quality, and an
  unstratified average hides it.
- Include per-field difficulty cases deliberately: multi-page tables, values that
  appear multiple times with conflicts, handwritten fields, missing fields, documents
  in unexpected layouts/languages.
- Include NEGATIVE documents (wrong document type entirely); correct behavior is
  refusal/empty, and models love to extract something anyway.
- Ground-truth labeling is expensive but uniquely valuable here because it's
  objective; 1–2 careful passes over a few hundred documents beats any judge. Grow it
  from production disputes (every human correction downstream is a free label).

## Phoenix implementation notes

- Field-comparison logic = custom code evaluators (`@create_evaluator`) in
  Experiments; the labeled dataset is a Phoenix Dataset with expected output per
  example; per-field results log as separate eval names so the UI can filter by field.
- Trace the full pipeline (OCR/preprocess span → LLM span → parse span) so you can
  attribute a wrong field to bad OCR text vs bad extraction from correct text —
  the retrieval-vs-generation split of this use case.
- Experiment axes: prompt/schema wording, model, structured-output mode vs free
  decoding, single-shot vs field-by-field extraction, preprocessing variants.
- In production: schema validity + faithfulness judge on samples, plus drift watch on
  parse-failure and null rates (spikes usually mean a new upstream document format).
