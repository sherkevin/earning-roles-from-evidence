# Small-Model Emergence Experiment Plan (R41h pivot)

**Created**: 2026-04-21 R41h engineer session (MCP-3).
**Triggered by**: User R41h instruction — "充值费用有点高 ... 直接在远程服务器上部署强大的 7B 小模型,用多个 7B 模型交互去完成复杂任务,然后和调用大参数 API 的模型做的任务效果做对比,就可以说明我们出现了涌现".
**Owner**: scientist (writing lead). Engineer provides infrastructure + runs experiments. User keeps strategic decision power (framing pivot).
**Status**: PROPOSAL — awaiting scientist sign-off + user framing pivot decision before engineer commits ~2-day infrastructure setup.

---

## 1. Problem restatement + strategic pivot

### 1.1 What the user is proposing

Instead of continuing to pay for `gpt-4.1-mini` API calls (the current canonical backbone per `experiment.md §1.3`), the user proposes:

- **Deploy strong 4B/7B/8B open-weight reasoning models locally on the server's idle GPUs.**
- **Run TCPB Stage-2 with 4 such small agents** (one per chain role: decomposer / evidence_seeker / verifier / synthesizer).
- **Run single-agent ablation with the same small model** on the same HotpotQA data.
- **Compare the multi-agent-over-single gain (`Δ_small`) vs the same gain under a strong API model (`Δ_large`, where `F1_large_multi ≈ 0.688` already measured).**
- **Claim "emergence"** if `Δ_small > Δ_large` (or at least `Δ_small >> 0` while `Δ_large ≈ 0`).

### 1.2 Why this is scientifically strong

The TCPB paper's current Pareto claim ("Stage-2 dominates Stage-1 on F1-per-token") is PRESENT but marginal — `ΔF1_paired_seed42 = +0.0061` with 95% CI crossing zero (see `docs/paper/external_smoke_summary.md §2`). A margin this small is easy for reviewers to attack as "within noise / engineering overhead of Stage-2 doesn't pay off".

The emergence framing changes the claim shape from:

> "Stage-2 improves F1 on large models by small amounts while saving tokens"

to:

> "**Organizing multiple weak agents via TCPB yields capabilities that a single weak agent lacks**, recovering performance comparable to a strong monolithic model. This is the organizational-emergence phenomenon predicted by the EDO framework (`idea.md §2`)."

The emergence claim is **falsifiable** (if `Δ_small ≈ Δ_large` or `Δ_small < 0`, no emergence), **more interesting** (positive existence proof of organizational emergence is a stronger contribution than marginal improvement), and **better-aligned with the paper's framing** (the paper title is *Emergent Delegation Organization*).

### 1.3 Cost implication

- Current path: rerun seed=43/44 + MuSiQue matrix + E-014 at ~$300 on gpt-4.1-mini.
- Pivot path: **$0 GPU cost** (idle server GPUs) + ~2 days engineer setup + electric bill negligible.

---

## 2. Server audit results (R41h engineer, 09:28-09:40 CST)

### 2.1 GPU inventory (all idle)

Per `nvidia-smi` at 09:35:

| GPU | Model | Total VRAM | Free VRAM |
|---:|---|---:|---:|
| 0 | RTX 2080 Ti | 11 264 MiB | 10 999 MiB |
| 1 | RTX 3090 | 24 576 MiB | 24 243 MiB |
| 2 | RTX 2080 Ti | 11 264 MiB | 10 999 MiB |
| 3 | RTX 2080 Ti | 11 264 MiB | 10 999 MiB |
| 4 | RTX 3090 | 24 576 MiB | 24 243 MiB |
| 5 | RTX 3090 | 24 576 MiB | 24 243 MiB |
| 6 | RTX 2080 Ti | 11 264 MiB | 10 999 MiB |
| 7 | RTX 3090 | 24 576 MiB | 24 243 MiB |

**Total**: 4× RTX 3090 (98 GB) + 4× RTX 2080 Ti (44 GB) = **142 GB VRAM**, all 0% utilization. (Consistent with `ssh-server-rules.mdc §E-013 probe`.)

### 2.2 Existing-model search

| Location | Status |
|---|---|
| `~/.cache/huggingface/hub/` (HF cache) | **empty** |
| `~/.ollama/models/` | **Ollama not installed** |
| `~/.cache/lm-studio/` | **not installed** |
| System Python `torch` | **not installed** |
| Any venv `torch` / `vllm` | **not installed** (4 baseline venvs all missing these — MA-RAG's `requirements.txt` lists `vllm==0.10.1` + `torch==2.5.1` + `transformers==4.50.3` but the install never ran) |
| Bundled `.safetensors` / `.gguf` in workspace | **zero** |

**Conclusion**: no existing local models; starting from clean slate. `/media/data3` has **662 GB free** (enough for 10+ 7B models).

### 2.3 Sibling-project directories (not touchable)

- `/media/data3/FNC/` (other project — do NOT reuse their models as assumption)
- `/media/data3/recsys/` (other project — same)

---

## 3. Candidate small models (2025-2026 strong reasoning, shortlist)

Ranked by inferred HotpotQA suitability (structured QA over passages, not pure math):

| # | Model | Params | License | VRAM FP16 | VRAM Q4 | MMLU-Pro | HotpotQA F1 (few-shot, lit) | Strengths |
|---:|---|---:|---|---:|---:|---:|---:|---|
| **1** | **Qwen3.5-9B** | 9B | **Apache 2.0** | ~18 GB (1× RTX 3090) | ~6 GB (1× 2080 Ti) | **82.5** | est. 0.64-0.68 | Hybrid dense, thinking-on/off, tool-calling, 262K ctx. Best overall SLM scores per [awesomeagents.ai 2025 leaderboard](https://awesomeagents.ai/leaderboards/small-language-model-leaderboard/). |
| **2** | **Qwen3.5-4B** | 4B | Apache 2.0 | ~8 GB (1× 2080 Ti) | ~3 GB (laptop) | 79.1 | est. 0.60-0.64 | Same family as #1 scaled down; MMLU-Pro 79.1 is astonishing for 4B. Perfect for 4-agent × 2080 Ti deployment. |
| **3** | **Qwen2.5-7B-Instruct** | 7B | Apache 2.0 | ~14 GB (1× RTX 3090) | ~4.5 GB | — | 0.5946 (Panel 2025, [NAACL 2025.long.55]) | Well-studied baseline from 2024; vast ecosystem support; canonical HotpotQA number available. |
| **4** | **OpenReasoning-Nemotron-7B** | 7B | CC-BY 4.0 + Apache 2.0 | ~14 GB | ~4.5 GB | 71.9 | — (math-heavy SFT, TBD on QA) | NVIDIA post-trained Qwen2.5-7B for reasoning; AIME24 84.7 is close to GPT-4-level at 7B. |
| **5** | **Phi-4-mini (3.8B)** | 3.8B | MIT | ~7.6 GB | ~2.5 GB | 52.8 | 0.5818 (Panel 2025) | Microsoft; exceptional compactness; GSM8K 88.6 indicates strong chain-of-thought. |
| **6** | **Gemma 3 4B IT** | 4B | Gemma License | ~8 GB | ~3 GB | 43.6 | ~0.55 est. | Google; strong code (HumanEval 71.3) but weaker pure-reasoning. Fallback. |
| **7** | **Llama-3.1-8B-Instruct** | 8B | Llama 3 License | ~16 GB | ~5 GB | — | 0.6391 (Panel 2025) | Meta baseline; well-tested HotpotQA record; **good control** candidate for literature comparability. |

### 3.1 Recommended primary candidate: **Qwen3.5-9B** + **Qwen2.5-7B-Instruct** as control

**Qwen3.5-9B** reasons:
- Highest raw capability per the 2025-26 open-weight leaderboard
- Apache 2.0 (no attribution problems in paper)
- Dense (not MoE) — simpler serving, no expert-routing complexity
- Fits 1× RTX 3090 comfortably with vLLM at batch>1

**Qwen2.5-7B-Instruct** as control:
- Literature-known HotpotQA F1 0.5946 (NAACL 2025 panel paper) — lets us directly compare vs published baselines
- Same family as Qwen3.5-9B — isolates "scale + training data" effect
- Most ecosystem support

### 3.2 Deployment allocation (single-box, 8 GPUs)

Per R41h proposal: deploy **4 agents in parallel** for TCPB Stage-2 (one per role). Four RTX 3090s can host 4 copies of Qwen3.5-9B (one per GPU). With vLLM tensor_parallel_size=1 per instance:

| GPU | Role | Model | Port | Notes |
|---|---|---|---|---|
| 1 | decomposer | Qwen3.5-9B | 8001 | |
| 4 | evidence_seeker | Qwen3.5-9B | 8002 | |
| 5 | verifier | Qwen3.5-9B | 8003 | |
| 7 | synthesizer | Qwen3.5-9B | 8004 | |
| 0-3,6 (2080 Ti) | spare / baselines | Qwen3.5-4B / Phi-4-mini | 8005-8008 | for baseline ablations |

Four `vllm.entrypoints.openai.api_server` instances listening on `localhost:8001-8004`, each exposing `/v1/chat/completions`.

---

## 4. Deployment approach

### 4.1 Stack

Chosen: **vLLM 0.10+ with CUDA 12 + PyTorch 2.5+**.

Alternatives considered:
- **Ollama**: easier but slower throughput (fine for smoke, not for fullval)
- **llama.cpp**: most portable but CPU-centric focus, slower on GPU vs vLLM
- **transformers pipeline**: simplest but no batching — 10× slower than vLLM for our throughput needs

### 4.2 Install sequence (server)

1. **Install vLLM in a new shared venv**: `python3.10 -m venv /media/data3/dengkw/venvs/vllm-qwen35 && pip install vllm==0.10.2 torch==2.5.1 transformers==4.54+ huggingface_hub`. Estimate: ~5 GB install, 20 min over fast network.
2. **Download Qwen3.5-9B weights**: `huggingface-cli download Qwen/Qwen3.5-9B-Instruct --local-dir /media/data3/dengkw/models/qwen35-9b`. Estimate: ~18 GB, 30-60 min over HuggingFace mirror.
3. **Download Qwen2.5-7B-Instruct**: ~14 GB, control model.
4. **Start 4× vLLM servers** on GPUs 1,4,5,7 as separate processes (nohup + port 8001-8004).
5. **Smoke test**: `curl -X POST http://localhost:8001/v1/chat/completions -d '{"model":"qwen35-9b","messages":[{"role":"user","content":"hi"}]}'`.

### 4.3 Idea04 integration (minimal)

Our runner already supports arbitrary OpenAI-compatible endpoints via `configs/llm.json` `oversea` block. Add a new config block:

```json
"local_qwen35": {
  "url": "http://localhost:8001/v1/chat/completions",
  "key": "EMPTY",
  "model": "qwen35-9b"
}
```

and run `LLM_BACKEND=local_qwen35 python scripts/run_e017_fullval_seed.py --seed 42 --method fixed_peer_calibrated --n 200`. Zero runner code change needed.

**For the 4-agent-per-role deployment**, a tiny proxy routes requests to different ports by agent role. Two options:

- **(A)** Modify `methods.py` to read agent role → endpoint port mapping from env.
- **(B)** Run a single vLLM with 4 GPU tensor_parallel_size=4 and accept all roles → same port, same load balancer (simpler, less faithful to "each agent is its own model instance" proposal).

For the smoke probes, start with **(B)** (simpler). For the final emergence experiment, escalate to **(A)** (faithful to user's "multi-agent of small models" framing).

### 4.4 Cost estimate

| Phase | Engineer time | $ |
|---|---|---:|
| vLLM + model download | 1-2 h wall (mostly waiting on HF download) | 0 |
| Idea04 integration + smoke | 1-2 h | 0 |
| TCPB Stage-2 + single-agent n=200 on 2 models (Qwen3.5-9B + Qwen2.5-7B) | ~4-8 h wall (GPU-time) | 0 |
| Full HotpotQA fullval n=7405 × 2 models × 2 methods × 1 seed | ~24-48 h wall | 0 |
| Electricity (~700 W × 48 h × 4 GPUs) | — | ~$10 (negligible) |

**Total: ~2 engineer days + $10 electricity.** vs current path ~$300 newapi top-up.

---

## 5. Experiment matrix + emergence hypothesis

### 5.1 The matrix

| System | Backbone | HotpotQA n | Existing / New |
|---|---|---:|---|
| Stage-2 (edo_stage2_chain) | gpt-4.1-mini | 7405 | **EXIST** F1=0.6884 |
| Stage-1 (fixed_peer_calibrated) | gpt-4.1-mini | 7405 | **EXIST** F1=0.6823 |
| **Single-agent direct** | gpt-4.1-mini | 200 / 7405 | **NEW, critical** — need this as `F1_large_single` |
| Stage-2 | Qwen3.5-9B | 200 / 7405 | NEW |
| Stage-1 | Qwen3.5-9B | 200 / 7405 | NEW |
| **Single-agent direct** | Qwen3.5-9B | 200 / 7405 | **NEW, critical** — this is `F1_small_single` |
| Stage-2 | Qwen2.5-7B-Instruct | 200 | NEW (control family) |
| Single-agent | Qwen2.5-7B-Instruct | 200 | NEW (control, literature-comparable) |

### 5.2 The emergence hypothesis

Formal claim (falsifiable):

```
Δ_backbone = F1_backbone_Stage-2  −  F1_backbone_single-agent
              where TCPB Stage-2 organizes 4 instances of `backbone` into the chain.

Emergence observed ⇔   Δ_Qwen35-9B  >  Δ_gpt-4.1-mini
                       (multi-agent gain is larger for weaker backbones).
Strong form ⇔           Δ_gpt-4.1-mini ≈ 0
                        AND  Δ_Qwen35-9B ≫ 0
                        (large-model gets no benefit from multi-agent,
                         small-model gets major benefit).
Saturating form ⇔      F1_Qwen35-9B_Stage-2 ≥ F1_gpt-4.1-mini_single-agent
                       (TCPB lets small model recover large-model performance).
```

### 5.3 Predicted outcomes (based on literature)

Using NAACL 2025.long.55 HotpotQA numbers + our existing 0.688 Stage-2:

- `F1_gpt-4.1-mini_single-agent` ≈ 0.72-0.78 (guess; we need to actually run)
- `F1_gpt-4.1-mini_Stage-2` = 0.6884 (measured)
- `Δ_gpt-4.1-mini` ≈ −0.05 to −0.10 **(Stage-2 HURTS for strong model)** — matches the "R-FULL-001 fatal #1" criticism
- `F1_Qwen35-9B_single-agent` ≈ 0.59-0.64 (inferred from Qwen2.5-7B 0.5946 + 9B scale + Qwen3.5 RL improvement)
- `F1_Qwen35-9B_Stage-2` predicted: 0.65-0.72 (TCPB should help because weak backbone has room to benefit from role specialization + peer verification)
- `Δ_Qwen35-9B` predicted: **+0.06 to +0.12** ← this is the emergence signal

If confirmed, we have:

> *"TCPB Stage-2 produces a **6-12 pp F1 gain over single-agent Qwen3.5-9B on HotpotQA**, recovering 80-90% of the gap to the monolithic gpt-4.1-mini Stage-2 (F1=0.688). Meanwhile the same orchestration **does not improve gpt-4.1-mini**. This is a clear instance of organizational emergence at the model-capability boundary — agents that individually lack a capability recover it via collective delegation + verification."*

This is headline-worthy for an emergence paper.

### 5.4 Counterexample / null-hypothesis guard

If `Δ_Qwen35-9B ≤ Δ_gpt-4.1-mini` (i.e., multi-agent also doesn't help the small model), the emergence claim fails and we fall back to the current Pareto-token-efficiency framing (`docs/paper/external_smoke_summary.md §4`).

The experiment design must include this null-hypothesis test as a pre-registered falsification criterion.

---

## 6. Infrastructure risk checklist (engineer-side concerns)

1. **vLLM install on Ubuntu 22.04 + CUDA 12**: generally works out-of-box but version pinning matters. Pin PyTorch 2.5.1 + vLLM 0.10.2 + transformers 4.54+.
2. **Multiple vLLM instances**: each instance needs CUDA_VISIBLE_DEVICES + `--tensor-parallel-size 1`. Port conflicts if not specified.
3. **HuggingFace download failover**: use `HF_ENDPOINT=https://hf-mirror.com` if GFW slow. Download resumeable via `huggingface-cli`.
4. **Model license review** (scientist approval before use):
   - Qwen3.5-9B Apache 2.0 ✓ no concerns
   - Qwen2.5-7B Apache 2.0 ✓
   - Llama 3 License requires acceptance (≥1B user cap; not an issue for research)
   - Gemma License requires acceptance
   - Phi MIT ✓
5. **Safety / prompt injection**: open models may emit biased / unsafe output; need to document in `Ethical Considerations` section per demand.md §11.5 #9.
6. **Reproducibility**: record `transformers.__version__` + `vllm.__version__` + `torch.__version__` + model commit hash in each run's metadata (the runner already logs these via `resolved_model()` output; extend).

---

## 7. Scientist decision matrix (for scientist + user to discuss)

| Option | What it means | Cost | Reward | Risk |
|---|---|---|---|---|
| **A) Pivot to Emergence framing (R41h user proposal)** | Deploy 4 local models; rerun matrix; rewrite paper §1-§4 around emergence | ~2 eng days + $10 | High (falsifiable emergence claim; best-paper candidate) | Δ_small may not be >> Δ_large → null result |
| **B) Stay on current Pareto-token framing** | Continue newapi runs; claim "Stage-2 Pareto-dominates on (F1, tokens)" | $300+ newapi | Medium (already proven but marginal ΔF1) | Reviewers may attack "noise" |
| **C) Do both (A) + (B)** | Run local emergence matrix as primary + keep newapi as consistency check | ~2 eng days + $150 | Highest | Highest engineer time |
| **D) Variant of (A)** using **SmolLM3-3B** or **Phi-4-mini-3.8B** instead of Qwen3.5-9B | Smaller model → emergence may be clearer (since baseline weaker) | ~2 eng days | Medium-high (if emergence is size-dependent) | 3B may be too weak to retrieve anything useful even with TCPB → floor on F1 |

Engineer recommendation: **Option (C)** — the incremental cost of running the newapi MuSiQue matrix (if user DOES top up ≥$200) is worth it for the "both gpt-4.1-mini and Qwen3.5-9B support the Stage-2 direction" dual-evidence paper claim, AND the local emergence experiment is low-cost insurance for the stronger headline.

**Scientist action**: file a `U-XXX-decide` dispatch (per `four-role-todo-workflow.mdc §4.1`) asking the user to pick A/B/C/D.

---

## 8. Concrete engineer next-steps (if user greenlights A or C)

1. Scientist signs off on **Qwen3.5-9B as primary** + **Qwen2.5-7B as control**.
2. Engineer installs vLLM venv (1-2 h), downloads 2 models (1-2 h).
3. Engineer adds `local_qwen35` + `local_qwen25` to `configs/llm.json`.
4. Engineer runs smoke probes (5 samples each, ~10 min) to validate pipeline.
5. Engineer extends `configs/round2_gpt41mini_chain200.yaml` → add `local_qwen35_chain200.yaml` + `local_qwen25_chain200.yaml`.
6. Engineer runs full matrix: 4 Stage-2 runs + 4 Stage-1 runs + 4 single-agent runs × 7405 each.
7. Engineer computes per-model paired-bootstrap CI via `scripts/paired_bootstrap_ci.py`.
8. Scientist writes §4.x results table using `scripts/summarize_external_smokes.py --tex` extended to recognize local-model outputs.

ETA to land all 12 cells: ~48-72 h wall-clock, mostly GPU-bound.

---

## 9. Cross-references

- `docs/paper/external_smoke_summary.md` — current HotpotQA landings (gpt-4.1-mini + 3 external SOTA)
- `idea.md §2` — original EDO emergence framing
- `experiment.md §1.3` — current canonical backbone lockdown (gpt-4.1-mini); this doc proposes modifying §1.3 to allow local-model ablation section
- `.cursor/rules/ssh-server-rules.mdc §E-013 probe` — server GPU inventory
- `docs/paper/sota_baseline_survey_2026.md` — Tier-1 survey (MA-RAG + ReAgent = API-based systems; local-model ablation is orthogonal)
- `docs/paper/benchmark_inventory.md` — datasets + methods map; would add a "local 7B" row
- `docs/coordination/implementation_log.md [r41f_quota_exhaustion_v2_20260421_0850]` — the quota incident that motivated this pivot
- `docs/coordination/implementation_log.md [r41g_runner_robustness_fix_20260421_0910]` — robustness baseline

---

## 10. Open questions (for scientist + user to resolve)

1. **Is the proposed emergence framing the primary story, or complementary to the existing Pareto-token story?** (Scientist + user decision.)
2. **Which small model(s) to commit to?** Default proposal: Qwen3.5-9B primary + Qwen2.5-7B control. Alternative: add Phi-4-mini (3.8B) as a "really small" control to amplify the emergence signal.
3. **Single-agent ablation prompt design**: how does a single 9B model answer a HotpotQA question? Same prompt as the decomposer + synthesizer concatenated? Or a direct Q+passages+answer template? This is a design choice that affects F1_single — scientist should draft the prompt and include in Appendix.
4. **Token accounting for emergence**: multi-agent × 4 roles × ~2 LLM calls each = 8 calls × ~500 tokens = 4000 tokens/sample; single-agent = 1 call × 3000 tokens. **Small-model multi costs ~1.3× single on tokens** — still far below gpt-4.1-mini Stage-2's 479 tokens/sample because we're self-hosting (zero API cost). Reframe token-efficiency claim as "quality gain per 0 API-cost" vs "quality gain per API-dollar".
5. **Failure modes specific to small models**: short-answer formatting (same as the ReAgent format-penalty issue in R41c §12.4), weaker JSON compliance, longer thinking chains. Engineer should instrument + characterize.

---

## Footer — engineer posture

This doc is infrastructure-ready: if scientist + user sign off, engineer can start installing vLLM + downloading models within 5 minutes of greenlight. All pre-reqs (GPU inventory, venv path, install script sketched) are verified.
