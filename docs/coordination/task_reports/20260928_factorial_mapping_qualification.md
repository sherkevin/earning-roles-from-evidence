# 2026-09-28 J/A/U/F factorial mapping qualification

- 状态：`PARTIAL`
- 对应 Goal：ER-G1（完整机制与 sharp 故事线）、ER-G2（可审计方法）、ER-G3（可信 benchmark/baseline）、ER-G4（AAMAS 可复现证据）
- `goal_change_requested=false`
- 真实 API：0；GPU：0；科学效果结论：不允许。

## 这次检查回答什么

有机闭环的四个实验因素必须分别对应可观察事件、权限边界和策略输入。否则后续 factorial 结果会把“账本里记录了某件事”误当成“策略使用了某件事”。本次只检查接口和因果顺序，不估计任何效果。

## 冻结与证据

运行前先写入配置：[config.json](../../../experiments/logs/n03_factorial_mapping_qualification_20260928_v2/config.json)。配置同时记录执行时的脚本和协议源码 SHA-256。随后用固定的 PIPE3 协议构造两个完整 episode，并在 episode 1 开始前写入引用 episode 0 evidence 的 `LaterAssignment`。原始 17 条 hash-chain 事件和映射结果保存在 [raw.jsonl](../../../experiments/logs/n03_factorial_mapping_qualification_20260928_v2/raw.jsonl)，汇总在 [summary.json](../../../experiments/logs/n03_factorial_mapping_qualification_20260928_v2/summary.json)。初版日志保留在 `n03_factorial_mapping_qualification_20260928/`；执行入口是 [peerrolebench_factorial_mapping_qualification.py](../../../scripts/peerrolebench_factorial_mapping_qualification.py)。

## 结果

底层 `PeerRoleLedger` 和独立 replay 对四个协议因素都给出可验证结构：

- **J**：`recipient_judgment → consumer_action`，绑定 recipient 和 artifact digest，顺序可回放；
- **A**：`ProducerScore` 是独立事件，能保留 producer-owned delivery 的质量状态，严格 replay 通过；
- **U**：sidecar 已有 `arrived_at/delay`，replay 按到达顺序，policy bridge 有更新入口；
- **F**：`LaterAssignment` 引用 `evidence-0`，在 task 1 启动前写入，后续 `selection-1` 消费相同 agent 与 propensity。

因此本次工程资格状态为 `QUALIFIED_OFFLINE`，账本 replay 为 `PASS`。但当前策略层只支持四个没有 A/F 的 cell：`0000`、`0010`、`1000`、`1010`（顺序为 J/A/U/F）。含 A 的 cell 缺少 producer-score/attribution sidecar；含 F 的 cell 缺少 assignment/evidence sidecar 及 policy snapshot 中的 consumption 记录。12 个 cell 被明确列为 unsupported，而不是静默当作可运行。

## 与 Goal 的对照

- 已满足：四因素的原始协议含义、事件顺序、assignment 的 ledger 消费关系都有真实可回放实例；本次日志可复核。
- 部分满足：J/U 有 policy sidecar seam，但 PIPE3 fixture 尚未提供 eligible recipient judgment，也没有把四个因素作为统一开关接入 live runner。
- 未满足：A 的 producer quality/attribution 必须进入 policy-visible replay；F 必须证明 policy 使用 evidence 形成 assignment 并影响后续选择；因此没有任何 factorial 效果证据，也没有 benchmark/baseline freeze。

缺口属于 **实现/测量接口不足**，不是实验失败、数据不准或 Goal 可以降级。当前 strict 故事线评分不因这次资格结果上调。

## 下一步

1. 设计 `ProducerScoreSidecar` 或等价 attribution-gate 字段，并将其纳入 sidecar manifest/coverage；
2. 增加 assignment/evidence sidecar，且在 decision snapshot 中保存 `assignment_consumed`、`evidence_ids` 与来源版本；
3. 只在这两个 seam 完成零调用 mutation/replay 矩阵后，才冻结真实 runner 的 J/A/U/F cells；
4. 重新检查同信息 baseline、独立 root 和完整成本，再决定是否启动下一条真实 API 链。

本报告没有申请修改任何 Goal 标准。

## 后续审计修正

独立复审发现本报告把 sidecar 的字段存在误称为可运行 policy cell，并把 assignment 与下一 selection 的字段一致误称为 policy 消费 evidence。该历史报告和 v1/v2 日志保留不改写；当前口径以 [factorial 设计审计与口径修正](20260928_factorial_design_correction.md) 和 v3 capability-audit 日志为准。当前 scientific cell 为 0/16。
