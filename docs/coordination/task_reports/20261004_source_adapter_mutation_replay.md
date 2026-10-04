# Task report — source-adapter and history-mutation replay

Date: 2026-10-04
Status: `QUALIFIED_OFFLINE` (adapter and mutation engineering only)
Goal change requested: `false`

## Purpose

The canonical seven-arm public-input replay currently exercises a positive
recipient-judgment row.  Before any live stream, we need independent evidence
that the two declared channel comparators can receive their own legal source
and that malformed source/history material fails closed.  This task replays
the existing typed adapter qualifications at the current commit; it does not
claim that all channels are already in the canonical scientific matrix.

## Executed receipts

All three runs were written before analysis and used zero API/LLM calls and
zero GPU jobs:

1. `experiments/logs/n03_policy_matrix_20261004_v1/` — seven-arm root-level
   matrix, seven hand-authored protocol cases, manifest and snapshot replay.
2. `experiments/logs/n03_raw_acceptance_replay_20261004_v1/` — typed raw
   acceptance sidecar replay with canonical, wrong-decision, wrong-producer
   and duplicate-sidecar cases.
3. `experiments/logs/n03_history_adversarial_20261004_v1/` — two-entry public
   history replay with valid, permutation, candidate-identity, projection
   aggregate and scope-isolation cells.

Focused regression for the runner, raw sidecar, registry and peer-history
modules passed: `34 passed` via
`python3 -m pytest -q tests/test_peerrolebench_policy_matrix_runner.py
tests/test_peerrolebench_raw_acceptance_replay.py
tests/test_peerrolebench_candidate_registry.py
tests/test_peerrolebench_peer_history.py
tests/test_peerrolebench_peer_history_adapter.py
tests/test_peerrolebench_history_selector.py`.

## Results

- The root-level matrix passed all seven cases.  In its positive controls,
  `raw_acceptance` consumed exactly one eligible row and made one update only
  in the raw arm; `terminal_only` did the same only in the terminal arm.
  UNKNOWN, unselected, unsupported correction and recipient-judgment cases
  preserved their declared ignore/no-update semantics.
- The raw sidecar replay passed its canonical positive control and rejected
  wrong decision, wrong producer and duplicate sidecar material with zero
  updates.
- History replay passed the valid two-entry and scope-isolation cells.  Entry
  permutation, candidate mismatch and aggregate-rate mutation were rejected
  as `UNKNOWN`, with zero policy updates.

## What this closes

These receipts close a reusable engineering sub-gate: the current policy
implementations have reachable positive raw/terminal update paths, and the
typed raw sidecar plus public peer-history store reject the tested identity,
ordering and aggregate mutations.  The evidence is reproducible and is
recorded separately from the canonical v21 public-input receipt.

## What remains open

The positive controls are not yet a canonical same-information comparison:
the raw replay uses a dedicated sidecar stream, while the terminal control
still uses the existing `FeedbackSidecar` contract.  The canonical PIPE3
seven-arm stream has not yet been rebuilt from those source projections, and a
terminal-specific mapping must be kept separate from producer responsibility
attribution.  Registry reorder/version/source mutations also need runner-level
preflight cells, not only module tests.  Therefore benchmark authority,
scientific baseline parity, independent live histories, later-use utility,
measured cost, real-time/forgetting claims and A800 work remain closed.

The next design task is a zero-call canonical channel card: construct raw
acceptance from the native recipient-judgment sidecar, add an independent
terminal-outcome projection with explicit label provenance, run both through
the same seven-arm menu/read-cut/arrival/feature contract, and add registry
and history digest mutation cells.  It must preserve the strict UNKNOWN and
zero-update rule and must not be described as a benchmark result.
