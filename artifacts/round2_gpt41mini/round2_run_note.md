# Round 2 — gpt-4.1-mini Chain-200 Primary Evidence Package

**Date**: 2026-04-14  
**Engineer**: Agent 1, Session 6  
**Run dir**: `artifacts/round2_gpt41mini/run_20260414_115614`

---

## Intended Backbone
`gpt-4.1-mini` (OpenAI-compatible via `https://kuaipao.ai/v1`)

## Actual Resolved Runtime Model
`gpt-4.1-mini` — confirmed in both `run_notes.md` files:
- `fixed_peer_calibrated/run_notes.md`: `model_resolved_runtime: gpt-4.1-mini`
- `fixed_static_roles/run_notes.md`: `model_resolved_runtime: gpt-4.1-mini`

---

## Exact Commands

```powershell
# Step 1 — fixed_peer_calibrated (fresh run, new run dir)
python scripts/run_round1_v3.py `
  --config configs/round1_hotpotqa.yaml `
  --samples-jsonl artifacts/seed/hotpotqa_validation_200.jsonl `
  --methods fixed_peer_calibrated `
  --artifacts-root artifacts/round2_gpt41mini `
  --no-write-summary --workers 8

# Step 2 — fixed_static_roles (resumed into same run dir)
python scripts/run_round1_v3.py `
  --config configs/round1_hotpotqa.yaml `
  --samples-jsonl artifacts/seed/hotpotqa_validation_200.jsonl `
  --methods fixed_static_roles `
  --artifacts-root artifacts/round2_gpt41mini `
  --resume-run-dir artifacts/round2_gpt41mini/run_20260414_115614 `
  --no-write-summary --workers 8
```

Config: `configs/round1_hotpotqa.yaml` (`main_model: gpt-4.1-mini`, n=200, chain, max_handoff=4).

---

## Resume Status
- `fixed_peer_calibrated`: fresh start, no prior checkpoint. Completed in ~4 min.
- `fixed_static_roles`: added to existing run dir via `--resume-run-dir`. No interruption; completed in ~3.5 min.
- Neither run required mid-run resume.

---

## Validation
```
[OK]  fixed_peer_calibrated  (200 samples, 100% coverage)
[OK]  fixed_static_roles     (200 samples, 100% coverage)
```

---

## Metrics

| method | F1 | EM | PAR | MHC | api_tokens/sample | cost_norm_F1 |
|---|---|---|---|---|---|---|
| fixed_peer_calibrated | **0.7462** | 0.625 | 0.0 | 2.00 | 6414 | 0.888 |
| fixed_static_roles    | 0.7452 | 0.620 | 0.0 | 1.677 | 4662 | 1.169 |

*(PAR = premature_accept_rate; MHC = mean_handoff_count; cost_norm_F1 = F1 / (heuristic_token_cost/1000))*

---

## Comparison: Stage-1 GLM vs Stage-2 gpt-4.1-mini

| backbone | method | F1 | EM | PAR | MHC |
|---|---|---|---|---|---|
| glm-4-flash (Stage-1) | fixed_peer_calibrated | 0.5955 | 0.475 | 0.0 | 1.0 |
| glm-4-flash (Stage-1) | fixed_static_roles    | 0.5802 | 0.455 | 0.0 | 1.677 |
| **gpt-4.1-mini (Stage-2)** | fixed_peer_calibrated | **0.7462** | **0.625** | **0.0** | **2.00** |
| **gpt-4.1-mini (Stage-2)** | fixed_static_roles    | **0.7452** | **0.620** | **0.0** | **1.677** |

**Key observations**:
1. F1 improves by +15pp (peer) / +16.5pp (static) with the stronger backbone.
2. Peer maintains a slight F1 edge over static (0.7462 vs 0.7452, Δ=0.001). This is narrow — bootstrap significance testing needed.
3. Peer MHC=2.00 (vs static 1.677) indicates the gpt-4.1-mini backbone actually uses the multi-hop forwarding path more aggressively — the model is better at recognizing multi-hop questions and triggering delegation.
4. Both methods have PAR=0.0 — the decomposer force-forward gate is effective on this backbone.
5. Token cost: peer uses more tokens than static (6414 vs 4662 api/sample) due to longer chains.

---

## Anomalies / Caveats
- `--workers 8` used for both runs. For `fixed_peer_calibrated`, post-sample competence updates are thread-safe (lock-protected) but not ordered — the competence trajectory may differ slightly from a sequential run.
- `first_accept_success_rate=0` for both: no samples completed in 1 hop (decomposer accepted immediately). This is expected given the multi-hop force-forward gate and static role routing.
- The F1 margin (peer vs static = 0.001) is very small at n=200 on gpt-4.1-mini. The PAR/MHC differentiation is the more reliable signal for TCPB mechanism claims. Collect bootstrap statistics before paper-reporting the F1 gap.

---

## Status: Part of New Mainline Evidence Package

This run (`run_20260414_115614`) is the Stage-2 primary evidence for:
- `fixed_peer_calibrated` on `gpt-4.1-mini`
- `fixed_static_roles` on `gpt-4.1-mini`

**Pending for complete primary table**: `fixed_self_claim` (not yet run, assigned by coordinator).
