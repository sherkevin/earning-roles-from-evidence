# Frozen real PIPE3 v6 source-bound replay — 2026-09-30

## Result

The source-bound adapter was replayed against the frozen `n03_pipe3_real_smoke_20260929_v6` ledger and its real actor/scorer artifact lineage. The replay used no model call and did not modify the historical v6 result. It reconstructed the selection sidecar, linked the real delivery, recipient judgment, and consumer action records, and passed the v4 schedule and responsibility-lineage checks.

The v6 episode had a recipient-owned `processor.py` repair and therefore no
eligible producer label. The adapter emitted a public `UNKNOWN` row with the
fixed reason `recipient-owned-change`, preserved the selected `peer-b@v1`,
and sealed a later assignment offer. No label crossed the policy boundary.

## Evidence

- Qualification: `scripts/peerrolebench_v6_source_bound_replay_qualification.py`
- Source artifact: `experiments/logs/n03_pipe3_real_smoke_20260929_v6/`
- Final artifact: `experiments/logs/n03_v6_source_bound_replay_qualification_20260930_v1/`
- Source ledger replay status: `UNKNOWN` because the historical episode is
  intentionally pending responsibility evidence; this is preserved rather
  than upgraded.
- Qualification result: **QUALIFIED_OFFLINE**; targeted replay test: **1
  passed**; full `tests/test_peerrolebench_*.py` regression after this task:
  **296 passed**.
- New API calls: **0**; GPU jobs: **0**; policy updates: **0**.

## Boundary

This is a replay and adapter integration result, not a new scientific episode.
It shows that an actual prior ledger can enter the guarded source-bound path
and remain `UNKNOWN` when attribution is pending. It does not provide a live
next selection, profile generation, isolated policy-read trace, independent
history, baseline parity, or an efficacy result. The historical v6 model
calls remain evidence of the old integration smoke only; they are not relabeled
as a learning experiment.

## Goal reconciliation

The replay advances ER-G1's source-bound delivery chain and ER-G4's auditability. It does not satisfy ER-G1's complete live loop, ER-G2's online-learning requirement, ER-G3's frozen benchmark/baseline requirement, or ER-G4's new real-API scientific evidence requirement. The active Goal is unchanged and `scientific_readiness=false` remains correct.

## Next gate

Wire this adapter into the versioned live runner after each real actor/scorer/
action/outcome episode, then add an auditable isolated policy-read trace and
one later selection that actually consumes the offer. Until that path is
qualified, do not call a new episode an online-learning result.
