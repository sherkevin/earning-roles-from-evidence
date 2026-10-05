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
- `validate_later(...)` 先运行 canonical ledger replay，再调用
  `derive_later_credit_from_ledger` 和 `build_history_binding_receipt`，并把真实 target
  judgment/terminal label 与 feedback channel 对齐；
- `apply_validated_later_credit(...)` 是严格路径的唯一更新入口。它检查 replay/binding
  digest、namespace、source evidence、assignment candidate、target policy selection、
  accepted channel 和 outcome id，然后复用 `DelayedCreditLedger.apply_once`；
- `apply_later_credit(LaterChannelPayload)` 保留为 policy-side unit seam，不能单独称作
  canonical validation；
- adapter 自己维护 assignment-level applied map，堵住 ledger 仅按
  `assignment_id + later_outcome_id` 造成的 alternate-outcome 二次更新；
- policy updater 失败或容量检查失败时恢复 policy、credit ledger 和 assignment map；
- `snapshot()/restore()` 保存策略、公开 evidence、credit ledger、namespace、容量和
  assignment-level idempotency。

## 证据

qualification runner 为 [`delayed-policy-adapter-qualification-v1`](../../../scripts/peerrolebench_delayed_policy_qualification.py)，
配置和原始事件位于：
[`experiments/logs/n03_delayed_policy_adapter_qualification_20261005_v8/`](../../../experiments/logs/n03_delayed_policy_adapter_qualification_20261005_v8/)。

结果为 `8/8 QUALIFIED_OFFLINE`：valid publish/update、duplicate no-op、alternate
outcome rejection、wrong candidate、wrong channel、closed source gate 和
snapshot/restore idempotency，以及由真实 canonical ledger fixture 驱动的 replay、
source evidence/artifact lineage、target assignment/selection/outcome binding 和 label
mutation rejection 全部通过。此前实现修订前的 v1、v2、v3 回执保留，没有覆盖历史
证据；v4/v5 的导入失败没有生成运行目录，v6/v7 也保留。snapshot digest mutation
拒绝新增后，adapter、two-stage gate、history binding/adapter 定向测试为 `26 passed`；没有
LLM/API/GPU 调用。

## 三份审核标准对照

| 标准 | 本任务关闭的部分 | 仍未满足 |
|---|---|---|
| 故事线与创新点 | 使“situated evidence → future assignment → delayed credit”具备真实 policy 状态转移的工程载体 | 不能证明角色专业化、闭环收益或论文创新优于现有方法 |
| 方法论 | 真实策略上的 publish/update 分离、canonical replay、source/target history binding、assignment 级幂等、channel/subject 绑定、回滚与恢复 | adapter 尚未拥有 preview→assignment→commit；它仍需与已有 `role_evidence_selection` composition 合并，并在独立 later histories 上验证 |
| benchmark+baseline | 为后续四格 `public evidence only / delayed update only / both` 提供可执行 adapter seam | 七臂 manifest、closest published、第二 root、独立 live parity、完整成本和 scientific baseline 仍未冻结 |

这次结果把“接口不存在/用字典假更新/不验证 later lineage”的阻塞降为“候选 adapter
已有 canonical CPU qualification”；
不允许把 `QUALIFIED_OFFLINE` 写成实时训练收益，也不允许把
`contextual_trust_linear` 写入 active baseline matrix。`goal_change_requested=false`。

## 下一步

在启动任何真实 API/A800 前，必须把 adapter 接入 canonical PIPE3 的 preview→assignment→
commit 与 `derive_later_credit_from_ledger` replay，使用独立 target history 验证四格
信息价值和 assignment-level outcome。若 canonical 接缝继续暴露责任或成本缺口，应先修复
测量并保留 UNKNOWN，而不是扩大实验规模。
