# Model Backbone Control Check

**Date**: 2026-04-14  
**Engineer**: Agent 1, Session 3–5

---

## Problem Fixed

Prior to this patch, `configs/*.yaml`'s `main_model` field was only a logging label.
All LLM calls in `workspace/idea04_core/methods.py` invoked `call_llm()` without a
`model` argument, silently resolving to the hardcoded `DEFAULT_MODEL = "glm-4-flash"`.
No mechanism existed to switch the backend to `gpt-4.1-mini` or any other provider.

---

## Patch Summary

### `workspace/idea04_core/llm_client.py`
- Added `_RUNTIME` dict (model, base_url, api_key, use_system_proxy).
- Added `configure_runtime(model, ...)` — auto-detects provider from `configs/llm.json`:
  - model in `oversea_model` list → `oversea_url` + `oversea_key` (OpenAI-compat path)
  - otherwise → `ZHIPU_BASE_URL` + `ZHIPU_API_KEY` (GLM path)
- Added `resolved_model()` — returns the model that will be used by the next `call_llm()`.
- `call_llm()` now defaults `model` to `_RUNTIME["model"]`; explicit overrides still work.
- Merged `_zhipu_urlopen` into `_urlopen` — reads `use_system_proxy` from `_RUNTIME`.

### `workspace/idea04_core/runner.py`
- Imports `configure_runtime`, `resolved_model`.
- At the start of `RoundRunner.run()`: calls `configure_runtime(run_config["main_model"])`.
- `_write_run_files()` now writes both `model_config_label` and `model_resolved_runtime`
  to `run_notes.md`, allowing post-hoc audit of what was actually called.

---

## Backward Compatibility

- If `main_model` is not set in config, defaults to `"glm-4-flash"` → identical to pre-patch.
- `ZHIPU_API_KEY` env var continues to work; `configs/llm.json` `KEY` field is secondary fallback.
- Existing GLM result directories are not affected.

---

## Config Contract for New Runs

### GLM path (current Stage-1 results):
```yaml
main_model: glm-4-flash
```
Resolved runtime: `open.bigmodel.cn` · key: `ZHIPU_API_KEY` env var.

### gpt-4.1-mini path (new primary backbone):
```yaml
main_model: gpt-4.1-mini
```
Resolved runtime: `https://kuaipao.ai/v1/chat/completions` · key: `oversea_key` from `configs/llm.json`.  
No environment variable change needed; the key is read from `llm.json` automatically.

---

## Smoke Test Results

| run_dir | model_config_label | model_resolved_runtime | n | F1 | EM | validation |
|---|---|---|---|---|---|---|
| run_20260414_062110 | glm-4-flash | glm-4-flash | 10 | 0.6333 | 0.60 | [OK] |
| run_20260414_062253 | gpt-4.1-mini | gpt-4.1-mini | 10 | **0.9333** | **0.80** | [OK] |

Both runs: `fixed_peer_calibrated`, chain topology, `artifacts/seed/hotpotqa_validation_200.jsonl` (first 10 samples).

---

## Assessment

**GREEN LIGHT**: `gpt-4.1-mini` is fully runnable in the experiment harness.

- The runtime truly switches provider — `model_resolved_runtime: gpt-4.1-mini` confirmed in `run_notes.md`.
- F1 improves from 0.63 → 0.93 on the 10-sample smoke (n=10, treat as directional, not final).
- MHC=2 (vs 1 for GLM on the same samples), indicating `gpt-4.1-mini` triggers more forwarding hops — plausibly because the model is better at recognising multi-hop questions and delegating.
- Both smoke logs pass `validate_logs.py` at 100% coverage.

### Remaining caveat before large runs
- The 10-sample comparison is indicative only. Full 200-sample rerun on `gpt-4.1-mini` is needed to measure stable F1, PAR, and MHC for the paper.
- `api_total_tokens_per_sample` is higher for `gpt-4.1-mini` (6944 vs 3336) because it generates richer intermediate reasoning. Monitor cost for 200-sample runs.

---

## Archive Notice: Stage-1 GLM Results

All prior runs under `artifacts/round1/` and `artifacts/round1_star/` used `glm-4-flash`
as the true runtime backbone. These are **archived as Stage-1 guidance artifacts** — valid for
illustrating mechanism differences (PAR, MHC patterns) but **not the final paper evidence set**.

Future primary runs must specify `main_model: gpt-4.1-mini` in their config.
The `model_resolved_runtime` field in each run's `run_notes.md` is the authoritative audit trail.

---

## Recommended Next Step (for Coordinator + Agent 2)

To relaunch main experiment on `gpt-4.1-mini`:
```powershell
# Edit configs/round1_hotpotqa.yaml: set main_model: gpt-4.1-mini
# Then:
python scripts/run_round1_v3.py `
  --config configs/round1_hotpotqa.yaml `
  --samples-jsonl artifacts/seed/hotpotqa_validation_200.jsonl `
  --methods fixed_peer_calibrated,fixed_static_roles,fixed_self_claim `
  --artifacts-root artifacts/round2_gpt41mini
```
Use `--resume-run-dir` if the run is interrupted — checkpoint/resume is enabled.
