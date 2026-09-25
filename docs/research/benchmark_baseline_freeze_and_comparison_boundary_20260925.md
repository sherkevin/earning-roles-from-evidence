# 本项目 Benchmark、Baseline 与效果结论

> 日期：2026-09-25
> 状态：按本项目决议 0008 修正后的范围说明
> 目标：只用 earning-roles 自己的任务和证据评价 peer-judged role formation。

## 先纠正项目边界

BBB、LLMRouterBench、ASlib SAT12-ALL 属于另一个工具选择/动态 JEV 项目。它们可以共享事件格式、延迟反馈队列、版本管理、checkpoint 和 updater API，但不属于 earning-roles 的 benchmark，也不能用来证明本项目的方法效果。

此前把 BBB 数字放进本项目的效果说明，是项目边界混淆，已在本文件中撤回。这个项目当前没有 BBB 的实验结果，也没有完成 LLMRouterBench/ASlib 上的 peer-role 方法比较。

本项目应遵守已经接受的[决议 0008](../user/decisions/0008-freeze-benchmarks-and-baselines.md)：

- **角色形成主 substrate：** CooperBench 薄适配；
- **选择器 benchmark：** DecisionBench；
- **外部有效性：** AgentWorld；
- **威胁与控制：** MARBLE/MultiAgentBench、TeamBench、AgentNet 等同信息对照。

## 本项目要评价的科学对象

研究问题不是一般的“哪个 agent/tool 得分更高”，而是：

> 一个 producer 的交付物被真实 consumer 使用、返工或拒绝后，这个 situated judgment 是否形成可归因的 role evidence，并改变该 producer 后续承担的责任。

因此至少要出现完整链条：

```text
producer delivery
  -> actual recipient judgment/use/rework
  -> independent terminal check
  -> producer role evidence
  -> later responsibility assignment
```

只有选择结果或终端成功率，没有 consumer 的实际使用和后续职责变化，不能称为本项目的 role-learning benchmark。

## Benchmark 层次

### 1. CooperBench：角色形成主 substrate

固定审计版本为 `63b9d44d9f39a02fccf5bf0052db48a917a011fd`，但当前仍是**有条件候选**，不是已经完成的主 benchmark。

进入科学实验前必须通过：

1. producer → recipient judgment/use/rework → terminal scorer → later assignment 的完整 vertical slice；
2. 许可证、数据和 scorer 的可再分发/独立运行确认；
3. held-out task-root split；
4. 相同任务、模型、工具、预算和可见信息的 matched controls。

已知问题包括 feature owner 预分配、缺少原生 recipient acceptance/role update 字段，以及 merge conflict 时的 fallback。`both_passed` 不能单独证明 recipient 使用了 producer 的交付物。

### 2. DecisionBench：选择器 benchmark

DecisionBench 用来测量 peer-selection 的适应、探索、成本和 calibration。它可以回答“选择器是否改善了选择”，但单独不能证明 role formation，因为公开实现没有从 recipient use 更新 peer profile 并改变后续职责的完整链条。

### 3. AgentWorld：外部有效性

AgentWorld 用来检验 stateful multi-agent transfer。它的 preset skills、resources 和 usernames 需要随机化或做成可交换的，否则无法把预设角色差异解释成 role learning。它不是第一阶段的主证据。

### 4. CooperBench/DecisionBench 之外的公开工作

MARBLE/MultiAgentBench、TeamBench 可提供固定角色、确定性 grader、role violation 和 verifier disagreement 控制；AgentNet 是 decentralized routing、dynamic graph 和 experience-based update 的重要威胁 baseline。它们用于控制和外部比较，不替代主 substrate。

## 冻结的 baseline 矩阵

所有方法必须拥有相同任务根目录、agent/model/tool access、局部邻居、存储、反馈可见性、总 API/test 预算和随机种子。

| 编号 | 方法 | 作用 |
|---|---|---|
| B0 | pooled single-agent / centralized selector | 检验多 agent 是否真的必要 |
| B1 | fixed cooperation, no role update | 有协作但没有在线角色学习 |
| B2 | recipient redo / no handoff | 测量交付使用和返工的必要性 |
| B3 | raw recipient acceptance | 直接使用接受率，但不做校准/角色证据 |
| B4 | same-information local contextual trust or bandit | 最强的普通选择器近邻 |
| B5 | terminal-only feedback | 判断 consumer judgment 的增量价值 |
| B6 | closest reproducible peer-feedback/dynamic-role control | 对齐已有动态角色方法 |
| P | proposed situated judgment → role evidence → later assignment | 本项目方法 |

DecisionBench 另外报告 random-local、static profile、static trust、same-information contextual bandit、global selector 和 no-online-update。AgentNet-style dynamic router 在信息和预算可匹配时必须加入威胁比较。

## 我们目前真正做过的效果比较

本项目目前只完成了小型合成 selected-only 流上的更新器诊断，没有完成 CooperBench 或 DecisionBench 的正式 role-learning 结果。

在 5 个 seed 的 stationary 长流中：

| 方法 | reward | regret | 结论 |
|---|---:|---:|---|
| Static | 0.3686 | 0.1104 | 不更新 |
| Associative S/Z | 0.4501 | 0.0290 | 能学习稳定关系 |
| OnlineRLS | 0.4578 | 0.0212 | 当前最强简单在线基线 |
| Residual fast-weight | 0.4192 | 0.0598 | 尚未超过 RLS |

在 regime-switch 流中，Residual fast-weight 为 `0.5466`，高于 Static `0.4980`、Associative `0.5183` 和 OnlineRLS `0.5240`。因此当前严格结论是：

> 当前更新器在稳定环境中不如 OnlineRLS；在分布切换中出现潜力；尚无本项目真实 multi-agent benchmark 证据。

短流 smoke 中 Associative `0.4187` 与 Static `0.4183` 几乎相同，低于 OnlineRLS `0.4257`。这只能说明短流没有显示出稳定收益，不能推出 peer-role 方法整体无效。

证据文件：[bounded residual fast-weight 结果](/Users/jingwu/work/earning-roles/references/aamas/streamjev_20260924/experiments/logs/bounded_residual_fast_weight_isolation_20260925_results.json) · [associative smoke 决议](../user/decisions/0014-linear-associative-smoke-gate.md)

## BBB 等外部项目结果的正确用法

BBB/LLMRouterBench/ASlib 的结果可以帮助 companion tool-selection 项目比较 LinUCB、LinTS、ACTS、PAK/RFF-UCB 等选择器，也可以帮助我们复用：

- selected-only delayed event schema；
- candidate/version identity；
- delayed queue、乱序重放和 checkpoint；
- update latency、memory 和 forgetting 的记录方式。

但它们不能作为本项目的 peer-role accuracy、role transfer 或 consumer-use 结果。两个项目的 label scope、action semantics、objective 和 evaluator 不同；这条边界已记录在[跨项目对齐说明](cross_project_dynamic_jev_alignment_20260925.md)。

## 下一步实验顺序

1. 先做 CooperBench 薄适配的 scorer/label audit 和最小 vertical slice；记录 producer 交付、真实 recipient judgment、use/rework、terminal outcome 和 later assignment。
2. 在同一 task-root 和相同信息权限下跑 B0–B6；先证明 P 的输入信息和成本没有额外优势。
3. 用 DecisionBench 单独测 peer selector 的探索、校准、成本和 delayed feedback 适应。
4. 只有通过前两步，才在 AgentWorld 做外部有效性；先随机化预设技能和身份。
5. 之后再做真实 `内部` API 小批量；所有 call、label、失败和总预算写入 JSONL。

在这条路径完成前，不应引用 BBB 结果判断本项目，也不应把 AnyJev、Laya、Qwen 或 RLS 写成最终创新。AnyJev/Laya 是 baseline 或候选 scaffold；本项目的创新必须仍然落在“他人的 situated judgment 如何形成 role evidence 并改变未来责任”上。
