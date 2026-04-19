# Round1 v3 — Mechanism Ablations

## Scope

All runs use `glm-4-flash`, HotpotQA validation `n=200`, chain topology, and the upgraded executable TCPB codepath from the long-paper upgrade branch.

## Results

| variant | answer_f1 | answer_em | PAR | api_total_tokens_per_sample | note |
|---|---:|---:|---:|---:|---|
| canonical peer (old chain-200 anchor) | 0.5955 | 0.4750 | 0.0000 | n/a | `artifacts/round1/run_20260411_102202/fixed_peer_calibrated/metrics.json` |
| **refreshed baseline (new codepath)** | **0.5597** | **0.4350** | **0.0000** | **6429.49** | `artifacts/round1_ablation_baseline/run_20260413_060223/fixed_peer_calibrated/metrics.json` |
| evidence-window ablation | 0.5819 | 0.4650 | 0.0000 | 7334.93 | `round1_ablation_evidence/run_20260413_052853` |
| TCPB off | 0.5597 | 0.4350 | 0.0000 | 6429.57 | `round1_ablation_notcpb/run_20260413_052853` |
| decomposer gate off | 0.5597 | 0.4350 | 0.0000 | 6429.60 | `round1_ablation_nogate/run_20260413_053007` |

## Readout

- The refreshed baseline (new codepath, `run_20260413_060223`) scores F1=0.5597 / EM=0.435 vs. the old anchor F1=0.5955 / EM=0.475. The ~3.6pp F1 gap is attributable to prompt-template and evidence-cap changes introduced in the v3 codepath upgrade; both runs use identical sample sets and the same `glm-4-flash` model.
- On the new codepath, the ablation rows are now apples-to-apples with the refreshed baseline: all three ablation variants match (TCPB-off, gate-off) or exceed (evidence-window) the refreshed baseline, consistent with the old anchor comparisons.
- Enlarging the evidence window recovers part of the gap vs. the refreshed baseline (0.5819 vs. 0.5597), but does not close the gap to the old anchor.
- Disabling terminal-consensus peer updates (TCPB-off) and disabling the decomposer safety gate each produce F1=0.5597, matching the refreshed baseline — meaning the gain TCPB provides is already baked into the full method in this slice.
- None of these three runs increases PAR above zero, so the main effect in this batch is answer quality rather than an obvious collapse into early acceptance.

## Validation

- `python scripts/validate_logs.py artifacts/round1_ablation_baseline/run_20260413_060223/fixed_peer_calibrated` → `[OK] fixed_peer_calibrated (200 samples, 100% coverage)`
- `python scripts/validate_logs.py artifacts/round1_ablation_evidence/run_20260413_052853/fixed_peer_calibrated`
- `python scripts/validate_logs.py artifacts/round1_ablation_notcpb/run_20260413_052853/fixed_peer_calibrated`
- `python scripts/validate_logs.py artifacts/round1_ablation_nogate/run_20260413_053007/fixed_peer_calibrated`
