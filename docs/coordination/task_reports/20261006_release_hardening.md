# Task report — parent-source release hardening

Date: 2026-10-06
Status: `PARTIAL`
Goal change requested: `false`
Scientific result: `none`

## Purpose

The live-smoke re-audit found four nonblocking release risks. This task closes
the three local, low-risk runner risks without touching the frozen live result:
parent-source status must reflect the typed gate, the API budget must be
validated before any actor call, and a root run cannot be marked complete when
its canonical cost ledger is invalid. The independently supplied source seal
and exact runner pin remain explicit prerequisites for the next scientific
card; they are not approximated here.

## Changes and evidence

- `parent_source/summary.json` now reports `COMPLETE_SOURCE_ONLY` only when
  `evidence_publish_allowed=true`; complete but unattributable episodes are
  reported as `PENDING_ATTRIBUTION`, and incomplete episodes as `UNKNOWN`.
- The runner validates that `maximum_api_requests` equals the declared parent
  plus per-arm target budget before `_prepare_context()` or any API call.
- `validate_cost_ledger()` returns `valid=true`; root completion requires this
  flag, and cost-ledger validation errors are represented as an invalid root
  rather than an uncaught success path.
- The default runner card is the parent-source card, so an accidental default
  invocation cannot silently use the older arm-local development card.

The pre-run configuration and raw test output are in
[`n03_release_hardening_regression_20261006_v2`](../../../experiments/logs/n03_release_hardening_regression_20261006_v2/summary.json).
It used committed runner `8fc63e4`, 0 real API calls and 0 GPU jobs; all 19 focused
tests passed. No historical live output was modified or reclassified.

## Goal reconciliation

This improves ER-G3/ER-G4 fail-closed execution and reproducibility. It does
not add a second root, a same-information baseline, an independent seal, an
exact scientific runner pin, or a quality estimate. ER-G1 and ER-G2 remain
open, the A800 gate remains closed, and `goal_change_requested=false`.
