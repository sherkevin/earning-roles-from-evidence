# Isolated public-profile read qualification — 2026-09-30

## Result

The assignment runner now has an explicit separate-process read path. When
`consume_profiles(..., isolated_policy_read=True)` is used, the parent first
seals the profile attestation, sends only the public profile payload to a
small worker process, and accepts the state transition only after the worker
returns matching `offer_digest`, sorted profile IDs, read cut, and
`policy_input_digest`. The trace records the worker hash and switches to
`isolated_process_public_digest` with `isolated_policy_trace=true`.

The default path is unchanged and remains explicitly non-isolated. This keeps
old offline qualifications and historical outputs reproducible while making
the stronger boundary opt-in for the versioned live runner.

## Evidence

- Worker: `scripts/peerrolebench_policy_read_worker.py`
- Parent verifier: `scripts/peerrolebench_isolated_policy_read.py`
- Runner integration: `scripts/peerrolebench_pipe3_assignment_runner.py`
- Qualification: `scripts/peerrolebench_isolated_policy_read_qualification.py`
- Tests: `tests/test_peerrolebench_isolated_policy_read.py`
- Final artifact: `experiments/logs/n03_isolated_policy_read_qualification_20260930_v1/`
- Qualification checks: **5 passed**; targeted tests with the runner: **3
  passed**; full `tests/test_peerrolebench_*.py` regression after this task:
  **298 passed**.
- The run made **0 API calls** and submitted **0 GPU jobs**.

The rejection matrix covers a read cut before profile availability, an unknown
profile ID, and non-canonical profile ID order. The positive trace verifies
that the worker's policy input digest equals the assignment attestation's
digest.

## Boundary

The worker receives only the sealed public offer payload and is separate from
the parent process, scorer, ledger, and actor source. This is a
non-adversarial process-boundary qualification, not a hostile-code sandbox:
the worker is trusted project code and the parent verifies its response. It
does not execute a real producer/recipient episode, generate a profile with an
LLM, measure later-use effect, or establish benchmark/baseline parity.

## Goal reconciliation

This advances ER-G1's auditable assignment path and provides the missing
positive engineering seam for isolated policy reads. It does not satisfy
ER-G1's complete live delivery chain, ER-G2's online-learning requirement,
ER-G3's frozen benchmark/baseline requirement, or ER-G4's real-API scientific
evidence requirement. The active Goal is unchanged and
`scientific_readiness=false` remains correct.

## Next gate

Use this opt-in isolated read path inside the versioned PIPE3 live runner,
after a real episode has produced a source-bound offer and before the next
selection. Record the worker trace in the native/auxiliary ledger lineage and
test that the later selection actually consumes the profile. Do not treat the
process flag alone as proof of online learning.
