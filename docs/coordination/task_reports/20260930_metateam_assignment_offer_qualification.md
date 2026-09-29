# Meta-Team profile assignment offer/consumption qualification — 2026-09-30

## 结论

在已通过的 profile/source replay seam 上增加了 profile-specific assignment offer 和
consumption attestation。offer 固定候选菜单、profile payload、profile digest、decision index
和 read-cut；attestation 固定本次真正纳入 assignment 输入的 profile IDs、offer digest 和
policy input digest。profile watermark 尚未到达、profile 不属于候选菜单、profile 来自当前
或未来 decision 的情况都会被拒绝。

这只是零调用 protocol contract，不能证明隔离进程中的 policy 实际读了 profile，也不能证明
Meta-Team profile 能改善 later assignment、质量或成本。运行 `real_api_calls=0`、
`gpu_jobs=0`、`scientific_claim_allowed=false`。

## 实现与检查

新增 `MetaTeamAssignmentOffer` 和 `MetaTeamAssignmentAttestation`，复用既有的 canonical
SHA-256/digest 约定，但不把 qualitative profile 强行编码成 numeric label。offer payload
包含每个 profile 的固定定性字段；attestation 的 `policy_input_digest` 只由 offer digest、
消费的 profile IDs 和 read-cut 计算，后续 live runner 可把它和隔离 policy 的输入回执对齐。

qualification 还覆盖：

- valid profile consumption at a later decision；
- profile availability after arrival watermark；
- UNKNOWN/unselected/terminal projection 不得生成 public profile；
- profile correction/supersedes、source/profile/attestation digest mutation；
- wrong candidate、wrong public payload 和过早 assignment offer 的拒绝。

## 证据

- 脚本：`scripts/peerrolebench_metateam_profile_qualification.py`
- 定向 schema/offer 检查：**14 passed**
- 完整 `test_peerrolebench_*.py`：**279 passed**
- 最终回执：[`experiments/logs/n03_metateam_public_profile_qualification_20260930_v10/`](../../../experiments/logs/n03_metateam_public_profile_qualification_20260930_v10/)
- 最终 fixture qualification：13 个语义检查均为 `PASS`；配置明确 0 API/0 GPU。

## 边界与下一步

本任务没有执行真实 selector、没有启动下一 episode、没有测量 profile 摘要调用和成本，
也没有实现隔离进程 policy-read trace。attestation 可以由一个诚实的 runner 正确生成，
但不能单独防止恶意 policy 伪造“已读取”。下一步把该 offer/attestation 接入 versioned
PIPE3 runner，令 assignment 在执行前消费已到 watermark 的 profile，并将独立 live history、
真实 profile generator、完整成本和 replay 纳入同一 cell；在此之前 Meta-Team-L2-public
仍为 `NOT_IMPLEMENTED / QUALIFICATION_REQUIRED`，baseline 仍 `NOT_FROZEN`。
