# Typed public feedback-row adapter qualification — 2026-09-30

## Result

The next boundary after sidecar projection is now explicit. A
`PolicyFeedbackProjection` can be serialized into the scalar public row that
`AssignmentEvidenceOffer` and the versioned PIPE3 runner consume. The adapter
requires event-time `arrival_index`, preserves candidate version keys and
correction lineage, requires an explicit public reason for `UNKNOWN`, and
never accepts an arbitrary scorer dictionary.

The adapter also provides one canonical constructor from typed projections to
`make_offer`. This removes the repeated hand-written row dictionaries that
could otherwise omit the candidate key, evidence version, or event-time
fields. The existing projection layer remains responsible for converting a
validated sidecar and attribution gate into the typed projection.

## Evidence

- Implementation: `scripts/peerrolebench_public_feedback_rows.py`
- Qualification: `scripts/peerrolebench_public_feedback_rows_qualification.py`
- Tests: `tests/test_peerrolebench_public_feedback_rows.py`
- Final artifact: `experiments/logs/n03_public_feedback_rows_qualification_20260930_v1/`
- Qualification checks: **7 passed**; targeted projection/adapter tests:
  **24 passed**; full `tests/test_peerrolebench_*.py` regression after this
  task: **290 passed**.
- The run made **0 API calls** and submitted **0 GPU jobs**.

The qualification covers eligible rows, UNKNOWN rows with a fixed public
reason and no label, wall-clock-only projections, candidate-menu mismatch,
missing UNKNOWN reason, and rejection of an untyped/private-shaped input.

During this task, the UNKNOWN branch of `project_feedback` was also corrected
to retain v4 `arrival_index` and `supersedes`. The regression fixture confirms
that a responsibility-ineligible correction still carries its event-time and
lineage fields without exposing private gate data.

## Boundary

This qualification starts from a typed `PolicyFeedbackProjection`; it does
not itself prove that the projection came from a canonical ledger record, that
the full responsibility lineage was replayed, or that its arrival index
matches the frozen global schedule. Those checks remain upstream requirements:
the live adapter must bind each sidecar to its ledger event, run the v4
responsibility-lineage validation, validate the expected schedule, then call
this row/offer constructor. The run is therefore an offline contract result,
not a benchmark, profile-quality, online-learning, or scientific-effect
result.

## Goal reconciliation

This closes a concrete public-information serialization gap under ER-G1 and
improves ER-G4 reproducibility. It does not satisfy ER-G1's real delivery
chain, ER-G2's online-learning requirement, ER-G3's frozen benchmark/baseline
requirement, or ER-G4's real-API evidence requirement. The active Goal is
unchanged and `scientific_readiness=false` remains correct.

## Next gate

Build the source-bound adapter that performs, in one guarded path: canonical
ledger binding, v4 responsibility-lineage validation, frozen arrival-schedule
validation, typed projection, this public-row conversion, and offer sealing.
Then connect that offer to the real versioned PIPE3 source/scorer/action/
outcome runner. No new API episode should be used to bypass those checks.
