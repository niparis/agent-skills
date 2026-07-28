# Core Principles for LLM Evaluation

## Why evals, framed correctly

LLM apps replace unit/integration tests with dynamic, context-sensitive assessment of
non-deterministic behavior. The goals are unchanged — track improvements, detect
regressions before users do, quantify quality on the axes that matter, and benchmark
alternatives (models, prompts, retrieval strategies). Without evals every change is a
vibe check, and vibe-checked systems can't be modified safely.

## The three evaluator types, and when each applies

1. **Code-based evals** — deterministic checks in Python/TS: output structure (valid
   JSON, schema conformance), presence of required data, string/regex assertions,
   numeric tolerances, latency/cost thresholds. Zero token cost, zero latency, perfectly
   reliable. Always prefer these when the criterion is objective.
2. **LLM-as-a-judge** — one LLM classifies another's output using a prompt template.
   Needed when the criterion is subjective or requires language understanding
   (hallucination, relevance, tone, correctness against a reference). Costs tokens,
   needs validation, drifts with judge-model changes.
3. **Human annotation** — the ground truth that everything else is calibrated against.
   Too expensive to scale, so use it to (a) do error analysis, (b) build the labeled
   set that validates your judges, (c) spot-check production. ~100 labeled examples
   is typically enough to validate a judge.

Do a cost-benefit check before building any evaluator: does this failure mode justify
the investment? A judge evaluator implies labeled examples and ongoing maintenance;
an assertion is nearly free. Generic off-the-shelf metrics (BLEU/ROUGE/BERTScore,
cosine similarity, generic "coherence") are not useful as quality gates for product
evals — at most they're exploration tools for finding interesting traces.

## Error analysis: the core development loop

The single highest-leverage activity. Process:

1. Collect traces (production if available; otherwise generate synthetic queries that
   span your intended input distribution and run them through the app).
2. Read them one at a time. Write free-form notes on anything wrong ("open coding").
3. Group notes into a small taxonomy of failure modes ("axial coding"). Make each
   failure mode binary: it happened or it didn't.
4. Count frequencies. Fix pervasive/obvious failures directly in the prompt or system
   first — don't build a judge to detect a failure you can simply fix.
5. Build evaluators only for the failure modes that persist and matter.
6. Re-run error analysis periodically (and after any major change or new user segment);
   the taxonomy goes stale.

Key insight from Shankar et al. ("Who Validates the Validators?"): people can only
define their evaluation criteria BY grading outputs. Criteria emerge from the data;
you cannot write a good judge prompt before you've read the transcripts.

## Label design

- **Binary pass/fail** is the default. It forces clear definitions, aggregates cleanly,
  and correlates far better across annotators and judge runs than numeric scores.
- **Small multi-class categorical** (e.g., correct / incorrect / unsure, or a failure-mode
  taxonomy) when a binary collapses too much information.
- **Avoid continuous 1–10 scores.** LLMs are inconsistent on fine-grained scales; results
  shift with trivial prompt changes and across judge models. If you need an average,
  use a categorical score of 1/0 and average the binary outcomes.
- Always capture the judge's **explanation** — it's the debugging signal and the raw
  material for improving both app and judge.

## Dataset strategy

- **Golden dataset**: versioned, curated examples with expected behavior. Seed it from
  error analysis; every interesting production failure gets promoted into it. Keep it
  hard — a dataset the app passes 100% of isn't stress-testing anything; ~70% pass rates
  often indicate a more meaningful benchmark mid-development.
- **Synthetic data**: use an LLM to generate inputs (e.g., question–context pairs from
  your own document chunks for RAG; paraphrase clusters for agents; adversarial or
  edge-case variants). Synthetic generation is how you get pre-production coverage
  when you have no users yet. Validate a sample by hand — synthetic data inherits the
  generator's blind spots.
- **Segment/slice** the dataset by input type, difficulty, language, and user segment
  so regressions in a slice aren't averaged away.
- Partition data used to build/tune a judge from data used to measure with it, to avoid
  the judge overfitting to memorized answers.

## Lifecycle: offline → CI → online

- **Offline (pre-production)**: run evaluators against golden datasets while iterating
  on prompts/models/retrieval. This is where experiments live.
- **CI/CD**: run the experiment suite on every PR that touches prompts, models, tools,
  or retrieval; fail the build if an aggregate metric drops below threshold. Same
  evaluators as offline — one unified evaluator library across all stages.
- **Online (production)**: run evaluators on sampled live traffic; alert on threshold
  breaches. Use for monitoring and dataset mining, not blocking.
- **Guardrails**: the special case where an eval runs in real time in the request path
  and can block/revise output (e.g., critical-error checks in a regulated domain).
  Reserve for genuinely high-stakes failure modes — they add latency and cost.

Decision rule: block it (guardrail) only if a bad output causes real harm; otherwise
flag it (online eval); and everything you can check pre-release, check pre-release
(offline/CI).

## Team practices

- Designate a domain expert as the quality owner whose judgment the judges are aligned
  to ("benevolent dictator" pattern) — committee-of-annotators averaging blurs criteria.
- Make trace review easy (Phoenix's trace viewer + eval annotations) so reviewing data
  stays a daily habit, not a quarterly project.
- Track evaluator versions alongside prompt versions; a judge prompt change invalidates
  longitudinal comparisons unless re-benchmarked.
