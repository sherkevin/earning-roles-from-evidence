# Task report — ownership-gate candidate design

- **Date:** 2026-10-06
- **Status:** `BLOCKED_BY_EVIDENCE`
- **Goal change requested:** `false`
- **Active decision:** none; A/B confirmation pending

## Purpose

To reduce idle time while waiting for the responsibility-gate decision, this task writes the
recommended structural-owner design as an explicitly inactive candidate. It does not modify the
active method, benchmark manifest, scorer, or experiment card.

## Candidate prepared

[`ownership_gate_structural_owner_v0.1.md`](../../research/candidates/ownership_gate_structural_owner_v0.1.md)
defines separate contract-derived `structural_owner_role` and model-observed
`judged_target_role` fields, a conservative producer-eligibility rule, eight zero-call mutation
and replay cells, and falsifiers. The design preserves disagreement for judge calibration rather
than silently treating it as producer evidence.

## Why this is useful

It directly addresses C1's arm-specific censoring while retaining the safety property that
recipient-owned or mixed edits cannot train a producer. It also gives the next test a bounded
manifest instead of another prompt tweak. If the user selects strict judged-role gating (B), this
candidate remains a documented rejected alternative.

## Goal reconciliation

No scientific claim, result, or Goal item changed. The next live comparison is still blocked until
the user confirms A or B and the selected gate is versioned with tests. `goal_change_requested=false`.
