# 2026-09-29 Benchmark、baseline 与实验结果验收审计

- **状态**：`COMPLETE`（评价标准已补齐；科学 benchmark/baseline 验收仍 `OPEN`）
- **对应 Goal**：ER-G3（benchmark/baseline 硬标准）、ER-G4（实验与论文证据标准）、ER-G5 G1/G3 阶段门
- **Goal 变更请求**：`false`
- **本任务范围**：只审计和收紧 benchmark/baseline 验收标准；不启动新的真实 API、GPU 或 A800，不把 v6 工程链写成科学结果。

## 1. 运行前冻结与证据

本次审计固定读取：

- active benchmark 计划 [`benchmark_baseline_v1.0_20260928.md`](../../research/versions/benchmark-baseline/benchmark_baseline_v1.0_20260928.md)；
- active 评价标准 v1.1 及其官方来源记录；
- TeamBench/PeerRoleBench-TB 资格、PIPE3 v6 真实链和责任审计；
- baseline implementation/bridge audit；
- 另一条候选 selector 复审 [`peer_selection_benchmark_reassessment_20260925.md`](../../research/peer_selection_benchmark_reassessment_20260925.md)。

本次产生的规范版本是 [`benchmark_baseline_v1.2_20260929_eval.md`](../../research/versions/evaluation/benchmark-baseline/benchmark_baseline_v1.2_20260929_eval.md)，并已登记为唯一 active evaluation version。没有重算历史 raw output、没有修改历史日志、没有调用 LLM/GPU。

## 2. 发现的关键缺口

| 验收部分 | 当前状态 | 证据与原因 |
|---|---|---|
| Benchmark 选型适配性 | `NOT_READY` | active 计划把 TeamBench-derived `PeerRoleBench-TB` 作为候选；另一份复审提出 graph-ipd/PeerSelect-IPD 作为 selector 机制轨道。两者尚未确定 primary/secondary，也没有唯一的 claim boundary。 |
| Benchmark 权威性/复现 | `PARTIAL` | TeamBench commit、许可证和部分 scorer 已固定；但自定义协议尚未 freeze，缺 clean reconstruction、污染审计和公开复现入口的完整 gate。 |
| Root 独立性/覆盖 | `NOT_READY` | DIST1 有历史任务文本泄露修复方向；PIPE3 仍未完成科学文本、later assignment、独立 live streams 和责任四类对照。seed 或改名不构成独立 root。 |
| Causal signal | `PARTIAL` | v6 的 Qp/Qr/adoption、结构化责任判断和 recipient-owned repair 已真实通过，gate 正确输出 `PENDING_ATTRIBUTION`；没有 producer-defect 对照、future assignment 或闭环效果。 |
| Baseline 可执行性 | `NOT_READY` | uniform/no-update/terminal/contextual 只有统一接口/离线资格；raw acceptance、pooled、RARE、online logistic、periodic refit 尚未统一接入真实 runner。 |
| Closest published baseline | `OPEN` | active 评价要求 faithful adapter，但当前计划未固定具体论文、版本、差异映射和 fallback。 |
| Information/cost parity | `BLOCKED_BY_EVIDENCE` | 旧 N02 ledger bridge 为 `NOT_MAPPABLE`；新 v6 没有 policy update，尚未能比较 judge 成本、延迟、state、propensity 和同信息输入。 |
| 实验矩阵 | `NOT_FROZEN` | 当前是 policy 名单和 RQ，不是包含 root、责任情形、信息条件、arrival/drift、stream、资源预算和每格 primary endpoint 的 cell manifest。 |
| 结果合理性 | `NOT_STARTED` | 尚无 policy comparison、独立 root/stream、CI/effect、ITT/per-protocol、quality-cost Pareto 或数值 precision gate。v6 只能支持协议/责任安全结论。 |

## 3. 已完成的标准修订

v1.2 新增并强制执行：

1. `PeerSelect` 机制轨道和 `ArtifactRole` 任务轨道的 primary/secondary 选择，禁止用一个轨道的结果代替另一个轨道；
2. benchmark 选型评分卡：主张适配、上游权威、任务多样性、信号可识别、污染/clean replay、规模/精度六项必须全部通过；
3. baseline 角色分层和 executable/parity gate，包含 closest published faithful adapter、same-menu pooled 与 oracle 边界、无 judgment arm 的成本口径；
4. 完整实验 cell manifest 要求，显式冻结信息条件、责任四类、局部/集中语义、时间因素、stream/seed、资源和主终点；
5. 结果合理性 truth table，预注册信息增量、质量、成本、延迟、UNKNOWN、遗忘/恢复门，并规定 ITT、per-protocol、缺失、聚类和多重比较处理；
6. `Findings-ready` 与 `Proceedings-ready` 的证据等级以及停止规则。

这些是验收门的补齐，不是对 Goal 的降级，也没有宣称任何 benchmark 或 baseline 已通过。

## 4. 与 Goal 的逐项对照

- **ER-G3**：协议工程显著推进，但唯一 primary track、权威 benchmark freeze、独立 root、强 baseline 和 parity 尚未满足，状态 `PARTIAL/OPEN`。
- **ER-G4**：v6 使用真实 API 并保存完整链，但没有 future assignment、独立确认、policy effect 和统计结果，状态 `PARTIAL/OPEN`。
- **ER-G5 G1**：未通过；先修 benchmark/runner/label 资格。
- **ER-G5 G3**：未开始；在 cell manifest、baseline parity 和数值门冻结前禁止新的正式效果流。
- **ER-G1/ER-G2**：本审计不改变故事、创新和方法目标，也不以工程失败为理由修改它们。

## 5. 下一步顺序

1. 在 active benchmark 计划中解决 `PeerSelect` 与 `ArtifactRole` 的 primary/secondary 关系，并固定一份 benchmark authority/root selection scorecard；
2. 为 uniform/no-update/raw/terminal/contextual/pooled/closest/RARE 建立统一真实 runner 入口，完成 parity table 和四类 responsibility controls；
3. 生成执行前封存的 cell manifest，包含数值精度门、统计单位、stream 数、缺失处理和停止规则；
4. 只有以上三步全部通过，才执行新的独立真实 API 小流；A800 仍需等待真实信号和明确训练瓶颈。

当前不需要用户决定，也不应通过增加 API 次数来掩盖 benchmark/baseline 门未通过的问题。
