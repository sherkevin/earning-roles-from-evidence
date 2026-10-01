# PIPE3 two-stage evidence/update composition — 2026-10-01

状态：`PARTIAL`。Goal 变更：无。此任务只验证方案 A 的 CPU 工程接缝，不是科学效果或
benchmark 结果。

## 运行与结果

新 runner 使用 pinned PIPE3 material、实际 v2 sandbox producer/recipient/adoption scorer、
`RoleEvidenceOffer`、isolated public read、selection preview/commit、native ledger replay
和 `DelayedCreditLedger`。配置和 component hash 在每个 control 读取/执行前写入；默认路径
没有 unsandboxed candidate fallback。

- v1 保留在 [`n03_pipe3_two_stage_composition_20261001_v1`](../../../experiments/logs/n03_pipe3_two_stage_composition_20261001_v1/)。真实 scorer 暴露 producer patch 把 `timestamp` 写死而 seed 1 使用 `measured_at`；target scorer 返回 UNKNOWN，旧代码随后错误地把不完整 ledger 抛成 failure。
- v2 保留在 [`n03_pipe3_two_stage_composition_20261001_v2`](../../../experiments/logs/n03_pipe3_two_stage_composition_20261001_v2/)。18 次真实 sandbox scorer 调用（0 LLM API、0 GPU）后，suite `QUALIFIED_OFFLINE`，`contract_passed=true`，科学声明仍关闭。
- `producer_owned`：source Qp/Y 为完整，发布 RoleEvidenceOffer 不更新 policy；isolated read、assignment commit、target task-start 的顺序为 assignment → selection → task-start；target terminal outcome 完整，17-event ledger replay PASS，delayed credit 单次 apply，policy update=1。
- `recipient_owned` 与 `mixed`：实际 scorer/action/outcome 完成后分别得到 `PENDING_ATTRIBUTION`/`UNKNOWN`，不发布 producer evidence、不启动 target、不更新 policy；它们的 `status=UNKNOWN` 是被测保护行为，`contract_passed=true`，不能读成任务成功。

## 仍不能支持的主张

1. assignment 当前没有把不同 candidate 的 artifact/model/config 绑定成可识别 treatment；
   选择记录改变不等于实际执行者改变。
2. 当前 authored repair 可修改 `producer.py`，producer evidence 仍可能与 recipient repair
   混淆；必须把 delivered snapshot/Qp 与 recipient integration cost 分开，producer credit
   只来自预注册 producer defect 或独立 counterfactual。
3. later quality 在 composition 中仍通过 `Feedback(source="recipient_judgment")` 写回；正式
   baseline parity 前必须改为 `terminal_outcome` channel，并预注册哪些 policy 可以读取。
4. RoleEvidenceOffer 仍以独立 qualification 的 `GENESIS` auxiliary root 读取，尚未接入
   canonical boundary 的 append-only auxiliary manifest。
5. judgment/action 仍是 parent-authored control；尚未有真实 recipient judgment 或 blinded
   judge 的 situated signal。

因此 v2 只关闭“责任门→公开证据→隔离读取→执行前 assignment→后续 outcome→延迟更新”
的有限 CPU contract/replay 子门，不解冻 ArtifactRole benchmark、baseline parity、真实
LLM pilot 或 A800。下一步先修上面的 treatment、归因和 feedback-channel 问题，再讨论
独立 history 与实时更新效果。
