# Task report — candidate formula/implementation contract repair

- **Date**：2026-09-29
- **Status**：`done / candidate-only qualification`
- **Scope**：zero API, zero GPU; active method v1.0 unchanged

## Repairs

The candidate card and reference updater now agree on three boundary rules:

1. `lambda` is fixed to `1` for the candidate; non-default values are rejected
   instead of silently defining another updater.
2. An empty fast window exposes the protected anchor directly. The projection
   formula applies only when the window contains rows.
3. Pending correction keys and superseded tombstones have an explicit finite
   capacity (`K_pending=128` in the candidate card), so the bounded-state claim
   includes the structures that can otherwise grow without limit.

The card also separates a visible raw recipient signal from the independent
producer label. Ineligible attribution is represented as `label=None`; missing
signals remain `UNKNOWN` and are never recoded as zero.

## Verification

Seven targeted candidate tests passed, including snapshot/restore, event-time
ordering, consolidation retention, bounded late queues and rejection of a
non-candidate ridge value. This is a deterministic contract check only; it does
not establish a useful label distribution, efficacy, novelty, or online service
performance.

Evidence: `experiments/logs/n03_candidate_formula_contract_20260929_v1/`.
