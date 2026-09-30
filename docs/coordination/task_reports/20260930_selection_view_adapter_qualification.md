# Versioned/native selection view qualification — 2026-09-30

## Result

The selection boundary now has an explicit view adapter between the native
ledger representation and the versioned sidecar representation. It resolves
only exact `candidate_id@candidate_version` registry keys, preserves menu
order and the selected index, and carries the task index, selection time, and
selector identity required by later assignment binding.

This closes an identity and timing ambiguity that the preceding task-start
seam left open: native `PeerSelection` stores bare IDs and does not itself
carry versions, `candidates` as versioned references, or `selected_at`. The
adapter therefore does not infer a version or reconstruct a menu from a bare
ID. A later assignment is bound only after the explicit view has passed the
same-menu, task-index, and read-cut checks.

## Evidence

- Implementation: `scripts/peerrolebench_selection_view_adapter.py`
- Qualification: `scripts/peerrolebench_selection_view_adapter_qualification.py`
- Tests: `tests/test_peerrolebench_selection_view_adapter.py`
- Final artifact: `experiments/logs/n03_selection_view_adapter_qualification_20260930_v1/`
- Qualification checks: **8 passed**; targeted tests: **4 passed**; the
  complete `tests/test_peerrolebench_*.py` suite after this addition: **285
  passed**.
- The qualification used a hand-authored registry and native selection. It
  made **0 API calls** and submitted **0 GPU jobs**.

The rejection matrix covers unknown versions, duplicate or malformed keys,
wrong choices, negative selection times, native menu/registry mismatch, and
menu reordering at assignment binding. The raw fixture records the registry,
native selection, explicit versioned view, offer, and consumption attestation.

## Boundary

This is an offline identity/lineage qualification, not a benchmark result. It
does not construct a public feedback row from a real producer/recipient
episode, run a source/scorer/action/outcome chain, generate a profile, or
provide an isolated policy-read trace. The native task-start runner still has
`isolated_policy_trace=false`; baseline parity, independent live histories,
cost accounting, later-use effect, benchmark freeze, and A800 evidence remain
open.

## Goal reconciliation

The adapter advances the auditable selection-to-assignment interface and
therefore improves ER-G1's protocol completeness and ER-G4's reproducibility.
It does not satisfy ER-G1's real delivery chain, ER-G2's online-learning
requirement, ER-G3's frozen benchmark/baseline requirement, or ER-G4's
real-API scientific-evidence requirement. The active Goal is unchanged and
`scientific_readiness=false` remains the correct status.

## Next gate

Construct a public, source-bound feedback row from the existing PIPE3
producer-score, situated-judgment, recipient-action, adoption, and ownership
sidecars. The row must retain the selected versioned candidate, source and
delivery digests, eligibility/UNKNOWN reason, event-time and cost, and must
be accepted by the versioned runner without allowing private scorer fields to
cross the policy boundary. Qualify that adapter offline before considering a
new real API episode.
