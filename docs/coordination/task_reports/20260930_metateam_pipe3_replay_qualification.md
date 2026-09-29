# Meta-Team-L2-public × PIPE3 source replay qualification — 2026-09-30

## 结论

将 `MetaTeam-L2-public` 的 fixture builder/replay 接到了真实的 PIPE3 zero-LLM public
sidecar seam。它使用 pinned PIPE3 seed-0 material、实际 `PeerRoleLedger` record hash、
`DecisionSidecar`、eligible/public `FeedbackSidecar`、`AttributionGate` 和
`PolicyFeedbackProjection`，生成 profile 后从相同 typed sidecars 重放，得到完全相同的
`profile_digest` 与 `source_input_digest`。替换 selected candidate 或公开 projection
label 会被拒绝。

这关闭的是 PIPE3 的 source binding/replay 工程子门，不是 profile 生成质量、Meta-Team
效果、baseline parity 或 role-learning 结果。运行没有调用 LLM/API，`gpu_jobs=0`，
`scientific_claim_allowed=false`。

## 运行内容

脚本：`scripts/peerrolebench_metateam_pipe3_replay_qualification.py`

1. 从 `load_pipe3(0)` 构造 pinned PIPE3 material，计算 producer delivery digest。
2. 用真实 protocol ledger 写入 selection → delivery → recipient judgment → consumer
   action → terminal outcome → role evidence update，并保留每条 `record_hash`。
3. 创建并绑定 selection/feedback sidecar；`bind_to_ledger_record` 检查 sidecar 与原生
   ledger event 的 hash/type/id 一致。
4. 用 `project_feedback` 生成只含 recipient judgment public fields 的 typed projection，
   再由 `build_public_profile_fixture` 生成定性 profile；profile 输入不读取 terminal
   outcome、完整轨迹、operator ledger 或 private scorer。
5. 用 `replay_public_profile_fixture` 从同一组 sidecar 重建 profile；错误 candidate 和
   公开 label mutation 均必须拒绝。

## 证据与失败记录

- v1 在构造 `FeedbackSidecar` 时把 PIPE3 原生 event type 写成了不存在的 `delivery`，
  得到 `KeyError`；失败回执保留在
  `experiments/logs/n03_metateam_pipe3_public_replay_qualification_20260930_v1/failure.json`。
- v2 修正 event type 后通过；v3 重新封存运行元数据、脚本 hash 和 profile-sidecar hash，
  最终 `QUALIFIED_OFFLINE`。回执目录：
  [`experiments/logs/n03_metateam_pipe3_public_replay_qualification_20260930_v3/`](../../../experiments/logs/n03_metateam_pipe3_public_replay_qualification_20260930_v3/)。
- v3 关键结果：`wrong_candidate=REJECTED`、`wrong_public_payload=REJECTED`；profile 与
  source input digest 均可重放。完整 selection/judgment/projection/profile payload 在
  `raw.json`，配置和 summary 分开保存。

## 仍未关闭的门

profile 内容是 fixture 中预先给定的定性文本，不是 Meta-Team L2 摘要模型生成；因此没有
测量摘要准确性、调用 token/延迟、profile 的 later-use 预测力、profile-only 与 L3 对照、
隔离进程的 policy-read trace、真实 next-episode assignment、独立 live history 或完整
成本。PIPE3 仍只有一个零调用 seed-0 source replay，不能作为 benchmark 结果或公平 closest
baseline。

下一小任务是把 source replay 接到 versioned PIPE3 runner 的 assignment offer/consumption
attestation，并验证 profile watermark 在下一次执行前真正可见；在真实 profile generator、
独立 history、later assignment 和完整成本通过前，保持 `MetaTeam-L2-public` 为
`NOT_IMPLEMENTED / QUALIFICATION_REQUIRED`，不启动正式 API/A800。
