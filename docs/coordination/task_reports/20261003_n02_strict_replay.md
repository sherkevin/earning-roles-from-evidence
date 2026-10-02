# N02 v3 真实 API ledger 严格归因回放

日期：2026-10-03  
状态：`PARTIAL / HISTORICAL-GATE RECONCILIATION`；真实 judgment、action 和 terminal
outcome 已存在，但 producer correctness/defect registration 缺失，因此旧 evidence
路径不能通过当前方法门。

## 输入与方法

只读读取冻结的 N02 v3 真实 API 回执：

```text
experiments/logs/n02_peerrole_dev_v3_20260926/
```

两个 episode 的 ledger 均包含真实 `RecipientJudgment`、`ConsumerAction`、
`TerminalOutcome`、`RoleEvidenceUpdate` 与 episode-0 的 `LaterAssignment`。卡片和
summary 同时明确 `objective_producer_quality = not independently measured`，ledger
没有 `ProducerScore`。新增 `scripts/peerrolebench_n02_v3_replay.py` 将真实字段映射到
当前 responsibility gate；producer score 保持 `UNKNOWN`，没有从 consumer score 或
terminal success 推断 producer label。

## 结果

命令：

```bash
python3 scripts/peerrolebench_n02_v3_replay.py \
  --output experiments/logs/n03_n02_v3_strict_replay_20261003_v2
```

结果：`REPLAY_QUALIFIED_UNKNOWN`，2/2 episode 通过保守回放；
`ELIGIBLE=0`、`PENDING_ATTRIBUTION=2`、`UNKNOWN=0`、`label_count=0`、
`policy_update_allowed=false`。历史 ledger 中的 2 条 role-evidence 记录均被当前 gate
判定为不可用于 producer attribution；旧 receipt 未改写，回放结果单独保存并绑定
summary/ledger SHA256。

## 这说明什么

N02 的问题不是“没有 recipient 信号”：真实模型确实产生了 `accept_with_rework`，
并且实际只改了 recipient-owned `mqueue/consumer.py`，终局行为检查也完成。真正缺口
是没有独立 producer Qp/contract-defect registration；因此 recipient repair 与终局成功
不能安全地变成 producer role evidence。这个回放验证了 active method v1.1 的责任边界，
也解释了为什么历史 N02 的 evidence transfer 和 assignment 不能当作方法效果。

## Goal 对照

| Goal 要求 | 状态 | 说明 |
|---|---|---|
| 真实 recipient situated judgment | `OBSERVED / DIAGNOSTIC` | 2 个真实 API episode 均有 judgment/action/outcome |
| producer evidence 可归因 | `BLOCKED_BY_EVIDENCE` | 无独立 producer score/registered defect |
| evidence→future assignment | `HISTORICAL PATH REJECTED` | 旧 evidence 存在，但当前 gate 不接受 |
| 未见任务 quality/cost | `OPEN` | 没有合法 source evidence，不能解释后续 assignment |
| 实时更新/A800 | `NOT_RUN` | N02 预算已耗尽，且方法资格未通过 |

## 下一步

不重启 N02、不修改历史 ledger。下一条真实小链使用已探明的 PIPE3 seam：在 producer
交付封存后独立测 Qp/registered defect，在 recipient action 中记录 ownership，生成
independent later outcome，再由 `evaluate_source_gate`、typed role-evidence offer 和
preview→commit assignment 串起来。小链失败仍保留 UNKNOWN，不进入 baseline effect 或
A800。

`goal_change_requested=false`；未修改 Goal、active method 或 benchmark/baseline。
