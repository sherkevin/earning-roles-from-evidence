# PIPE3 source/scorer/action/outcome → profile composition qualification — 2026-09-30

## Result

The first root-specific composition now executes the actual pinned PIPE3
material and v2 CPU scorer workers before entering the assignment path. It
does not use case names or hand-authored score labels to decide eligibility.

## Evidence

- Runner: [`scripts/peerrolebench_pipe3_profile_episode_qualification.py`](../../scripts/peerrolebench_pipe3_profile_episode_qualification.py)
- Test: [`tests/test_peerrolebench_pipe3_profile_episode.py`](../../tests/test_peerrolebench_pipe3_profile_episode.py)
- Log: `experiments/logs/n03_pipe3_profile_episode_qualification_20260930_v1/`
- Two controls executed, with 25 streamed JSONL events and per-scorer raw
  evidence directories.
- **0 API calls, 0 GPU jobs**, `scientific_claim_allowed=false`.

## Control outcomes

| Control | Actual CPU evidence | Action change | Responsibility gate | Profile/assignment |
|---|---|---|---|---|
| producer-owned defect | Qp `FAIL` with complete coverage; post-action Qr/Y `PASS` | `producer.py` only | `ELIGIBLE` | profile generated; isolated read → selection → native task-start passed |
| recipient-owned repair | delivered Qp `PASS`; post-action Qr/Y `PASS` | `processor.py` only | `PENDING_ATTRIBUTION` | no profile and no assignment update |

The scorer transport emitted macOS permission errors in this environment; the
qualification logged them and used the same pinned v2 scorer workers through a
temporary CPU source tree. The fallback did not hard-code scores. Module
imports were cleared between temporary trees so a previous case could not leak
into the next result.

## Boundary

This is a protocol and runner qualification, not a benchmark result. The
profile is still the deterministic fixture generator; the two controls share
one structural TeamBench root; no LLM judgment was generated; there is no
independent live history, baseline comparison, later-use quality effect, or
online policy update. The recipient-owned control remains a required negative
control against responsibility leakage.

## Goal reconciliation

This closes the zero-call path from real task material and scorer/action
outputs to the source-bound offer and isolated assignment seam. It does not
close the Goal's real API, independent-root, baseline, real profile quality,
online-learning, or A800 gates. The active Goal is unchanged and benchmark /
baseline remain `NOT_READY`.

## Next gate

Review this composition and its scorer fallback as an engineering boundary,
then implement a separately metered public-only profile generator. Only after
that is qualified should one bounded real PIPE3 episode be attempted; no
larger sample or A800 job is justified by this zero-call result.
