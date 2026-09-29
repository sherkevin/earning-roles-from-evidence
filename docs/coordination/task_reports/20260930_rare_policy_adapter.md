# RARE selection adapter qualification — 2026-09-30

## Scope

This task connected the RARE-Anchor candidate state to the shared selected-only
policy boundary and to the PIPE3 selection seam. It is an implementation gate,
not a benchmark result, an efficacy result, or a method promotion.

The qualification is versioned as
`n03_rare_policy_adapter_20260930_v5`. The v1–v4 logs are preserved; v5
records the final sidecar/projection source hashes after frozen-schedule replay
and strict correction-lineage checks were tightened.

## Changes

- `RarePolicy` now consumes the same `CandidateRef`/`Selection`/`Feedback`
  contract as the comparator policies.
- Every RARE selection must carry a finite feature vector for every candidate,
  with the fixed dimension and L2 bound used by `RareAnchorState`.
- A sealed selection must use `hash64-v1`; an arbitrary encoder version is not
  silently treated as the candidate encoder.
- Eligible recipient judgments require a non-negative `arrival_index`.
  `UNKNOWN`/non-public rows may carry `label=None` and never update state.
- Corrections may share a source event only when they declare `supersedes`;
  known cross-selection/channel corrections are rejected. Feedback replay
  markers are committed only after the concrete updater accepts the event, so a
  malformed event can be retried after metadata repair.
- PIPE3 forwards captured features, optional labels, arrival indices and
  correction references.
- Policy sidecar v4 adds the frozen `arrival_index` and optional `supersedes`
  fields, retains the v3 artifact/delivery/action lineage requirements, and
  cannot omit `arrival_index`. Event-time replay requires the caller to supply
  the frozen `feedback_id → arrival_index` schedule; otherwise it is invalid.
  Historical v2/v3 rows retain their legacy wall-clock replay path. The raw
  acceptance projection carries the same optional event-time fields so a raw
  comparator cannot silently fall back to a different clock.
- Assignment evidence offers can carry a late correction without duplicating
  the source-event identity in `evidence_ids`.

## Evidence

The zero-call qualification wrote:

`experiments/logs/n03_rare_policy_adapter_20260930_v5/`

It records the configuration and source hashes before execution, direct RARE
update/correction/restore traces, and a PIPE3 native/auxiliary manifest trace.
It reports `QUALIFIED_OFFLINE`, with `real_api_calls=0`, `gpu_jobs=0`, and
`scientific_claim_allowed=false`.

The targeted regression set passed **78 tests**. It covers the existing policy,
candidate-state, sidecar, assignment-attestation, event-time, runner-boundary,
and new RARE adapter tests. Full repository pytest remains unsuitable as a
gate because historical fixture trees and optional external dependencies fail
during collection; that limitation is not hidden by this task.

The historical v2/v3 sidecar compatibility path was also re-run as
`experiments/logs/n03_policy_sidecar_stream_qualification_20260930_v5/`; its
five replay/mutation cases passed with zero API calls and zero GPU jobs.

## Interpretation and remaining gates

This closes an executable interface gap: RARE can now be replayed through the
shared selection boundary with typed event-time metadata. It does not show that
RARE improves assignment, quality, regret, cost, or stability. The candidate
method remains `CANDIDATE_NOT_ACTIVE`.

Still open before a scientific run are the frozen benchmark/root split, closest
published adapter parity, independent producer-quality and later-assignment
labels, complete responsibility-lineage runner coverage, and a pre-registered
baseline matrix. No LLM API, benchmark episode, or A800 job was started by this
task.
