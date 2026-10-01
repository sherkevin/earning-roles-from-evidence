# 方法论评价标准 v1.2

- **状态**：`ACTIVE`
- **类别**：evaluation/method
- **评价对象**：[`method_v1.1_20260930.md`](../../method/method_v1.1_20260930.md)
- **生效日期**：2026-09-30
- **前一版本**：[`method_v1.1_20260928_eval.md`](method_v1.1_20260928_eval.md)
- **用途**：审查两阶段 role-evidence 方法是否真正新、可运行、可验证、实时且稳定；不保证录用。

## A. 三层状态硬门

方法必须把以下状态分开记录并可重放：

- `attribution_eligible`：源 producer contract、recipient judgment、实际 action、terminal outcome 和 digest 唯一绑定；later outcome 不能单独制造源归因；recipient-only/mixed/UNKNOWN 必须拒绝。
- `evidence_publish_allowed`：可发布不可变 public evidence，供未来 read cut 使用；发布阶段持久 policy digest 和 update count 不变。
- `policy_update_allowed`：只有 assignment 在 selection/start 前成立、selection 消费同一 evidence snapshot、later task 完成后，才允许一次 selected-only delayed credit。

Role evidence offer 必须与 policy feedback offer 分离；native `evidence_id`、producer/version、delivery/artifact lineage 和 target assignment subject 必须可从 canonical ledger 重放。必须有 preview→assignment→selection 的 exact chosen/propensity 检查，禁止把 source selection id 当 evidence id，或用错误 peer 消费别人的 evidence。

任何把 diagnostic ELIGIBLE 直接当训练标签、把 later outcome 回填成旧 producer 标签、或在早期 selection 读取未来结果的实现均不通过。

## B. 形式完整性与事件顺序

独立读者必须能从 source selection → Qp/J/A/Y → gate → publication → assignment → later selection/outcome → delayed update 重放出结果。文档和测试必须定义：输入、公开/私有状态、read cut、arrival index、UNKNOWN/INVALID、版本、supersession、重复/乱序、snapshot/restore、容量/淘汰和停止规则。原生 ledger 的 assignment 必须在目标 selection/task start 前写入并保持 agent/propensity 一致；无 assignment 的 task_start 是否允许需单独遵守底层协议，不能误写成方法必然约束。

## C. 创新与正交消融

必须完成 closest-method audit，并证明收益不能由普通 contextual trust/bandit、RLS、online SGD、periodic refit 或现成 JEV wrapper 在同信息/同预算下复现。至少报告四格：no evidence/no update、public evidence only、delayed update only、public evidence + delayed update；再做责任门、延迟 credit、遗忘保护和 correction/replay 的去除消融。不能把组件堆叠本身作为充分创新。

## D. 在线性质与成本

分别测 publish、read/assignment、delayed update 的 p50/p95、service lag、吞吐/backlog、状态字节、CPU/GPU/RAM、token/API/tool/人工成本。实时训练必须说明冻结与更新参数、每次读写数据、是否 full-model forward/backward、并发、限流、恢复和 checkpoint。批量 refit 不能冒充逐条更新。

## E. 时效性与稳定性

在预注册 drift 后，报告 evidence 对未来 assignment 的 propensity、future quality/regret 和完整成本的响应窗口；later outcome 不得泄漏到 source read cut。报告旧 root/task 的平均和峰值 forgetting、恢复时间、UNKNOWN 率、late correction/replay 一致性。source FAIL→later PASS 不得被解释为 source 被修复。

## F. 统计与可识别性

主 estimand 是 assignment-level future quality/regret 或 team quality–complete-cost utility，而不是 source producer score 自身。使用独立 streams/root split、selected-only propensity、missing-label/UNKNOWN 分母、judge reliability/calibration 和 95% interval。四格中的公开证据与持久更新必须能分开估计，confirmation split 的 updater、阈值、词表和停止规则必须在看到结果前封存。

## G. 反驳与停止

以下任一情况时方法主张不通过：

1. public evidence 发布已隐式改变持久 policy；
2. later outcome 重写源 label 或给 recipient repair 计 producer credit；
3. assignment/selection/read cut 顺序不合法，或 propensity 被修改；
4. assignment 引用 producer B 的 evidence 却选择 producer C，或 preview 后重采样；
5. UNKNOWN、重复、乱序或 correction 没有 no-op/幂等语义；
6. contextual trust/bandit 在同信息和成本下解释全部收益；
7. 只有 zero-call fixture 或单次 API 链，没有独立 live histories 和 confirmation split。

## H. 两档交付门

`Findings-ready` 至少需要可复现的 two-stage CPU/live 机制、四格消融和负结果解释；`Proceedings-ready` 还需要独立 confirmation、closest-method 对照、future assignment 效果、负迁移/遗忘分析和 clean-environment replay。两档都要求原始事件、失败、成本和 digest 可追溯。

## 来源边界

本标准延续方法评价 v1.1 的 soundness、reproducibility、成本和统计要求，并将 ADR 0043 确认的三层状态和 assignment-level estimand 设为本项目实时 role-evidence 主张的硬门。
