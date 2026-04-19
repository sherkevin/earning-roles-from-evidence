# NVIDIA Backup Supplier Validation Note

**Date**: 2026-04-14  
**Engineer**: Agent 1, Session 7  
**Run dir**: `artifacts/provider_fallback_check/run_20260414_135133`  
**Config**: `configs/smoke_nvidia_llama33_70b.yaml`

---

## Test Parameters

| field | value |
|---|---|
| Provider | NVIDIA NIM (`https://integrate.api.nvidia.com/v1`) |
| Model tested | `meta/llama-3.3-70b-instruct` |
| Backup candidate 2 (not tested) | `mistralai/mistral-large` |
| Method | `fixed_peer_calibrated` |
| Samples | 10 (first 10 of `hotpotqa_validation_200.jsonl`) |
| Topology | chain, max_handoff=4 |
| Workers | 1 (sequential, RPM-safe) |

---

## Endpoint / Routing

- Provider auto-detection: `meta/llama-3.3-70b-instruct` contains `/` + is in `nvidia.models` list → routed to NVIDIA NIM.
- Chat URL: `https://integrate.api.nvidia.com/v1/chat/completions`
- API key: `nvidia_key` from `configs/llm.json` (`nvapi-...`).
- Slash-ID routing: **confirmed working** — model name passed as-is to the API, no rewrite needed.
- RPM gate: `_SlidingWindowLimiter(max_events=40, window_seconds=60)` engaged automatically.
- `model_resolved_runtime: meta/llama-3.3-70b-instruct` confirmed in `run_notes.md`.

---

## Results (n=10, directional)

| metric | value |
|---|---|
| answer_f1 | 0.677 |
| answer_em | 0.500 |
| premature_accept_rate | 0.0 |
| mean_handoff_count | 2.0 |
| api_prompt_tokens/sample | 6639 |
| api_completion_tokens/sample | 85.1 |
| api_total_tokens/sample | 6724 |
| cost_norm_F1_api | 0.101 |

Validation: `[OK]`, 10 samples, 100% coverage.

---

## Comparison: Provider Benchmarks (n=10 smoke, same samples, fixed_peer_calibrated)

| run | model | provider | F1 | EM | api_tokens/sample | wall_time_10s |
|---|---|---|---|---|---|---|
| run_20260414_062110 | glm-4-flash | zhipu | 0.633 | 0.60 | 3336 | ~68s |
| run_20260414_062253 | gpt-4.1-mini | oversea | **0.933** | **0.80** | 6944 | ~71s |
| **run_20260414_135133** | **meta/llama-3.3-70b-instruct** | **nvidia** | **0.677** | **0.50** | **6724** | **~128s** |

*(n=10 is directional only; ranking may shift at n=200+)*

---

## Throughput / Latency Analysis

- **Wall time**: 128 seconds for 10 samples (sequential, 1 worker).
- **Effective LLM call rate**: ~40 calls / 10 samples / 128s ≈ 18-19 calls/minute (well under the 40 RPM cap, including network latency).
- **At n=200 sequential**: ~2,560s ≈ 43 minutes per method.
- **At n=200 with workers=4**: RPM-limited to 40/min; 200 samples × ~4 calls/sample = 800 calls; minimum 20 minutes per method. Actual wall time with latency: ~35-40 min.
- **At n=7405 sequential**: ~47,000s ≈ 13 hours per method. **Not viable for fullval under current RPM cap.**
- **At n=7405 with workers=4 (RPM-limited)**: ~770 minutes ≈ 13 hours. Same bottleneck.
- **RPM stability**: No throttle errors observed; the rate limiter ensured clean sequential calls.

---

## Resume Safety

- `_ckpt_preds.jsonl` written and flushed per sample.
- All JSONL logs written incrementally.
- A mid-run interruption can be resumed with `--resume-run-dir artifacts/provider_fallback_check/run_20260414_135133`.

---

## Coordinator Decision

### ✅ NVIDIA is a **VIABLE** emergency backup supplier

**Conditions for use**:
1. Only as a **separately labeled backup run**, never invisibly merged with the `gpt-4.1-mini` mainline evidence.
2. Use the run dir label `artifacts/provider_fallback_check/` or a clearly named backup dir (e.g. `artifacts/round2_nvidia_backup/`).
3. Record `model_resolved_runtime` and `provider` in every run note.

### Approved Fallback Model: `meta/llama-3.3-70b-instruct`

- Slash-ID routing works cleanly.
- Logs, validate, checkpoint/resume: all functional.
- `mistralai/mistral-large` was NOT tested (not needed; llama-3.3-70b succeeded on first try).

### Suitability Assessment

| use case | suitable? | notes |
|---|---|---|
| Emergency 10-sample smoke / reviewer check | ✅ YES | ~2 min, low cost |
| 200-sample method comparison | ✅ YES (slow) | ~35-40 min/method with rate limiter |
| 7405-sample fullval | ⚠️ NOT RECOMMENDED | ~13 hrs/method under 40 RPM cap |

**For fullval**, NVIDIA is usable only if: (a) RPM can be increased (contact NVIDIA support), or (b) the scientific question can be answered at n=200 and fullval is deferred. Otherwise, the `oversea` (kuaipao.ai / gpt-4.1-mini) path remains the correct primary for fullval.

### F1 Note

NVIDIA `llama-3.3-70b` F1=0.677 at n=10 is significantly below `gpt-4.1-mini` F1=0.933 on the same samples. If NVIDIA is used for a backup comparative run, the paper must clearly label it as a different backbone and not compare numerically against the `gpt-4.1-mini` mainline.

---

## Files

| file | note |
|---|---|
| `artifacts/provider_fallback_check/run_20260414_135133/fixed_peer_calibrated/` | NVIDIA smoke run dir |
| `configs/smoke_nvidia_llama33_70b.yaml` | NVIDIA smoke config |
| `artifacts/provider_fallback_check/nvidia_backup_supplier_note.md` | this file |
