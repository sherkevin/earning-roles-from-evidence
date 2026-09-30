# Task report — source-bound PIPE3 boundary continuation (2026-09-30)

## Purpose

Close the smallest missing runner seam: a responsibility-gated v4 public
feedback offer must reach a later versioned selection while preserving the same
native ledger and auxiliary manifest chain.

## What was tried and rejected

The first implementation introduced a separate policy wrapper with a fresh
ledger. Independent review found that it could not prove continuity with the
source episode, relabeled source task index `0` as destination task index `0`,
and its mutation test failed at a stale offer digest before exercising the
runner. Those attempts remain in `experiments/logs/n03_source_bound_selection_qualification_20260930_v1/`
and `v2/`; they are not evidence of a passing boundary.

## Final qualification

The final qualification reuses the existing `Pipe3SelectionBoundary` instance:

1. task 0 selection is sealed on the canonical boundary;
2. producer delivery, producer score, recipient judgment, consumer action,
   terminal outcome and evidence lineage are recorded on that ledger;
3. the v4 source-bound adapter checks canonical ledger membership, frozen arrival
   schedule and responsibility gate, then seals a public offer for explicit
   target task index 1;
4. the same boundary consumes the offer before task 1 selection;
5. the native and auxiliary manifests are validated after the transition.

Receipt: `experiments/logs/n03_pipe3_source_bound_boundary_qualification_20260930_v3/`.
The qualification passed with 0 API calls, 0 GPU jobs, 9 ledger events, one
policy update, and valid native/auxiliary roots. A prior v1 run with an
incorrect event-count expectation is preserved as a failed qualification.

## Interpretation

This closes a runner/lineage seam. It does not demonstrate live agent quality,
profile quality, baseline parity, independent streams, later-use utility, or
RARE efficacy. The next engineering gate is to preflight all attestation and
availability constraints before `choose_and_seal` mutates policy/ledger state;
only then can this seam be considered safe for a future live runner.
