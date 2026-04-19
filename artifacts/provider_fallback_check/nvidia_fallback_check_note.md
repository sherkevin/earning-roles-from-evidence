# NVIDIA Backup Supplier Validation Note

**Date**: 2026-04-14  
**Run dir**: `artifacts/provider_fallback_check/run_20260414_135402`  
**Config**: `configs/smoke_nvidia_llama33_70b.yaml`  
**Model tested**: `meta/llama-3.3-70b-instruct`  
**Provider endpoint**: `https://integrate.api.nvidia.com/v1`  
**RPM limit (llm.json)**: 40 RPM  
**Workers used**: 4  
**Samples attempted**: 36 (process stopped after ~9 min; config had sample_size=10 but the CLI loaded all from jsonl — use `--sample-size 10` CLI flag in future)

## Connectivity Result

**API connectivity**: CONFIRMED working.  
Quick single-call smoke: `configure_runtime('meta/llama-3.3-70b-instruct')` → model resolves to NVIDIA backend, endpoint responds `ok` in ~8.5 seconds.  
Slash-id routing via `llm_providers._is_nvidia_routable()` works correctly.

## Smoke Run Quality Results (n=36 partial)

| metric | value |
|--------|-------|
| EM | 0.0000 |
| F1 | 0.0185 |
| mean_handoff_count | 4.0 (= max_handoff, all samples exhausted) |
| zero-F1 samples | 35/36 |

## Root Cause Analysis

### Issue 1: 429 Rate-Limit Errors (PRIMARY)
With 4 concurrent workers, each multi-hop sample makes ~4 API calls. At 4 workers × 4 hops = up to 16 concurrent/rapid calls, the NVIDIA API returns HTTP 429 `Too Many Requests` errors despite the 40 RPM sliding-window limiter. The `call_llm()` retry loop catches the 429 and retries (up to 3×), but burst conditions still produce failed calls.

Evidence from `raw_model_outputs.jsonl`:
```
hop=2 node=synthesizer: [ERROR: LLM API error 429: {"status":429,"title":"Too Many Requests"}]
```

When a hop fails, no answer is finalized, the chain exhausts max_handoff, and `answer_pred` is empty → F1=0.

### Issue 2: Mean hops = 4.0 (secondary / compounding)
Every sample hit `max_handoff=4`. This means:
- Either the model keeps forwarding and never decides to accept
- Or a 429 error early in the chain prevents the accept decision

The routing protocol text (`[forward to node_name]`) IS being produced correctly by the model — the model understands the instruction format. When calls succeed, the routing steps proceed correctly. The issue is purely the 429 disruptions preventing chain completion.

### Issue 3: High per-call latency (~8–9 seconds)
NVIDIA NIM `llama-3.3-70b-instruct` takes ~8.5 seconds per API call vs ~2 seconds for gpt-4.1-mini. At 4 hops per sample, each sample takes ~34 seconds minimum (even without 429). At sequential 1-worker throughput: ~34 seconds × 7405 = ~70 hours for fullval — completely infeasible.

## Verdict: **NOT USABLE as backup for fullval**

| criterion | result |
|-----------|--------|
| API connectivity | ✅ Confirmed |
| slash-id routing | ✅ Works |
| RPM compliance | ❌ 429 errors with 4 workers |
| multi-hop chain completion | ❌ 0% at n=36 |
| throughput for fullval (7405) | ❌ ~70 hours @ 1 worker |
| answer quality | ❌ F1=0.019 (possibly model quality + 429 compounding) |

## Recommendation

- **Do NOT use NVIDIA as fallback for 7405 fullval** under any circumstances.
- NVIDIA is usable only for: single-call unit tests, connectivity checks, and potentially single-worker reviewer-loop runs with ≤50 samples where throughput is not a concern.
- If `oversea`/gpt-4.1-mini quota fails during fullval, **stop the run** and preserve the partial checkpoint. Do not switch to NVIDIA mid-run.
- The `mistralai/mistral-large` alternative (second backup candidate) was not tested because the primary issue (RPM/throughput) is provider-level and would affect Mistral equally.

## Alternative Backup Paths (for coordinator consideration)

1. **Refill oversea quota** — simplest option; quota is the only blocker.
2. **Use `deepseek-ai/deepseek-v3.1` via NVIDIA** — potentially faster if it supports 512-token chains, but still faces the same 40 RPM and 429 issues.
3. **Direct Zhipu GLM-5.1** — has its own API limits but no latency issues; was viable for Stage-1 guidance runs.

## Preserved Artifacts

- `artifacts/provider_fallback_check/run_20260414_135402/fixed_peer_calibrated/_ckpt_preds.jsonl` — 36 partial predictions
- `artifacts/provider_fallback_check/run_20260414_135402/fixed_peer_calibrated/raw_model_outputs.jsonl` — 144 raw API outputs with error records
- `artifacts/provider_fallback_check/run_20260414_135402/fixed_peer_calibrated/routing_traces.jsonl` — routing decisions per hop
- `configs/smoke_nvidia_llama33_70b.yaml` — smoke config
