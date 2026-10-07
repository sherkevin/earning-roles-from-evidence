# ADR 0049 — 区分交付评价观察与可归因收益

日期：2026-10-07

状态：Accepted（用户明确选择“确认方案 B，保持责任与实测收益约束”，助手接受）

范围：source observation publication 与 delayed-credit 的方法边界

## Context

现行 strict source gate 只允许 accept、原样 use、Qp FAIL 的记录发布；下游
assignment scorer 只读 J 的类别映射。因此 published source J 恒为 1，其分数
等价于合格事件计数。补全 Qp PASS 分支仍不能恢复 J 的差异。
这是现有代码的符号审计结论，不是新 LLM 实验，也不否定全部后续 target J 信号。

## Decision

采用方案 B：保留绑定真实交付的正负评价，类型为有噪声的 observation；将它与
producer quality/attributable credit 区分。模型说 accept/rework/reject 本身既不
证明正确性，也不直接给 producer 奖惩。责任对象由冻结 contract、registry 和
交付来源决定，producer 生成的 diff 与 recipient 行动的 diff 独立记录。

J 在行动前封存，源任务完成且 lineage 完整后才可发布版本化 observation 视图；
完成前只作 auxiliary trace。发布不改变持久 policy state。后续责任分派必须在
执行前封存，并在真实执行和结果完整后才有资格接受 delayed update。

现有 ledger credit 只校验绑定、时序等前提，不充分定义 reward。target J 直接
作为 producer label 的当前 C1 更新只作诊断；必须补足责任与独立结果/成本规则
才能作为新方法训练。recipient-only/mixed 工作不得直接变成 producer reward。

目标、创新要求、两个结构 root、全基线公平比较、实时性和遗忘要求均不降低。
新方法必须与 count-only/J-masked、合法 Qp/terminal 和 contextual 对照区分，
通过独立 live histories 的真实质量及完整成本结果证明增量，而非只展示门通过。

## Rationale

原门把“能看到怎样的评价”与“可以把结果归因给谁”合成一个条件，过滤了要研究
的信息变化。拆分后能够检验评价价值，同时用独立责任和后续结果阻止错归因。
这是检验主张的必要修正；它本身不证明创新、有效性或最终训练器已确定。

## Consequences

- 方法升级为 v1.3、方法评价升级为 v1.4；注册表每类仍只一个 ACTIVE。
- ADR0047 的结构化 owner 原则保留；其把全部 observation publication 等同于
  producer attribution 的语义由本决议替代。历史 gate/回执不改写。
- 新 observation schema 与现有 RoleEvidenceOffer/feedback schema 区分；先完成
  三类 J × recipient 动作的零调用反例，再冻结真实小流实验卡。
- 当前 C1 固定产物、target J 更新、post-update preview 仍仅为开发诊断；不能
  被重新描述为新方法或角色学习效果。GPU 准入与科学投稿 gate 均未打开。

审计与候选依据：
[方案 B 与数学说明](../../research/candidates/judgment_observation_credit_split_v0.1_20261007.md)。
