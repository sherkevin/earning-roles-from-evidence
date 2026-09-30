# Isolated read → selection → task-start composition qualification — 2026-09-30

## Result

The opt-in isolated profile reader now composes with the existing assignment
state machine and native ledger seam in one trace:

`offer_emitted → profile_consumed(isolated) → selection_sealed → task_started`.

The qualification checks that the worker's `policy_input_digest` equals the
consumption attestation digest, that selection occurs after the isolated read,
and that native `PeerRoleLedger.task_start` uses the same decision index as the
assignment offer.

## Evidence

- Qualification: `scripts/peerrolebench_isolated_assignment_runner_qualification.py`
- Test: `tests/test_peerrolebench_isolated_assignment_runner.py`
- Final artifact: `experiments/logs/n03_isolated_assignment_runner_qualification_20260930_v1/`
- Qualification checks: **4 passed**; targeted tests across the composed
  runner: **4 passed**; full `tests/test_peerrolebench_*.py` regression after
  this task: **299 passed**.
- The run made **0 API calls** and submitted **0 GPU jobs**.

## Boundary

This is still a hand-authored offline composition. It proves the state-machine
and ledger ordering but does not execute a producer, private scorer,
recipient, action, terminal outcome, or profile generator. The worker remains
a trusted non-adversarial process boundary. No later assignment effect,
online update, independent history, baseline parity, or benchmark result is
claimed.

## Goal reconciliation

The composition advances ER-G1's end-to-end protocol seam and ER-G4's
reproducibility. It does not satisfy ER-G1's real delivery chain, ER-G2's
online-learning requirement, ER-G3's frozen benchmark/baseline requirement,
or ER-G4's real-API scientific evidence requirement. The active Goal is
unchanged and `scientific_readiness=false` remains correct.

## Next gate

Insert this composed state machine after a real source-bound PIPE3 episode,
then record the isolated read trace alongside the actual source/scorer/action/
outcome lineage and execute a later selection. Only that live path can test
whether the profile changes a choice and whether any resulting role evidence
is attributable.
