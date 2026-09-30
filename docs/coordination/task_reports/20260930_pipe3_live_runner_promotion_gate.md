# Task report — PIPE3 versioned live-runner promotion gate (2026-09-30)

## Purpose

Promote the existing source-bound composition from a single in-process trace to
a root-specific, versioned, two-control runner without spending an external
API call or GPU job. The runner gives each control its own policy, ledger, RNG
namespace and output directory, and records the public event/cost/UNKNOWN
trace before a future scientific run.

## Implementation

`peerrolebench_pipe3_live_runner_v2_qualification.py` reuses the pinned PIPE3
material, CPU scorer/action path, canonical selection boundary, source-bound
offer adapter and isolated public reader. For both `producer_owned` and
`recipient_owned` controls it records:

```text
actor_output → scorer_before → action → outcome → source_offer
→ policy_read → next_selection → promotion_blocked
```

The per-control receipt includes source/material/registry hashes, event-time
schedule metadata, cost fields, ledger and manifest roots, replay status,
unknown denominators and failure preservation. The test also injects a failure
in one control and verifies that the other control's receipt is retained.

## Result

- V1 exposed a duplicate initial/source offer identifier at auxiliary-manifest
  validation; its `FAILED_OFFLINE` receipts are preserved.
- V3 fixes that identifier and records the complete qualification metadata; it
  reaches the intended stop for both controls:
  `BLOCKED_BY_RESPONSIBILITY_GATE`, with `policy_updates=0`, one UNKNOWN row,
  no `LaterAssignment`, no next `task_start`, and no next outcome.
- The runner returns `passed=false` deliberately. It does not claim a live
  history, learning effect or benchmark result.
- Targeted tests: **2 passed**; full PeerRoleBench regression: **317 passed**.
  All API/GPU counters remain zero.

## What the failure establishes

The stop is a contract deadlock, not a transport failure. The current
`producer_feedback_eligibility` function can report diagnostic `ELIGIBLE`, but
`policy_update_allowed` is hard-closed. The public offer must therefore remain
UNKNOWN. `LaterAssignment` requires non-empty role-evidence IDs, so fabricating
an assignment or treating diagnostic eligibility as a trainable label would
break the responsibility and information-boundary contracts.

The next method decision is therefore to define a two-stage evidence/update
semantics (or another user-approved rule) that can produce a legally attributed
pre-execution assignment without leaking recipient-owned repairs. This report
does not change that contract or the Goal.

## Gate status

The promotion gate remains **NO-GO** for real API/A800 work. Independent live
histories, same-information baseline parity, a qualified closest adapter,
later-use outcomes, complete cost/precision accounting and the online update
method are still open. The blocked receipt is the evidence required before
those claims can be made.
