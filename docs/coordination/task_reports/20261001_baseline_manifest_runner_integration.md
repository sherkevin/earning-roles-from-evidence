# Task report — baseline manifest consumed by offline runner (2026-10-01)

## 状态

`PARTIAL`。manifest 已进入离线 matrix runner 的启动/回执路径，但尚未连接真实
canonical ledger 或 live episode；`goal_change_requested=false`。

## 变更

`PolicyMatrixRunner.run` 现在可接收并校验 `RootRunnerManifest`，要求 manifest 的
registry digest 和 schedule digest 与本次输入一致；回执保存 `manifest_digest`。离线
fixture suite 为每个 case 建立独立 manifest，固定 `offline_policy_matrix:<case>`、
当前 commit、source/generator/scorer hash、schedule/registry digest、seed、RNG、可见性
规则和零 API 预算。错误 schedule digest 的 manifest 会在 runner 启动时拒绝。

相关实现为 [`peerrolebench_policy_matrix_runner_v1.py`](../../../scripts/peerrolebench_policy_matrix_runner_v1.py)，
测试新增了正确 manifest 和错误 manifest 两个路径。

## 证据

[`n03_policy_matrix_runner_20261001_v13`](../../../experiments/logs/n03_policy_matrix_runner_20261001_v13/)
的回执为 `QUALIFIED_OFFLINE`，manifest digest 出现在每个 case 的 config 和结果中；
0 API、0 GPU、`scientific_claim_allowed=false`。PeerRoleBench 回归为 360 passed。

## 边界

这只证明 runner 不会忽略 root identity；它没有证明 root 的真实 task material、
scorer、later assignment 或 outcome 已正确接入。schedule 仍由 hand-authored offline
fixture 提供，成本仍是 `measured=false`，contextual-vs-RARE 仍未形成同信息 live
comparison。因此 benchmark/baseline 仍未冻结，不能启动正式效果 API/A800。

## 下一步

将 manifest 校验移到 PIPE3/PIPE2 的 canonical-ledger runner，先做零调用 replay 和
mutation rejection，再由作者确认第二 root authority A–D，最后才进入 live baseline
history。
