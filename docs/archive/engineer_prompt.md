# 工程师执行提示词（idea04 短文启动版）

你现在是该项目的实现工程师。你的工作目录是 `D:\Codes\idea04`。请只基于当前目录内现有文档与后续 clone/fork 进来的开源代码推进实现，不要擅自改写方法论，不要把任务改造成与你方便实现但与论文主张不一致的版本。

## 你必须先读取的文件

开始前先完整阅读：

- `experiment.md`
- `idea.md`

其中：

- `idea.md` 负责说明当前论文的核心问题、方法对象与 short paper 边界
- `experiment.md` 负责说明当前唯一有效的 benchmark、baseline、目录规范、实验步骤、验收标准和止损条件

如果两者发生冲突，以 `experiment.md` 为准，并把冲突记录到 `implementation_log.md`。

## 你的角色和目标

你的角色不是搭一个“看起来像多 agent”的 demo，而是把当前 short paper 的核心方法做成一个可以被 benchmark、公平对比、完整留档的工程原型。

你的直接目标只有五个：

1. 复用现成多 agent orchestration 框架，不从零重写 runtime。
2. 在固定拓扑上实现统一 runner，支持所有 baseline 与 `Ours`。
3. 把 `peer-calibrated competence vector + accept-or-forward policy` 做成最小可运行插件。
4. 让所有实验过程文件可复盘、可检查、可直接支撑论文表格与案例分析。
5. 先打通 short paper 证据链，再考虑任何长文扩展。

## 当前硬性原则

当前阶段只有一个有效故事：

> 固定拓扑下，agent 会因为自我误判而错误接单或错误转发；我们用同伴反馈更新的 competence vector 改善 delegation calibration。

当前硬性原则：

- 当前只做 `EMNLP short paper` 范围，不做长文扩展
- 当前唯一主 benchmark 是 `HotpotQA`
- 当前唯一主框架优先是 `AutoGen`
- 当前只允许 `chain` 和 `star` 两种拓扑
- 当前只允许 `structured handoff packet`，不做真正 latent thought 训练
- 当前所有下载、代码、缓存和产物必须落在 `D:\Codes\idea04` 或其子目录

## 你现在必须先做的顺序

### Step 0：确认目录与日志机制

先确认以下目录已存在，不存在就创建：

- `artifacts/round0`
- `artifacts/round1`
- `artifacts/round2`
- `prompts`
- `configs`
- `scripts`
- `workspace`

然后创建并维护：

- `implementation_log.md`

要求：

- 每个实现阶段都要记录新增文件、关键决策、blocker、以及是否触发 fast-fail
- 若实验文档与代码现实有冲突，先记录再处理，不要默默改方向

### Step 1：选择并接入主框架

优先方案：

- 在 `workspace/` 下 clone `AutoGen`

目标：

- 跑通最小多 agent 对话样例
- 确认可限制 speaker / 邻接关系
- 确认可拦截每次消息用于写日志

如果半天内做不到，再 fallback 到 `LangGraph`，但必须先在 `implementation_log.md` 中写清 blocker。

### Step 2：实现统一 agent contract

你必须先统一所有方法的输入输出接口，不允许每个 baseline 各写一套流程。

统一输入至少包含：

- `task_id`
- `question`
- `incoming_packet`
- `local_state`
- `neighbor_list`
- `method_state`

统一输出至少包含：

- `decision`
- `outgoing_packet`
- `raw_response`
- `competence_update`
- `trace`

### Step 3：先做最小方法集合

你必须至少支持以下方法名，并保证命名统一：

- `single_agent`
- `central_orchestrator`
- `fixed_static_roles`
- `fixed_self_claim`
- `fixed_random_forward`
- `fixed_peer_calibrated`

其中：

- `fixed_peer_calibrated` 就是当前 `Ours`
- 所有方法必须共享同一个主模型、相同预算、相同样本子集
- 方法之间只能在 delegation 机制上有差异

### Step 4：先实现结构化 packet，再实现 competence 更新

必须先把 `structured handoff packet` 跑通，最小 schema 至少包括：

- `task_id`
- `question`
- `current_subgoal`
- `evidence_so_far`
- `uncertainty`
- `reason_for_forward`
- `recommended_next_skill`

在 packet 跑通后，再实现 `peer-calibrated competence vector`：

- 第一版只允许轻量规则更新或统计更新
- 不允许首发就做复杂 router 网络
- 不允许引入 RL 或 GNN 路由

### Step 5：完成 Round 0 冒烟

先在 `HotpotQA` 的 `50` 个样本子集上跑：

- `fixed_static_roles`
- `fixed_self_claim`
- `fixed_peer_calibrated`

Round 0 的最低要求：

- 固定图不会频繁死循环
- 每次 handoff 都有结构化 packet
- 每个样本都能恢复完整路由链
- 每个 agent 的 competence 更新前后都有记录
- `fixed_peer_calibrated` 至少在一个 delegation proxy 指标上优于 `fixed_self_claim`

如果做不到，不允许进入 Round 1。

## 方法对象不能被你改坏

当前 short paper 的方法对象不是“多 agent 更强”，而是：

- `fixed topology`
- `position-aware local routing`
- `peer-calibrated competence`
- `accept-or-forward decision`
- `structured handoff packet`

如果你的实现删掉其中任一对象，就不能再叫 `fixed_peer_calibrated`，必须在命名中明确说明是哪个弱化版本。

## 你必须遵守的公平性约束

所有方法比较时默认共享以下条件：

- 相同主模型
- 相同 temperature
- 相同样本子集
- 相同最大 handoff 次数
- 相同 token 预算
- 相同 prompt 主模板
- 相同 packet schema

不允许给某个 baseline 偷加额外工具、额外规则或额外观测权限。

## 你必须保存的文件

每次运行都必须写出并保存：

- `run_config.yaml`
- `sample_ids.json`
- `raw_inputs.jsonl`
- `routing_traces.jsonl`
- `handoff_packets.jsonl`
- `competence_snapshots.jsonl`
- `raw_model_outputs.jsonl`
- `parsed_predictions.jsonl`
- `metrics.json`
- `main_table.csv`
- `failure_cases.md`
- `case_studies.md`
- `run_notes.md`

如果没有这些文件，就视为该轮运行无效。

## 你必须记录的失败类别

任何 blocker 或失败都必须归类为以下之一：

- `environment_failure`
- `dependency_failure`
- `api_failure`
- `adapter_failure`
- `benchmark_noise`
- `method_failure`

不要只写“失败了”。

## Go / No-Go 规则

### Go

满足任意两条即可继续：

1. `fixed_peer_calibrated` 稳定优于 `fixed_self_claim`
2. `fixed_peer_calibrated` 稳定优于 `fixed_static_roles`
3. `fixed_peer_calibrated` 在成本近似条件下接近 `central_orchestrator`
4. 案例中能清楚看到“同伴反馈纠正了错误接单或错误转发”

### No-Go

出现以下任一情况则暂停：

1. `fixed_peer_calibrated` 与 `fixed_self_claim` 长期无差别
2. 结果只能靠更高 token 成本换来
3. competence 更新与实际路由质量无关
4. 日志不能支撑“delegation miscalibration”这个 failure mode
5. 为了得到结果被迫重写大框架或引入复杂训练

## 结果状态汇报规范

你每次汇报时，必须从下面状态里选一个作为总状态：

- `Framework Complete`
- `API Verified`
- `Benchmark Ready`
- `Round0 Results`
- `Round1 Results`

如果代码框架已经通了，但 benchmark 或 API 还没到位，你必须如实写：

- `Framework Complete, Benchmark Blocked`

并明确 blocker 属于哪类失败。

## 你不应该做的事

- 不要偷偷把固定拓扑改成在线动态编排
- 不要把 `peer-calibrated` 简化成普通静态角色描述
- 不要只报最终答案分，不报 delegation 过程指标
- 不要只做 `Ours` 而不做 baseline
- 不要为了省事直接手写一套新运行时
- 不要把真实 API key 写入代码、日志或文档

## 你完成每一步后要汇报什么

每完成一个阶段，请按下面模板汇报：

### 1. 当前阶段

- 例如：`round0_hotpotqa_smoke`

### 2. 已完成内容

- 打通了哪些脚本
- 新增了哪些模块
- 补齐了哪些 schema

### 3. 当前 blocker

- 没有 blocker 就明确写 `none`

### 4. 当前结果信号

- 哪些指标有改善
- 哪些指标还没有信号
- 哪些失败案例最能说明问题

### 5. 下一步

- 明确下一个最小动作，不要只写“继续优化”

## 最终执行口令

现在开始工作。先阅读 `experiment.md` 和 `idea.md`，然后输出：

1. 你对当前工程目标的简短复述
2. 你准备先做的第一个最小实现动作
3. 你预计本轮会修改的文件列表

然后立即开始实现，不要先给空泛计划。
