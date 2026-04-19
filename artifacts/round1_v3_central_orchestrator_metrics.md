# Round1 v3 — 中心化调度 + 反思（baseline）专项

**数据来源**：`artifacts/round1/run_20260411_102202/` 下各方法目录中的 `metrics.json`（`sample_count` = 200，与 `artifacts/round1/round1_v3_main_table.csv` 一致）。

**对照焦点**：`fixed_peer_calibrated` vs **`central_orchestrator`（无反思）** vs **`central_orchestrator_with_reflection`（有反思）**。

## 1. Peer vs 无反思 / 有反思中央调度

| 方法 | F1 (`answer_f1`) | EM (`answer_em`) | PAR (`premature_accept_rate`) | MHC (`mean_handoff_count`) | `token_cost_per_sample` | `cost_normalized_f1` |
|------|-----------------|------------------|------------------------------|----------------------------|---------------------------|----------------------|
| `fixed_peer_calibrated` | 0.5955 | 0.475 | 0.00 | 1.0 | 480 | 1.240553 |
| `central_orchestrator` | 0.5802 | 0.455 | 0.00 | 1.6773 | 637.5 | 0.910168 |
| `central_orchestrator_with_reflection` | 0.5794 | 0.440 | **0.65** | 1.0 | **363** | **1.596062** |

**缩写**：PAR = premature accept rate（过早接单率）；MHC = mean handoff count（平均交接次数）。

## 1.1 为何 `central_orchestrator` 与 `fixed_static_roles` 聚合指标可完全一致？

实现均在 `workspace/idea04_core/methods.py`。

1. **同一 `preferred` 来源**：两法在 `_policy_decision` 中都用 `_infer_preferred_role(question)`（问题前缀关键词 → 四类角色之一，缺省为 `synthesizer`）。
2. **accept / forward 在「有邻居」时一致**：`central_orchestrator` 当且仅当 `agent_name == preferred` 时 `accept`，否则 `forward`。`fixed_static_roles` 在 `agent_name == preferred` 时 `accept`；若未命中 `preferred` 且 **仍有邻居**，同样 `forward`。二者在非 peer 路径下转发目标均由 `_pick_best_neighbor(neighbor_list, preferred, ...)` 决定：**`preferred` 若在邻居中则选之，否则取邻居字典序第一个**。
3. **唯一语法差异**：`fixed_static_roles` 在 **`neighbor_list` 为空** 时仍 `accept`（链式拓扑下仅 `synthesizer` _sink）；`central_orchestrator` 在「当前节点非 preferred」时一律 `forward`。在本实验的 **chain** 与样本集上，轨迹均在到达 **preferred 节点** 处以 `accept` 结束，**不会**落到「已在 synthesizer、但 `preferred` 仍指向链上更早角色、仅靠 static 空邻居兜底接单」的分叉，因而 **逐跳路由与每跳触发的 `call_llm` 一致**，F1、EM、启发式 `token_cost_per_sample`（由 `runner` 中 hop 数公式决定）在聚合上相同。
4. **表述边界**：这是 **本仓库当前启发式中央调度** 与 **static 角色路由** 的 **观测等价**，不是一般命题「中央调度 ≡ static」。若审稿人要求可区分对照，需改 CO 的邻居偏好/拓扑或引入与 static 不同的分配规则，再与 Agent1 约定重跑。

### 稻草人防御（一句结论）

已并排 **无反思** 与 **有反思** 中央调度：二者 F1 均低于 peer；**有反思** 在更低启发式 token 下 **PAR 飙升、cost_norm 上升**，**无反思** 在本 run 的聚合指标与 **`fixed_static_roles` 完全一致**（同 F1 / token / MHC），故对照不仅是「加强版稻草人」，也包含 **弱中央 / 静态拓扑等价轨迹**；主要分歧在 **接单行为与成本结构**，而非单点 F1 的单调提升。

## 2. 叙事：性价比与行为缺陷（有反思线）

- **F1 / EM**：中央 + 反思在 F1 上略低于 peer（0.5794 vs 0.5955），EM 亦略低（0.44 vs 0.475），属于「互有胜负 / 不占优」区间；单靠准确率不足以说明中央方案更优或更差。
- **PAR 偏高**：中央 + 反思的 PAR 为 **0.65**，而 peer 与 **无反思中央** 均为 **0**（本数据）。说明反思路径大量在**尚未充分多跳推理或证据检索**时即被调度为「接单」终止。
- **cost_normalized_f1**：与 `workspace/idea04_core/runner.py` 一致，为 `answer_f1 / (token_cost_per_sample / 1000)`。有反思线 token 更低（363 vs 480），故 **cost_normalized_f1 更高（1.596 vs 1.241）**——在**当前启发式 token 计账**下**单位 token 的 F1 更好**；但若强调**答案质量优先**，须同时报告 PAR 与 F1。
- **过早接单与失败**：高 PAR 表示调度在反思后仍常将「接单」判给早期节点，跳过后续 verifier / synthesizer 的纠错机会，从而在复杂多跳题上产生**表面连贯、事实错误**的答案。

## 3. 证据链（可复现，有反思线）

**`task_id`: `hotpotqa-0001`**

- **金标**：`Chief of Protocol`；**模型最终答案**：`Shirley Temple Black`（F1 = 0，EM = 0）。

**`routing_traces.jsonl`**：`hop_index` 0，`decomposer`，`decision`：**`accept`**，`reason` 含 `central_orchestrator_with_reflection: ... accepting`。

**`parsed_predictions.jsonl`**：`accepted_node`: `decomposer`，`hop_count`: 1，`termination_reason`: `accepted`，`answer_f1`: 0.0。

## 4. 图表与命令（可复现）

| 产出 | 数据源 | 生成命令 |
|------|--------|----------|
| Peer vs Self-Calibrated 收敛对比 | `run_20260411_102202` peer + `run_20260411_132631` self | `python scripts/plot_dynamics.py --snapshots artifacts/round1/run_20260411_102202/fixed_peer_calibrated/competence_snapshots.jsonl:peer artifacts/round1/run_20260411_132631/fixed_self_calibrated/competence_snapshots.jsonl:self --out artifacts/round1_v3_convergence_compare.png` |
| 同 run 六方法 F1 vs token（主表子集） | `run_20260411_102202` | `python scripts/plot_round1_f1_vs_tokens.py --run-dir artifacts/round1/run_20260411_102202 --methods fixed_static_roles,fixed_self_claim,fixed_peer_calibrated,central_orchestrator,central_orchestrator_with_reflection,fixed_self_calibrated --out artifacts/round1_v3_f1_vs_tokens_run_20260411_102202.png` |
| 同 run **八方法** F1 vs token | `run_20260411_102202`（含 `single_agent`、`fixed_random_forward`） | `python scripts/plot_round1_f1_vs_tokens.py --run-dir artifacts/round1/run_20260411_102202 --methods single_agent,central_orchestrator,central_orchestrator_with_reflection,fixed_static_roles,fixed_self_claim,fixed_random_forward,fixed_peer_calibrated,fixed_self_calibrated --out artifacts/round1_v3_f1_vs_tokens_eight_methods_run_20260411_102202.png` |

## 5. 相关附录

- **配对 bootstrap / 符号检验**：`artifacts/round1_v3_statistics.md` + `artifacts/round1_v3_paired_stats.csv`。
- **无反思 CO 跑数**：`python scripts/run_round1_v3.py --config configs/round1_hotpotqa.yaml --samples-jsonl artifacts/round1/run_20260411_102202/fixed_peer_calibrated/raw_inputs.jsonl --methods central_orchestrator --artifacts-root artifacts/round1 --resume-run-dir artifacts/round1/run_20260411_102202`；校验：`python scripts/validate_logs.py artifacts/round1/run_20260411_102202/central_orchestrator`。
- **真实 API `usage` 与启发式分列**：`artifacts/round1_v3_usage_appendix.md`；新跑数的 `metrics.json` 含 `api_*_tokens_per_sample` 与 `cost_normalized_f1_api`，`raw_model_outputs.jsonl` 每行含 `usage_calls`。**历史 `run_20260411_102202` 未重跑，API 列在主表中为空**，需全量重跑后填满。
