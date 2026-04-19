# Runtime Integrity Guard — Session 8 Note

**Date:** 2026-04-15  
**Scope:** forensic audit of model drift in `run_20260414_135408`, root cause identification, guardrail implementation, positive + negative smoke tests.

---

## 1. Corrupted Run Summary

| Method | Samples | F1=0 rate | mean_F1 | gpt-5.1 error rate in raw_outputs |
|--------|---------|-----------|---------|-----------------------------------|
| fixed_peer_calibrated | 7405 | ~7% | ~0.46 (clean) | ~0% |
| fixed_static_roles | 7405 | **92.7%** | 0.0604 | 32.5% of 21 030 entries |
| fixed_self_claim | 574 (partial) | **99.5%** | 0.0004 | 25.0% of 2 296 entries |

`fixed_self_claim` had errors from sample 2 (line 3 of `raw_model_outputs.jsonl`) — drifted from the very first LLM call. `run_notes.md` for `fixed_static_roles` recorded `model_resolved_runtime: gpt-4.1-mini` at end-of-run, proving the end-state `_runtime["model"]` was correct but LLM calls had already gone wrong mid-run.

---

## 2. Root Cause

**External provider remapping, not a code bug.**

The kuaipao.ai oversea proxy endpoint silently remaps `gpt-4.1-mini` requests to `gpt-5.1` on its backend. `gpt-5.1` is then rejected by the upstream Codex/ChatGPT route with:

```
400 Bad Request: "The 'gpt-5.1' model is not supported when using Codex with a ChatGPT account."
```

Evidence:
1. The error was reproduced immediately when running the positive smoke today — kuaipao.ai is still in this broken state.
2. `fixed_peer_calibrated` ran clean (~16h earlier on 2026-04-14) when the provider was healthy; the other two methods were corrupted when the provider had already degraded.
3. The `model_resolved_runtime: gpt-4.1-mini` in `run_notes.md` is correct — the `_runtime` module state was properly configured. The drift was **provider-side**, not a stale-default Python bug.

**Secondary fragility (also fixed):** The prior `call_llm()` used `model: str = DEFAULT_MODEL` as its parameter default and a `model == DEFAULT_MODEL` comparison to detect "use runtime model". This comparison is fragile: if `llm.json` is edited between runs, the frozen function default and the module-level constant can diverge, silently bypassing the runtime redirect. This was not the primary cause of this specific failure, but it is a latent bug that could trigger under development-time config churn.

---

## 3. Changes Made

### `workspace/idea04_core/llm_client.py`

1. **`call_llm()` signature**: `model: str = DEFAULT_MODEL` → `model: str | None = None`
   - When `model is None` (all `methods.py` call sites), the runtime model is used unconditionally — no fragile string comparison.

2. **Pre-send contract check** (new):
   ```python
   if enforce and intended_model_pre and model != intended_model_pre:
       raise ModelDriftError(...)
   ```
   Fires *before* the HTTP request is built. Catches: stale-default, env-var override, explicit caller override — anything that would send the wrong model.

3. **Existing post-response checks kept**:
   - Response `model` field mismatch → `ModelDriftError`
   - HTTP 400 error body mentioning a different model → `ModelDriftError`

`ModelDriftError` inherits from `BaseException` (not `Exception`) so it cannot be swallowed by the generic `except Exception` handlers in `methods.py`.

### `workspace/idea04_core/runner.py` (no changes needed)

Already contains:
- `ModelDriftError` import
- `executor.shutdown(wait=False, cancel_futures=True)` + re-raise on `ModelDriftError`
- `runtime_model: resolved_model()` in each `raw_model_outputs` entry for per-hop traceability

---

## 4. Smoke Test Results

### Positive smoke — GLM-5.1 (Zhipu, healthy provider)
- **Run:** `artifacts/runtime_integrity_guard/run_20260415_030738`
- **Config:** `configs/smoke_integrity_glm.yaml` · `main_model: GLM-5.1` · 5 samples · 1 worker
- **Result:** F1=0.4000, EM=0.4000, exit 0 — **no ModelDriftError**
- **Conclusion:** Guard passes cleanly when provider is healthy and model contract is respected.

### Guard trigger via live provider (gpt-4.1-mini oversea, broken state)
- **Config:** `configs/smoke_gpt41mini.yaml` · `main_model: gpt-4.1-mini` · 5 samples
- **Result:** `ModelDriftError` raised at sample 1, hop 2 — **run aborted immediately**
- **Error:** `Provider error references unexpected model 'gpt-5.1' (intended='gpt-4.1-mini')`
- **Conclusion:** Post-response HTTP-error body check fires correctly; kuaipao.ai is still broken.

### Negative smoke — pre-send contract violation (offline, no HTTP call)
- **Script:** `scripts/_negative_smoke_guard.py`
- **Test:** `configure_runtime("GLM-5.1")` → `call_llm(model="gpt-5.1", ...)`
- **Result:** `PASS - ModelDriftError raised before HTTP call`
- **Conclusion:** Pre-send guard fires for explicit wrong-model caller override without touching the network.

---

## 5. Affected Artifacts (Forensic, Preserved)

| Path | Status |
|------|--------|
| `artifacts/round2_gpt41mini_fullval/run_20260414_135408/fixed_peer_calibrated/` | **VALID** — use for analysis |
| `artifacts/round2_gpt41mini_fullval/run_20260414_135408/fixed_static_roles/` | **CORRUPTED** — 92.7% F1=0, do not cite |
| `artifacts/round2_gpt41mini_fullval/run_20260414_135408/fixed_self_claim/` | **CORRUPTED** — 99.5% F1=0, do not cite |

---

## 6. Provider Status

`gpt-4.1-mini` via kuaipao.ai oversea is **currently broken** (remaps to gpt-5.1 → 400 error). Any new mainline run on the oversea provider will fail immediately on the first `gpt-4.1-mini` call and raise `ModelDriftError`.

**Coordinator decision needed:**
- Option A: Wait for kuaipao.ai to restore `gpt-4.1-mini` routing (no ETA known).
- Option B: Switch mainline to NVIDIA Llama-3.3-70b (viable per Session 7 note, but limited to ~40 RPM).
- Option C: Switch mainline to Zhipu GLM-5.1 / GLM-4 (local key, no proxy dependency, slower but stable).

---

## 7. Guard Operational Notes

- `configure_runtime(model_name, enforce_model=True)` is the default for all mainline runs. Do not set `enforce_model=False` unless doing one-off debugging.
- `call_llm(model=None)` always uses the runtime model. Never pass an explicit `model=` string in experiment code.
- `ModelDriftError` inherits `BaseException` — it cannot be silently swallowed.
- After a `ModelDriftError`, the checkpoint (`_ckpt_preds.jsonl`) is valid up to the last completed sample; the run can be resumed after the provider is fixed.
