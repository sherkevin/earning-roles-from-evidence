# PIPE3 assignment runner boundary qualification — 2026-09-30

## Result

Added a zero API / zero GPU runner boundary around the existing
`MetaTeamAssignmentOffer`, `MetaTeamAssignmentAttestation`, and
`bind_assignment_to_selection` contract. The runner records the accepted
sequence `offer_emitted → profile_consumed → selection_sealed → task_started`
as JSONL events. Every event carries the offer digest, consumed policy input
digest (when present), `policy_read_trace_mode=recorded_public_input_digest`,
and `isolated_policy_trace=false`.

## Rejection matrix

The offline qualification covers missing attestation, selection before profile
consumption, a wrong candidate menu, duplicate profile consumption, a
pre-watermark profile, and post-offer profile mutation. Each case is expected
to raise `ValueError` and is included in `summary.json` with its reason.

## Evidence

- Runner: `scripts/peerrolebench_pipe3_assignment_runner.py`
- Qualification: `scripts/peerrolebench_pipe3_assignment_runner_qualification.py`
- Test: `tests/test_peerrolebench_pipe3_assignment_runner.py`
- Artifacts: `experiments/logs/pipe3_assignment_runner_boundary_20260930_v1/`
  and final `experiments/logs/pipe3_assignment_runner_boundary_20260930_v3/`.
- Verification: targeted runner test `1 passed`; full `tests/test_peerrolebench_*.py`
  regression `281 passed`; qualification status `QUALIFIED_OFFLINE`;
  `real_api_calls=0`, `gpu_jobs=0`. The qualification writes `config.json`
  before constructing the fixture runner and streams the accepted trace to
  `trace.jsonl`.

This qualification does not claim isolated policy execution or model quality;
`isolated_policy_trace=false` is explicit until a versioned isolated runner is
implemented.
