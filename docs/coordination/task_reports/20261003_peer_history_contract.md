# 2026-10-03 最小持久 peer history contract（设计前置）

## 为什么需要它

PIPE3 的 source→target 接缝已经可以零调用回放，但如果所有 peer 使用同一模型、同一
prompt、fresh call 且没有合法持久状态，那么 assignment 的变化无法解释为 peer
suitability 学习。该问题是 N02 已观察到的 exchangeability 缺口。本报告只记录一个
待 runner 实现的最小 contract，不修改 active method、benchmark 或 Goal，也没有调用
API/GPU。

## 最小状态

每个 peer 初始状态完全相同；`peer_id` 只用于 lineage，不注入预置能力差异。可实现的
`PeerHistoryV1` 包含：

```text
agent_key,
entries[
  subject_key, role_signature_hash, execution_state_fingerprint,
  delivery_digest, judgment_id/label, outcome_id/label,
  metric_digest, cost(tokens/tool_calls/wall_ms), arrival_index
],
aggregate[scope_key] = {
  n_pass, n_fail, n_unknown, smoothed_rate, cost_mean, last_arrival
}
```

`agent_key`/`subject_key` 是 opaque registry IDs。初始 entries 和 aggregate 必须为空且
相同，禁止初始化 expert prior。第一条记录只能由真实 source→target 链产生；
`UNKNOWN` 保留 provenance 但不提供正向支持。

## 信息边界与写入时机

每条记录绑定 `(subject_peer_id, role_signature_hash, execution_state_fingerprint,
delivery_digest, recipient_judgment_id, later_outcome_id)`。selector 在后续 read cut
只能看到每个候选的 scope、计数、平滑统计、成本区间、版本 hash、样本数和 evidence
digest；不能看到原始 artifact、expected/gold、task-id 路由信号、recipient 私有文本
或 hidden scorer。agent 本地可以保留自己的 history，但共享 evidence 只能通过 parent
ledger projection 进入 selector，不能修改已经封存的 assignment。

`E0` 必须按 source→target 完成：source peer A 交付，peer B 接收并判断/使用；assignment
封存后，独立 terminal outcome 到达，才能把 attribution record append 到 A 的 history。
`E1` 使用新 task/material 和 E0 结束前冻结的 candidate menu，让 selector 读取 A/B
history 再选择；E1 的 judgment/outcome 只能在 selection 和 task 完成后写入，不能反写
E1 的选择。

## 最小可证伪矩阵

正式开发流至少保留 `history`、`no-history`、`history-shuffled` 和 `reset-history`
四个对照，记录 pre/post probabilities、propensity、terminal quality、attribution
errors、update latency 和完整成本。若 E1 不优于 no-history，或打乱 peer ID 后效果不变，
则不能把收益归因给 peer experience；若跨 role/state 聚合提升而没有同 scope evidence，
说明存在归因泄漏；若 E0 反馈在 assignment seal 前改变选择，违反 delayed read-cut。

两 episode 只足以检查协议和最小可学习性，不能证明稳定专业化、跨 root 泛化或最终方法
收益。该 contract 是下一 runner 的放行条件，不是已完成的科学证据。

## 零调用实现回执

`scripts/peerrolebench_peer_history.py` 已实现 `AssignmentSealV1`、`HistoryEntryV1`、
`HistoryCostV1` 和 `PeerHistoryV1`；它拒绝未 seal 追加、重复或 scope 不匹配 lineage，
并把 UNKNOWN 计入审计但不计入正向平滑率。`selector_projection()` 只输出 scope 聚合、
成本和 digest，不输出 artifact、task、gold、private text 或 raw prompt。

- v1 receipt：`experiments/logs/n03_peer_history_qualification_20261003_v1/`，一个平滑率
  断言写错，`FAILED_OFFLINE`，失败已保留；
- v2 receipt：`experiments/logs/n03_peer_history_qualification_20261003_v2/`，5/5
  `QUALIFIED_OFFLINE`，0 API、0 GPU；
- focused tests：`tests/test_peerrolebench_peer_history.py`，5 passed。

这仍只是状态/投影工程子门；真实 E0/E1、同信息对照、later-use 和科学结果没有运行。

`goal_change_requested=false`。
