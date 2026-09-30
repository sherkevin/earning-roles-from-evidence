# Task report — versioned source-bound PIPE3 composition (2026-09-30)

## Purpose

Connect the pinned PIPE3 producer/recipient/adoption scorer and action
validator to the versioned `Pipe3SelectionBoundary` without making a live API
call. The check uses two ownership controls and asks whether the responsibility
contract reaches the later selection boundary without leaking a label.

## What was tried

The first attempt (`..._v1/`) stopped during construction of the producer score
record. The second attempt (`..._v2/`) completed the scorer/action/outcome
composition, but a post-run audit found a semantic error: it treated the
diagnostic status `ELIGIBLE` as permission to update the policy even though the
current responsibility function explicitly returns `policy_update_allowed=false`.
That output is retained for audit and is not accepted as a qualification.

## Accepted qualification

The v3 script uses the real pinned CPU scorer workers (sandbox transport when
available, with the existing direct CPU fallback and its transport events), the
PIPE3 action validator, and the same canonical `Pipe3SelectionBoundary` for
selection 0, delivery, judgment, action, outcome, source-bound public offer,
and selection 1. It preserves the current gate: both controls produce an
UNKNOWN public row with reason `policy-update-gate-closed`, and neither changes
policy state. The producer-owned control is still reported diagnostically as
`ELIGIBLE`; the recipient-owned control is `PENDING_ATTRIBUTION`.

Receipt: `experiments/logs/n03_pipe3_versioned_source_bound_composition_qualification_20260930_v3/`.
Both controls passed scorer/outcome completeness, same-boundary task 0→1,
state-preserving no-update, and native/auxiliary manifest validation. The run
used 0 external API calls and 0 GPU jobs, and sets
`scientific_claim_allowed=false`.

## Interpretation and remaining gate

This closes a composition seam between the existing scorer/action code and the
versioned source-bound boundary. It does not show profile quality, online
learning, later-use utility, independent live histories, baseline parity, or a
benchmark result. The v2 semantic mistake is a reminder that diagnostic
eligibility and permission to train must remain separate until the later-use
and update contract is explicitly accepted. The next live-runner step must
preserve the same distinction and add isolated actor/scorer/action traces
before any new real API episode or A800 job.
