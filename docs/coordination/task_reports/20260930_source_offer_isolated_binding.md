# Task report — source-bound offer isolated-read binding (2026-09-30)

## Purpose

Close the gap left by the previous isolated trace: the child process must read
the exact `AssignmentEvidenceOffer` produced by the source-bound feedback
adapter, rather than an independent profile offer.

## Implementation

Added a typed parent/child reader for `AssignmentEvidenceOffer`. The child
receives only the canonical public payload, the operator record hash, bundle
digest, and read cut. It rejects unknown/private row fields, candidate-menu
violations, and rows unavailable at the watermark. The parent verifies the
offer identity, task/role/context, candidate versions, bundle digest, read
cut, policy-input digest, and public-bundle digest before returning an isolated
read trace.

## Qualification

The accepted run is
`experiments/logs/n03_pipe3_isolated_live_trace_qualification_20260930_v8/`.
It reuses the pinned PIPE3 CPU scorer/action/outcome path and the canonical
source-bound boundary. The trace order remains
`actor_output → scorer_before → action → scorer_after → outcome → policy_read`,
but the policy-read event now carries the exact source offer ID, record hash,
bundle digest, candidate menu, read cut and public-row digest. The isolated
child also returns and the parent verifies task/role/context, evidence version,
availability watermark and the canonical policy-input digest; the child also
recomputes the bundle and policy-input digests before responding. The later
selection consumes that same offer. The responsibility gate remains closed,
so the public row is UNKNOWN and `policy.updates=0`.

Attempt v5 is retained as a failed receipt: the trace reached the scorer and
fallback records but crashed while serializing stale `task_id`/`task_index`
fields that were not part of the new read trace. V8 reran the corrected path
after adding child-side digest checks; the failure is not overwritten.

The run is `QUALIFIED_OFFLINE`, with 0 external API calls, 0 GPU jobs, and
`scientific_claim_allowed=false`. The full PeerRoleBench suite passed 315/315;
the earlier v2/v3/v4/v5/v6/v7 traces remain immutable for audit.

## Boundary

This closes the typed public-object and process-order seam. It still does not
provide independent live histories, same-information baseline parity, later-use
outcome, profile quality, online-learning efficacy, or benchmark evidence. No
new real API episode or A800 job is authorized by this qualification.
