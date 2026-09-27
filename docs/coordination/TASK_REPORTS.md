# Task reports

每个小任务完成后必须在 `docs/coordination/task_reports/` 写一份报告，并与
[`GOAL.md`](GOAL.md) 对照。报告不能只写“做了什么”，必须回答：

1. 本任务对应 Goal 的哪条硬标准；
2. 运行前冻结了什么，真实使用了什么 API/fixture，原始证据在哪里；
3. 哪些标准已满足、哪些只部分满足、哪些未开始；
4. 未完成的具体原因是实现缺陷、任务/评分缺陷、证据不足还是外部阻塞；
5. 下一步修复是什么，是否需要用户决定；
6. 是否存在 Goal 变更请求。没有用户明确同意时，必须写 `goal_change_requested=false`。

固定状态含义：`COMPLETE` 只表示对应 Goal 条目有足够证据；`PARTIAL` 表示工程或
协议进展但科学门未过；`OPEN` 表示尚未取得证据；`UNKNOWN` 表示运行无法判定；
`BLOCKED_BY_EVIDENCE` 表示继续运行前必须先修复测量/资格问题。失败不会自动变成
Goal 修改。

## Reports

- [2026-09-27 Goal reconciliation](task_reports/20260927_goal_reconciliation.md)：
  当前故事、方法、benchmark、实验和论文状态的第一份逐项对照；未请求 Goal 降级。
- [2026-09-27 recipient runtime probe](task_reports/20260927_recipient_runtime_probe.md)：
  recipient payload、selected delivery 和有限 lineage hash-chain 的运行时边界检查；未请求 Goal 降级。
- [2026-09-27 ledger replay gate](task_reports/20260927_ledger_replay_gate.md)：
  parent-side ledger 的 hash/因果回放和变异矩阵通过；仍是协议资格，不是 benchmark 或在线学习结果。
- [2026-09-27 runner replay integration](task_reports/20260927_runner_replay_integration.md)：
  将 replay gate 接到真实 runner 的恢复、role update 和 episode summary 边界；未重跑历史实验。
- [2026-09-27 runner boundary qualification](task_reports/20260927_runner_boundary_qualification.md)：
  用保存的真实 ledger 验证中断、retry 和 scorer 异常的 UNKNOWN/拒绝语义；hidden scorer IPC 仍开放。
- [2026-09-27 scorer IPC preflight](task_reports/20260927_scorer_ipc_preflight.md)：
  记录 digest 混淆失败并修正；独立 private scorer 与 candidate read denial 通过，真实 runner 接入仍开放。
- [2026-09-27 producer scorer contract qualification](task_reports/20260927_producer_scorer_contract_qualification.md)：
  producer-only 五格零 LLM 矩阵区分 buggy/correct/near-miss，并发现独立 consumer scorer 与旧 parent scorer 的实际差异；producer event、live runner 和 benchmark 资格仍开放。
- [2026-09-27 producer-score event replay](task_reports/20260927_producer_score_event_replay.md)：
  新增独立 producer-score protocol event、状态/digest 约束和 replay causal order；旧 N02 ledger 回归通过，真实 runner/controller 接入仍开放。
- [2026-09-27 runner producer-score boundary](task_reports/20260927_runner_producer_score_boundary.md)：
  可选 scorer 已接到 delivery→judgment 边界并写入独立 ProducerScore；旧 N02 不重跑，controller/A800 仍未启动。
- [2026-09-27 producer scorer mutation matrix](task_reports/20260927_producer_scorer_mutation_matrix.md)：
  P5/P6/P7 扩展到 dict/list、tie-break、10k/20+20 并发和 response mutation；资源失败保留 UNKNOWN，benchmark/scorer qualification 仍未锁定。
- [2026-09-27 producer scorer seed regression](task_reports/20260927_producer_scorer_seed_regression.md)：
  seed 1/2 类名与 transport/malformed mutation 回归通过；seed 2 压力 worker-exit 保留 UNKNOWN，第二 root/baseline/真实 API 链仍开放。
