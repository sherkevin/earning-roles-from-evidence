# Task report — activate structural-owner responsibility gate

**Date:** 2026-10-06  
**Status:** `PARTIAL`  
**Goal change requested:** `false`

## Purpose and Goal mapping

This task closes the attribution-design ambiguity exposed by the C1 live development trace. It
implements ER-G2 (responsibility-safe evidence), and supports the method and benchmark gates that
require a recipient-only repair, mixed ownership, duplicate replay, and contract mutation to be
distinguished from a producer-owned defect. It does not claim that the scientific role-learning
gate is complete.

## Decision and implementation

Following the user's approval of the recommended design A, ADR 0047 makes the structural owner a
parent-derived field. The frozen task contract, candidate registry, changed paths, independent
producer check, and explicit registered defect/quality event determine `structural_owner_role`.
The model's `target_role` and paths remain raw judged observations; `judged_role_agrees` is a
calibration field and cannot independently create or cancel producer evidence.

The active method is now
[`method_v1.2_20261006.md`](../../research/versions/method/method_v1.2_20261006.md), and v1.1 is
marked superseded. Code versions are `pipe3-responsibility-label-v2-structural-owner` and
`two-stage-role-evidence-v3-structural-owner`. The paper's source gate now states the same rule.

## Evidence and checks

The zero-call qualification was configured before execution at
[`config.json`](../../../experiments/logs/n03_structural_owner_gate_qualification_20261006_v2/config.json)
and produced immutable raw/summary receipts under
[`n03_structural_owner_gate_qualification_20261006_v2`](../../../experiments/logs/n03_structural_owner_gate_qualification_20261006_v2/).
All eight cells passed:

- producer owner with matching, recipient, and unknown judged role;
- recipient-only and mixed ownership rejection;
- missing registration rejection;
- duplicate replay idempotence;
- contract/path mutation fail-closed.

The qualification used 0 LLM calls, 0 GPU jobs, no native grader, and explicitly sets
`scientific_claim_allowed=false`. A first attempt that pre-created the output directory is retained
as `v1/attempt_failure.json`; it did not enter qualification logic.

The focused structural-owner, two-stage, PIPE3 contract/profile, delayed-adapter, responsibility,
and composition regression suite passed **43 tests**. These are engineering checks only.

## Goal reconciliation

- **Satisfied partially:** the responsibility gate no longer depends on stochastic role wording;
  disagreement is observable and reproducible; historical receipts are not rewritten.
- **Still open:** real live parity with explicit owner registration, independent roots and streams,
  producer-quality measurement, later-use outcome, baseline parity, future assignment quality,
  complete cost, online latency, forgetting, and scientific efficacy.
- **Reason for remaining gap:** the prior C1 run was one development root and the new qualification
  is intentionally zero-call. No failure or missing result is used to lower the Goal.

## Next action

Version a new bounded live card that carries the structural-owner registration and reports judged-role
disagreement under the same candidate menu, propensity, budget, and read-cut contract. Only after
that card and the independent-root/baseline gates pass should a scientific comparison or A800
challenger be considered.
