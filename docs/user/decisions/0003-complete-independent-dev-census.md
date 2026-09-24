# 0003 — Complete one independent native dev headroom census

Status: Execution decision under resumed empirical work, 2026-09-22.
Authority: decision 0001, existing AAMAS_TASKS B5.2, independent review.
This does not authorize a new treatment, model search or confirmation run.

## Context

Prior work measured three development siblings of one family. Acquisition v1
subsequently measured six training siblings; both control and treatment achieved
all six final task successes. Neither experiment establishes headroom across
the complete AppWorld development population.

B5.2 already calls for the complete 57-task direct-agent diagnostic, with the
competent prompt and existing model/call budget. It is logically independent
of the failed acquisition package's treatment continuation gate.

## Decision

Run exactly one fresh empty-agent episode for each native dev task. Freeze all
57 IDs, deterministic order, shared native runtime, qwen3.8-max, temperature
zero, 30 attempted calls, 2048 requested output tokens, serial requests and
error accounting before inference. No memory, induction or task replacement.

Apply the existing open-interval headroom heuristic: at most five successes
or at least 52 successes stops this content-gain regime. At least six clean
successes and six clean failures establish headroom only. Infrastructure
uncertainty is retained and propagated as success-count bounds; it cannot
silently become a model failure or a favorable exclusion.

## Rationale

The census can rule out an unsuitable environment without weakening the model
or selecting a difficult subset. A useful negative result avoids spending on
an elaborate coordination mechanism under a saturated endpoint. Conversely,
headroom is only a necessary condition and does not establish a useful learner.

## Consequences

- Maximum 57 native episodes and 1,710 real LLM attempts; no induction calls.
- Provider-reported reasoning and cached tokens count; prices stay unknown.
- All tasks finish regardless of intermediate scientific outcomes; a sustained
  provider outage stops execution with an explicitly incomplete record.
- A mixed result permits zero-new-LLM classification of every failure and a
  concrete learner/handoff design. It does not trigger treatment automatically.
- The old acquisition gate remains failed. No hard-only success headline,
  weaker-model search, shortened prompt or newly selected dataset follows.
- Confirmation splits remain untouched; every outcome is development evidence.

Executable contract: [headroom census v1](../../../configs/aamas2027/headroom_census_v1.json).
