# Task report — RARE-Anchor candidate repair

- **Date**：2026-09-29
- **Status**：`done / candidate-only qualification`
- **Scope**：zero API, zero GPU; active method v1.0 unchanged

## Repairs

1. An empty fast window now exposes the protected anchor directly. Consolidation no longer refreshes an all-zero raw state that erases the newly promoted preference.
2. Added `pending_size`, bounded correction queue, bounded superseded tombstones and an overflow counter. The candidate no longer claims bounded state while retaining unbounded pending structures.
3. Added regression tests for consolidation retention and queue/tombstone capacity.

## Verification

`python3 -m pytest -q tests/test_peerrolebench_raresafe_candidate.py` passed `6` tests. A separate zero-call qualification recorded `theta 0.5 → 0.5`, queue length `3` under `pending_size=3`, and overflow `7` after ten late events.

Raw pre-repair and post-repair configs/summaries remain separate under:

- `experiments/logs/n03_raresafe_anchor_static_audit_20260929_v1/`
- `experiments/logs/n03_raresafe_anchor_static_audit_20260929_v2/`

## Limits

This repairs deterministic candidate invariants only. It does not show quality, novelty, realtime service, drift recovery, forgetting, or superiority to contextual trust. The next gate remains the four-event offline replay with fixed same-information baselines.
