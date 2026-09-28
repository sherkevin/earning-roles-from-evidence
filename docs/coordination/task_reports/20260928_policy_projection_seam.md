# 2026-09-28 typed policy projection seam

- 状态：`PARTIAL`
- 对应 Goal：ER-G1（situated evidence 可识别）、ER-G2（责任边界可验证）、ER-G4（主张与证据一致）
- `goal_change_requested=false`
- 真实 API：0；GPU：0；科学效果主张：不允许

## 这一步解决的具体问题

现有 `FeedbackSidecar` 为了审计而保留了 scorer/operator 的完整字段：
`raw_value`、`responsibility_status`、`attribution_basis` 和 mapping digest。若直接把
sidecar 交给在线 policy，策略可以绕过公开责任闸门读取评分器内部信息；这会破坏
“recipient 的 situated judgment 经责任归因后才成为可学习 evidence”的故事线，也会
令 J/A/U/F 的信息边界无法解释。

本任务新增 `scripts/peerrolebench_policy_projection.py`，将 operator-only 的
`AttributionGate` 与 policy-visible 的 `PolicyFeedbackProjection` 分开。projection
只携带 feedback identity、candidate version、evidence version、source index、到达
时间、action、eligible/unknown disposition，以及通过 gate 的 label。gate 现在有
canonical digest，并绑定 ledger record、sidecar digest、protocol/source/selection
event、delivery、producer/version、recipient 与 label mapping；调用还必须提供 sealed
`DecisionSidecar`，由它核验 selected-only 的 chosen candidate。`public_payload()` 不
包含 raw scorer value、责任理由、mapping digest、gate digest、operator weight 或其他
operator 状态。UNKNOWN projection 的 `to_feedback()` 返回 `None`，因此不能更新
controller。

## 验证与保留的失败

测试文件 `tests/test_peerrolebench_policy_projection.py` 覆盖 17 个断言，包括 eligible
最小投影、UNKNOWN no-update、非公开升级、delivery/producer/version 三种 lineage
变异、label mapping/label 变异、跨 event/recipient/ledger/selection 变异、未选中
peer、private label 和非有限时间。qualification 运行记录按配置→raw JSONL→summary
写入：

- v1 `experiments/logs/n03_policy_projection_qualification_20260928_v1/`：全部单例
  断言通过，但脚本错误地把 8 个 case 计成 7，状态为 `FAILED_OFFLINE`；日志保留。
- v2 `..._v2/`：修正 case 计数后通过，但随后发现没有检查 mapping-version 变异；不把
  它当作最终资格记录。
- v3 `..._v3/`：9 个 case 全部通过，状态 `QUALIFIED_OFFLINE`，但独立复审随后发现
  UNKNOWN 升级、label 替换和跨 event lineage 漏洞；不把它当作最终资格记录。
- v4 `..._v4/`：18 个强化 case 全部断言通过，但脚本把 18 个 case 计成 19；失败日志
  保留。
- v5 `experiments/logs/n03_policy_projection_qualification_20260928_v5/summary.json`：
  18 个强化 case 全部通过，状态 `QUALIFIED_OFFLINE`，`scientific_claim_allowed=false`。
- v6 `experiments/logs/n03_policy_projection_qualification_20260928_v6/summary.json`：
  在最终源码快照上重跑同一 18 格矩阵并通过；这是当前可引用的离线资格记录。

## 不能由此推出的结论

这只是 typed boundary 的零调用资格检查；它也不是进程级隐私或恶意代码隔离，因为
projection 与 policy 仍在同一 Python address space，private 字段只是没有序列化到
policy payload。它没有证明 producer scorer 正确、真实 runner 能产生完整 lineage、
policy 在下一次 assignment 前确实消费 evidence，也没有证明 RARE-Anchor 或任何
更新器带来效果。因此 active method、benchmark/baseline 和故事线仍保持 `NOT_READY`；
不会启动真实 API 或 A800。

## 下一步

把 projection 接到 root-specific PIPE3 runner，并增加两类不可绕过的事件：

1. assignment/evidence-consumption attestation，证明 F 条件下 policy 在执行前读取了
   sealed evidence，而不是仅在 ledger 中写入 assignment；
2. event-time interleaving，证明 feedback 在 `t+1` decision watermark 前到达时改变
   下一次 probability/state digest，迟到事件只进入预定义 correction queue。

完成这两项离线 mutation qualification 后，才可以冻结 16-cell factorial 的输入/状态
转移，再考虑新的真实 API 小链和同信息 baseline。
