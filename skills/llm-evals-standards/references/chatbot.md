# Support / Conversational Chatbot Evaluation Playbook

## Turn-level vs session-level: evaluate both

Chatbots differ from single-shot apps because quality lives at two granularities.
A bot can produce individually fine turns and still fail the conversation (loses
context, never resolves the issue). Map both onto Phoenix: turn evals attach to LLM
spans; session/conversation evals attach at the trace/session level (Phoenix groups
spans into sessions when you propagate a session ID in instrumentation).

### Turn-level evals

- **Response relevance** — does this reply address the user's latest message given the
  history?
- **Groundedness / hallucination** — if the bot answers from a knowledge base (most
  support bots are RAG underneath), apply the full RAG playbook (rag.md) to the
  retrieval spans inside each turn.
- **Policy compliance** — code + judge checks for domain rules: no unauthorized
  promises (refunds, legal/medical advice), required disclaimers present, no
  competitor mentions, PII handling. These are usually your first guardrail
  candidates because a single bad turn can be materially harmful.
- **Tone/brand adherence** — judge with a rubric written from your actual style guide,
  not a generic "politeness" score.
- **Toxicity** (Phoenix pre-tested template) as a safety net.

### Session-level evals

- **Task/conversation completeness** — the single most important conversational
  metric: extract the user's intents from the transcript and check whether each was
  satisfied. If the task isn't done, nothing else matters.
- **Knowledge retention** — does the bot re-ask for information the user already gave
  (email, order number)? Classic support-bot failure, invisible at turn level.
- **Role adherence** — does it stay in persona/scope across the whole session,
  including under pressure to break character?
- **User frustration** (Phoenix pre-tested template) — detect sessions where the user
  is getting frustrated; excellent for mining production sessions for review.
- **Escalation correctness** — did it hand off to a human at the right moments
  (and not too eagerly)? Judge against explicit escalation criteria.
- **Resolution efficiency** — turns-to-resolution as a code metric; regressions here
  are cost and UX regressions even when quality holds.

For long sessions, avoid judge context overload: summarize the conversation and judge
the summary, or judge segments and aggregate.

## The dataset problem: you can't pre-write turn N

Turn N depends on the bot's turn N-1, so fixed multi-turn scripts break the moment
the bot changes. Three data strategies, in ascending order of power:

1. **Historical conversations** — evaluate real production sessions. Best for
   monitoring and error analysis; useless for pre-release testing of a changed bot.
2. **Golden first-turns + partial replays** — good for turn-level regression checks.
3. **User simulation** — an LLM role-plays the user from a scenario + persona spec
   ("angry customer seeking refund for order placed with old email"), conversing with
   the real bot; session-level evaluators score the resulting transcripts. This is the
   standard for pre-release multi-turn benchmarking: same scenario set on every
   version → comparable runs. Build scenarios from your real intent taxonomy and from
   error analysis, including hostile users, topic-switchers, vague users, and
   jailbreak attempts.

Implement simulation as the `task` in a Phoenix Experiment: each dataset example is a
scenario/persona; the task runs the simulated dialogue against the bot and returns the
transcript; evaluators score it.

## Error analysis specifics for support bots

Read whole sessions, not sampled turns — most damning failures (loops, contradictions
across turns, unresolved intents) only appear at session scope. Cluster failures by
intent category; support-bot quality is almost always wildly uneven across intents,
and per-intent slicing is what makes the numbers actionable. Use the user-frustration
eval on production traffic as an automatic "review this session" flag.

## Production loop

Online evals on sampled sessions: frustration, policy compliance, completeness.
Correlate with human signals (thumbs down, CSAT, human-takeover rate) — if your judges
don't correlate with these, fix the judges. Feed flagged sessions into the golden
scenario set.
