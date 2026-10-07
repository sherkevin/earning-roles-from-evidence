# PIPE1 offline adapter qualification — 2026-10-07

状态：`QUALIFIED_OFFLINE_ADAPTER`。本轮把已存在的零调用契约接成一个可复用的
source→target adapter，用于在将来进入真实 route 前检查 task identity、ledger
replay、candidate menu/propensity、source→target 顺序、责任归属和 UNKNOWN
no-update 规则。没有调用模型 API、生成器、候选程序或 GPU，也没有更新任何策略。

## 为什么做这一层

此前的 route receipt validator 和 preflight 已经能拒绝材料错配，但还缺少一个把
已有 PIPE3/ledger 合同投影成 PIPE1 source→target fixture 的窄接缝。直接复制 N02
runner 会重新引入“接收方返工即上游奖励”的归因错误，因此本轮只复用已有合同，
不复用 N02 controller update。

## 实现

新增 `scripts/peerrolebench_pipe1_offline_adapter.py`：

- 统一检查 task-bearing events 的 `task_id`，再调用已有 ledger key binding 和
  replay validator；
- 调用已有 source→target schedule 与 selection receipt validator，固定候选版本、
  menu、chosen index、propensity 和 event-time 顺序；
- 用已有 `classify_ownership()` 标出 `ELIGIBLE`、`PENDING_ATTRIBUTION` 和
  `UNKNOWN`，并在不确定时通过 `unknown_no_update()` 关闭 label、assignment 与
  policy update；
- 合法离线 fixture 返回 `READY_FOR_ROUTE`，但始终返回
  `policy_update_allowed=false`。这只表示 route 前的合同准备好，不表示真实 route
  已执行，也不产生科学结果。

route receipt 的 native material digest、shared structural root、provider/timezone、
真实 message/artifact/Executor/Verifier lineage 仍由独立 preflight 检查；adapter
没有复制这些门。

## 验收与失败记录

执行前先冻结配置于
[`config.json`](../../../experiments/logs/n03_pipe1_offline_adapter_qualification_20261007_v1/config.json)，
源码和测试哈希也写入回执。初次 shell wrapper 使用了 zsh 的只读变量名
`status`，pytest 尚未启动；该 wrapper 失败保存在
[`shell_command_failure.txt`](../../../experiments/logs/n03_pipe1_offline_adapter_qualification_20261007_v1/shell_command_failure.txt)。
改用 `rc` 后重新执行，结果为：

- adapter + 既有 PIPE3 contract：`9 passed`；
- adapter 与测试文件 `py_compile`：通过；
- 合法 fixture 通过，task-id、ledger hash、schedule、menu、ownership、UNKNOWN
  和 no-update 的篡改均 fail-closed；
- 一次早期 fixture 误把序列化事件中的 task id 事后改写，触发 native
  `record_hash_mismatch`；测试随后改为从 PIPE1 task id 构造 ledger，保留 hash 链约束。

完整回执见
[`summary.json`](../../../experiments/logs/n03_pipe1_offline_adapter_qualification_20261007_v1/summary.json)。
本轮计数为 0 API、0 generator、0 candidate、0 GPU、0 policy update，
`scientific_claim_allowed=false`。

## Goal 对照与下一步

本轮只关闭了“已有离线合同无法组合为 PIPE1 接缝”的工程缺口。它没有证明真实
actor 交付、Verifier 终局质量、后续 assignment 收益、peer selection 改善、任务
泛化、baseline parity 或实时训练效果；三份验收标准和投稿 gate 继续保持原状态，
Goal 没有降级。

下一步应把该 adapter 接到一个**不产生策略更新**的 source→artifact→Executor→Verifier
离线投影，再让 route receipt/material preflight 在执行前消费它；只有这条链完成并
获得新的预算与真实 API 配置后，才讨论受限 live episode。
