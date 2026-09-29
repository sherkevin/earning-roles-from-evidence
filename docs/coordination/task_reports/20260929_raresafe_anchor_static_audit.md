# Task report — RARE-Anchor candidate static audit

- **Date**：2026-09-29
- **Status**：`done / candidate blocked`
- **Scope**：zero API, zero GPU, no active-method change

## What was checked

Using the current candidate implementation `scripts/peerrolebench_raresafe_candidate.py`:

1. `d=1, φ=1, y=1, λ=1, ρ=2` gives `θ=0.5` after one eligible update. `consolidate_if_safe` accepts the update, moves the anchor, clears fast statistics, refreshes, and returns `θ=0.0`. The just-learned preference is erased without new evidence.
2. After watermark 10, 300 unique source-index-0 corrections produce a correction queue of length 300. The candidate declares a bounded state form but has no queue cap/eviction rule.

## Interpretation

These are deterministic implementation/design failures in a candidate, not evidence against the research Goal and not a scientific effect result. The candidate cannot be promoted until consolidation semantics, residual state and correction-queue capacity are repaired and requalified.

Raw config and summary are stored in [`experiments/logs/n03_raresafe_anchor_static_audit_20260929_v1/`](../../experiments/logs/n03_raresafe_anchor_static_audit_20260929_v1/). The findings are added to the method-lock candidate as open repair gates; active method v1.0 is unchanged.
