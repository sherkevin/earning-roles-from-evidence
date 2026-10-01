# ADR 0043 — Two-stage evidence publication and delayed policy update

- **状态**：Accepted
- **日期**：2026-09-30
- **范围**：方案 A；责任归因、未来分派和持久更新的时序
- **取代**：无；本决议细化 0019、0022、0028，不改变其责任边界

## 背景

PIPE3 的资格 runner 将“可归因事实公开给未来分派”和“改变持久策略状态”合并成一个门。这样 producer-owned 的诊断事件虽然可以被归因为候选事实，却不能形成可引用的 role evidence；而 `LaterAssignment` 又必须引用已登记的 evidence。独立代码审查确认，这不是原生 ledger 必然要求 `task_start` 依赖 `LaterAssignment`，而是 runner 的发布策略造成的闭环。若直接把诊断 `ELIGIBLE` 当训练标签，又会把责任归因和策略学习混为一谈。

## 决议

采用两阶段语义，并把三个状态分开记录：

1. `attribution_eligible`：源 episode 的 producer contract、recipient judgment、实际 action、terminal outcome、artifact digest 和顺序完整绑定；recipient-only、mixed ownership、缺失/UNKNOWN 或 later outcome 单独出现都不能通过。
2. `evidence_publish_allowed`：通过第一层的源事实可以写入不可变、带版本和 digest 的公共 role evidence，供后续任务在执行前引用。发布不等于更新；发布阶段不得调用持久 policy updater。
3. `policy_update_allowed`：只有后续 assignment 已在该 evidence 的封存快照上执行，且该后续任务产生完整 later-use outcome 后，才允许对持久状态进行一次 selected-only delayed credit。later outcome 只能评价未来 assignment/use，不得重写源 episode 的 producer label，也不得把 recipient repair 归因给 producer。

事件顺序固定为：

```text
source episode
  -> attribution gate
  -> immutable evidence publication
  -> pre-execution assignment/read cut
  -> later task selection and outcome
  -> delayed policy update
```

源 evidence 在发布和分派时只进入公开快照；未来结果在它产生前不可见。UNKNOWN、INVALID、重复、乱序或无法重放的事件都是 no-op，并保留独立 UNKNOWN 分母。late correction 只影响 correction 到达后的未来快照；已封存 assignment 不回写。

## 兼容性与实现约束

- 不新增或伪造 `RoleEvidenceUpdate` 以绕过 strict ledger；只有 source terminal outcome 完成后才登记原生 evidence，再登记 `LaterAssignment`。
- 发布阶段调用 selection boundary 时必须 `consume_evidence=False`；只有 later outcome 到达、通过 parent replay gate 后，才允许 `consume_evidence=True` 的 selected-only updater。
- `LaterAssignment` 必须在目标 selection 和 task start 之前写入，并保持 agent 与 propensity 一致。
- 原有 ledger/replay schema 保持兼容；临时的“候选 evidence 可见”状态放在辅助 manifest/trace 中，不冒充已训练的 evidence。

## 反例与验收

必须有 CPU 资格测试覆盖：producer unchanged + later outcome 不产生源 evidence；recipient-only/mixed change 为 UNKNOWN；source FAIL 不因 later PASS 被改写；发布后持久 policy digest 不变；later outcome 后最多一次更新；重复/乱序/correction 幂等；assignment 先于 selection；无 assignment 的 `task_start` 仍按原生 ledger 规则单独测试。

## 后果

这会增加一个可审计的 delayed-credit 阶段和 assignment-level 指标，但保留原有 ledger/replay。它使“证据影响未来责任”和“策略真正学习”成为两个可分别消融的因素，也明确了在真实 API/A800 之前必须先完成的 CPU qualification。该决议不锁定 backbone、updater 或 benchmark，不降低 Goal 标准。

