# R41h Emergence Pivot — Smoke Results (Placeholder)

**Status**: placeholder — filled automatically by `workspace/tmp/r42_emergence_pipeline.sh` after vLLM server launches on GPU 1 and the Phi-4-mini × {single_agent, edo_stage2_chain} × n=5 HotpotQA smoke completes.

## 1. Hypothesis (falsifiable, per `docs/paper/small_model_emergence_plan.md §4`)

Define, for a given backbone B and benchmark D:

- `F1_single(B)`  — `single_agent` method on n samples from D
- `F1_multi(B)`   — `edo_stage2_chain` (TCPB Stage-2 4-agent pipeline) on same samples
- `Δ(B) = F1_multi(B) − F1_single(B)`

**Emergence hypothesis**: `Δ(Phi-4-mini) > Δ(gpt-4.1-mini) ≥ 0`, i.e., organising 4 weaker agents via TCPB yields a larger gain than organising 4 stronger agents. Equivalently, capabilities "emerge" from organisational structure in the small-model regime.

**Null / falsification**: `Δ(Phi-4-mini) ≤ Δ(gpt-4.1-mini)` or `Δ(Phi-4-mini) ≤ 0`. If either holds, no emergence claim; we fall back to the pre-existing Pareto-token-efficiency framing (`F1_multi_gpt41mini = 0.688` vs `F1_single_gpt41mini` at half the tokens).

## 2. Experimental setup (to be logged by the pipeline)

| Field | Value |
|---|---|
| Server | viplabserver12 (10.103.16.12) |
| GPU for vLLM | 1 × RTX 3090 (24 GB), index 1, port 8001 |
| Backbone (primary) | `microsoft/Phi-4-mini-instruct` (3.8B, MIT) |
| Backbone (control) | `HuggingFaceTB/SmolLM3-3B` (3B, Apache 2.0) — R42 deferred run |
| vLLM version | TBD |
| `configs/llm.json` block | `local_vllm` (R42 E-6) |
| Method for null | `single_agent` (methods.py:285,450 pre-existing) |
| Method for emergence | `edo_stage2_chain` (E-005 Stage-2) |
| Benchmark | HotpotQA fullval subset, first 5 samples (smoke) → 50 (scale) |
| Seed | 42 |
| Temperature | 0.0 |
| Max tokens | inherits yaml config |

## 3. Results (populated post-smoke)

### 3.1 Phi-4-mini × single_agent

| Metric | Value |
|---|---:|
| n | TBD |
| answer_f1 | TBD |
| answer_em | TBD |
| api_total_tokens_per_sample | TBD |
| mean_handoff_count | 1 (by construction) |
| dead_end_rate | TBD |

### 3.2 Phi-4-mini × edo_stage2_chain

| Metric | Value |
|---|---:|
| n | TBD |
| answer_f1 | TBD |
| answer_em | TBD |
| api_total_tokens_per_sample | TBD |
| mean_handoff_count | TBD |
| premature_accept_rate | TBD |
| dead_end_rate | TBD |

### 3.3 Δ_Phi4 summary

| Metric | single_agent | edo_stage2_chain | Δ |
|---|---:|---:|---:|
| F1 | — | — | — |
| EM | — | — | — |
| tokens/sample | — | — | — |

### 3.4 Emergence verdict (to be stated)

- [ ] `Δ_Phi4_F1 > 0` — organisation adds measurable F1 to Phi-4-mini
- [ ] `Δ_Phi4_F1 > Δ_gpt41mini_F1` — **emergence held** vs baseline (requires U-EXEC-008 recharge to run `gpt-4.1-mini × single_agent` side)
- [ ] Pareto on tokens: token cost of organisation vs single-agent

## 4. Scaling plan (post-smoke)

If `n=5` smoke passes the sanity check (vLLM responding, JSONL valid, F1 > 0 for single_agent baseline), re-run at `n=50`:

```bash
# on server
bash workspace/tmp/r42_emergence_pipeline.sh   # currently hardcoded n=5
# edit --n 50 then re-run
```

SmolLM3-3B control run fires after Phi-4-mini n=50 lands.

## 5. Cross-references

- Plan document: [`docs/paper/small_model_emergence_plan.md`](./small_model_emergence_plan.md)
- R41h pivot proposal: `ENGINEER_TODO.md` `[r41h_emergence_pivot_proposal_20260421_0945]`
- R42b pivot execution: `ENGINEER_TODO.md` `[r42b_r41h_pivot_execution_20260421]` (forthcoming)
- vLLM env setup: `workspace/tmp/r42_vllm_env_setup_v2.sh`
- Parallel model download: `workspace/tmp/r42_download_models_parallel.sh`
- Auto-watcher: `workspace/tmp/r42_auto_watcher_emergence.sh`
- Emergence pipeline: `workspace/tmp/r42_emergence_pipeline.sh`
- llm.json routing: `configs/llm.json` `local_vllm` block
- Provider routing code: `workspace/idea04_core/llm_providers.py` `_is_local_vllm_routable` + `local_vllm_target`
- single_agent method: `workspace/idea04_core/methods.py:285,450`
