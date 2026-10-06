# Task report — ownership gate design review after C1

- **Date:** 2026-10-06
- **Status:** `BLOCKED_BY_EVIDENCE`
- **Goal change requested:** `false`
- **Scientific claim allowed:** `false`

## Trigger

C1 v3 used the same frozen PIPE3 source artifact and the same public prompt contract in each
arm. `no_update` and RARE returned a source judgment with `target_role=producer`; the
`contextual_trust_linear` response returned `target_role=recipient`, so the current strict gate
stopped that arm before assignment. The raw responses and gate payloads are preserved in
[`n03_c1_pipe3_bounded_live_20261006_v3/`](../../../experiments/logs/n03_c1_pipe3_bounded_live_20261006_v3/).

The result is a measurement problem, not an efficacy comparison: arm completion depends on a
free-text/model-selected responsibility field even though the runner already has a disjoint
ownership contract and an independently registered producer defect.

## First-principles distinction

There are two different variables:

1. **Structural owner**: which contracted component owns the path containing the registered
   defect. This is determined by the public task contract, candidate registry, changed-path
   set, and independent scorer.
2. **Judged target role**: what the recipient says it is diagnosing in its judgment. This is a
   noisy observation useful for judge calibration, but it is not the source of ownership truth.

The active gate currently requires `judgment.target_role == "producer"` in addition to the
structural producer-defect and direct-use conditions. C1 shows that this extra requirement can
turn identical information into arm-specific UNKNOWN censoring. It also allows a prompt-level
label fluctuation to decide whether a real, independently registered event becomes public role
evidence.

## Candidate repairs (not yet active)

### A — structural attribution with role calibration (recommended for design review)

Use the contract/registry/scorer to compute `structural_owner_role` and require it to be
`producer` for source evidence. Keep `judgment.target_role` and `target_paths` in the immutable
record as a judge-calibration field; score disagreement separately. The source gate still
requires complete Qp, recipient judgment, action, outcome, artifact binding, registered defect,
direct unrepaired use, and no mixed ownership. A disagreement cannot silently create evidence for
an unregistered defect.

This preserves responsibility safety while making eligibility depend on auditable ownership
facts rather than stochastic wording. The falsifier is a path/registry/scorer mutation: any
mutation that changes structural owner or introduces mixed ownership must still produce
`UNKNOWN`/no evidence.

### B — retain the current strict judged-role gate

Keep `target_role == producer` as a hard condition and treat C1's arm-specific stop as the
intended conservative behavior. This is simple, but a live arm comparison must then report the
completion/censoring process as a primary outcome and cannot compare selectors on a common
realized sample without a much larger pre-registered sample.

### C — prompt or retry until the role field agrees

Do not use this repair. It would condition the sample on a generated label, spend unequal calls,
and hide the exact judge disagreement that the method should measure. It violates the current
no-retry/UNKNOWN contract.

## Decision boundary

No active method document, benchmark manifest, or historical result is changed by this report.
Before another live comparison, the project must explicitly choose whether the judged role is a
hard attribution condition (B) or a calibration observation under structural ownership (A), then
version the gate, tests, and experiment card. Until that choice is recorded, C1 remains a
single-root engineering result and no A800/scientific baseline run is justified.

`goal_change_requested=false`; this is a measurement repair, not a Goal downgrade.
