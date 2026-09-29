# Task report — benchmark track confirmation and active-plan upgrade

- **Date**：2026-09-30
- **Status**：`done / active-plan governance change`
- **User confirmation**：received in the current session
- **API/GPU/A800**：0 / 0 / 0

## Decision recorded

The user confirmed `ArtifactRole` as the paper primary track and `PeerSelect` as
the mechanism secondary track. ADR 0042 records the scope and consequences.

## Documents updated

- Active benchmark plan: `benchmark_baseline_v1.1_20260930.md`.
- Canonical registry: registry `v1.6`, with the new active benchmark plan.
- Candidate cell manifest: primary/secondary fields filled; it remains
  `CANDIDATE_NOT_FROZEN` and contains no result values.
- Active method/storyline cross-references now point to benchmark plan v1.1.

The plan keeps the tracks separate: PeerSelect can qualify selector dynamics,
but cannot substitute for ArtifactRole's recipient judgment, responsibility
attribution, future assignment and quality-cost claim.

## What remains open

The benchmark is still not frozen. Root qualification, closest published
adapter, baseline runner parity, later assignment, independent live streams,
and the complete cell manifest still need to pass the active v1.2 evaluation
standard. No formal API effect run or A800 job is authorized by this change.

Evidence: [`ADR 0042`](../../user/decisions/0042-confirm-artifactrole-primary-peerselect-secondary.md),
[`benchmark_baseline_v1.1_20260930.md`](../../research/versions/benchmark-baseline/benchmark_baseline_v1.1_20260930.md),
and [`active_versions.json`](../../research/canonical/active_versions.json).
