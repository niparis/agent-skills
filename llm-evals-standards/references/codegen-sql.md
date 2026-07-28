# Text-to-SQL and Code Generation Evaluation Playbook

## The prime directive: execute, don't opine

Code and SQL are the use cases where ground truth is executable, so execution-based
code evals outrank judges everywhere they're feasible. A judge guessing whether SQL is
correct is strictly worse than running it.

## Text-to-SQL stack

1. **Syntactic validity** (code): does it parse for the target dialect? Gate on this.
2. **Safety/policy** (code): reject writes/DDL if the app is read-only; enforce
   table/column allowlists; require LIMITs where mandated. These double as production
   guardrails.
3. **Execution accuracy** (code, the primary metric): run generated SQL and a
   ground-truth query against a fixed test database; compare result SETS (order-
   insensitive unless ORDER BY was requested, tolerant to column aliasing). Exact
   string match against golden SQL is a bad metric — many different queries are
   correct — but keep it as a cheap first pass since exact matches need no execution.
4. **Semantic-intent judge** (Phoenix's SQL Generation template) for what execution
   can't catch: queries that return the right answer on the test DB by luck but
   misread intent, and for triaging when no execution sandbox is available. Give the
   judge the schema, the question, and the SQL.
5. **Efficiency** (code, secondary): flag full scans / pathological joins via EXPLAIN
   if cost matters.

Dataset: real analyst questions stratified by difficulty (single-table filters →
joins → aggregation → window functions/CTEs), ambiguous questions (should ask, not
guess), unanswerable-with-this-schema questions (should refuse), and a frozen test
database with verified golden results per question.

## Code generation stack

1. **Compiles/parses + lints** (code).
2. **Functional correctness via tests** (code, primary): execute generated code
   against unit tests in a sandbox — the HumanEval pattern, applied to your own task
   distribution. Report pass@1 (and pass@k if you sample). Writing test suites per
   golden task is the main dataset cost and is worth it.
3. **Security scan** (code): static analysis for injection, unsafe eval/exec, secrets.
4. **Readability/quality judge** (Phoenix's code-generation template, benchmarked on
   HumanEval/WikiSQL/CodeXGlue): style, naming, idiomatic usage — real concerns that
   tests can't see, and legitimately subjective, hence a judge. Keep it separate from
   correctness; never let a readability judge overrule a passing test suite, and never
   let elegant-looking code that fails tests pass.

Sandboxing is non-negotiable for execution evals — untrusted generated code runs in an
isolated container with timeouts (infinite loops are a normal failure mode, so a
timeout IS a test failure, not an infra error).

## Phoenix implementation notes

- Execution harness = custom code evaluators in Experiments: the evaluator runs the
  SQL/tests and returns pass/fail plus an explanation (stderr, diff of result sets).
- Log per-difficulty-slice results as separate eval names; text-to-SQL regressions
  are almost always slice-specific (e.g., window functions break while filters hold).
- Judges (`llm_classify` with the SQL or code templates) run only on execution
  failures (why did it fail — wrong join? hallucinated column?) to accelerate error
  analysis, and on samples of passes to catch lucky-correct outputs.
- Hallucinated schema elements (nonexistent tables/columns) deserve their own tracked
  code metric — it's the dominant text-to-SQL failure mode and trivially detectable
  by validating identifiers against the schema.
