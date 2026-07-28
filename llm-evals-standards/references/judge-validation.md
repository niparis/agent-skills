# Building and Validating LLM-as-a-Judge Evaluators

An unvalidated judge is a random-number generator with confidence. Phoenix benchmarks
its pre-tested templates against public datasets (WikiQA, WikiToxic, HumanEval, etc.)
and publishes confusion matrices per judge model — hold your custom judges to the same
standard on YOUR data.

## Build process (Husain/Shankar methodology, adapted to Phoenix)

1. **Do error analysis first** (core-principles.md). You cannot write a judge prompt
   for a criterion you haven't seen violated. Fix pervasive errors before building a
   judge to detect them — the judge's job is finding residual errors.
2. **Draft the judge prompt** for ONE binary failure mode. Include: the task context,
   the precise definition of pass/fail (from your error-analysis notes), 2–3 borderline
   few-shot examples with verdicts, and structured output constrained by rails.
   Start from a Phoenix pre-tested template when one is close; customize the wording
   to your domain.
3. **Create a labeled validation set**: ~100 examples labeled by your domain expert
   (a single accountable expert, not a committee average). Deliberately oversample
   failures and borderline cases; a set that's 95% passes can't measure the judge.
   Keep this set partitioned from anything used to tune the judge prompt.
4. **Measure agreement**: run the judge over the labeled set; compute the confusion
   matrix, and specifically true-positive rate AND true-negative rate (accuracy alone
   is misleading on imbalanced labels; Cohen's kappa if you want chance-correction).
   Read every disagreement's explanation — disagreements are either judge-prompt bugs
   (fix the prompt) or criteria ambiguity (fix the definition, sometimes relabel).
5. **Iterate** until agreement is acceptable for the metric's stakes (many teams
   target ~90%+ TPR/TNR for gating metrics; lower is tolerable for exploratory ones).
6. **Freeze and version** the judge (prompt + model + temperature). Re-benchmark on
   the labeled set whenever any component changes, including silent judge-model
   upgrades — otherwise longitudinal metrics are incomparable.
7. **Recalibrate on drift**: quarterly, or when the app's input distribution shifts,
   sample fresh production traces, label, and re-measure agreement.

## Design rules

- One judge per failure mode. Compound rubrics ("relevant, accurate, and helpful?")
  produce unactionable labels and lower agreement.
- Binary or small categorical output with rails; explanations always on. Explanation-
  then-label ordering in the template gives the judge room to reason before deciding.
- Judge model: use a strong model for the judge even if the app uses a cheaper one;
  temperature 0. Using the same model family for task and judge risks self-preference
  bias — acceptable for narrow criteria checks, risky for open-ended "which is better"
  comparisons; mitigate by validating against human labels (step 4 covers you either
  way, which is the deeper point: agreement with humans is the only license a judge
  has).
- Known judge biases to design around: position bias in pairwise comparisons (swap
  order and average), verbosity bias (longer ≠ better — say so in the prompt),
  self-preference, and leniency drift on long inputs (chunk or summarize).
- Judges get cost-benefit scrutiny too: a judge needs ~100 labels up front and ongoing
  maintenance. If an assertion can catch the failure, the assertion wins.

## Phoenix-specific mechanics

- Benchmarking a judge is itself an eval run: labeled set as dataframe → `llm_classify`
  → compare judge labels vs ground-truth column with scikit-learn
  (`precision_recall_fscore_support`, confusion matrix). Phoenix's own benchmark
  notebooks (`download_benchmark_dataset`) show the exact pattern to copy.
- Log judge outputs with explanations back to Phoenix and review disagreements in the
  trace viewer; judge runs are themselves traced, so you can debug the judge's inputs
  exactly as you debug the app.
- Keep a per-judge "spec" doc: failure-mode definition, labeled-set location,
  last-benchmarked agreement, version history. This is what makes eval numbers
  auditable when a stakeholder asks why the dashboard moved.
