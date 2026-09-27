# 2026-09-28 canonical policy sidecar stream replay

## 任务

把 sidecar bridge 放到完整 strict `PeerRoleLedger` 之后验证，避免把简化 record 的单事件单测误报成真正的 ledger replay。

## 实现

- [`scripts/peerrolebench_policy_sidecar_replay.py`](../../scripts/peerrolebench_policy_sidecar_replay.py) 先调用 `replay_ledger_events(..., allow_incomplete=True)`；canonical ledger 不是 `PASS` 时 policy 更新关闭。
- sidecar 必须以 `(event_type,event_id)` 一对一覆盖 ledger 中的 selection/judgment/terminal 事件，且带非空 sidecar digest；record hash、event identity、时间差和 selected producer/version 均检查。
- selection 按 canonical ledger index 注册；feedback 输入可以被置换，但按预注册的 `(arrived_at, protocol_event_id)` 顺序重放。Beta policy 的更新顺序因此不被含糊地当作可交换。
- eligible public feedback 才进入 policy；UNKNOWN/pending/non-public 只计审计；重复 sidecar 直接 INVALID，错误 producer lineage 直接 INVALID。

## 实际验证

```text
python3 scripts/peerrolebench_policy_sidecar_stream_qualification.py \
  --out-dir experiments/logs/n03_policy_sidecar_stream_qualification_20260928_v2
```

提交 `1d93fc0` 的代码先执行 v1；提交 `ac1f279` 后的 v2 作为最终记录。完整 strict fixture 的 5 个 case 全部通过：canonical 更新 1 次；feedback permutation 与 canonical snapshot 相同；duplicate sidecar 为 INVALID 且 0 次更新；truncated canonical ledger 为 UNKNOWN 且关闭更新；wrong producer/version 为 INVALID 且 0 次更新。

该 qualification 使用内存中确定性 protocol fixture，`real_api_calls=0`、`gpu_jobs=0`、`scientific_claim_allowed=false`；它证明 replay gate 的工程边界，不证明 benchmark、role efficacy 或实时训练效果。

## Goal 对照

| 标准 | 状态 | 说明 |
|---|---|---|
| situated judgment→role evidence 主线 | `MAINTAINED` | 只收紧证据绑定，不改故事线或创新点 |
| policy 更新可审计、可回放 | `QUALIFIED_OFFLINE` | canonical ledger、sidecar coverage、乱序、UNKNOWN、lineage case 通过 |
| benchmark/baseline 公平比较 | `OPEN` | 还没有真实 PIPE3 sidecar 或冻结 baseline card |
| 科学效果/实时训练/A800 | `OPEN` | 本任务无 API/GPU，没有效果结论 |
| Goal 变更 | `UNCHANGED` | 无降级或修改请求 |

## 尚未解决

真实 runner 仍要生成 sidecar manifest 并与 append-only ledger 做一对一 attestation；当前只验证 sidecar digest 与 record hash 的离线关系，尚未把 sidecar digest 写成 protocol event。PIPE3、第二 root、baseline freeze、真实 API 和 A800 仍未解锁。
