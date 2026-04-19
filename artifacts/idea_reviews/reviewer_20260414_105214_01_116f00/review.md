# Review of `idea.md`

- reviewer_id: `theory_reviewer_01`
- reviewer_profile: Theory-leaning NLP/ML reviewer focused on crisp method objects, falsifiability, and distinctness from prior work.
- model: `gpt-4.1-mini`
- idea_sha16: `36829053bbcc974b`
- verdict: `weak_reject`
- confidence: `4`
- is_8_plus_ready: `False`
- estimated_score_after_fixes: `8`

## Scores

- novelty: 8
- technical_clarity: 7
- technical_soundness: 6
- executability: 6
- empirical_plan: 6
- falsifiability: 6
- overall: 6

## API Usage

- prompt_tokens: 11669
- completion_tokens: 490
- total_tokens: 12159

## Summary

The document presents a well-motivated, organization-formation framing (EDO) over an existing TCPB prototype. Conceptual objects (task tree, personas, recursive audit, local utilities, sparse graph) are thoughtfully laid out, with a staged engineering plan and plausible experimental questions. However, several core mechanisms (persona update, utility estimation, task signature extraction, audit protocol) remain semi-formal and underspecified, and the empirical plan is broad but not yet tied to concrete, falsifiable ablations and metrics definitions.

## Top Strengths

- Clear separation between theoretical framework (EDO) and restricted prototype (TCPB) with explicit mapping.
- Well-scoped, non-trivial research object: emergent organization from local delegation and audit on sparse graphs.

## Top Weaknesses

- Core update rules (persona, neighbor beliefs, utilities) remain conceptual, not yet algorithmically pinned down.
- Empirical plan is broad but lacks precise protocols, metrics definitions, and ablation designs to test key claims.

## Ambiguous Algorithm Points

- Persona update equations gloss over how LocalValue/TerminalValue/ReworkPenalty are computed from logs.
- Utility terms (SplitGain, Risk, Costs) lack concrete estimators, normalization, and how LLM queries instantiate them.

## Missing Definitions Or State Variables

- none

## Missing Or Weak Experiments

- No concrete ablation protocol to isolate contributions of split, recursive audit, and persona tags individually.
- No explicit plan for evaluating emergent specialization beyond informal entropy/divergence metrics definitions.

## Overclaims Or Risky Claims

- none

## Implementation Risks

- none

## What To Fix For 8 Plus

- Specify full algorithmic pipeline: task-signature extraction, utility estimators, persona/belief updates, audit protocol, all with implementable pseudo-code.
- Design a tight empirical core: concrete benchmarks, baselines, ablations, metric formulas, and tests for each falsifiable prediction in §14.4.

## Recommended Next Actions

- none
