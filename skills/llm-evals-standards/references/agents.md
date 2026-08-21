# Agent Evaluation Playbook (tool calling, routers, multi-step)

## Decompose the agent, then evaluate each capability

Agents fail at distinct stages, and each stage gets its own evaluator. Phoenix ships
pre-tested templates for most of these:

1. **Router / skill selection** — did the agent pick the right capability for the
   query? (Judge on the first LLM span's tool choice.)
2. **Tool selection & function calling** (Agent Function Calling template) — right
   tool, at the right time?
3. **Parameter extraction** — were the arguments passed to the tool correct and
   complete? Often checkable with code (schema + value assertions against the query);
   use a judge only for fuzzy parameters.
4. **Tool execution** — did the tool succeed? Pure code eval: status codes, non-empty
   results, exception rates. No LLM needed.
5. **Planning** (Agent Planning template) — for agents that emit explicit plans: is
   the plan coherent and sufficient for the goal?
6. **Reflection** (Agent Reflection template) — does the agent correctly recognize
   failure/success of intermediate steps and adapt?
7. **Trajectory** — is the whole sequence of steps sensible? (below)
8. **Final response quality** — standard output evals (correctness, groundedness if it
   used retrieved/tool data, tone).

Instrument with OpenInference so every tool call is a span; trajectory evals then group
tool-call spans per trace, in order.

## Trajectory evaluation

Extract the ordered tool-call list per trace and judge it against the user input and
tool definitions. The standard rubric: the trajectory progresses logically, uses the
right tools, and is reasonably efficient with no unnecessary detours — output exactly
`correct` or `incorrect`, with explanation, logged to the root span so whole traces
are filterable.

```python
results = llm_classify(
    dataframe=trace_df,               # one row per trace: tool_calls, input, tool defs
    template=TRAJECTORY_ACCURACY_PROMPT,
    model=OpenAIModel(model="gpt-4o-mini", temperature=0.0),
    rails=["correct", "incorrect"],
    provide_explanation=True,
)
```

Trajectory judges catch loops (same tool called repeatedly), skipped-then-backtracked
steps, and detours that inflate cost/latency — failure classes invisible to
final-answer evals. If you have golden trajectories, add code-based comparison
(exact/in-order/any-order match of the tool sequence) as a cheaper first gate.

## Path convergence (consistency + efficiency)

For query types with a known optimal step count: build a dataset of the SAME question
phrased many ways, run the agent on each while recording steps taken, then score
`optimal_path_length / actual_path_length` (1.0 = perfect) as a code evaluator attached
after the experiment. Agents should take the same path for semantically identical
queries; in practice they often don't, and convergence quantifies that instability.

```python
@create_evaluator(name="Convergence Eval", kind="CODE")
def evaluate_path_length(output) -> float:
    return optimal_path_length / float(output["path_length"]) if output.get("path_length") else 0
```

## Dataset and experiment design

- Segment the dataset by intended tool/route so router accuracy is measurable per class
  (it's a classification problem — confusion matrices apply).
- Include: queries needing no tools (over-calling is a failure), queries needing
  multiple tools in sequence, ambiguous queries (should ask for clarification),
  and adversarial inputs (prompt injection via tool results; unsafe tool calls).
- Combine all component evaluators plus trajectory into a single experiment for a
  unified per-change report.
- Track cost and latency per trace alongside quality — agents regress on efficiency
  (steps, tokens) even when accuracy holds, and runaway loops are an operational risk
  worth alerting on in production.

## End-to-end task completion

Ultimately judge: did the agent accomplish the user's goal? For single-shot agents a
final-response judge suffices; for conversational agents, use session-level evals
(see chatbot.md). Component evals explain WHY task completion moved; task completion
is the number stakeholders care about.
