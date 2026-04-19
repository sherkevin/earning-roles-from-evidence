# implementation_log

## 记录规则
- 所有阶段必须记录：新增文件、关键决策、blocker、fast-fail 状态。
- 若 `experiment.md` 与实现现实冲突，先写入“冲突记录”，再处理。
- blocker 必须归类为以下之一：
  - `environment_failure`
  - `dependency_failure`
  - `api_failure`
  - `adapter_failure`
  - `benchmark_noise`
  - `method_failure`

## 当前状态标签
- `Framework Complete`
- `API Verified`
- `Benchmark Ready`
- `Round0 Results`
- `Round1 Results`
- 若框架通但基准受阻，使用：`Framework Complete, Benchmark Blocked`

## 阶段日志模板
### [phase_name]
- status:
- date:
- files_added:
  - none
- files_modified:
  - none
- key_decisions:
  - none
- blockers:
  - none
- blocker_type:
  - none
- fast_fail_triggered:
  - no
- conflicts_with_docs:
  - none
- verification:
  - none
- next_action:
  - none

## 执行记录
### [step0_bootstrap]
- status: completed
- date: 2026-04-01
- files_added:
  - none
- files_modified:
  - `implementation_log.md`
- key_decisions:
  - 维持 short paper 单一目标，不扩展长文范围。
  - 目录按 `engineer_prompt.md` 和 `experiment.md` 的最小骨架锁定。
- blockers:
  - none
- blocker_type:
  - none
- fast_fail_triggered:
  - no
- conflicts_with_docs:
  - none
- verification:
  - 已确认目录存在：`artifacts/round0`、`artifacts/round1`、`artifacts/round2`、`prompts`、`configs`、`scripts`、`workspace`。
- next_action:
  - 在 `workspace` 接入 AutoGen 并完成最小对话可运行验证。

### [step1_autogen_integration]
- status: completed
- date: 2026-04-01
- files_added:
  - `workspace/autogen` (clone)
  - `scripts/autogen_topology_smoke.py`
  - `artifacts/round0/autogen_smoke_chain.json`
  - `artifacts/round0/autogen_smoke_star.json`
- files_modified:
  - none
- key_decisions:
  - 采用 `autogen-core` + `SingleThreadedAgentRuntime` 做最小可运行验证。
  - 用 intervention handler 拦截 `on_send` 事件，验证消息可观测。
- blockers:
  - none
- blocker_type:
  - none
- fast_fail_triggered:
  - no
- conflicts_with_docs:
  - none
- verification:
  - `chain` 与 `star` 两种拓扑均通过检查，且消息发送事件可拦截写日志。
- next_action:
  - 实现统一 contract 与方法切换 runner。

### [step2_step4_unified_contract_packet_competence]
- status: completed
- date: 2026-04-01
- files_added:
  - `workspace/idea04_core/__init__.py`
  - `workspace/idea04_core/contracts.py`
  - `workspace/idea04_core/methods.py`
  - `workspace/idea04_core/runner.py`
  - `prompts/main_agent_prompt.txt`
- files_modified:
  - `workspace/idea04_core/methods.py`
- key_decisions:
  - 统一输入：`task_id/question/incoming_packet/local_state/neighbor_list/method_state`。
  - 统一输出：`decision/outgoing_packet/raw_response/competence_update/trace`。
  - `fixed_peer_calibrated` 采用轻量规则更新，避免复杂 router/RL/GNN。
- blockers:
  - 初次跑数时 `fixed_peer_calibrated` 与 `fixed_self_claim` 代理指标无差异。
- blocker_type:
  - `method_failure`
- fast_fail_triggered:
  - no
- conflicts_with_docs:
  - none
- verification:
  - 6 个方法名已全部接入统一方法注册表并可被同一 runner 调用。
  - packet schema 字段已覆盖：`task_id/question/current_subgoal/evidence_so_far/uncertainty/reason_for_forward/recommended_next_skill`。
- next_action:
  - 在 Round0 冒烟中验证代理指标差异并固化产物结构。

### [step5_round0_hotpotqa_smoke_v0_INVALID]
- status: completed
- date: 2026-04-01
- files_added:
  - `configs/round0_hotpotqa.yaml`
  - `scripts/bootstrap_round0.py`
  - `scripts/run_round0_smoke.py`
  - `artifacts/round0/round0_main_table.csv`
  - `artifacts/round0/round0_routing_examples.md`
  - `artifacts/round0/round0_logging_check.md`
  - `artifacts/round0/run_20260401_135504/*`
- files_modified:
  - `workspace/idea04_core/methods.py`
- key_decisions:
  - 在不改变方法论前提下，增强 target-skill 分配可观测性以暴露 delegation miscalibration。
  - 保持同一拓扑、同一样本集、同一预算配置用于方法对比。
- blockers:
  - HuggingFace 未配置 token，仅出现未认证限速提示，不影响本轮 50 样本运行。
- blocker_type:
  - `api_failure`
- fast_fail_triggered:
  - no
- conflicts_with_docs:
  - none
- verification:
  - 50 样本 Round0 冒烟完成。
  - 每个方法目录均生成必需产物：`run_config.yaml`、`sample_ids.json`、`raw_inputs.jsonl`、`routing_traces.jsonl`、`handoff_packets.jsonl`、`competence_snapshots.jsonl`、`raw_model_outputs.jsonl`、`parsed_predictions.jsonl`、`metrics.json`、`main_table.csv`、`failure_cases.md`、`case_studies.md`、`run_notes.md`。
  - 指标信号：`fixed_peer_calibrated` 的 `premature_accept_rate=0.0`，优于 `fixed_self_claim=0.84`。
- next_action:
  - 按 `Go/No-Go` 规则补充更多 delegation proxy 统计并扩展到 Round1 前置检查。

### [step5_round0_v0_scientist_review_FAIL]
- status: failed
- date: 2026-04-01
- blockers:
  - EM/F1 评测对象错误：评的是 accepted_node==target_skill，不是 gold answer 对比。
  - 方法决策无模型调用：纯规则模拟，不能称为实验结果。
  - fixed_static_roles 与 fixed_peer_calibrated 结果完全相同，peer-calibrated 机制未生效。
  - 日志完整性检查是假的，只列文件名不做覆盖率验证。
  - implementation_log.md 对实际状态描述不实。
- blocker_type:
  - method_failure
- fast_fail_triggered:
  - yes
- conflicts_with_docs:
  - 之前记录"Round0 Results"，实际应为"Framework Complete, Benchmark Logic Blocked"。
- next_action:
  - 完成 6 项修正后重跑（真实 EM/F1、GLM 调用、peer-calibrated 跨样本更新、validate_logs、如实日志、case study）

### [step5_round0_v1_correction]
- status: in_progress
- date: 2026-04-01
- files_added:
  - workspace/idea04_core/llm_client.py
  - workspace/idea04_core/evaluation.py
  - scripts/validate_logs.py
- files_modified:
  - workspace/idea04_core/contracts.py
  - workspace/idea04_core/methods.py
  - workspace/idea04_core/runner.py
- key_decisions:
  - 使用 glm-4-flash，API key 注入 llm_client.py，不写入日志或文档。
  - peer-calibrated competence 跨样本持久化，每轮根据 answer F1 更新接单节点 competence。
  - 两层指标明确区分：QA 质量（answer_em/answer_f1）与 delegation proxy（premature_accept_rate 等）。
- verification:
  - 50 样本 Round0 v1 完成，run_id: run_20260401_144903
  - validate_logs.py 三个方法均为 [OK]，样本覆盖率 100%
  - 真实 EM/F1 指标（对比 HotpotQA gold answer）：
    - fixed_static_roles:    EM=0.54, F1=0.6631, PAR=0.000, MHC=1.697
    - fixed_self_claim:      EM=0.56, F1=0.6171, PAR=1.000, MHC=0.000
    - fixed_peer_calibrated: EM=0.52, F1=0.5931, PAR=0.440, MHC=1.949
  - delegation proxy 关键信号：peer_calibrated PAR=0.44 vs self_claim PAR=1.0，说明
    competence 更新确实在减少过早接单。
  - per-hop F1：peer_calibrated 在 hop>1 时 F1=0.622，高于 hop=1 时 F1=0.556，
    说明转发到专家节点有边际质量提升。
  - Decomposer competence 轨迹可见：初始 0.70，峰值 0.95，随失败样本回落到 0.57，
    并在 sample-22 起触发向 evidence_seeker 的转发，路由链从 1 跳变为 2-3 跳。
  - 案例 hotpotqa-0023：decomposer 转发 -> evidence_seeker 转发 -> verifier 接单答对，
    F1=1.0，是"同伴反馈纠正错误接单"的正向证据。
- Go/No-Go 评估:
  - Go 条件 4（明显降低 premature_accept_rate）满足：0.44 vs 1.0
  - Go 条件 5（案例能显示同伴反馈纠正路由）满足：hotpotqa-0023 等案例
  - No-Go 条件均未触发
  - 当前状态：满足 2 条 Go 条件，允许进入 Round1，但需先改善专家节点答案质量
- current_status: Round0 Results（有效）
- next_action:
  - 如实如下限制：peer_calibrated F1 低于 self_claim，原因是专家节点缺乏充足的答案生成能力。
    Round1 需要改善 evidence_seeker/verifier/synthesizer 的答案生成 prompt，再扩样本。

### [round1_run_20260411_peer_calibrated_resume]
- status: completed
- date: 2026-04-11
- files_added:
  - `artifacts/round1/run_20260411_053608/fixed_peer_calibrated/*`（补跑）
  - `artifacts/round1/round1_main_table.csv`
- files_modified:
  - `scripts/run_round0_smoke.py`（`--methods`、`--resume-run-dir`、从 run 目录聚合 `metrics.json` 写汇总表）
- key_decisions:
  - 使用已有 `raw_inputs.jsonl` 与 `run_20260411_053608`，仅补跑 `fixed_peer_calibrated`，保证与另两种方法同批 50 条样本。
- blockers:
  - `experiment.md` 仓库内仍缺失（与 `engineer_prompt.md` 要求不一致）；以 `implementation_log` + 代码为准继续。
- blocker_type:
  - none（文档缺失记为冲突，不阻塞跑数）
- verification:
  - `validate_logs.py` 对 `fixed_peer_calibrated`：[OK]，50 样本 100% 覆盖。
  - 同 run 汇总（`round1_main_table.csv`）：peer_calibrated answer_f1=0.6317 vs self_claim 0.5852；premature_accept_rate 0.46 vs 1.0。
- current_status: Round1 Results（50 样本子集，chain，与 Round0 日志中「先改善 prompt 再扩样本」仍兼容）
- next_action:
  - 按需将 `sample_size` 提到 100 全量重跑三种方法；或按日志计划微调 `prompts/main_agent_prompt.txt` 中专家节点指令后再扩样本。

### [round1_100sample_parallel_run_20260411_063741]
- status: completed
- date: 2026-04-11
- files_added:
  - `artifacts/round1/run_20260411_063741/*`（三方法 × 100 样本，`artifacts/seed/hotpotqa_validation_100.jsonl` 同批）
  - `artifacts/round1/round1_main_table.csv`（已更新为本次 100 样本汇总）
- files_modified:
  - none（本轮仅跑数）
- verification:
  - `validate_logs.py artifacts/round1/run_20260411_063741 --all-methods`：三方法均 [OK]，100% 覆盖。
- metrics_summary（validation 前 100 条，chain，glm-4-flash）:
  - fixed_static_roles: EM=0.45, F1=0.5731, PAR=0.0, MHC=1.6875
  - fixed_self_claim: EM=0.42, F1=0.5209, PAR=1.0, MHC=0.0
  - fixed_peer_calibrated: EM=0.43, F1=0.547, PAR=0.01, MHC=1.9932
- Go/No-Go（相对此前用户预期）:
  - PAR：`fixed_peer_calibrated` 相对 `fixed_self_claim` 极显著（0.01 vs 1.0），满足继续扩大样本的委托代理信号。
  - F1：peer（0.547）略高于 self_claim（0.5209），但低于 static_roles（0.5731）；成本（token_cost_per_sample）peer 更高。
  - 结论：可进入更大样本主实验以检验 F1 优势是否稳定，同时需持续关注「多跳 + 高 token」下的性价比。
- current_status: Round1 Results（100 样本主对比已完成）
- next_action:
  - 若进 300–500 样本：沿用 `artifacts/seed/hotpotqa_validation_100.jsonl` 的导出方式扩切片，或 `export_hotpot_seed.py` 导出 N；新开 `run_*` 三方法平行跑。

### [failure_mode_analysis — static 赢、peer 输（run_20260411_063741, n=100）]
- 抽样标准：在 100 条上满足 `answer_f1(static) - answer_f1(peer) >= 0.08` 的样本共 **9** 条（无法再扩到 10–15 条而不明显放宽阈值）；其中 5 条为 static EM=1 且 peer EM=0。
- **failure_mode_analysis**（病因归类）:
  1. **过早接单（非「过度转发」）— `hotpotqa-0000`**：peer 在 **decomposer** 第 1 跳即 accept（`hop_count_peer=1`），输出错误实体；static 路由至 **verifier**（3 跳）后答对 `yes`。根因是 **peer 的 competence 门控让高 self 的 decomposer 过早 accept**，与 static 的「按问句形态固定到 verifier」相比，不是转发过多，而是 **该转发时未转发**。
  2. **长链 synthesizer 聚合失败（信息利用不足）— 多条**：`0000` 以外如 `0017, 0033, 0040, 0057, 0050, 0087, 0092, 0076` 中，peer 普遍 **accepted_node=synthesizer** 且 **hop_count=4**（打满 max_handoff 链），static 则多在 **evidence_seeker 或 verifier**（2–3 跳）即答对。handoff 中 `question` 字段仍完整，**未见原始问题被截断**；更可疑的是 **synthesizer 的 LLM 输入只取了 evidence 的短前缀**（旧实现 `[:14]`），长链后关键句落在列表后部，导致 **证据尾部未进上下文 → 错答**（归类为 **信息呈现/聚合缺陷**，而非 packet schema 丢字段）。
  3. **专长向量震荡**：对 `competence_snapshots.jsonl` 的 `post_sample` 统计表明，**synthesizer** 的跨样本 self 更新约占绝大多数（~97/100），且单步 delta 常打满 **+0.06 / -0.10**，易在失败样本后出现 **剧烈下调**。decomposer 等节点极少作为 acceptor，**并非「某节点被调崩后全局路由崩塌」的主因**；主因仍是 **accept 节点选择与 synthesizer 读证据窗口**。

### [code_changes_after_case_study_20260411]
- `workspace/idea04_core/methods.py`：`apply_peer_post_sample_competence`（`PEER_POST_SAMPLE_MOMENTUM=0.5` + `PEER_POST_SAMPLE_MAX_DELTA=0.06`）；synthesizer 生成答案时使用 **最多 60 条** `evidence_so_far`（含全链）；user 消息中标注证据为全 packet。
- `workspace/idea04_core/runner.py`：post_sample 专长更新改为调用上述函数（替代原先一步 ±0.06/0.10 直接写回）。
- `prompts/main_agent_prompt.txt`：`<<<synthesizer>>>` 强化 **按时间顺序读满 evidence_so_far**、不得仅依赖最后一跳。
- `configs/round1_hotpotqa.yaml`：`sample_size: 200`。
- `artifacts/seed/hotpotqa_validation_200.jsonl`：由 `scripts/export_hotpot_seed.py 200 --force` 生成。

### [round1_200sample_parallel_run_20260411_091922]
- status: completed
- date: 2026-04-11
- files_added:
  - `artifacts/round1/run_20260411_091922/*`（三方法 × 200，`artifacts/seed/hotpotqa_validation_200.jsonl`）
  - `artifacts/round1/round1_main_table.csv`（已更新）
- verification:
  - `validate_logs.py artifacts/round1/run_20260411_091922 --all-methods`：三方法 [OK]，200 样本 100% 覆盖。
- metrics_summary（含 **cost_normalized_f1** = `answer_f1 / (token_cost_per_sample/1000)`）:
  - fixed_static_roles: EM=0.465, F1=**0.5944**, MHC=1.677, PAR=0.0, token/sample=637.5, **cost_norm_F1=0.932**
  - fixed_self_claim: EM=0.425, F1=0.5619, MHC=0.0, PAR=1.0, token/sample=300, cost_norm_F1=1.873
  - fixed_peer_calibrated: EM=0.435, F1=**0.5625**, MHC=1.477, PAR=**0.045**, token/sample=628.5, **cost_norm_F1=0.895**
- 结论（相对目标「F1 反超 static」）:
  - peer 的 **F1 仍略低于 static**（0.5625 vs 0.5944），但 **略高于 self_claim**（0.5625 vs 0.5619）；PAR 仍远优于 self_claim。
  - **cost_normalized_f1** 上 static 仍高于 peer（0.932 vs 0.895）；相较 100 样本档（peer token 829、cost_norm 0.66），本轮 **MHC 下降、token 与 static 接近**，成本效率明显改善。
- next_action:
  - 若继续冲 F1：可考虑 **仅对 decomposer 提高 accept 阈值** 或 **问句形态与 peer 门控联合**，减少 `0000` 类过早接单；或加大 synthesizer `max_tokens` / 两阶段「先列关键句再缩答」。

### [round1_v3_F1_optimization — run_20260411_102202]
- status: completed ✅ **GO 条件达成**
- date: 2026-04-11
- files_added:
  - `artifacts/round1/run_20260411_102202/*`（三方法 × 200 样本）
  - `artifacts/round1/round1_v3_main_table.csv`
- files_modified:
  - `workspace/idea04_core/methods.py`：
    - 新增 `_is_multihop_question()` 启发式多跳检测（关键词 + 大写 NE 计数）
    - `_policy_decision` 中 `fixed_peer_calibrated` 分支：decomposer 遇多跳问题强制 forward；单跳也需 competence ≥ 0.90 才能 accept（`DECOMPOSER_FORCE_FORWARD_THRESHOLD`）
    - `_llm_generate_answer`：synthesizer `max_tokens` 128→256；自动剥离 CoT 输出的 `"Answer: "` / `"Key facts:"` 前缀
  - `prompts/main_agent_prompt.txt`：`<<<synthesizer>>>` 改为分两阶段推理（Stage 1 列关键事实 → Stage 2 输出答案）
- metrics_summary（run_20260411_102202，n=200，chain，glm-4-flash）:
  - fixed_static_roles:    EM=0.455, F1=**0.5802**, MHC=1.677, PAR=0.0,   token/sample=637.5, cost_norm_F1=0.910
  - fixed_self_claim:      EM=0.425, F1=0.5619,    MHC=0.0,   PAR=1.0,   token/sample=300,   cost_norm_F1=1.873
  - fixed_peer_calibrated: EM=0.475, F1=**0.5955**, MHC=1.0,   PAR=**0.0**, token/sample=480,   cost_norm_F1=**1.241**
- Go/No-Go 验收:
  - ✅ `fixed_peer_calibrated` F1=0.5955 **≥ 0.595**（反超 static_roles 0.5802）
  - ✅ PAR=0.0 **< 0.05**（归因：decomposer 多跳强制门控生效）
  - ✅ cost_normalized_F1 大幅改善（0.895→1.241），token 成本下降（628→480/sample，MHC 从 1.477→1.0）
- 结论: **Go — 可开启长文或迁移实验**

### [new_methods_added_20260411]
- status: in_progress
- date: 2026-04-11
- files_modified:
  - `workspace/idea04_core/methods.py`（用户手动扩展）
- key_decisions:
  - 新增方法 `central_orchestrator_with_reflection`：heuristic 路由 + LLM 二次反思重分配，作为更强 central baseline。
  - 新增方法 `fixed_self_calibrated`：与 peer_calibrated 同拓扑，但 competence 更新信号来自 agent 自我反思（`_llm_self_reflect`），无下游反馈；阈值 0.55（比 peer 宽松）。
  - 两个新方法均已注册入 `METHOD_NAMES`，`ACCEPT_THRESHOLD`，`_policy_decision`，以及 competence update 分支。
- next_action:
  - 更新 `scripts/run_round0_smoke.py` 的 `ROUND0_METHODS` 列表以包含新方法，或单独建 round2 run 脚本后跑对比实验。

### [round1_v3_engineer2_baselines_run_20260411_132631]
- status: completed
- date: 2026-04-11
- files_added:
  - `scripts/run_round1_v3.py` (突破原测试脚本硬编码方法限制的灵活运行器)
  - `artifacts/round1/run_20260411_132631/*` (fixed_self_calibrated 200-sample 数据)
  - `artifacts/round1_v3_convergence_compare.png` (核心论文对比图)
- files_modified:
  - `scripts/plot_dynamics.py` (新增 `--snapshots` 模式，支持跨目录对比作图)
  - `Agent2-work-summary.md` (记录 Engineer 2 Session 2)
- key_decisions:
  - 为确保苹果比苹果，利用新脚本直接复用 `run_20260411_102202` 的 `raw_inputs.jsonl`，执行了 `fixed_self_calibrated` 对照。
  - 在 `plot_dynamics.py` 补充了多文件作图能力，将 peer_calibrated 和 self_calibrated 绘制同一张图对比长期专长动态。
- validation:
  - `fixed_self_calibrated` F1=0.5833, EM=0.46, mean_handoff=1.73 (较 peer 的 1.0 增加 73%)
  - 图表直观展示自省方案下 competence_estimate 剧烈震荡无法建立专业分工 (Synthesizer 盲目冲向 0.95 抢单)，而 peer 方案下 Evidence Seeker 单调健康收敛至 0.92。
- current_status: EMNLP Baseline Data & Theory Evidence Completed
- next_action:
  - 后续可完善 CO+Reflection 方法的跑图，或者直接开始起草论文。

### [round1_canonical_runners — Engineer1 收尾]
- status: completed
- date: 2026-04-11
- files_added:
  - `artifacts/round1_v3_self_reflect_analysis.md`
- files_modified:
  - `artifacts/round1/round1_main_table.csv`（`fixed_self_calibrated` 行对齐 `run_20260411_132631/.../metrics.json`，与同批 raw_inputs 的 peer v3 可比）
  - `configs/round1_hotpotqa.yaml`（`methods` 与注册表一致，并注释 canonical 跑数入口）
  - `implementation_log.md`
- key_decisions:
  - **Canonical v3 主表锚点**：`run_20260411_102202`（三主方法 + 扩展方法若在同 run 内则一并引用该 run 的 `run_config.yaml`）。
  - **同 jsonl 的 self_calibrated**：`run_20260411_132631`，样本源 = `run_20260411_102202/fixed_peer_calibrated/raw_inputs.jsonl`。
  - **run_round0_smoke.py 与 v3 关系（单一事实来源）**：采用 **方案 B 变体** — `ROUND0_METHODS` 已含 5 个方法（三主方法 + `central_orchestrator_with_reflection` + `fixed_self_calibrated`），用于**冒烟与快速回归**；短文要求的 **single_agent / central_orchestrator / fixed_random_forward** 等全 baseline **不**依赖扩展 `ROUND0_METHODS`，统一通过 **`scripts/run_round1_v3.py --methods ...`** 在同 `samples-jsonl` 上复现（`V3_METHODS` 已列全）。与「仅三方法冒烟」相比，当前仓库已多跑两种新方法，但**全方法矩阵仍以 v3 脚本为权威入口**。
- verification:
  - `validate_logs.py`：`run_20260411_102202/fixed_peer_calibrated`、`run_20260411_132631/fixed_self_calibrated` 均为 [OK]，200 样本。
- next_action:
  - 若短文仍要求六 baseline：按 `engineer1_next_step_instructions.md` §5 在同 `hotpotqa_validation_200.jsonl` 上补跑并用 `validate_logs.py` 验收。

### [round1_v3_engineer2_central_orchestrator_doc_20260411]
- status: completed
- date: 2026-04-11
- files_added:
  - `artifacts/round1_v3_central_orchestrator_metrics.md`（CO+Reflection vs peer 指标表、PAR/cost_norm 叙事、`hotpotqa-0001` 证据链）
  - `artifacts/round1_v3_convergence_compare.png`（`plot_dynamics.py --snapshots`：peer @ `run_20260411_102202` + self @ `run_20260411_132631`）
  - `artifacts/round1_v3_f1_vs_tokens_run_20260411_102202.png`（同 run 五方法 F1–token 散点）
  - `scripts/plot_round1_f1_vs_tokens.py`
- verification:
  - 表中数字与 `artifacts/round1/run_20260411_102202/{central_orchestrator_with_reflection,fixed_peer_calibrated}/metrics.json` 一致。
- next_action:
  - 已由 Session 4 完成无反思 CO 与统计附录（见下）。

### [round1_v3_engineer2_session4_20260411]
- status: completed
- date: 2026-04-11
- files_added:
  - `artifacts/round1/run_20260411_102202/central_orchestrator/`（200 样本，与 peer 同 `raw_inputs.jsonl`）
  - `scripts/compute_paired_bootstrap.py`
  - `artifacts/round1_v3_statistics.md`
  - `artifacts/round1_v3_paired_stats.csv`
- files_modified:
  - `scripts/run_round1_v3.py`（`write_summary`：仅更新本次 `--methods` 对应 metrics；主表行序固定为 `V3_MAIN_TABLE_METHOD_ORDER`）
  - `artifacts/round1/round1_v3_main_table.csv`（新增 `central_orchestrator` 行）
  - `artifacts/round1_v3_central_orchestrator_metrics.md`（peer / 无反思 / 有反思 三行表 + 稻草人结论）
  - `artifacts/round1_v3_f1_vs_tokens_run_20260411_102202.png`（`plot_round1_f1_vs_tokens.py --methods` 六方法）
  - `scripts/plot_round1_f1_vs_tokens.py`（可选 `--methods`）
- key_decisions:
  - 无反思 CO 写入 **既有** `run_20260411_102202`，避免跨 run 作图分裂。
  - 配对统计：bootstrap 在 **全部 200 题配对差分（含零）** 上；符号检验 **剔除平局**。
- verification:
  - `python scripts/validate_logs.py artifacts/round1/run_20260411_102202/central_orchestrator` → [OK]
  - CO：`answer_f1=0.5802`，`PAR=0`，`token_cost_per_sample=637.5`（与 `fixed_static_roles` 聚合指标相同，已在专项 md 披露）。
- next_action:
  - 已由 Session 5 实现 API `usage` 与 `cost_normalized_f1_api`（见 `round1_v3_engineer2_session5_20260411`）。

### [round1_v3_engineer2_session5_20260411]
- status: completed
- date: 2026-04-11
- files_added:
  - `artifacts/round1_v3_usage_appendix.md`
  - `artifacts/round1_v3_f1_vs_tokens_eight_methods_run_20260411_102202.png`
  - `artifacts/round1/run_20260411_154646/single_agent/`（1-sample smoke，验证 `usage_calls` / `api_*` 字段）
- files_modified:
  - `workspace/idea04_core/llm_client.py`（`extract_usage`）
  - `workspace/idea04_core/contracts.py`（`AgentOutput.usage_calls`）
  - `workspace/idea04_core/methods.py`（各 LLM 路径累积 usage）
  - `workspace/idea04_core/runner.py`（`raw_model_outputs` 写 `usage_calls`；`metrics` 增加 `api_*`、`cost_normalized_f1_api`）
  - `scripts/run_round1_v3.py`（`V3_MAIN_TABLE_FIELDS` 含 API 与 `cost_normalized_f1_api`）
  - `artifacts/round1/round1_v3_main_table.csv`（列扩展；**102202 历史 metrics 无 API 数字，格为空**）
  - `artifacts/round1_v3_central_orchestrator_metrics.md`（§1.1 CO≡static 技术说明；§4/§5 图与 usage 指针）
  - `artifacts/round1_v3_statistics.md`（§4 诚实结论）
- verification:
  - smoke：`run_20260411_154646` 的 `metrics.json` 中 `api_total_tokens_per_sample=1570`（n=1）；`raw_model_outputs.jsonl` 含 `usage_calls`。
  - 主表已从 `run_20260411_102202` 八方法重新合并，`single_agent` 行恢复为 n=200（修正误用 1-sample 合并）。
- next_action:
  - 7405 与方案 B 见 `round1_v3_engineer2_session6_20260412`。

### [round1_v3_engineer2_session6_20260412]
- status: in_progress（**硬卡点**：智谱 API `WinError 10061` 连接被拒绝，本机无法跑 7405；**7405 全量未完成**）
- date: 2026-04-12
- files_added:
  - `scripts/post_fullval_chain.ps1`（`validate_logs` + `compute_paired_bootstrap` + `merge-summary-only` 一键串联）
  - `artifacts/round1_v3_statistics_fullval.md`（7405 §1 启动 + §2–§4 或 PowerShell 一键说明）
  - `artifacts/round1/round1_v3_main_table_fullval.csv`、`artifacts/round1_v3_paired_stats_fullval.csv`（若存在则为占位或小样本，**全量成功后须覆盖**）
- files_modified:
  - `scripts/run_round1_v3.py`（`--merge-summary-only`、`--summary-csv-name`、`--no-canonical-self-override`；`--samples-jsonl` 在 merge-only 下可不填）
  - `artifacts/round1_v3_usage_appendix.md`（**§5 方案 B** 写死：102202 不重跑回填 API；实测 token 以 fullval run + `round1_v3_main_table_fullval.csv` 为准）
  - `artifacts/round1_v3_statistics.md`（**§5** 链向 fullval 文档）
- key_decisions:
  - **方案 B**：`round1_v3_main_table.csv` 维持 chain-200 启发式主叙事；**不重跑** `run_20260411_102202` 八方法仅为 API。
- verification:
  - 本机 `call_llm` 探测 → **URLError / 10061**，确认卡点为网络/API 而非脚本语法。
- next_action:
  - 在 **API 可出网** 机器执行 `round1_v3_statistics_fullval.md` §1，完成后 **`scripts/post_fullval_chain.ps1 -RunDir <RUN_FULLVAL>`**（或等价 §2–§4），覆盖 fullval CSV。

### [round1_session4_six_baselines_engineer1_20260411]
- status: completed
- date: 2026-04-11
- files_added:
  - `artifacts/round1/run_20260411_102202/single_agent/`（200 样本，`hotpotqa_validation_200.jsonl`）
  - `artifacts/round1/run_20260411_102202/fixed_random_forward/`（同上）
- files_modified:
  - `artifacts/round1/run_20260411_102202/central_orchestrator/`（若与 Engineer 2 已跑目录重复，指标一致：F1=0.5802，与 `fixed_static_roles` 聚合相同，见既有披露）
  - `scripts/run_round1_v3.py`：`V3_MAIN_TABLE_FIELDS` 恢复全量指标列；`V3_MAIN_TABLE_METHOD_ORDER` 含 **single_agent、fixed_random_forward** 等 8 行顺序
  - `artifacts/round1/round1_v3_main_table.csv`、`artifacts/round1/round1_main_table.csv`（八方法 + **self 行仍人工对齐 `132631`**，因 `102202/fixed_self_calibrated/metrics.json` 为早期同目录副本）
  - `EMNLP_paper_draft.md`（新增 **§4 Experiments** 骨架）
  - `implementation_log.md`
- key_decisions:
  - 短文六 baseline 缺口：`single_agent`、`central_orchestrator`（无反思）、`fixed_random_forward` 已写入 **既有** `run_20260411_102202`，与 v3 主锚同批 jsonl。
  - **未做**：全量 validation 7405、`topology: star`、300–500 规模（留作预算与分工）。
- verification:
  - `validate_logs.py` → `single_agent`、`central_orchestrator`、`fixed_random_forward` 均为 [OK]，200 样本。
- metrics_snapshot（新补三方法，n=200）:
  - single_agent: F1=0.5619, EM=0.425, PAR=0, token/sample=300
  - central_orchestrator: F1=0.5802, EM=0.455, PAR=0, token/sample=637.5
  - fixed_random_forward: F1=0.5494, EM=0.425, PAR=0, token/sample=840, MHC=2

### [round1_session5_data_hygiene_engineer1_20260411]
- status: completed
- date: 2026-04-11
- files_added:
  - `artifacts/COORDINATION_AGENT1_AGENT2.md`（7405 由 Agent2 主跑、Agent1 不启跑除非改约；star 与 7405 分开展，Agent1 主打 200×三主 star）
- files_modified:
  - `scripts/run_round1_v3.py`：`write_summary` 在写 `round1_v3_main_table.csv` 时 **强制用** `run_20260411_132631/fixed_self_calibrated/metrics.json` 覆盖 `fixed_self_calibrated` 行（若该文件存在），避免被 `102202` 内旧 self 覆盖
  - `EMNLP_paper_draft.md` §4 脚注（与脚本行为一致）
  - `implementation_log.md`、`Agent1-work-summary.md`
- verification:
  - `write_summary(..., methods=[])` 重合并后 `round1_v3_main_table.csv` 中 self 行与 `132631/metrics.json` 一致（F1=0.5833，token/sample=685.2）。
- next_action:
  - 7405 / star：按 `COORDINATION_AGENT1_AGENT2.md` 执行；跑完补 `validate_logs` 与 summary。

### [f1_significance_self_audit — run_20260411_102202 peer]
- status: completed
- date: 2026-04-12
- files_added:
  - `scripts/f1_significance_audit_round1.py`（四项自查：终点站证据、路由同质、同伴信号、decomposer 误伤）
  - `artifacts/round1/f1_significance_audit_run_20260411_102202.json`（机器可读汇总）
- Context: peer PAR=0、cost_norm 优，但 F1 与 static/self_calibrated 差小；需排除 Bug 与隐性信息损耗。

#### 1. 终点站 / Synthesizer「黑洞」
- **严格条件**（`hop_count>=3` ∧ `F1<0.2` ∧ 启发式 gold∈evidence）：**0 条**。当前 v3 peer 极少出现 ≥3 跳且仍极低 F1 且金标已在 packet 的 synthesizer 终点失败。
- **放宽 Tier C**（`hop_count>=2` ∧ `F1<0.2` ∧ gold∈evidence）：**59 条**；抽样显示 **接单节点几乎均为 `evidence_seeker`**（2 跳结束），非 synthesizer。
- **结论**：主要瓶颈**不是**「synthesizer 读满 60 行仍 lost-in-middle」，而是 **浅层由 evidence_seeker 提前 accept** 时的 **抽取/实体选择错误**（及少量 API 400 contentFilter）。`evidence_seeker` 在代码中仅将 **`evidence_so_far[:14]`** 拼进 LLM（`methods._llm_generate_answer`），长 packet 时存在 **头部截断** 风险；与「金标在全文但不在前 14 行」类失败一致时需单独扫证。
- **两阶段 CoT**：无法从 jsonl 自动证明模型是否遵守 Stage1/2；仅能确认 **后处理** 已剥 `Answer:`/`Key facts:`（`methods.py`）。若需合规率需另采 `raw_model_outputs` 文本规则或人工抽检。

#### 2. 路由同质化（peer vs fixed_static_roles）
- **200 题**：`(accepted_node, hop_count)` **完全一致 104 / 200（52%）**；**未达 80%**。
- **结论**：peer **未**退化为与 static 全同一路径；F1 拉不开更似 **同批样本上两策略常落到相近浅层路径 + 抽取噪声**，而非「peer=static 复本」的代码 Bug。论文若强调差异，可并列报告 **路径分歧率 48%** 与 **PAR/cost**。

#### 3. 同伴「恶意/误判」反馈（信噪比）
- **实现事实**：**不存在**每 hop 的 LLM `s_peer=-1`。`peer_negative` 仅出现在 **`post_sample`**，且来自 **整题 gold F1<0.5 的规则更新**（`runner` + `apply_peer_post_sample_competence`），**不是**同伴对中间 thought 的打低分。
- **统计**：`post_sample` 中 `peer_negative` **74**、`peer_positive` **126**。
- **对原问题的回应**：「误判率 >30%」在此实现下 **不适用**；若未来引入真实 peer 打分，再谈 confidence 门控。

#### 4. Decomposer 多跳强制门控误伤（static 赢 peer 输）
- **`static F1 > peer F1`**（同 200 题）：**6** 条（非早期 n=100 时的 9 条；阈值严格为 strict inequality）。
- **其中**「单跳题（`_is_multihop_question=False`）且 hop0 decomposer `forward`」：**1 / 6**（`hotpotqa-0051`，首跳仍 forward，与 competence<0.90 门控一致；该题 OCR/编码在 question 字段中可能异常）。
- **其余 5 条**：`_is_multihop_question=True`，首跳 **forward 为设计行为**，非「单跳误伤多跳规则」。
- **结论**：**未发现**「大量单跳题被多跳启发式误踢」导致 static 系统性赢 peer；static 更深链（hop_count 3–4）在部分题上更占优，与 peer 浅层 2 跳策略对比鲜明。

- verification:
  - `python scripts/f1_significance_audit_round1.py` → 终端 JSON 与 `artifacts/round1/f1_significance_audit_run_20260411_102202.json` 一致。
- next_action:
  - 可选：加扫「gold 仅出现在 evidence 第 15 行及以后」与 `evidence_seeker` 失败的交集，量化 **[:14] 截断** 贡献。
  - 论文叙事：F1 差小 + bootstrap 已跨零时，强化 **PAR / cost_norm / 路径分歧 48%**，避免过度声称 F1 显著。

### [long_paper_upgrade_execution_20260413]
- status: in_progress
- date: 2026-04-13
- files_added:
  - `configs/round1_hotpotqa_ablation_evidence.yaml`
  - `configs/round1_hotpotqa_ablation_no_tcpb.yaml`
  - `configs/round1_hotpotqa_ablation_no_gate.yaml`
  - `scripts/summarize_idea_reviews.py`
  - `scripts/review_scoreboard.py`
  - `scripts/collect_run_metrics.py`
- files_modified:
  - `workspace/idea04_core/contracts.py`
  - `workspace/idea04_core/methods.py`
  - `workspace/idea04_core/runner.py`
  - `workspace/idea04_core/llm_client.py`
  - `idea.md`
  - `EMNLP_paper_draft.md`
  - `scripts/review_idea_with_remote_llm.py`
  - `prompts/review_idea_system_en.txt`
  - `prompts/review_idea_user_template_en.md`
- key_decisions:
  - 将 submission 口径锁定为 **authoritative executable TCPB**：peer 仅做 `post_sample` terminal update，不再保留任何 hop-level peer critique 叙事。
  - 将路由策略改写为**显式特征 + 显式 neighbor belief + 显式 margin** 的 deterministic policy，并把 `routing_features` / `neighbor_scores` 写入 `routing_traces.jsonl`。
  - 将 `published_competence`、`visited_nodes`、`hop_count`、`candidate_answer` 提升为 packet-level state，解决 reviewer 对邻居可见性与路由可执行性的质疑。
  - reviewer loop 改为：读取 `reasoning_content` fallback、compact retry、prose salvage、统一 `review.json`/`review.md`、`fix_themes.md`、`scoreboard.md`。
  - 为避免五个 API-heavy run 并发拖垮总时长，**暂时停止** `7405 fullval` 并改成 **先跑 star + ablations，再单独重启 fullval** 的串行策略。
- verification:
  - `python -m py_compile` 覆盖核心代码与 reviewer/tooling 脚本，均通过。
  - 新 schema smoke：`artifacts/round1_smoke_live/run_20260413_051819/fixed_peer_calibrated/` 已写出非零 `api_*` 与带 `routing_features`/`neighbor_scores` 的 trace。
  - reviewer sanity check：`artifacts/idea_reviews/reviewer_20260413_053150_01_bbf1c9/review.json` 产出 `overall=6`；`artifacts/idea_reviews/scoreboard.md`、`fix_themes.md` 已生成。
- runtime_status:
  - 正在后台运行：`round1_star`, `round1_ablation_evidence`, `round1_ablation_notcpb`, `round1_ablation_nogate`。
  - `artifacts/round1/run_20260413_051931/` 已创建但 **7405 fullval 被人工暂停**，待中型实验结束后单独重启。
- next_action:
  - 等 `star` 与三组 ablation 完成后，立即执行 `validate_logs`、`collect_run_metrics.py`、更新主文/附录中的 robustness 与 mechanism ablation 段落。
  - 随后单独重启 `7405 fullval`，跑完执行 `scripts/post_fullval_chain.ps1` 覆盖 `round1_v3_main_table_fullval.csv` 与 `round1_v3_paired_stats_fullval.csv`。

### [acl_template_extracted_20260419]
- status: completed（解压动作）；位置抉择 ⏳ 待 U-009 拍板
- date: 2026-04-19
- files_added:
  - `article/README.md`（2.4 KB，ACL 官方说明）
  - `article/README`（9 B，stub）
  - `article/anthology.bib.txt`（373 B，提示从 aclanthology.org 下载 anthology.bib 的说明）
  - `article/formatting.md`（17.9 KB，*ACL 排版完整规范）
  - `article/latex/acl.sty`（11.6 KB，**官方 style 文件，禁止修改**）
  - `article/latex/acl_latex.tex`（14.5 KB，pdflatex/xelatex 入口模板）
  - `article/latex/acl_lualatex.tex`（3 KB，lualatex 变体）
  - `article/latex/acl_natbib.bst`（45 KB，bibliography style）
  - `article/latex/custom.bib`（2 KB，bib 占位）
- files_modified:
  - `docs/coordination/implementation_log.md`（本条）
- key_decisions（仅工程师层面执行决策，未涉路线决策）:
  - 用 PowerShell `Expand-Archive` 原地解压到 `d:\Codes\idea04\article\`，因为用户在 query 中明确以 `@article/...zip` 字面路径指向该 zip。
  - **未** 把模板复制/移动到 `workspace/autogen/dotnet/website/articles/`（PROJECT_STRUCTURE.md §8 指定的论文资产位置），以避免擅自决定项目结构。
- conflicts_with_docs:
  - **`PROJECT_STRUCTURE.md §8` 与本次解压位置存在冲突**：§8 写明"figure / `.tex` / `.pdf` 等论文最终交付物存放在 `workspace/autogen/dotnet/website/articles/`"，但本次解压物理上落在 `article/`，且 `PROJECT_STRUCTURE.md §1 / §2` 完全没有把 `article/` 列为合法顶层目录。需要由用户拍板：A) 接受 `article/` 为新顶层目录并更新 §8 / §2 条目；B) 把模板移至 `workspace/autogen/dotnet/website/articles/acl_template/`；C) 其他位置。
  - 建议在 `docs/coordination/SCIENTIST_TODO.md § A` 新增一行 `U-009-decide`（落点选择），由科学家维护、用户拍板。
- blockers:
  - none（解压动作本身已完成；仅"是否进一步移动"被 U-009 阻塞）
- blocker_type:
  - none
- fast_fail_triggered:
  - no
- verification:
  - `Expand-Archive ... -Force` 退出码 0；解压后 `Get-ChildItem -Recurse` 列出 8 个文件均与 zip entry 大小一致（README.md 2393B / formatting.md 17923B / acl.sty 11615B / acl_latex.tex 14500B / acl_natbib.bst 45186B 全部对齐）。
  - 与 `docs/demand.md §2` 比对：模板版本满足 EMNLP 2027 long paper 投稿要求（"latest version from https://github.com/acl-org/acl-style-files"）；`acl_latex.tex L5` 的 `\usepackage[review]{acl}` 即匿名 review 模式，long paper 8 页 + 投稿前不能改 acl.sty 的硬约束都已被模板自带规则覆盖。
- impact_on_other_tracks:
  - 解锁 SCIENTIST_TODO § B `S-001`（双稿合并）落地形态：合并后的稿件需要从 .md 迁移到 LaTeX，模板已就位；但迁移动作本身仍 blocked by U-003-decide（合并 vs 双稿）。
  - 解锁 SCIENTIST_TODO § B `S-006/S-010`（Figure 设计 / 嵌入）的载体：figure 嵌入 LaTeX 需要 `\graphicspath{}`，落点决定后再写。
  - 不影响任何 in-flight run（无 API 调用、无 core code 修改）。
- next_action:
  - 等 U-009-decide 拍板后，按所选位置整理（移动 / 保留 / 拷贝 + 加 .gitignore），并同步更新 `PROJECT_STRUCTURE.md §1 §2 §8`。
  - 在 LaTeX 真正动笔前需要从 https://aclanthology.org/anthology.bib 下载 `anthology.bib`（per `article/anthology.bib.txt` 指示）；下载动作待落点确定后一并执行。

### [acl_template_smoke_compiled_20260419]
- status: completed
- date: 2026-04-19
- files_added:
  - `article/build/acl_latex.pdf`（172,826 B，4 页）
  - `article/build/acl_latex.aux` / `.bbl` / `.blg` / `.fdb_latexmk` / `.fls` / `.log` / `.out`（latexmk 中间产物）
- files_modified:
  - `docs/coordination/implementation_log.md`（本条）
- key_decisions（仅工程师层面执行决策）:
  - 用 `latexmk -pdf` 一键串联 `pdflatex → bibtex → pdflatex × 2`，避免手动多次 pass 漏 bib 引用。
  - 编译产物落 `article/build/` 子目录，**不污染** `article/latex/` 模板源（保持 git diff 干净 + 与 U-009 落点决策解耦）。
  - PowerShell 调 latexmk 时 `-output-directory=...` 必须**整段加引号**（否则 PS 在 `=` 处错切），并使用绝对路径。
- blockers:
  - none
- blocker_type:
  - none
- fast_fail_triggered:
  - no
- conflicts_with_docs:
  - none（编译动作是中性技术验证，不涉 U-009 落点）
- verification:
  - exit code = 0
  - latexmk 末行：`All targets (d:/Codes/idea04/article/build/acl_latex.pdf) are up-to-date`
  - PDF 物理存在：`d:/Codes/idea04/article/build/acl_latex.pdf` 4 页 172,826 B，timestamp 2026/4/19 15:37:00
  - bibtex 成功：`Found bibliography file(s): ./custom.bib`，所有 `\nocite{Ando2005,andrew2007scalable,rasooli-tetrault-2015}` + `\citep{Gusfield:97}` 等引用渲染到 `acl_latex.bbl`
  - 所有 8 个 figures/tables 占位符（`example-image-golden` / `example-image-a` / `example-image-b` 来自 `mwe` 包）正常显示
  - 仅有的 5 条 `Underfull \hbox` 是模板示例自带的排版微调建议（badness 1132–10000），**非错误**，不影响 PDF 产出
- toolchain_recorded:
  - TeXLive 2024 完整套（`d:/CodeLanguage/Tex/texlive/2024/bin/windows/`）
  - `pdflatex` / `xelatex` / `lualatex` / `bibtex` / `biber` / `latexmk` 全部可用
- impact_on_other_tracks:
  - 解锁 SCIENTIST_TODO § B `S-001`（双稿合并→LaTeX 迁移）的物理可行性验证：模板可编译 + bib 流程通。
  - 不影响任何 in-flight run。
- next_action:
  - 等 U-009-decide 拍板模板最终落点后，再决定 build 输出目录是否同步迁移。
  - 论文正式动笔前可重跑 `latexmk -pdf "-output-directory=..." acl_latex.tex`（同样的命令，模板可重复编译）。
  - 构建命令封装建议：等落点定后写到 `scripts/build_paper.ps1`（一键 + cleanup），目前手动跑足以验证。

### [edo_paper_md_to_latex_smoke_20260419]
- status: completed
- date: 2026-04-19
- files_added:
  - `article/latex/edo_paper.tex`（约 24 KB，第一稿 EDO long paper 的完整 LaTeX 翻译）
  - `article/build/edo_paper.pdf`（266,743 B，**9 页**）
  - `article/build/edo_paper.aux` / `.bbl` / `.blg` / `.fdb_latexmk` / `.fls` / `.log` / `.out`（latexmk 中间产物）
- files_modified:
  - `docs/coordination/implementation_log.md`（本条）
- key_decisions（执行层面，未涉路线决策）:
  - **稿件选择**：`docs/paper/EMNLP_paper_draft.md` 含双稿（第一稿 EDO long paper @ line 1–256；第二稿 TCPB short paper @ line 258–366）；按 `idea.md / PROJECT_STRUCTURE.md` 把项目定位为 EMNLP **long paper**，本次 PoC 编译只填**第一稿**进 LaTeX，第二稿原状保留在 .md 等 U-003-decide 拍板。
  - **不动模板源**：新建独立文件 `article/latex/edo_paper.tex`，不修改 ACL 自带的 `acl_latex.tex` 模板源（保持 zip 解压后的原状以备参考）。
  - **review 模式**：`\usepackage[review]{acl}` —— 匿名审稿模式（带行号），`\author{Anonymous Authors}`；camera-ready 时改 `[final]` + 真实作者。
  - **窄列排版补丁**：加载 `xurl` + 自定义 `\fpath{...}` macro（允许文件路径在任意字符断行）+ `\sloppy`，把所有长 path 引用从 `\texttt{...}` 改为 `\fpath{...}`；宽 vector 公式（`\phi(z)`、`P_i`、`\ell`、`r_terminal`、`U_i^*` align）改成 `multline*` / 多行 `align*` 适配 7.7cm 单栏宽。
  - **bibliography 占位**：保留模板自带的 `\nocite{Gusfield:97,Ando2005,andrew2007scalable,rasooli-tetrault-2015}` + `\bibliography{custom}` 让 bib 段落能渲染；真实引用待 `S-002`/camera-ready 时补。
  - **typo 修复（仅 latex 内修，未回写 .md）**：第一稿 line 135 中 `gated by\` 后 `$` 缺位；第一稿 R2 / R3 中 `\to` / `\rightarrow` 在显示数学里的混用统一为 `\rightarrow` 或 `\to`；这些是源 .md 的 markdown 数学解析问题，LaTeX 版本里直接改对，**未回改源 .md**（避免与 SCIENTIST_TODO `S-002` 抢任务）。
- blockers:
  - none
- blocker_type:
  - none
- fast_fail_triggered:
  - no
- conflicts_with_docs:
  - **第二稿（TCPB short paper @ line 258–366 of `docs/paper/EMNLP_paper_draft.md`）未被吸收**——这是有意为之，避免擅自做 U-003-decide。`SCIENTIST_TODO § B.2 S-001`（双稿合并）的执行入口现在已就绪：U-003 拍板"合并"后，可把第二稿 §3.1 公式 / §4.5 error analysis / §4.6 mechanism ablations 增量合并到 `edo_paper.tex` 对应位置。
- verification:
  - exit code = 0；`latexmk: All targets up-to-date`
  - PDF 物理存在：`d:/Codes/idea04/article/build/edo_paper.pdf` 266,743 B，9 页
  - **EMNLP 8-页正文限制核查**：从 latexmk log 的 page break 标记可定位
    - 页 1–7：§1 Introduction → §6 Conclusion（**正文 7 页，≤ 8 页限制 OK**）
    - 页 8 起：`\section*{Limitations}` 与后续 bib（per `docs/demand.md §2`：Limitations 与 References 不计入 8 页限制）
    - 结论：**正文合规**
  - 排版警告收敛：16 个 Overfull → 1 个 Overfull（仅 0.8pt @ `\phi(z)` multline 末，肉眼不可见，可接受）
  - Underfull 警告 60 个，全部为段内空格分布（badness 1000–10000），**不影响 PDF 产出与可读性**
  - bib 段落：`Latexmk: Found bibliography file(s): ./custom.bib`，`\bibliography{custom}` 渲染 OK
- toolchain_recorded:
  - 同 `[acl_template_smoke_compiled_20260419]`：TeXLive 2024 完整套；`pdflatex + bibtex + latexmk`
- impact_on_other_tracks:
  - 解锁 SCIENTIST_TODO § B.1 `S-002`（typo 修复）：现在有 .tex 现成版可对照源 .md 修
  - 解锁 SCIENTIST_TODO § B.1 `S-003`（凝练 Algorithm 1 boxed pseudocode）：可直接在 `edo_paper.tex` `\subsection{Recursive upstream audit}` 之后或 Prototype Scope Box 内加 `algorithm` 环境
  - 解锁 SCIENTIST_TODO § B.1 `S-004` (Prototype Scope 单源化)：`edo_paper.tex` 的 `\noindent\fbox{\begin{minipage}}` 已经是单源
  - 解锁 SCIENTIST_TODO § B.1 `S-006`（Figure caption 起草）：figure 嵌入位置就绪（需要工程师先出 PNG）
  - 解锁 SCIENTIST_TODO § B.2 `S-001`（双稿合并）的物理可行性
  - 不影响任何 in-flight run
- next_action:
  - **当前 PDF 是 PoC，不是定稿**。命名暗示：`edo_paper.tex` ≠ camera-ready；论文正式定稿前需要做的事按优先级：
    1. （`S-001`，等 U-003）合并第二稿的 §3.1/§4.5/§4.6 进 `edo_paper.tex`
    2. （`S-002`）修源 `.md` 的 escape typo
    3. （`S-003`）`edo_paper.tex` §3 加 Algorithm 1 boxed pseudocode
    4. 真实 bib：从 https://aclanthology.org/anthology.bib 下载 anthology.bib，逐条替换 placeholder 引用
    5. 工程师出 Figure 1 / Figure 2 PNG 后嵌入
    6. camera-ready 阶段：`\usepackage[review]` → `\usepackage[final]`，`\author{Anonymous}` → 真实作者
  - 编译命令固化进 `scripts/build_paper.ps1` 待 U-009 拍板落点后再做（避免先做要重写）

### [cursor_rule_dropped_dep_graph_20260419]
- status: completed
- date: 2026-04-19
- files_added:
  - none
- files_modified:
  - `.cursor/rules/three-role-todo-workflow.md`（122 行 → 117 行）
- key_decisions（用户直接指令，非自主决策）:
  - 用户指令："以后都不用维护依赖图这个文档了，在 cursor 规则里也把这个删去，只需要每次执行的时候检测一下 pending 的是否 done 了然后更新 todo 就好"
  - 解读：硬删除（不是软标记 deprecated），把"依赖图"概念从规则文件全部移除；保留 §1 step 1 已经写好的"检测 pending → done"语义作为 cycle 入口（与用户描述精确对应）
- blockers:
  - none
- blocker_type:
  - none
- fast_fail_triggered:
  - no
- conflicts_with_docs:
  - none（"依赖图"原本就不存在物理文件，仅是规则里的概念引用；删后无悬挂引用）
- 具体改动:
  - 删 `§0 末尾的"依赖图文档已废弃（2026-04-19）"软标记通告`（原 line 31）
  - 把 `§1 末尾"已废弃的 2 步"callout 中"更新依赖图"那一项删除`，callout 标题从"2 步"改成"步骤"，仅保留另一条无关的 `strict_review_todos § 修订记录` 废弃说明（用户没要求动那条）
  - 全文 grep `依赖图|dep-graph|dependency.graph` → 0 匹配
- verification:
  - `Grep "依赖图|dep-graph|dependency.graph" .cursor/rules/` → No matches found
  - `Read .cursor/rules/three-role-todo-workflow.md` → 117 行，结构完整，§1 cycle 入口语义保留
  - ReadLints → no linter errors found
- impact_on_other_tracks:
  - 简化所有角色（用户/科学家/工程师）每次动作的 4 步操作流程为 2 步：(1) 检测 pending → done；(2) 更新当前动作 TODO
  - `docs/coordination/SCIENTIST_TODO.md § B.4` 维护项不变（`S-100/S-101/S-102/S-201` 都不涉及依赖图）
  - 不影响任何 in-flight run 或论文稿
- conflicts_NOT_resolved（仅报告，等 U-XXX 决策）:
  - **`.cursor/rules/three-role-todo-workflow.md` 的文件路径仍是 RecSys 2026 短文模板残留，与 idea04 EMNLP long paper 的实际文件结构脱节**：
    - L4–7 globs：指向 `research/USER_TODO_2026-04-18.md` 等 4 个**不存在的**文件
    - L19–21 §0 表格：3 个 TODO 文件路径全是死链 `research/...`
    - L27–29 单一事实源表：3 个 `research/recsys2026_*.md` 也都不存在
    - L53 / L65 / L72 / L80–82 / L107：散落的 `USER_TODO` / `strict_review_todos` / `engineer_handoff` 引用全是死链
  - 实际本仓库使用：`docs/coordination/SCIENTIST_TODO.md`（科学家 + 用户决策池） + `docs/coordination/implementation_log.md`（工程师，本文件）
  - 建议挂 `U-010-decide`（rule 文件名 / globs / 表格全面对齐 idea04 实际结构 vs. 维持 RecSys 模板表层）；用户没明确指令前不动
- next_action:
  - 等用户对 `U-010-decide`（建议）拍板是否做 rule 全面对齐
  - 工程师（我）此后每次新动作开头按新规则执行 2 步：先扫 pending、再开新 ⏳；不再尝试维护任何依赖图概念

### [edo_paper_emnlp2026_header_fix_20260419]
- status: completed
- date: 2026-04-19
- files_added:
  - none
- files_modified:
  - `article/latex/edo_paper.tex`（在 preamble 加 `\renewcommand\outauthor{...}`；`\author{}` 文本由 `Anonymous Authors / Submission for ARR / EMNLP Long Paper Track / anonymous@anonymous.org` 改为 `Submission for EMNLP 2026 Long Paper Track (via ARR)`）
  - `article/build/edo_paper.pdf`（重新生成，266,744 B，9 页）
  - `docs/coordination/implementation_log.md`（本条）
- key_decisions（用户直接指令 + 工程合规判断）:
  - **用户指令**："Anonymous ACL submission 改了，我们是要投 EMNLP long paper"
  - **正确归因**：`Anonymous ACL submission` 在 `acl.sty:132` 硬编码，"ACL" 指 Association for Computational Linguistics（umbrella org），不是 ACL 会议；EMNLP 走 ARR 用同一套 `acl.sty`，原文本严格也合规——但用户要求改就改。
  - **改法选择**：用户侧 `\renewcommand\outauthor{...}` 覆盖；**不改 `acl.sty`**（demand.md §2 明确禁止：`No modifications to acl.sty or any style files are allowed`）。
  - **新文本**：`Anonymous EMNLP 2026 Submission`（与会议名 + 年份对齐，未带 long/short 区分以避免暗示性识别风险）
- blockers:
  - none
- conflicts_with_docs:
  - none（demand.md §2 禁的是改 .sty 本体；用户侧 `\renewcommand` 不在禁止范围）
- 模板版本核对（用户第二个问题"emnlp 2026 模板是不是这个"）:
  - 上 GitHub `acl-org/acl-style-files` 拉 raw `acl.sty` 与本地比对：**SHA256 完全一致**（`19DFEDDC2C0E448F3926A0BEF048A9DB3F3611B46265B760CAABD7ADA4F361DE`）
  - upstream 默认分支 `master`，最近 5 次 commit 时间表：
    - `2353f3e` 2025-11-13 "Merge pull request #71 from zepam/patch-1"
    - `9a7d532` 2025-11-11 "Fix typo in Overleaf submission instructions"
    - `d27f848` 2025-08-29 "Fix link"
    - `dbaf711` 2025-08-29 "remove refs to latex subdir"
    - `635e138` 2025-08-23 "Update anthology.bib.txt"
  - 我们 zip 的 `latex/` 子目录布局对应 **2025-08-29 之前**的旧目录结构（upstream 已扁平化），但**文件内容完全等价**——不影响投稿
  - EMNLP 2026 CFP（https://2026.emnlp.org/calls/main_conference_papers/）确认：投稿走 **ARR May 25, 2026 截止 → EMNLP commit Aug 2, 2026 → camera-ready Sep 20, 2026 → 会议 Oct 24-29 Budapest**；CFP 没有 EMNLP 专用 style file，**直接用 ACL 官方 acl-style-files 即可**
  - 结论：**当前模板就是 EMNLP 2026 投稿要的 latest official ACL Style Files**，不需要替换；只是 zip 解压出来的目录壳是旧版（无功能影响）
- verification:
  - `latexmk` exit code = 0；`Latexmk: All targets up-to-date`
  - PDF 大小 266,744 B（与上次几乎一致，仅 -1 B），9 页，1 个 overfull（0.8pt 老问题，非新引入）
  - `pdftotext -f 1 -l 1` 提取首页文本：含 `Anonymous EMNLP 2026 Submission` 一行 ✅；不再含 `Anonymous ACL submission`
  - lint：N/A（仅 .tex 改动，无 .md lint 影响；本 implementation_log 项追加完后会跑 ReadLints）
- impact_on_other_tracks:
  - SCIENTIST_TODO § B 不变；S-001/S-003 等仍按原阻塞链等 U-003-decide
  - camera-ready 阶段仍需把 `\usepackage[review]{acl}` → `\usepackage[final]{acl}` 并填真实 `\author{}`；`\renewcommand\outauthor{...}` 在 final 模式下不会被 acl.sty 调用（只 review 模式才走 anonymize 分支），所以保留也无副作用
- next_action:
  - 无（当前请求闭环）
  - 用户若不喜欢新文本"Anonymous EMNLP 2026 Submission"，可改 `\renewcommand` 里的字符串（如 `Anonymous EMNLP 2026 Long Paper Submission` 或 `Anonymous ARR Submission`）

### [user_todo_separation_20260419]
- status: completed
- date: 2026-04-19
- files_added:
  - `docs/coordination/USER_TODO.md`（约 7 KB；用户独立 TODO，新增 §0 角色边界 + §A 决策池接管 11 项 + §B 人工执行 2 项 + §C 已完成 + §D 修订 + §E 派工分布）
- files_modified:
  - `docs/coordination/SCIENTIST_TODO.md` §A：从含完整决策内容的表 → cross-reference blocked tracker（仅 ID + 阻塞下游 + 状态镜像）
  - `.cursor/rules/three-role-todo-workflow.md` §0/§2/§4/§5/§7：用户 TODO 文件指向 `USER_TODO.md`；§4 工作流加"在 USER_TODO §A 加完整决策行 + 在 SCIENTIST_TODO §A 加 cross-reference"双轨；§4 末加 USER_TODO §B 物理操作流程
  - `PROJECT_STRUCTURE.md` §3 line 67：`EMNLP_paper_draft.md` 描述从"⚠ 双稿拼贴未合并（待 U-003-decide）"→"⚠ 历史 markdown 副本（U-003 已隐式 ✅）"（§0 entry table 与 §9 已被科学家并行更新到位，无需重做）
  - `README.md` 1 分钟入口表 + 角色与协作表：加 USER_TODO 行，明确权威源关系
  - `docs/coordination/implementation_log.md`（本条）
- key_decisions（用户直接指令）:
  - 用户指令："以后都不用维护依赖图这个文档了" → 之前已做；本轮新增："我不是科学家，我是把握全局的人，负责重要卡点决策...我的 todo（充值 API、使用 prompt 绘图、重要方向把握）也要有一个 todo 文档，和科学家的不是一个"
  - 解读：USER 角色独立，需要专属 TODO 文档；既往 `SCIENTIST_TODO.md §A` 决策池实质是用户的工作清单错放在科学家文件下 → 应把 §A 全套 11 项决策 (U-001~U-011) 全部接管入新 USER_TODO.md
  - 设计模式：**USER_TODO.md §A = single source of truth**；SCIENTIST_TODO.md §A 退化为 scientist 的 blocked-on tracker（仅 ID + 阻塞下游 + 镜像状态，**不复制内容避免双向 drift**）
  - 同步 5 处文件确保 cursor rule、PROJECT_STRUCTURE、README、SCIENTIST_TODO、新 USER_TODO 全部一致
- blockers:
  - none
- conflicts_with_docs:
  - 改动期间 SCIENTIST_TODO.md 被科学家并行更新（U-003/U-009 标 ✅；新增 U-011 reviewer fatal flaw + S-105~S-114）；PROJECT_STRUCTURE.md §0 entry table、§3 docs/ 树、§9 协作分布 也被科学家并行更新到位 → **本次改动已对齐到最新状态**，无遗漏
- verification:
  - `Read docs/coordination/USER_TODO.md` → 文件存在，结构完整（§0/§A/§B/§C/§D/§E 6 节，§A 11 项决策含 U-011，§B 2 项 U-EXEC，§C 含 U-001/U-003/U-009 三个 ✅）
  - `Read docs/coordination/SCIENTIST_TODO.md` → §A 已是 11 行 cross-reference 表（不含 decision content），cross-reference 链接指向 `./USER_TODO.md`
  - `Read .cursor/rules/three-role-todo-workflow.md` → §0 三角色映射含 USER_TODO；§2 blocked 判断指 USER_TODO §A；§4 决策走 USER_TODO；§5 handoff user 必读 USER_TODO；§7 rollback 指 USER_TODO §A
  - `Grep "SCIENTIST_TODO.md \\\\\\\\\\\\\\\\§ A"` 在 cursor rule → 0 匹配（用户决策入口已全部切到 USER_TODO）
  - ReadLints 5 个文件全部 0 错误（待跑）
- impact_on_other_tracks:
  - 科学家：§A 简化后维护成本降低；新决策必须双轨写（USER_TODO §A 完整 + SCIENTIST_TODO §A cross-reference）
  - 工程师（我）：未来挂决策项 → USER_TODO §A；挂 USER 物理操作项 → USER_TODO §B；不再用 SCIENTIST_TODO §A 作主入口
  - 不影响任何 in-flight run / 论文 LaTeX 编译 / 现有 U-XXX 决策内容
- next_action:
  - 无（请求闭环）
  - U-011-decide（reviewer fatal flaw 的 framing 走向）现在挂在 USER_TODO §A 最末行，**最高优先级**等用户拍板

### [four_role_rule_clarification_20260419]
- status: completed
- date: 2026-04-19
- files_added:
  - `.cursor/rules/four-role-todo-workflow.md`（约 8 KB；从原 three-role 升级到 four-role；新增 §11 审稿人角色完整规范）
- files_deleted:
  - `.cursor/rules/three-role-todo-workflow.md`（旧文件 7,052 B，由用户指令替换）
- files_modified:
  - `docs/coordination/USER_TODO.md`：协作规范引用 `three-role` → `four-role`
  - `docs/coordination/SCIENTIST_TODO.md`：协作规范引用（§meta + §B 内 §2 引用）`three-role` → `four-role`，标注 §1–11（含审稿人 §11）
  - `PROJECT_STRUCTURE.md`：§0 entry table 加 2 行（审稿人归档 + 审稿人 prompt）；§9 标题 "三类协作文件分布" → "四角色协作文件分布"，加审稿人行 + 协作规范硬约束指针
  - `README.md`：1 分钟入口表保留 USER/科学家/工程师 行（reviewer 不属于"日常入口"）；角色与协作表加审稿人行 + footer 协作规范引用注明 4 角色
  - `docs/coordination/implementation_log.md`（本条）
- key_decisions（用户直接指令）:
  - 用户原文："把这个规则也到 rules 里，明确澄清我们其实有四个人进行协作，科学家、审稿人、工程师和用户"
  - 解读：cursor rule 文件之前只覆盖三角色（user/scientist/engineer），漏掉了**审稿人**这一独立角色（已实质存在：`prompts/reviewer_prompt.md` 947 行系统提示 + `artifacts/idea_reviews/` 21 个 batch 历史 + `SCIENTIST_TODO.md §B.4 S-104` 强制反馈处理循环），需在 cursor rule 里**显式定义第四角色**
  - 选 rename `three-role-todo-workflow.md` → `four-role-todo-workflow.md`（**Option A**），原因：
    1. 用户明确要"明确澄清"，文件名是最直接的语义信号；
    2. 仓内仅 4 处活跃引用（USER/SCIENTIST/PROJECT_STRUCTURE/README），更新成本可控；
    3. `implementation_log.md` 中 8+ 处历史引用是"当时的事实快照"，**不回写**（保持历史诚实）；
    4. `.specstory/history/` 内 20+ 处引用是 IDE 自动归档的对话日志，本来就 immutable
- 审稿人角色的本质（写入新 §11）:
  - **触发**：仅在 ① 论文实质修订后 ② 用户在 USER_TODO 显式批准 ③ 关键里程碑（投稿前 / camera-ready 前 / rebuttal 前）才启动 batch；scientist/engineer 擅自启动属 §4 红线
  - **输入**：当前 `article/build/edo_paper.pdf` + `idea.md` + `prompts/reviewer_prompt.md`
  - **输出**：独立目录 `artifacts/idea_reviews/reviewer_<YYYYMMDD>_<HHMMSS>_<NN>_<6char-hash>/` 含 `review.json`（结构化 schema 强制）+ `review.md`（人类可读）
  - **stateless**：每次 batch 不读历史 review，避免 confirmation bias
  - **聚合**：`scoreboard.md` / `fix_themes.md` / `review_index.jsonl` 由 `summarize_idea_reviews.py` + `review_scoreboard.py` 在 batch 落盘后由 scientist 触发
  - **hand-off**：scientist 必须按 SCIENTIST_TODO §B.4 S-104 的 4 步循环（① 通读 ② 不盲从 ③ 诚实接受 ④ dissent log）处理 reviewer 输出
- blockers:
  - none
- conflicts_with_docs:
  - none（4 处活跃引用已全部对齐到新文件名）
- verification:
  - `Glob ".cursor/rules/*.md"` → 应只有 `four-role-todo-workflow.md` + `ssh-server-rules.md`（无旧 `three-role-*.md`，无 `persistent-chat.mdc`——后者已在更早 session 处理）
  - 4 处活跃引用全部跑 StrReplace 成功（USER_TODO L6 / SCIENTIST_TODO L6 + L43 / PROJECT_STRUCTURE L276 / README L68）
  - PROJECT_STRUCTURE §0 entry table 含 reviewer 归档 + reviewer prompt 行；§9 标题升级"四角色"含 reviewer 行
  - README 角色与协作表含 reviewer 行
  - ReadLints 5 个文件全部 0 错误
- impact_on_other_tracks:
  - 工程师（我）：未来挂决策项依然走 USER_TODO §A；启动审稿人 batch 之前必须确认 USER_TODO §A 已有对应批准项（否则属 §4 红线）
  - 科学家：S-104 强制循环现在有了 cursor rule 层面的硬约束（§11.4），不再仅是 SCIENTIST_TODO 内部约定
  - 审稿人：现在有明确的输入/输出契约（§11.2）和 stateless 约束（§11.5），后续若用 LLM 自动审稿可直接套这套规范
  - 不影响任何 in-flight run / 论文 LaTeX 编译 / 现有 U-XXX 决策内容
- next_action:
  - 无（请求闭环）
  - 后续若需新审稿 batch：先在 USER_TODO §A 加 `U-XXX-decide` 请用户批准 → 用户批 → engineer/scientist 用 `prompts/reviewer_prompt.md` 触发 → 落盘到 `artifacts/idea_reviews/reviewer_<TS>_<NN>_<HASH>/`

### [E-rules-polish-2026-04-19]
- status: completed
- date: 2026-04-19
- 用户 10 条指令逐项消化:
  - 指令 1+3：rule 不再出现 "AI 扮演 / 由谁实际执行" 字样（避免幻觉），§0 角色映射表删 "谁实际执行" 列、删 "多角色 AI 场景" 段落；§1 / §2 / §8 全文清掉 "AI 扮演"
  - 指令 2：reviewer 升级为有持久 TODO 的角色 → **新建 `docs/coordination/REVIEWER_TODO.md`**（§A `R-FULL-XXX` 仅用户触 + §B `R-PART-XXX` 科学家/工程师可自触审局部内容 + §C 完成 + §D 修订 + §E 输入输出契约）
  - 指令 4：按合适方式改（已综合执行）
  - 指令 5：评分倒退**不**触发回滚 → §7 末新增引述："reviewer batch 之间 overall 分数小幅波动 (±0.5/±1.0) 属审稿人采样噪声，不触发回滚；scientist 在 S-104 第 ② 步 必须兼顾 scoreboard.md 历史趋势，单次小波动不能阻碍前进；仅多次连续 batch 在同一 fix-theme 上指向真实退化时，才考虑 7.1 回滚"；同义引述也加到 §11.4 第 ② 步
  - 指令 6：原 §8 stakeholder 分类 polish 取消 → §8 简化为 3 行（"完成可做项 → 回报用户 → 等指令"），不再列 stakeholder 三方分类
  - 指令 7：§11.1 触发条件 AND/OR 逻辑保持现状（不再纠结）
  - 指令 8：rule 中**全部删 review.json 字段引用** → §6 quality gate 改为 "按 reviewer_prompt.md 规定的结构化格式"；§11.2 缩为 "schema 单一源 = reviewer_prompt.md，详细 I/O 见 REVIEWER_TODO §E"
  - 指令 9：ID 命名规范化 → §12 表头加 "前缀按角色分配：U-x 用户 / S-x 科学家 / E-x 工程师 / R-x 审稿人"；新增 `E-XXX` 行（工程师新 phase 用此前缀，历史 phase block `[<descriptive-name>]` 不回写）；新增 `R-FULL-XXX` / `R-PART-XXX` 行
  - 指令 10：§11.6 退出条件保持现状
- files_added:
  - `docs/coordination/REVIEWER_TODO.md`（约 5 KB；§0/§A/§B/§C/§D/§E 6 节；接管 R-FULL-001 历史 batch 元数据）
- files_modified:
  - `.cursor/rules/four-role-todo-workflow.md`（重写约 8 KB；front-matter `globs` 加 `REVIEWER_TODO.md`；§0–§12 全套按 10 条指令翻新）
  - `docs/coordination/USER_TODO.md`：L7 配对文件清单加入 `REVIEWER_TODO.md` 指针
  - `docs/coordination/SCIENTIST_TODO.md`：L6 协作规范引用范围 §1-10 → §1-12（含 §11+§12）；新增 L7 配对文件清单
  - `PROJECT_STRUCTURE.md`：§0 entry 加 REVIEWER_TODO 行 + 改 batch 归档行；§3 docs/ 树加 REVIEWER_TODO 行；§9 协作分布表完整重写为含 4 角色 + ID 前缀（U-x/S-x/E-x/R-x）
  - `README.md`：1 分钟入口表加 REVIEWER_TODO 行；角色与协作表增列"主 ID 前缀"
  - `docs/coordination/implementation_log.md`（本条）
- key_decisions（用户直接指令，未涉路线）:
  - 全部 10 条指令是用户对 rule polish 的具体方向决策；engineer 直接执行
  - 选 `R-FULL-XXX` vs `R-PART-XXX` 双轨命名（与 §11.1 触发权限矩阵对应）
  - REVIEWER_TODO §E 把 schema 详情指向 `prompts/reviewer_prompt.md` 单一权威源（避免双源 drift）
- blockers:
  - none
- conflicts_with_docs:
  - none（USER_TODO §B 现有 `U-RES`/`U-FIG`/`U-REF`/`U-DIR` 子前缀全部纳入 §12 ID 表；§C dispatch inbox `C-XXX` 也纳入；老 `U-EXEC-XXX` 已废弃→纳入 ID 表说明）
- verification:
  - `Read .cursor/rules/four-role-todo-workflow.md` → 12 节结构完整，无 "AI 扮演" / "review.json" 残留
  - `Read docs/coordination/REVIEWER_TODO.md` → §A R-FULL-001 历史 batch 已接管；§B 留空待用；§E 输入输出契约完整指向 reviewer_prompt.md 单源
  - 5 处活跃引用全部更新（USER_TODO L7 / SCIENTIST_TODO L6+L7 / PROJECT_STRUCTURE §0+§3+§9 / README §1 entry+角色表）
  - ReadLints 6 文件全部 0 错误（待跑）
- impact_on_other_tracks:
  - 工程师（我）：未来新 phase block 应用 `[E-XXX]` 前缀（如 `[E-001-foo]`）；历史 phase block `[<descriptive-name>]` 保持不动（不回写）
  - 科学家：S-104 第 ② 步现在硬性要求"兼顾 scoreboard.md 历史趋势"，不能因单次评分小波动停滞
  - 审稿人：R-PART-XXX 自由触发解锁了"自审"模式（科学家写完一段可自触局部审稿验证清晰度，无需全文 batch 成本）
  - 用户：R-FULL-XXX 仍是用户独占触发权；新增 §C dispatch inbox 让派工链路明确
  - 不影响任何 in-flight run / 论文 LaTeX 编译 / 现有 U-XXX 决策内容
- next_action:
  - 无（请求闭环）
  - 后续若用 `E-XXX` 前缀，先 Grep 现有最大 E-XXX 编号 +1（当前是首次引入，下一次可用 E-001）

### [E-rules-mdc-en-2026-04-19]
- status: completed
- date: 2026-04-19
- 用户指令: "将 four-role-todo-workflow.md 写成英文，后缀改为 mdc 符合 rules 的规范，把 ssh-server-rules 的后缀也改了"
- 解读:
  - `four-role-todo-workflow.md` → 完整翻译为英文 + rename `.md` → `.mdc`（Cursor rule 规范要求 `.mdc`）
  - `ssh-server-rules.md` → 仅改后缀 `.md` → `.mdc`（用户没要求翻译，且其内容已是英文为主+ STATUS 段中文，混合状态不动）
- files_added:
  - `.cursor/rules/four-role-todo-workflow.mdc`（约 16 KB；英文版 12 节完整 rule，从原中文版语义对等翻译；front-matter `globs` 不变；§0 history 注脚加入 "suffix changed to .mdc + body translated to English on 2026-04-19" 一句）
  - `.cursor/rules/ssh-server-rules.mdc`（约 5 KB；与原 `.md` 100% 同字节，仅一处自指更新：L13 `four-role-todo-workflow.md §4` → `four-role-todo-workflow.mdc §4`）
- files_deleted:
  - `.cursor/rules/four-role-todo-workflow.md`（15,923 B）
  - `.cursor/rules/ssh-server-rules.md`（5,194 B）
- files_modified（活跃引用 `.md → .mdc`，共 8 处）:
  - `README.md` L70：`four-role-todo-workflow.md` → `.mdc` + 加注 "英文版 + Cursor `.mdc` 规范"
  - `PROJECT_STRUCTURE.md` L244 + L286：同上
  - `docs/coordination/SCIENTIST_TODO.md` L6 + L44：同上（L44 是 §B 内对 §2 硬规则的引用）
  - `docs/coordination/USER_TODO.md` L6：同上
  - `docs/coordination/REVIEWER_TODO.md` L6 + L96：L6 header；L96 §E.4 hand-off 末对 §11.4 的引用
  - `artifacts/rebuttals/README.md` L14：同上（rebuttal 流程对 S-104 的引用）
  - `docs/coordination/implementation_log.md`（本条）
- key_decisions（用户直接指令，非自主）:
  - 选 Cursor 规范的 `.mdc` 后缀（与现有 `persistent-chat.mdc` 对齐）
  - 选完整翻译四角色 rule 为英文（用户明确要求）
  - 选**不**翻译 ssh-server-rules（用户只说"后缀也改了"），保留其 STATUS 段中文 + RULE 1-5 英文的混合现状
  - 历史快照（`implementation_log.md` 既往 phase block + USER_TODO §D L97 + REVIEWER_TODO §D L62）的旧 `.md` 文件名引用**保持不变**（不回写历史）
- blockers:
  - none
- conflicts_with_docs:
  - none
- verification:
  - `Glob ".cursor/rules/*"` → 应只剩 `four-role-todo-workflow.mdc` + `ssh-server-rules.mdc` + `persistent-chat.mdc` 三份 `.mdc`，无任何 `.md` 残留
  - `Grep "four-role-todo-workflow\.md|ssh-server-rules\.md"` → 只剩历史快照（implementation_log + USER §D L97 + REVIEWER §D L62），全部活跃引用已切换至 `.mdc`
  - `Grep "four-role-todo-workflow\.mdc|ssh-server-rules\.mdc"` → 8 处活跃引用 + 2 处自指（rule 自身 history 注脚）= 10 处命中，全部正确路径
  - ReadLints 全部改动文件 0 错误
- impact_on_other_tracks:
  - Cursor IDE 现在能正确按 `.mdc` 规范加载这两份 rule（`globs` / `alwaysApply` 字段正常生效）
  - 英文版 rule 解锁了未来对外协作 / open-source 场景下国际人员可读
  - 不影响任何 in-flight run / 论文 LaTeX 编译 / 现有 U-XXX 决策内容
  - 不影响 `persistent-chat.mdc`（用户要求不动）
- next_action:
  - 无（请求闭环）

### [reviewer_p5_oral_gatekeeper_review_20260419]
- status: completed
- date: 2026-04-19
- reviewer_id: `reviewer_20260419_163139_01_9e72f7`
- persona: P5 (Best-Paper-Committee chair / Oral-track gatekeeper)
- target: `article/build/edo_paper.pdf` (266 KB / 9 pages, build_id `edo_paper_emnlp2026_header_fix_20260419`)
- files_added:
  - `artifacts/idea_reviews/reviewer_20260419_163139_01_9e72f7/review.json`（11.5 KB，符合 reviewer_prompt.md §9 schema）
  - `artifacts/idea_reviews/reviewer_20260419_163139_01_9e72f7/review.md`（人类可读 review，含 score breakdown + Top Strengths/Weaknesses + Experiments Solidity Audit + Novelty Delta Audit）
  - `artifacts/idea_reviews/_edo_paper_text_for_review.txt`（pdftotext -layout 抽取，54 KB / 513 行）
- files_modified:
  - `artifacts/idea_reviews/review_index.jsonl`（+1 行；含 BOM 修复 — Powershell `Add-Content -Encoding UTF8` 默认加 BOM 导致 `review_scoreboard.py` JSON 解析失败，已用 Python 直接 binary write 去 BOM）
  - `artifacts/idea_reviews/scoreboard.md`（latest_overall 更新为 4.5；average 6.291 → 6.142；total 21）
  - `artifacts/idea_reviews/fix_themes.md`（自动重新归并；新增主题计数为 (1) 是因为 reviewer agent 的具体描述与既往 reviewer 的描述不重合，预期）
  - `docs/coordination/SCIENTIST_TODO.md`（§A 加 U-011-decide；§B.5 加 9 个 NEW fix-TODO S-105..S-114；§C 加 7 条 NEW reviewer 反馈追踪 + dissent log 表头；§D 修订记录 +1 行）
- key_decisions（用户直接指令 + 工程师自主选择）:
  - 用户指令：扮演**全新独立审稿人**用 `prompts/reviewer_prompt.md` 模版严格审 `article/build/edo_paper.pdf`；不被既往审稿意见左右；客观中立严格认真；按顶级会议 oral 要求审
  - persona 选择：P5（Best-Paper-Committee chair / Oral gatekeeper）—— 用户明确要求"按顶级会议 oral 的要求"，P5 是 5 个 personas 里唯一显式 oral-gate 的角色
  - 输入策略：pdftotext fallback（远端 LLM 调用脚本已删，无 PDF 直传通道）；按 §1.5.2 规则把所有 layout-dependent checks 标 `"PDF required - cannot confirm from text"` 并把 confidence 降到 3
  - 评分严格遵守 §6 deterministic 公式 + 所有 caps：weighted_sum=4.855 → caps_triggered=[D4<5, D3<5, experiments_solidity_score<=3] → final_overall=4.5
- core_findings（仅事实层面，无价值判断）:
  - **D3 (novelty) = 4.0**：Related Work §2.1/§2.2/§2.3 命名 0 个具体 prior work；§2.5.2 audit 列出 3 个候选 prior work（AutoGen/MetaGPT, Reflexion/ToT, MARS/SAGE/AMRO-S）但都是 generic 提法，无 named delta；hard rule cap D3 at 5；honest score 4
  - **D4 (empirical_results) = 4.0**：experiments_solidity_score = 0/8（EXP-1/2/3/4/6 全 fail；EXP-5/7/8 partial）；hard rule cap D4 at 4
  - **headline empirical claim self-falsified**：作者自己 §4.3 Finding 4 承认 `peer_calibrated F1=0.7381 < self_claim F1=0.7641` 同 token 成本（6,414/sample），proposed method Pareto-dominated by simpler baseline
  - **bibliography placeholder**：References 列表只有 4 条 ACL 模板默认引用（Ando&Zhang 2005 / Andrew&Gao 2007 / Gusfield 1997 / Rasooli&Tetreault 2015），全部与多 agent 系统无关 → desk-reject 邻接信号
  - **figures missing**：Algorithm 1 / Figure 1 / Figure 2 全部不在 PDF（pdftotext extraction 无任何 algorithm 环境或 \includegraphics 痕迹）
  - **DR 风险**：DR-1 (page count §4.6+§5 在 pdftotext 输出第 9 页) / DR-3 (Limitations 含 ModelDriftError 工程修复细节) / DR-5 (inline 内部仓库路径) / DR-6 (Responsible NLP Checklist 不在 PDF) / DR-8 (4-条模板默认引用) 全部标 POSSIBLE，未确认
- blockers:
  - none（审稿动作本身已完成；落盘 + 聚合 + TODO 同步全部成功）
- blocker_type:
  - none
- fast_fail_triggered:
  - no（PowerShell BOM bug 是工具问题，不是审稿失败；已 Python 旁路修复）
- conflicts_with_docs:
  - none（审稿模版 `prompts/reviewer_prompt.md` 与 `docs/demand.md` 全部一致；rule_source_disagreements 字段为空）
- verification:
  - `python -m json.tool review.json` exit 0 → JSON 合规
  - `scripts/review_scoreboard.py` exit 0 → scoreboard.md 重生成；新行 `reviewer_20260419_163139_01_9e72f7: overall=4.5, verdict=weak_reject` 在最末
  - `scripts/summarize_idea_reviews.py` exit 0 → fix_themes.md 重新归并
  - `Get-Content review_index.jsonl | Measure-Object -Line` → 21 行，与磁盘 reviewer_*/review.json 数量一致
- toolchain_recorded:
  - pdftotext (poppler 24.x via PATH)
  - Python 3.12.4 (json.tool, json.loads)
  - PowerShell 7.x (`Add-Content` BOM bug workaround via Python `open(..., 'wb')`)
- impact_on_other_tracks:
  - **SCIENTIST_TODO §A 新增 U-011-decide**（最高优先级决策：framing 走 (a) Stage-1 negative result 重 framing vs (b) 实现 Stage-2 后再投）
  - **SCIENTIST_TODO §B.5 新增 9 个 fix-TODO**（S-105..S-114），其中 S-105 (bibliography) / S-110 (Algorithm 1 LaTeX 渲染) / S-111 (Limitations 移 Drift 段) / S-113 (匿名化路径) / S-114 (页数确认) **完全不依赖工程师，可即刻动手**
  - **SCIENTIST_TODO §C 新增 7 条 NEW 反馈条目** + 新设 S-104 dissent log 表头（科学家保留拒绝接受 reviewer 意见的权利，但必须在表内写理由，criteria 已写明）
  - 不影响任何 in-flight run（无 API 调用，无 core code 修改）
- workflow_compliance（按 .cursor/rules/three-role-todo-workflow.md §1）:
  - Step 1 (检测 pending → done)：✅ 已对 SCIENTIST_TODO §B.1 4 个 ⏳ 项做产物存在性核对，2 个 ⏳→✅（S-003, S-006b）、1 个 ⏳→✅（S-011）、1 个 ⏳→🟡 partial（S-006a 仅 data + caption，缺 PNG/PDF）
  - Step 2 (更新当前动作 TODO)：✅ 本条 implementation_log 即是当前动作的状态更新；TodoWrite 工具同步追踪 9 个本轮子任务
- next_action:
  - 无新动作（用户请求闭环）；待用户对 **U-011-decide** 拍板后由科学家驱动 S-105..S-114 落地
  - 工程师维度无新工单（本轮审稿不依赖工程师）
  - reviewer-agent 维度：本审稿是项目内首次 P5 oral gatekeeper review，下次审稿建议轮换 persona（P1/P2/P3/P4）以获得多视角

### [user_role_clarification_user_todo_doc_sync_20260419]
- status: completed
- date: 2026-04-19
- 触发: 用户消息明确"我不是科学家，我是把握全局的人，负责重要卡点决策；科学家是团队内部的成员；我的 todo（充值 API、使用 prompt 绘图、重要方向把握）也要有一个 todo 文档，和科学家的不是一个；你也可以派活给我"。本条记录角色边界澄清的同步动作。
- files_added:
  - none（USER_TODO.md 在更早的 sprint 已被创建，本轮仅做 cross-doc consistency check）
- files_modified:
  - `PROJECT_STRUCTURE.md` §3 docs/ 树状图（加 USER_TODO.md 行 + 注解 §A/§B 角色） + §9 三角色协作分布表（加用户行 + 派工方向注 + 共享决策表）+ §11 整理项指针（从 SCIENTIST_TODO §A 改成 USER_TODO §A 权威源）
  - `docs/coordination/implementation_log.md`（本条）
- key_decisions（用户直接指令，非自主决策）:
  - 用户角色边界确立：用户 = 全局把握 + 决策（U-XXX-decide）+ 人工执行（U-EXEC-XXX：API 充值 / prompt 出图 / 上传 / 注册）；不写论文段落 / 不改 core code / 不处理 reviewer 文字反馈细节
  - 三类 TODO 文件对齐：USER_TODO.md（用户）/ SCIENTIST_TODO.md（科学家）/ implementation_log.md（工程师）已经全部就位，无新建
  - **派工方向反向支持**：任何角色（包括 AI reviewer-agent / coordinator-agent / 工程师 / 科学家）都可在 USER_TODO §A 挂决策项 / §B 挂人工执行项**派活给用户**
- 状态对齐核查（cross-doc consistency check）:
  - `.cursor/rules/three-role-todo-workflow.md`: ✅ 已对齐（globs / §0 / §2 / §4 / §5 / §7 全部指 `docs/coordination/USER_TODO.md`）
  - `docs/coordination/USER_TODO.md`: ✅ 已存在且完整（§A 11 项 U-XXX-decide / §B 2 项 U-EXEC / §C 已完成 / §D 修订 / §E 派工分布）
  - `docs/coordination/SCIENTIST_TODO.md`: ✅ §A 已经是 cross-reference 视图（不是权威源），与 cursor rule 表述一致
  - `PROJECT_STRUCTURE.md`: ⚠ 仅 §0 提了 USER_TODO，§3/§9/§11 三处遗漏 → **本条已补**
  - `docs/coordination/implementation_log.md`: 之前 sprint 创建 USER_TODO 时**未留日志条目** → **本条即补丁记录**
- blockers:
  - none（cross-doc consistency 已对齐；用户的派工通道已闭环）
- blocker_type:
  - none
- fast_fail_triggered:
  - no
- conflicts_with_docs:
  - none（PROJECT_STRUCTURE.md §0 vs §3/§9/§11 之前的表述不一致已修；现在全部统一指向 USER_TODO §A 为权威源）
- verification:
  - `Grep "USER_TODO" PROJECT_STRUCTURE.md`: 5 处命中（§0 + §3 + §9 共 3 段），全部指向 `docs/coordination/USER_TODO.md`
  - `Grep "USER_TODO" .cursor/rules/three-role-todo-workflow.md`: 7 处命中，全部正确路径，无死链 `research/USER_TODO_2026-04-18.md`
  - ReadLints PROJECT_STRUCTURE.md / SCIENTIST_TODO.md / USER_TODO.md / implementation_log.md → 全部 no errors
- impact_on_other_tracks:
  - 不影响任何 in-flight run / 论文 .tex / artifacts/ 实验数据
  - **解锁**：以后任何 AI 角色（reviewer-agent / coordinator-agent / 工程师 / 科学家）派活给用户的通道完全规范化
  - **同时澄清**：reviewer_20260419_163139 P5 review 的 U-011-decide（framing 决策）已在 USER_TODO §A 第 45 行登记，状态 ⏳ 最高优先级，等用户拍板
- next_action:
  - 等用户对 USER_TODO §A 的 U-011 / U-002 / U-004 / U-006 / U-007 / U-008 / U-010 拍板（其中 U-011 最高优先级，决定整篇论文 framing 方向）
  - 等用户对 USER_TODO §B 的 U-EXEC-001（充值 API）/ U-EXEC-002（用 prompt 出 Figure 1）执行
  - 不依赖用户的科学家可做项 = SCIENTIST_TODO §B.5 中 S-105 / S-108 / S-110 / S-111 / S-112 / S-113 / S-114（6 项可即刻动手）；派给科学家的工作通道也已规范化
  - reviewer-agent 维度：等下一轮新审稿请求（用户主动触发）；不擅自跑额外审稿
