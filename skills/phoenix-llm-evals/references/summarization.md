# Summarization Evaluation Playbook

## The three axes

Every summarization eval program reduces to three questions, each with its own
evaluator; a single "is this a good summary" judge conflates them and hides which
lever to pull.

1. **Faithfulness** — everything in the summary is supported by the source. Run the
   hallucination template with the source document as reference. This is the axis with
   the highest stakes; a fluent-but-wrong summary is worse than a clumsy accurate one.
   For long summaries, judge claim-by-claim (split the summary into atomic claims,
   verify each against the source) rather than holistically — holistic judges miss
   single fabricated details in otherwise faithful summaries.
2. **Coverage / relevance** — the summary captures the points that matter. "Matter" is
   use-case-specific, so define it: for meeting notes it's decisions and action items;
   for financial reports it's figures and risks. The strongest pattern is a
   key-fact rubric: for each source document in the golden set, list the must-include
   facts (human-authored, or LLM-drafted then human-verified), then have a judge check
   each fact's presence — giving a coverage recall score instead of a vibe.
3. **Form compliance** — length limits, structure (sections, bullets), reading level,
   tone. Almost entirely code-checkable: word counts, section presence, forbidden
   content. Don't spend judge tokens on what `len()` can measure.

Phoenix's pre-tested summarization template (benchmarked on CNN/DailyMail, XSum,
GigaWorld) is a reasonable holistic starter for triage, but note those benchmarks are
news corpora — treat it as a starting point and evolve toward the decomposed axes
above on your own domain.

## Skip the classic NLP metrics

ROUGE/BLEU/BERTScore against reference summaries correlate poorly with the failures
that matter in product settings (a summary can score high on n-gram overlap while
fabricating the key number). Use them, at most, to hunt for interesting traces —
never as a quality gate.

## Dataset design

- Stratify by source length and type; summarization quality degrades non-linearly with
  input length, and long-document slices are where regressions hide.
- Include adversarial sources: documents with internal contradictions, documents whose
  most prominent content is NOT the most important, near-empty documents, and
  documents containing instructions (prompt-injection check — the summary should
  describe them, not obey them).
- For each golden example store: source, key-fact list, constraints (length, format),
  and optionally a reference summary for human comparison.

## Grounded-generation note

If summarization sits downstream of retrieval (summarize the top-k chunks), you've
built RAG — apply rag.md to the retrieval layer; faithfulness here is relative to the
retrieved context, and coverage is relative to what was retrieved (a perfect summary
of the wrong chunks still fails, but it fails in the retrieval layer).
