# Fullval Corruption Triage Note

**Date**: 2026-04-14  
**Run dir**: `artifacts/round2_gpt41mini_fullval/run_20260414_135408`  
**Agent**: Agent 2, Session 8

---

## Triage Summary

| method | status | evidence | usable as mainline? |
|--------|--------|----------|---------------------|
| `fixed_peer_calibrated` | **VALID** | F1=0.7703, EM=0.6117, 7405 samples, zero errors | ✅ Yes |
| `fixed_static_roles` | **CORRUPTED** | F1=0.0604, 6843/21030 outputs contain gpt-5.1 errors | ❌ No |
| `fixed_self_claim` | **CORRUPTED** | 574/574 ckpt predictions F1≈0, all with gpt-5.1 errors, no metrics.json | ❌ No |

---

## Evidence

### `fixed_peer_calibrated` — VALID
- `metrics.json`: `answer_f1=0.7703`, `answer_em=0.6117`, `sample_count=7405`, `mean_handoff_count=2`
- `run_notes.md`: `model_resolved_runtime: gpt-4.1-mini`
- Zero gpt-5.1 errors in `raw_model_outputs.jsonl`
- `validate_logs.py` would return `[OK]` (all files present, 7405 samples)

### `fixed_static_roles` — CORRUPTED
- `metrics.json` exists but reports F1=0.0604 (vs expected ~0.74 from chain-200 run)
- `raw_model_outputs.jsonl`: 21,030 total lines, **6,843 (32.5%) contain `gpt-5.1` error**:
  ```
  [ERROR: LLM API error 400: {"error":{"message":"The 'gpt-5.1' model is not supported when using Codex with a ChatGPT account.",...}}]
  ```
- `run_notes.md`: logged `model_resolved_runtime: gpt-4.1-mini` — drift occurred mid-run, after `configure_runtime()` correctly set up the runtime

### `fixed_self_claim` — CORRUPTED (no metrics.json)
- `_ckpt_preds.jsonl`: 574 entries, all F1≈0 (zero_f1=571/574)
- `raw_model_outputs.jsonl`: 2,296 lines, **574 with gpt-5.1 errors**
- No `metrics.json` — run was killed before completing all 7405 samples
- The method ran into the provider failure from its very first samples

---

## Root Cause

The `kuaipao.ai` oversea endpoint silently re-routed requests for `gpt-4.1-mini` to `gpt-5.1` mid-run, most likely after the `gpt-4.1-mini` quota was exhausted by `fixed_peer_calibrated` (~14,810 API calls). The account type does not support `gpt-5.1`, causing HTTP 400 errors. The old code's `except Exception` handlers swallowed these errors and wrote F1=0 predictions silently.

This is **not** a scientific result. It is a runtime integrity failure.

---

## Why These Runs Cannot Be Reported as Mainline Evidence

1. **Systematic API errors**: 32.5% of `static_roles` calls and nearly all `self_claim` calls failed with provider errors, not model responses.
2. **Unknown mix of valid/invalid**: For `static_roles`, 67.5% of calls succeeded — but we cannot know which prediction entries correspond to which calls without deep per-sample audit.
3. **Violated scientific comparability**: The three methods were not run under identical conditions. `peer_calibrated` used one quota tier; `static_roles` and `self_claim` hit the degraded tier.
4. **Fix now in place**: `ModelDriftError(BaseException)` in `llm_client.py` will abort any future run on first drift detection instead of silently continuing.

---

## What Is Preserved

All logs and checkpoints in `run_20260414_135408` are preserved as forensic evidence:
- `fixed_peer_calibrated/metrics.json` — valid result, should be used in the final table
- `fixed_static_roles/` — kept for forensic reference, NOT for scientific reporting
- `fixed_self_claim/` — kept for forensic reference, NOT for scientific reporting

**Do not delete this run dir.**

---

## Rerun Plan

Once the `kuaipao.ai` oversea endpoint recovers (or a new API key is supplied):

```powershell
python scripts/run_round1_v3.py --config configs/round2_gpt41mini_chain200.yaml --samples-jsonl artifacts/seed/hotpotqa_validation_full.jsonl --methods fixed_static_roles,fixed_self_claim --artifacts-root artifacts/round2_gpt41mini_fullval_rerun --no-write-summary --workers 8
```

Use a fresh run dir under `artifacts/round2_gpt41mini_fullval_rerun/`.  
**Do NOT resume the corrupted methods in-place from `run_20260414_135408`.**

Current provider status (2026-04-14 session end): `kuaipao.ai` is routing ALL GPT-4.x models to `gpt-5.1` — endpoint non-functional for rerun.

---

## Final Three-Method Table (pending rerun)

The complete `gpt-4.1-mini` fullval evidence package will consist of:

| method | source | status |
|--------|--------|--------|
| `fixed_peer_calibrated` | `run_20260414_135408` | **available** (F1=0.7703) |
| `fixed_static_roles` | `round2_gpt41mini_fullval_rerun/` | **pending provider recovery** |
| `fixed_self_claim` | `round2_gpt41mini_fullval_rerun/` | **pending provider recovery** |
