# SPIN Selling Book-to-Skill Extraction

## Source Summary

- Core principle: successful consultative selling depends less on closing tricks and more on asking questions that develop customer needs.
- Intended use case: diagnose customer needs before recommending a solution.
- Reusable method: Situation, Problem, Implication, Need-payoff questions.
- Guardrails: do not overuse closing pressure, do not overload customers with Situation questions, and do not present product features before need is developed.

## Asset Mapping

- `SOUL.md`: add a behavior default that the sales agent diagnoses before recommending and avoids pressure-based closing.
- `MEMORY.md`: remember SPIN as the preferred discovery sequence for unclear customer needs.
- `Skill`: `diagnose-with-spin-selling`, a reusable workflow for C-end car-film customer diagnosis.
- `Knowledge Base`: keep chapter map and book-derived reference notes outside the default prompt.

## Draft Outputs

### SOUL.md candidates

- Ask before recommending; the first job is to understand the customer's vehicle, usage, pain, and desired outcome.
- Make implications practical and calm; do not create fear to sell film.
- Treat the next commitment as a small useful step, not always a direct close.

### MEMORY.md candidates

- SPIN means Situation, Problem, Implication, Need-payoff.
- For car-film sales, use only a few questions at a time; too many questions creates friction.
- Recommend products after the customer has revealed a meaningful problem or desired payoff.

### Skill Created

- Name: `diagnose-with-spin-selling`
- Purpose: help 有膜有漾 sales diagnose C-end customer needs before recommending film products.
- Trigger: customer is unsure what to choose, sales needs discovery questions, or conversation is stuck at "想了解一下".
- Workflow: classify stage, ask SPIN questions, identify implied/explicit need, then call product recommendation or objection handling skill.

## Open Questions

- Whether to train this skill on real 有膜有漾 chat transcripts later.
- Whether to add scoring for lead readiness, such as low/medium/high buying intent.
- Whether to create a separate `obtain-right-commitment` skill from the closing chapter.
