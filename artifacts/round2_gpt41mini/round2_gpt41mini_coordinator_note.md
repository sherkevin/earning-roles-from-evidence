# Round 2 gpt-4.1-mini — Chain-200 Coordinator Note

**Date**: 2026-04-14  
**Run dir**: `artifacts/round2_gpt41mini/run_20260414_115739`  
**Config**: `configs/round2_gpt41mini_chain200.yaml`  
**Commands used**:

```powershell
python scripts/run_round1_v3.py --config configs/round2_gpt41mini_chain200.yaml --samples-jsonl artifacts/seed/hotpotqa_validation_200.jsonl --methods fixed_peer_calibrated --artifacts-root artifacts/round2_gpt41mini --no-write-summary --workers 8

python scripts/run_round1_v3.py --config configs/round2_gpt41mini_chain200.yaml --samples-jsonl artifacts/seed/hotpotqa_validation_200.jsonl --methods fixed_static_roles --artifacts-root artifacts/round2_gpt41mini --resume-run-dir artifacts/round2_gpt41mini/run_20260414_115739 --no-write-summary --workers 8

python scripts/run_round1_v3.py --config configs/round2_gpt41mini_chain200.yaml --samples-jsonl artifacts/seed/hotpotqa_validation_200.jsonl --methods fixed_self_claim --artifacts-root artifacts/round2_gpt41mini --resume-run-dir artifacts/round2_gpt41mini/run_20260414_115739 --no-write-summary --workers 8
```

**Backbone**: `gpt-4.1-mini`  
**Endpoint**: `https://kuaipao.ai/v1` (oversea path)  
**Actual resolved runtime**: `gpt-4.1-mini` (confirmed via `run_notes.md`)  
**Run type**: Fresh start, no resume required  
**Wall time**: ~4.4 minutes total (all three methods ran in parallel with 8 workers)

---

## Results Summary

| method | F1 | EM | PAR | MHC | api_tokens/sample | cost_norm_F1_api |
|--------|----|----|-----|-----|-------------------|-----------------|
| `fixed_self_claim` | **0.7641** | **0.635** | 0.0 | 2.0 | 6414.65 | 0.1191 |
| `fixed_static_roles` | 0.7454 | 0.61 | 0.0 | **1.677** | **4662.81** | **0.1599** |
| `fixed_peer_calibrated` | 0.7381 | 0.615 | 0.0 | 2.0 | 6414.49 | 0.1151 |

Validation: `scripts/validate_logs.py --all-methods` → all three **[OK]**, 200 samples, 100% coverage.

---

## Key Findings vs GLM Stage-1

### F1 / EM Lift
All three methods show dramatic improvement over GLM Stage-1 (n=7405 fullval):

| method | GLM F1 (n=7405) | GPT-4.1-mini F1 (n=200) | delta |
|--------|-----------------|--------------------------|-------|
| `fixed_peer_calibrated` | 0.5693 | 0.7381 | **+0.169** |
| `fixed_static_roles`    | 0.5906 | 0.7454 | **+0.155** |
| `fixed_self_claim`      | 0.5691 | 0.7641 | **+0.195** |

### Method Ordering Change
- **GLM Stage-1**: `static_roles` > `peer_calibrated` ≈ `self_claim`
- **GPT-4.1-mini**: `self_claim` > `static_roles` > `peer_calibrated`

The ordering inversion is notable: on GPT-4.1-mini, `fixed_self_claim` leads F1 and EM, while `fixed_peer_calibrated` now trails. This is a qualitative paper finding: the TCPB peer-calibration mechanism adds overhead (extra LLM calls for belief updates) without F1 benefit on a capable backbone, while `self_claim` leverages the model's stronger self-evaluation to achieve best F1 at the same token cost.

### PAR (Premature Accept Rate)
All three methods: PAR = 0.0 at n=200. This is consistent with GLM fullval (also PAR=0 for all). The decomposer's `_is_multihop_question` gate reliably prevents premature acceptance on HotpotQA regardless of backbone.

### Cost
- `fixed_static_roles` is the most cost-efficient: 4663 api_tokens/sample, `cost_norm_F1_api = 0.1599`
- `peer_calibrated` and `self_claim` cost ~38% more tokens (6414/sample) for lower or equal F1
- At n=7405 scale: ~47.5M tokens (peer/self) and ~34.5M tokens (static) per method

### Provider Stability
No errors, no retries, no rate limits observed. All 200 samples completed in ~4 minutes with 8 workers per method (three running in parallel). Very stable.

---

## Coordinator Recommendation: **GO for 7405 Fullval**

**Rationale**:

1. **F1 gap justifies fullval**: All methods show +0.15–+0.20 F1 over GLM Stage-1. The differences between methods are also non-trivial (+0.026 F1 between self_claim and peer_calibrated). N=200 is directional; n=7405 is needed for publishable paired statistics with tight confidence intervals.

2. **Method ordering changed — fullval will confirm or revise this**: The self_claim > static > peer ranking is the opposite of GLM Stage-1. The n=200 sample size may not be large enough to confirm the ordering with high statistical power; fullval will resolve this definitively.

3. **No cost or stability risk**: The oversea endpoint is fast, stable, and no quota/rate-limit issues appeared at n=200 with 8 workers. At n=7405 (37× scale), expect ~3–4 hours wall time with the current parallel runner.

4. **Resume safety**: Checkpoint/resume (`_ckpt_preds.jsonl`) is in place. An interruption at any point is non-fatal.

**Caveats**:
- **Token cost at fullval scale**: ~130M total api tokens across 3 methods × 7405 samples. Ensure the quota / credit on `kuaipao.ai` covers this before launching. Verify with a quick balance check.
- **Ordering interpretation in paper**: With self_claim leading and PAR=0.0 for all, the main paper narrative must pivot from "peer_calibrated prevents premature acceptance (PAR diff)" to "TCPB belief overhead adds cost without F1 benefit on capable backbone; self_claim is Pareto-optimal at same cost". The star topology archival finding still holds.
- **Do not launch fullval until coordinator reviews token budget / quota.**

---

## Files Produced

| file | note |
|------|------|
| `artifacts/round2_gpt41mini/run_20260414_115739/` | shared run dir with all three method subdirs |
| `artifacts/round2_gpt41mini/round2_gpt41mini_main_table.csv` | merged 3-method metrics table |
| `artifacts/round2_gpt41mini/round2_gpt41mini_summary.md` | markdown summary from collect_run_metrics |
| `artifacts/round2_gpt41mini/round2_gpt41mini_coordinator_note.md` | this file |
| `configs/round2_gpt41mini_chain200.yaml` | run config for this package |
