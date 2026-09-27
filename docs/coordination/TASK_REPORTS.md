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
