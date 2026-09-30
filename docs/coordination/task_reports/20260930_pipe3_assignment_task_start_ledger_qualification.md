# PIPE3 assignment to native task-start ledger qualification — 2026-09-30

## Result

The assignment boundary now accepts an optional native `PeerRoleLedger`. After
the Meta-Team profile offer is consumed and the later selection is sealed, the
runner appends `task_start` with the same `task_id` and `decision_index` bound
by the offer. The JSONL trace records the native ledger record hash. Source
dispatch, scoring, recipient action, and terminal outcome remain downstream
gates.

## Evidence

- Implementation: `scripts/peerrolebench_pipe3_assignment_runner.py`
- Qualification: `scripts/peerrolebench_pipe3_assignment_runner_qualification.py`
- Final artifact: `experiments/logs/pipe3_assignment_runner_boundary_20260930_v4/`
- The fixture qualification includes a native selection followed by the
  runner's `task_start`; the `ledger_task_start` check passes.
- Targeted test: **1 passed**; full `tests/test_peerrolebench_*.py` regression:
  **281 passed** before this seam refinement and the targeted test passes after
  it. The run used **0 API calls** and **0 GPU jobs**.

## Boundary

This remains a hand-authored offline fixture. It does not execute PIPE3 source,
producer/recipient actors, scorers, or a live profile generator. It does not
provide an isolated policy-read trace; `isolated_policy_trace=false` remains
explicit. Candidate-key canonicalization, policy-selection view construction,
public feedback-row construction, and the real source/scorer/action/outcome
runner are still required before a real episode can be attempted.

## Goal reconciliation

The change improves the auditable protocol path under ER-G1 and reproducibility
under ER-G4, but it does not satisfy ER-G1's real delivery chain, ER-G2's
online-learning requirement, ER-G3's frozen benchmark/baseline gate, or ER-G4's
real-API scientific evidence requirement. Goal remains unchanged and
`scientific_readiness=false`.
