# R43 Engineer → Scientist Progress Briefing

**Posted by**: engineer (R43, 2026-04-23, 工程师 session)
**Target reader**: scientist (writing lead)
**Expected reply-action ticket**: `S-203` in `SCIENTIST_TODO.md §B.5`
**Cross-ref**: `[r43_engineer_takeover_r42b_recovery_20260423]` in `ENGINEER_TODO.md` (lines ~5340-5418)

---

## 1. 一句话 TL;DR

**sprint-LLM 那条链仍被 `U-EXEC-008 v2` newapi 充值阻塞 (E-017 seed=43/44 + E-014 + MA-RAG/ReAgent reproduce 继续挂)**，但**我已经把 R42b 的 emergence pivot 基础设施在服务器上重新拉起来了**：Phi-4-mini + SmolLM3-3B 下载恢复在跑 (R43 retry wrapper, `hf download` + `--max-workers 2`, 挂了 10-attempt 自动重试)，`r42_auto_watcher_emergence.sh` 也重新挂成 nohup daemon（PID 383898），下载完自动起 vLLM + 跑 Phi-4 × {single_agent, edo_stage2_chain} × HotpotQA n=5 smoke。

**预期在本轮下一次 engineer checkpoint（下一次 SSH 能连上）前**，会出现：
- (a) `artifacts/emergence/phi4_single_n5/metrics.json`、
- (b) `artifacts/emergence/phi4_edo_stage2_chain_n5/metrics.json`、
- (c) 一个计算好的 `Δ_Phi4_F1 = F1_multi − F1_single`。

全程 **$0 API cost**（本地 GPU vLLM），不需要等用户充值。

---

## 2. 工程师 R43 session 发生过什么（diagnostic + recovery）

### 2.1 诊断到的服务器污染

1. `git sync` commit `b5a9182` overwrote 服务器的工作目录 **并 explicitly 排除了 `configs/llm.json`** → 服务器上的 `configs/llm.json` 是 R42b 之前的旧版本，**不含 `local_vllm` block**，即使 vLLM 起起来了，routing 也会打到 newapi 上（又要撞 insufficient_user_quota）。
2. 服务器 `/media/data3/dengkw/models/{phi4_mini_instruct,smollm3_3b,hf_home}/` 全空（4 K 每个）——R42b 的 download 在我接手之前某个时间 died（没有 log 留存）。
3. `logs/` 被 git sync 清空（11:08 mtime = sync 时间）。
4. **seed=43 run_dir 也被 git sync 干掉了**（R42b 最后记录 PARTIAL 3717/2955 on seed=43，现在服务器上空）——**用户等 quota 回来以后要拿的是 fresh launch 的 seed=43/44**，不是 resume。
5. 只有 `seed=42` fullval 的 `metrics.json` 通过 `artifacts/` 进 git 的原因活下来了：`edo_stage2_chain F1=0.6884`, `fixed_peer_calibrated F1=0.6823`。

### 2.2 R43 恢复动作

1. **scp `configs/llm.json` 本地版 → 服务器**（恢复 `local_vllm` routing block）。
2. **改写 `r42_download_models_parallel.sh`**：`huggingface-cli download` 在 `huggingface_hub >= 1.0` 已 deprecated，必须用 `hf download`；`--local-dir-use-symlinks False` 这个 arg 也被移除；加上 `HF_HUB_ENABLE_HF_TRANSFER=0` 避免 `hf-transfer` 依赖。scp 修好的版本回服务器。
3. **第一轮下载 stalled** （`httpx.ConnectTimeout: _ssl.c:990: The handshake operation timed out`）→ 新写 `workspace/tmp/r43_download_retry.sh`，10-attempt 重试 wrapper，加 `--max-workers 2` 降低并发压力，scp + nohup 启动。
4. **重新挂 `r42_auto_watcher_emergence.sh`** 成服务器端 daemon（PID 383898）：每 60 s polling `python -c "import vllm"` + `ls phi4_mini_instruct/*.safetensors | wc -l >= 2`。满足就自动 exec `r42_emergence_pipeline.sh`。

### 2.3 当前 R43 session 在服务器上的活跃 PID

| PID | 功能 | 日志 |
|---|---|---|
| 385134 | Phi-4-mini retry wrapper（10-attempt） | `logs/r43_download_phi4_<TS>.log` |
| 385141 | SmolLM3-3B retry wrapper（10-attempt） | `logs/r43_download_smollm3_<TS>.log` |
| 383898 | `r42_auto_watcher_emergence.sh` daemon | `artifacts/monitor/r42_auto_watcher_<TS>.log` |

上面三个都 survive SSH disconnect。

---

## 3. 对 Paper framing 的 2 个核心信号（**请 scientist 评估是否值得立刻入 §1 / §6**）

### 3.1 已到位的信号：**seed=42 fullval Stage-2 vs Stage-1 backbone (gpt-4.1-mini, chain-200)**

这是 `[r42_engineer_takeover_pipeline_20260421]` 之前就落地的数据，当前 on-disk 活着：

| Method | F1 | EM | Tok | F1 / Tok×10³ |
|---|---|---|---|---|
| `fixed_peer_calibrated` fullval seed=42 (n=7405) | **0.6823** | 0.4899 | 6414 | 0.1064 |
| `edo_stage2_chain` fullval seed=42 (n=7405) | **0.6884** | 0.4949 | 2331 | **0.2953** |
| Δ (Stage-2 − Stage-1) | **+0.0061** | +0.0050 | **−63.7%** | **+177%** |

这是 **1-seed 观察**，**没有 paired-bootstrap CI**（E-017 seed=43/44 被 quota 断了）。但**方向和 200-sample preliminary (E-005) + seed=42-only paired stats 一致**：
- ΔF1 的绝对量小（几个百分点范围内）；
- **Token 下降 very large**（≈ −60 ~ −63%，远超 200-sample 的 −37%，说明 scale up 对 token cost 效应更强）；
- **cost-normalised F1** 是 reviewer 提到的 "Pareto axis switch" 信号：Stage-2 把 "axis" 从 F1-绝对值切到 F1/token 上 —— 这条信号在 R45 scientist 已经入了 `S-166`, R-FULL-014 P5 也有 "reversing→reframes" 的 polish 建议。

**但 D4 cap 仍然 binding**（sole binding cap across R-FULL-014..021 7 batches），因为没有 paired CI + 单 benchmark。要真 break，要么等 quota 回来 E-017 3-seed + MuSiQue，要么**用 emergence smoke 把 "this mechanism scales with model size" 的独立证据补上**。

### 3.2 即将到位的信号：**Phi-4-mini emergence smoke**（R42b/R43 pivot）

**hypothesis**（R41h ack 过的, user 在 R40 approve 的 emergence pivot）：

- 如果 multi-agent coordination 是**涌现能力**（emergence），那么在 model scale 小到某个程度时，`Δ = F1_multi_agent − F1_single_agent` 会 collapse / negative；在大模型上，Δ 会 positive。
- 推论：用 **Phi-4-mini (3.8B)** + **SmolLM3-3B (3B control)** 作为 small-model 端，用 **gpt-4.1-mini** 作为 large-model 端，测三个点，看 Δ 是否单调增长。
- 如果 Δ_Phi4 ≈ 0 或 < 0（small model 无法受益于 multi-agent），Δ_gpt41mini > 0（large model 受益）**= emergence paper**。
- 如果 Δ 都正，也没问题，那就是 "scale-invariant multi-agent win" story 的证据（但这个 angle 比 emergence 弱一些）。

**本轮即将到位的**：
- `Δ_Phi4 ≈ F1(Phi4, edo_stage2_chain, n=5) − F1(Phi4, single_agent, n=5)` 作为**第一个数据点**。
- n=5 是 smoke（防止第一次跑就把 GPU 烧 8 小时），**如果方向 clear + 后续 quota unblocks**, 可以扩到 n=50 / n=200 / 更大。
- **下一步**：SmolLM3-3B parallel emergence smoke（我打算在 port 8002 / GPU 4 并行跑作 control backbone，第二个 data point）。

### 3.3 **给 scientist 的落地选项**（非强推）

| 选项 | 动作 | 预期 paper impact | effort |
|---|---|---|---|
| (a) **等 3-data-point emergence 齐了再改 §1 framing** | scientist 保持现状，等 `Δ_Phi4` + `Δ_SmolLM3` + (quota 回来后的) `Δ_gpt41mini` 三点齐了，重写 §1 emergence story | +1 angle for Best-Paper，D4 cap 有望在 EXP-8 emergent-structure 方向松 | 1.5 h 等 + 90 min 写 |
| (b) **现在预留 §1 / §6 一段 "Emergence evaluation"** | scientist 先在 `_pending_data_templates.tex` 里留一段 `Δ_Phi4 = [PENDING]`，等数据就无缝替换 | Minimal cost now, faster commit once data lands | 15 min 预留 + 15 min 替换 |
| (c) **把 cost-normalised F1 axis 作为当前 main story** | 用 seed=42 的 F1/token 重写 §1，把 emergence 作为 Appendix F future work | 不等新数据，ARR 时间线能保；但 D4 cap 仍 binding | 45 min |
| (d) **不动** | scientist 继续手头的 S-201 / S-202 / S-174..S-178 closure + S-166 stage2 interim templates | 零风险 | 0 |

**我（engineer）的观察**：选 (a) 或 (b) 都合理。(c) 的风险是 reviewer 会说 "cost-normalized F1 不是新 story"（R-FULL-014 P5 已经提示 "reversing" 有 overclaim 味）。(d) 最保守。真正的决定权**在 scientist + user**，我不拍板。

---

## 4. 服务器并行 GPU 使用现状（供 scientist 知情）

8 张 GPU：
- GPU 0-3: 4× RTX 3090 (24 GB each, 96 GB total)
- GPU 4-7: 4× RTX 2080 Ti (11 GB each, 44 GB total)

**R43 期间实际用法**（保守）：
- **GPU 1**: 保留给 Phi-4-mini vLLM server (port 8001, 等下载完 watcher 起)；占 ~85% 的 24 GB。
- **GPU 4**: 保留给 SmolLM3-3B vLLM server (port 8002)，我下一步会起第二个 pipeline。
- **GPU 0 / 2 / 3 / 5 / 6 / 7**: 暂未使用。**如果 scientist 有其他实验 idea**（例如 Llama-3.2-3B emergence smoke / Qwen-2.5-7B as second large-model comparator），可以在 §B.5 开一条 `S-XXX`，engineer 可以继续 stack 更多 vLLM server 把剩余 GPU 塞满。

**现在 engineer 是否在利用 idle GPU**：只有 1-2 张 GPU 被 vLLM 保留，剩余 6 张 idle。这是"start small, verify correct, scale out" 的 policy，不是纯粹并行用满；如果 scientist 想要我更激进地堆 experiment，发个 S-204 要求 "run 4 backbone sizes in parallel on GPUs 0/2/3/5"，我可以立刻实施。

---

## 5. 具体的 scientist actionables（**S-203 只要求 read + decide**）

1. **Read this doc 到这里**。
2. **做一个小决定**：§3.3 的 (a)/(b)/(c)/(d) 选哪个；如果选 (b)，提 engineer 不需要动作；如果选 (a)，engineer 按当前 plan 继续；如果选 (c)，engineer 不需要动作；如果希望更激进的 parallel experiment，开 `S-204`。
3. **scientist 的手头事务不受本 doc 影响**：`S-201` (H3 metric formalise) / `S-202` (R-FULL-021 S-104 closure) / `S-174..S-178` 补账 closure 继续做，与 engineer R43 pipeline 完全正交。

---

## 6. 工程师下一步 auto-actions（不阻塞科学家）

**即使 scientist 一句话不回**，engineer 会按以下自动推进：

1. 监测 `r43_download_phi4_*.log` + `r43_download_smollm3_*.log` 的下载百分比，直到 Phi-4-mini `.safetensors` 满足 auto-watcher 的 ≥ 2 条件。
2. auto-watcher 触发 `r42_emergence_pipeline.sh` → vLLM on port 8001 → `Δ_Phi4` smoke → 数据落 `artifacts/emergence/phi4_*/metrics.json`。
3. Engineer 读数据，填 `docs/paper/emergence_smoke_results.md`（已预留 template），update `ENGINEER_TODO.md`。
4. **给 scientist 再发一个 progress_for_scientist_v2.md**，届时 scientist 再评估 §3.3 的决定。
5. SmolLM3-3B 下载完，engineer 起第二 vLLM 并行跑 SmolLM3 × {single, edo} smoke（但这个先 pending scientist 是否真需要 control backbone, 如果 scientist 觉得 Phi-4 一条就够了，开 `S-204 = skip SmolLM3` engineer 会跳过）。
6. 如果 `U-EXEC-008 v2` 被用户充值了，engineer 会**在 engineer 自己的 ENGINEER_TODO 里**起 E-014 / E-017 seed=43/44 / MuSiQue 的链，**不会动 scientist 的 paper**。

---

## 7. 已存在的 artifacts + 日志（方便 scientist / reviewer audit）

| Artifact | 路径 | 说明 |
|---|---|---|
| R43 phase block | `docs/coordination/ENGINEER_TODO.md` L5340-5418 | R43 takeover + R42b recovery 完整 diagnostic |
| 本文档 | `docs/paper/r43_engineer_progress_for_scientist.md` | 给 scientist 看的 briefing |
| seed=42 fullval metrics | `artifacts/round2_gpt41mini_stage2_fullval/run_*/edo_stage2_chain/metrics.json` | 1-seed Stage-2 数据（**真数据**） |
| seed=42 fullval paired stats | `artifacts/round2_gpt41mini_stage2_fullval/paired_stats_seed42_only.csv` | seed=42 only paired CI (interim) |
| emergence smoke results (to-be-filled) | `docs/paper/emergence_smoke_results.md` | Phi-4 / SmolLM3 smoke 结果将落这里 |
| vLLM routing config | `configs/llm.json` `local_vllm` block | 本地 vLLM 路由（R43 scp 恢复了 server 侧） |

---

## 8. 给 scientist 的单行回复建议（可直接填在 SCIENTIST_TODO S-203 status 里）

**示例 1**（选项 b，最省力）：
> `✅ read @ 2026-04-23 HH:MM, chose (b) — predefined `\texttt{Δ_Phi4 = [PENDING]}` block in `_pending_data_templates.tex` L___; await engineer v2 doc.`

**示例 2**（选项 a，保守）：
> `✅ read @ 2026-04-23 HH:MM, chose (a) — wait for 3-data-point emergence trio before §1 framing pivot; engineer continue auto-plan.`

**示例 3**（选项 d，不动）：
> `✅ read @ 2026-04-23 HH:MM, chose (d) — scientist continue S-201/S-202 handoff; revisit after engineer v2.`
