# Benchmark、baseline 与实验计划 v1.0

- **状态**：`ACTIVE`
- **生效日期**：2026-09-28
- **类别**：benchmark-baseline
- **前一版本**：无；这是候选冻结前的唯一有效实验计划
- **目标约束**：[`docs/coordination/GOAL.md`](../../../coordination/GOAL.md) ER-G3/ER-G4

`ACTIVE` 只表示这是当前唯一的实验计划，不表示 benchmark 已冻结或 baseline 已实现。

## 1. Benchmark 状态

主候选为 TeamBench-derived `PeerRoleBench-TB`。它目前是候选协议，不是已冻结 benchmark。候选 root 为 `DIST1_queue_race`（development/诊断）和 `PIPE3_stream_processing`（confirmation 候选）；改 seed、改名或字段替换不增加独立 root。DIST1 的历史任务文本泄露修复方向，因此不能直接充当 discovery 科学样本；PIPE3 也必须先通过完整 runner、scorer、ledger 和 adoption 资格。

冻结前必须有不可变 manifest：TeamBench commit、root/source/generator hash、seed 与 root split、角色可见文件、写权限、scorer/ledger schema、模型/API 配置、预算、主指标和停止规则。任何 root 的信息泄漏、责任归因、评分覆盖或 replay 失败都只能是 `UNKNOWN`/停止，不能靠改 label、减少检查或扩大 timeout 变成通过。

## 2. 任务契约

每个 episode 必须独立记录 producer contract、recipient action/use/rework、sink adoption、final outcome、完整成本和 UNKNOWN 原因。决策在执行前封存；未来 owner 的 assignment 不能读到执行后结果。producer correctness 不等于 recipient integration；recipient 正常完成自己的工作不自动惩罚 producer。

主任务必须有真实依赖：recipient 能够接受、使用、修改、拒绝或返工具体交付。private gold、hidden scorer、operator ledger 和其他 policy 的状态必须隔离。development 与 confirmation 按 root 划分；确认 root 的材料不能在看完结果后重切。

## 3. Baseline 矩阵

所有 policy 共享候选集合、初始状态、探索机会、模型/API/工具预算、可见事件和完整成本；只能读取自己的合法历史。

| 条件 | 读取/更新 | 目的 |
|---|---|---|
| `uniform` | 候选集合；固定均匀选择 | 下界与探索上界 |
| `no_update` | 初始先验与当前上下文；不因反馈更新 | 判断单纯执行是否已足够 |
| `raw_acceptance` | 合法 accept/reject | 检验责任过滤的增量 |
| `terminal_only` | 独立 final outcome | 检验 situated judgment 的额外信息 |
| `contextual_trust` | 与主方法相同的 context/judgment/propensity/延迟 | 最强同信息信任/ bandit 对照 |
| `pooled_controller` | 允许的公共历史；不读 private scorer | 集中控制上界 |
| `RARE` | responsibility-aware judgment/action/contract | 主候选机制 |

RLS、online logistic/SGD、periodic refit 和候选增量 updater 是训练更新比较，不能被重复计入选择 policy，也不能称成 RARE 创新。所有选择 policy 的反馈输入合同必须在实验卡中逐项写明：`raw_acceptance` 只能读合法 recipient accept/reject；`terminal_only` 只能读独立 final outcome；`contextual_trust` 与 RARE 读取相同的 eligible/UNKNOWN、selected-only、propensity、arrival order 和延迟字段，但使用自己的更新规则。任何 policy 都不能把 UNKNOWN 当负例或读取另一个 policy 的 state。

## 4. 实验问题与指标

- **RQ1 信息价值**：situated judgment 能否预测独立 producer contract/later-use 结果，超出 raw acceptance 与 terminal-only？
- **RQ2 闭环**：反馈是否在下一次执行前改变未直接评价候选者 owner 的 assignment，并在新 root 上改变质量、返工和完整成本？
- **RQ3 实时更新**：每条合法反馈的 update/selection p50/p95、状态大小、service lag 和 token/tool/GPU/人工成本是否满足预注册预算？
- **RQ4 边界**：责任不清、consumer 自有错误、版本替换、漂移、延迟/乱序反馈时，UNKNOWN 与保护写入是否比错误惩罚更稳健？

主结果按独立 stream 汇总，不把同一 stream 的多个 episode 当独立样本。稳定性报告旧 root holdout 的峰值/平均下降和恢复窗口；时效性报告 drift 后响应窗口；成本包括 producer、recipient、judge、通信、重试、返工、scorer 和 replay。

## 5. 实验顺序与停止规则

1. 零 LLM：验证材料、可见性、权限、producer/recipient/adoption scorer、ledger replay、sidecar、重复/乱序/UNKNOWN 和 snapshot/restore。
2. 单 root 最小真实流：仅回答接口和信息价值问题；不宣称效果。
3. 两个 root、独立 live history 的开发卡：冻结 manifest、policy、预算、主指标和失败规则后执行。
4. 独立 confirmation root：不得在看完开发结果后改 split、label 或指标。
5. 只有真实信号和明确训练瓶颈出现，才提交一个 A800 bounded challenger。

停止条件：scorer/ledger/责任边界失败；没有真实 recipient action；policy 无法区分 eligible 与 UNKNOWN；或 RARE 与 contextual trust 在同信息、同成本下没有预注册增量。停止保留失败证据，不修改 Goal。

## 6. 当前证据与开放项

已有工程资产包括 task contract、sandbox、lineage/replay 和部分 policy sidecar qualification；N02 两条有限真实链没有产生概率变化，N03 仍未完成 live runner qualification。`PeerRoleBench-TB` 尚未冻结，强 baseline、RARE 统一实现、独立 confirmation stream 和 A800 训练结果均未完成。

## 7. 对照标准

本文件按 [`benchmark_baseline_v1.0_20260928_eval.md`](../evaluation/benchmark-baseline/benchmark_baseline_v1.0_20260928_eval.md) 审查。故事与创新见 [`storyline_v1.1_20260928.md`](../storyline/storyline_v1.1_20260928.md)，方法合同见 [`method_v1.0_20260928.md`](../method/method_v1.0_20260928.md)。
