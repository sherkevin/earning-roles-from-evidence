# 2026-09-29 PIPE3 pending-attribution replay audit

- 状态：通过；0 API、0 GPU
- 证据：[n03_pipe3_pending_replay_audit_20260929_v2](/Users/jingwu/work/earning-roles/experiments/logs/n03_pipe3_pending_replay_audit_20260929_v2)
- 失败尝试：[v1](/Users/jingwu/work/earning-roles/experiments/logs/n03_pipe3_pending_replay_audit_20260929_v1) 保留；仅因 tuple/list 比较造成 harness 自身误报，随后 v2 修正。

对 v6 的七事件 ledger 使用 `replay_ledger_events(..., allow_incomplete=True)`。结果为
`UNKNOWN`，唯一缺失阶段是 `role_evidence_update`，没有 hash、顺序或协议错误。审计因此
确认：v6 是“terminal outcome 已完成、role evidence 有意等待归因”的合法诊断状态，
不是崩溃；`policy_update_allowed=false`。

这同时暴露出当前严格 replay 的表达限制：它把 role evidence 当作 delivery 完整性的
必需事件，尚未原生表示 attribution sidecar。下一步需要在协议/adapter 层显式区分
observed terminal outcome、attribution review 和 eligible policy evidence，再考虑 later
assignment。没有这层分离，不能启动学习效果实验。
