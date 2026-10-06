# Task report — C1 v2 structural-owner live rerun

**Date:** 2026-10-06
**Status:** `PARTIAL`
**Goal change requested:** `false`
**Scientific claim allowed:** `false`

## Frozen run

The run used the pinned card
[`n03_c1_pipe3_bounded_live_dev_v2.json`](../../../configs/aamas2027/n03_c1_pipe3_bounded_live_dev_v2.json),
the `c1-pipe3-bounded-live-v2-structural-owner` runner, real `内部/qwen3.8-max` streaming API,
thinking disabled, one PIPE3 root, three arms, no retries, and the predeclared candidate menu. The
raw receipt is
[`n03_c1_pipe3_bounded_live_20261006_v4`](../../../experiments/logs/n03_c1_pipe3_bounded_live_20261006_v4/).
It contains 10 real API requests, all recorded with raw responses and usage; no GPU job ran.

## Observed result

| arm | source gate | judged role | structural owner | outcome |
|---|---|---|---|---|
| `no_update` | `ELIGIBLE` | `recipient` | `producer` | complete development chain; disagreement retained |
| `contextual_trust_linear` | `PENDING_ATTRIBUTION` | `recipient` | `recipient` | correctly stopped; `processor.py` changed |
| `RARE` | `ELIGIBLE` | `producer` | `producer` | complete development chain; one delayed update |

The structural-owner gate behaved as designed. It retained the no-update event despite a noisy
judged-role disagreement because the registered producer defect, independent producer score and
absence of recipient-owned changes identified a producer owner. It rejected the contextual arm
because the actual recipient modified its own `processor.py`; the model wording did not create the
rejection. RARE passed with matching producer judgment and owner.

This is not a three-arm scientific comparison. The contextual arm has no target assignment or
future outcome after its responsibility gate, so the run cannot estimate assignment utility,
quality, regret, or cost differences. The arm-specific recipient actions also show that this card
does not yet provide a common completed source episode for policy comparison.

## Cost and implementation audit

The receipt confirms 10 API attempts and preserves input/output usage. Two reproducibility defects
were found after the run: arm-level raw config lines still used the legacy runner version string,
and scorer/state cost aggregates were not emitted. Historical v4 files are immutable. The runner is
now patched for future cards to take the version from the card and emit scorer seconds, update
seconds, action wall time, repair cost, and state bytes; the zero-API contract suite remains
16/16 passed after the patch.

## Goal reconciliation

- **Progress:** structural ownership is now tested on real model outputs, and recipient-owned work
  is prevented from becoming producer evidence.
- **Still open:** common completed baseline cells, independent roots/streams, producer-quality
  information value, future assignment quality/cost, full cost accounting on a fresh run, drift,
  forgetting, and scientific efficacy.
- **Decision:** do not rerun this same card immediately. The next live card must make the source
  completion and recipient-action contract common across arms or explicitly model the arm-specific
  `UNKNOWN` denominator; otherwise another 10-call rerun would repeat the same identification gap.

No paper result cell is filled from this receipt, and the Goal remains unchanged.
