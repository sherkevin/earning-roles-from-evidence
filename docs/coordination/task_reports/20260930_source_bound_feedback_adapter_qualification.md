# Source-bound PIPE3 feedback adapter qualification — 2026-09-30

## Result

The sidecar-to-offer path is now guarded by one source-bound adapter. Given a
typed selection sidecar, its exact ledger record, typed feedback sidecar,
operator attribution gate, canonical ledger, and frozen arrival schedule, it
performs the following checks in order:

1. bind the selection and feedback sidecars to their canonical ledger records;
2. require event-time sidecar v4 and validate the full producer/delivery/
   recipient/action lineage;
3. require one-to-one agreement with the frozen arrival schedule;
4. project the sidecar through the existing public-information boundary; and
5. seal the result as the versioned `AssignmentEvidenceOffer` consumed by the
   PIPE3 selection runner.

The raw acceptance comparator is intentionally outside this adapter. It must
not be silently mixed with the responsibility-aware producer label path.

## Evidence

- Implementation: `scripts/peerrolebench_source_bound_feedback_adapter.py`
- Qualification: `scripts/peerrolebench_source_bound_feedback_adapter_qualification.py`
- Tests: `tests/test_peerrolebench_source_bound_feedback_adapter.py`
- Final artifact: `experiments/logs/n03_source_bound_feedback_adapter_qualification_20260930_v1/`
- Qualification checks: **5 passed**; targeted tests: **5 passed**; full
  `tests/test_peerrolebench_*.py` regression after this task: **295 passed**.
- The run made **0 API calls** and submitted **0 GPU jobs**.

The mutation matrix rejects a schedule event-type mutation, a sidecar/ledger
hash mismatch, a non-v4 online sidecar, a schedule-index mutation, and an
incomplete canonical ledger. The successful row includes the selected
versioned candidate, v4 arrival index, schedule digest, and sidecar digest.

## Boundary

This is a zero-call fixture using canonical protocol objects and a frozen v4
schedule. It is not a live PIPE3 episode: no LLM actor generated source, no
private scorer ran, no recipient action was produced by an actor, and no
policy update or later assignment was measured. The adapter currently calls
the existing strict lineage validator and offer constructor; isolated
policy-read tracing, real profile generation, cost accounting, independent
histories, and baseline parity remain open.

## Goal reconciliation

The source-bound path closes a concrete ER-G1 protocol gap and improves ER-G4
reproducibility. It does not satisfy ER-G1's real delivery chain, ER-G2's
online-learning requirement, ER-G3's frozen benchmark/baseline requirement,
or ER-G4's real-API scientific-evidence requirement. The active Goal remains
unchanged and `scientific_readiness=false` remains correct.

## Next gate

Use this adapter inside a versioned PIPE3 live runner that executes the
isolated producer, scorer, recipient, action, and terminal-outcome boundaries,
then writes the same source-bound offer before the next selection. Preserve
the existing stop rule: an UNKNOWN or attribution failure cannot update a
policy, and no new API sample is valid until the isolated policy-read trace is
auditable.
