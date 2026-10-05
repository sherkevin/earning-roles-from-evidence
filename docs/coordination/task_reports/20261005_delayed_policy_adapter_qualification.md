# Delayed policy adapter qualification — 2026-10-05

状态：`PARTIAL`。本任务只关闭方法合同中的一个可执行接口缺口，不改变
`GOAL.md`、active storyline、method、benchmark 或 baseline manifest，也不构成科学效果。

## 目的与硬标准

方法 v1.1 要求把 `publish(source_episode)` 与 `update(later_credit)` 分成两个
可独立消融的入口：公开责任证据可以进入未来 assignment 的输入，但发布本身不得改变
持久策略。只有目标任务已经完成、候选/selection/feedback channel 可重放绑定后，
selected-only delayed credit 才能更新策略。此前的 two-stage qualification 使用字典
模拟 updater，不能证明真实 policy state 改变；`DelayedCreditLedger` 的默认键
`assignment_id + later_outcome_id` 也不能单独保证一个 assignment 只更新一次。

本任务的可量化验收条件是：

1. 发布前后真实 `FeatureContextualTrustPolicy` 的 state digest 和 `updates` 相同；
2. 延迟阶段只接受目标 selection 的真实 `recipient_judgment` channel，且目标选择的
   candidate 必须等于 published evidence subject；
3. 同一 assignment 的重复 credit 是幂等 no-op，替换 outcome、错候选、错 channel、
   source evidence id 冒充 target selection 和关闭 source gate 均 fail-closed；
4. snapshot/restore 保留 public evidence 与 assignment-level 幂等状态；
5. config、raw JSONL、summary 在运行前/中/后落盘，明确 `real_api_calls=0`、
   `gpu_jobs=0`、`scientific_claim_allowed=false`。

## 实现

新增 [`peerrolebench_delayed_policy_adapter.py`](../../../scripts/peerrolebench_delayed_policy_adapter.py)：

- `publish(offer, source_gate)` 只保存 typed `RoleEvidenceOffer` 的公开字段和 subject
  digest，不把 role evidence 转成 `Feedback`；状态容量上限为 1 MiB；
- `apply_later_credit(LaterChannelPayload)` 是唯一可触发真实策略更新的入口。它检查
  namespace、source evidence、assignment candidate、target selection、accepted channel、
  outcome id 和 selected-only flags，然后复用 `DelayedCreditLedger.apply_once`；
- adapter 自己维护 assignment-level applied map，堵住 ledger 仅按
  `assignment_id + later_outcome_id` 造成的 alternate-outcome 二次更新；
- policy updater 失败或容量检查失败时恢复 policy、credit ledger 和 assignment map；
- `snapshot()/restore()` 保存策略、公开 evidence、credit ledger、namespace、容量和
  assignment-level idempotency。

## 证据

qualification runner 为 [`delayed-policy-adapter-qualification-v1`](../../../scripts/peerrolebench_delayed_policy_qualification.py)，
配置和原始事件位于：
[`experiments/logs/n03_delayed_policy_adapter_qualification_20261005_v3/`](../../../experiments/logs/n03_delayed_policy_adapter_qualification_20261005_v3/)。

结果为 `7/7 QUALIFIED_OFFLINE`：valid publish/update、duplicate no-op、alternate
outcome rejection、wrong candidate、wrong channel、closed source gate 和
snapshot/restore idempotency 全部通过。此前实现修订前的 v1 回执保留在
`..._v1/`，中间版本 v2 也保留，没有覆盖历史证据。定向测试为 `12 passed`（adapter + existing two-stage
gate）；没有 LLM/API/GPU 调用。

## 三份审核标准对照

| 标准 | 本任务关闭的部分 | 仍未满足 |
|---|---|---|
| 故事线与创新点 | 使“situated evidence → future assignment → delayed credit”具备真实 policy 状态转移的工程载体 | 不能证明角色专业化、闭环收益或论文创新优于现有方法 |
| 方法论 | 真实策略上的 publish/update 分离、assignment 级幂等、channel/subject 绑定、回滚与恢复 | canonical ledger replay、preview→assignment→commit 的 live composition、独立 later histories 仍未接入该 adapter |
| benchmark+baseline | 为后续四格 `public evidence only / delayed update only / both` 提供可执行 adapter seam | 七臂 manifest、closest published、第二 root、独立 live parity、完整成本和 scientific baseline 仍未冻结 |

这次结果只把“接口不存在/用字典假更新”的阻塞降为“候选 adapter 已有零调用资格”；
不允许把 `QUALIFIED_OFFLINE` 写成实时训练收益，也不允许把
`contextual_trust_linear` 写入 active baseline matrix。`goal_change_requested=false`。

## 下一步

在启动任何真实 API/A800 前，必须把 adapter 接入 canonical PIPE3 的 preview→assignment→
commit 与 `derive_later_credit_from_ledger` replay，使用独立 target history 验证四格
信息价值和 assignment-level outcome。若 canonical 接缝继续暴露责任或成本缺口，应先修复
测量并保留 UNKNOWN，而不是扩大实验规模。
