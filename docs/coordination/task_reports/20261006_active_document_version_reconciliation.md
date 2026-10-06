# Task report — reconcile active research-document versions

**Date:** 2026-10-06  
**Status:** `PARTIAL`  
**Goal change requested:** `false`

## Purpose

The structural-owner decision promoted the method contract from v1.1 to v1.2. A scan showed that
the active storyline, benchmark/baseline plan, and method evaluation standard still pointed to the
superseded method version. Leaving those links stale would make the six-document acceptance chain
internally inconsistent.

## Changes

- Created active [`method_v1.3_20261006_eval.md`](../../research/versions/evaluation/method/method_v1.3_20261006_eval.md).
- Added a hard evaluation rule separating contract-derived `structural_owner_role` from noisy
  judged `target_role`/paths, including disagreement calibration and fail-closed mutation cases.
- Marked method evaluation v1.2 superseded.
- Updated active storyline and benchmark/baseline references to method v1.2.
- Updated the canonical registry to v1.9 and the canonical README to expose exactly one active
  method contract and one active method evaluation standard.

## Evidence and reconciliation

This was a documentation consistency task; it used no LLM/API/GPU calls and makes no scientific
claim. The substantive structural-owner qualification remains in
[`20261006_structural_owner_gate_activation.md`](20261006_structural_owner_gate_activation.md),
with A1--A8 passed but real baseline parity, independent roots, future assignment utility, cost,
and efficacy still open. Goal v1.0 is unchanged and no requirement was downgraded.

## Next action

Use the reconciled v1.2/v1.3 contracts as the input to the next bounded live-card design. The card
must bind explicit structural ownership, judged-role calibration, same-information baseline inputs,
and complete cost fields before any new real API run.
