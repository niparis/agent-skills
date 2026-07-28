# RAG Evaluation Playbook

## The decomposition rule

Never evaluate RAG only end-to-end. A RAG failure is either a retrieval failure or a
generation failure, and the entire diagnostic value of evals comes from telling them
apart. Structure every RAG eval program as two layers plus one end-to-end check:

1. **Retrieval quality** (span-level on retriever spans; document-level per chunk)
2. **Generation quality given retrieved context** (span/trace-level)
3. **End-to-end answer quality** (trace-level, optionally vs ground truth)

Because the query+context live on the retriever span and the answer on the LLM span,
retrieval relevance is a span-level eval while answer correctness reads across spans
at the trace level.

## Layer 1 — Retrieval

Per-document LLM judge: the RAG relevance template classifies whether each retrieved
chunk contains information that can answer the specific question (binary
relevant/irrelevant, logged via `DocumentEvaluations`).

Then compute ranking metrics over those per-document labels with Phoenix's code
metrics:

- **Precision@k** — share of the top-k chunks that are relevant.
- **NDCG@k** — rewards putting relevant chunks earlier.
- **Hit rate / recall@k** — did any relevant chunk make the top-k (needs ground truth
  or the judge labels as proxy).

Diagnostic use: low precision@k with good end-to-end answers means the generator is
rescuing bad retrieval (fragile); high retrieval scores with bad answers means the
problem is the prompt/model, not the index. Common failure modes to look for in
embeddings/cluster views: queries with no coverage in the corpus (missing content),
right content but bad chunking (answer split across chunk boundaries), and semantic
near-misses (retriever finds topically similar but non-answering text).

## Layer 2 — Generation given context

- **QA correctness** (Phoenix `QAEvaluator` / Q&A template): given question, reference
  context, and answer — is the question correctly and fully answered based on the
  reference? Binary correct/incorrect.
- **Hallucination / groundedness** (`HallucinationEvaluator`): is the answer supported
  by the retrieved context, or does it introduce unsupported claims? Binary
  factual/hallucinated. This is context-relative — an answer can be true in the world
  but hallucinated relative to the provided context, and for RAG that still fails.
- **Citation correctness** (Reference Link template) if the app cites sources: does
  each citation actually support the claim it's attached to?
- Refusal behavior: when retrieval returns nothing relevant, the correct output is
  usually an explicit "not in the knowledge base" — add a code or judge check that
  the app doesn't answer from parametric memory on empty/irrelevant context. Build a
  dataset slice of deliberately unanswerable questions for this.

## Layer 3 — End-to-end

If you have ground-truth answers, use the AI-vs-human/ground-truth template or a
reference-based correctness judge. If not, QA correctness + hallucination together are
the standard proxy pair (e.g., a run reporting ~0.91 QA correctness with ~0.05
hallucination still has room to improve, and the split tells you where to look next).

## Dataset construction for RAG

- Synthesize question–context pairs directly from your own document chunks with
  `llm_generate` — guarantees every question is answerable by the corpus and gives you
  document-level ground truth for retrieval metrics for free.
- Add: paraphrase variants of the same question (retrieval robustness), multi-hop
  questions requiring 2+ chunks, unanswerable questions, ambiguous questions, and
  real production queries as they arrive.
- Slice by document type/section and question type; chunking regressions typically
  show up only in specific slices.

## Experiment axes worth testing

Chunk size/overlap, k, embedding model, reranker on/off, hybrid (BM25+vector) vs pure
vector, query rewriting, and prompt variants for the generator. Each is one Phoenix
Experiment against the same dataset with the same three-layer evaluators; compare runs
in the UI. Change one axis at a time.

## Online

Sample production traffic and run relevance + hallucination continuously; feed
low-relevance queries into corpus-gap analysis (what are users asking that we don't
cover?) and hallucinated answers into the golden dataset.
