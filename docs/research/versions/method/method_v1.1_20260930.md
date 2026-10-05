# 方法论与训练合同 v1.1

- **状态**：`ACTIVE`
- **生效日期**：2026-09-30
- **类别**：method
- **前一版本**：[`method_v1.0_20260928.md`](method_v1.0_20260928.md)
- **目标约束**：[`docs/coordination/GOAL.md`](../../../coordination/GOAL.md) ER-G2

`ACTIVE` 只表示当前唯一的方法合同，不表示算法已经验证或 backbone/updater 已经选定。v1.1 由 ADR 0043 确认的两阶段 evidence/update 语义取代 v1.0 中把公开反馈和持久更新放在同一入口的含混之处；v1.0 保留为历史版本。

## 1. 最小数学问题与信息边界

每个 episode 给出任务上下文 `x_t` 和合法候选 producer 集合 `C_t`。执行前选择一个 `a_t ∈ C_t`，producer 产生交付 `o_t`，recipient 读取并采取动作 `m_t`。独立 contract/later-use 检查产生结果 `y_t`；不可归因、不可见或资源失败的事件为 `UNKNOWN`。

$$
a_t \sim \pi_\theta(\cdot\mid x_t,C_t,R_t),
\qquad
R_t = \operatorname{Snapshot}(E_{\le w_t}),
$$

其中 `E_{≤w_t}` 是该决策 read cut 前已发布且通过公开责任门的 evidence。隐藏 gold、未来 later outcome、private scorer 和其他 policy 的 realized memory 不能进入本轮决策。

episode index `t` 与 feedback-arrival index `k` 分开。每个 arrival batch 为 `B_k={g_t:τ_t=k}`，但更新不再直接由源 episode 触发：

$$
R^{(k+1)} = U_{\mathrm{pub}}(R^{(k)}, B_k),
\qquad
\theta^{(k+1)} = U_{\mathrm{delay}}(\theta^{(k)}, L_j),
$$

其中 `U_pub` 只登记不可变 public evidence，`L_j` 只有在后续 assignment `j` 已经执行并有完整 later-use outcome 后才存在。发布阶段不改变 `θ`；`U_delay` 对一个 assignment 最多生效一次，且只对未来 assignment/use 的 credit 生效。

## 2. 三层责任/更新状态

对源 episode `i`，父进程生成并封存三个独立布尔量和原因：

### 2.1 `attribution_eligible(i)`

该量为真当且仅当：

- producer 的 contract 变化或预注册 source defect 能被 action 的路径集合唯一绑定；
- producer score `Q_p`、recipient judgment `J`、consumer action `A`、terminal outcome `Y` 均完整且 digest/版本/顺序可回放；
- 目标角色是 producer，且 recipient-owned path 为空；
- `later_valid` 不得单独把一个没有 producer-owned change 的源 episode 变成 eligible。

因此 recipient-only、mixed ownership、缺字段、资源失败、later outcome 单独出现都返回 `UNKNOWN`/`PENDING_ATTRIBUTION`，不产生源 role evidence。

### 2.2 `evidence_publish_allowed(i)`

若 `attribution_eligible(i)=true`，父进程可追加一个不可变的 `RoleEvidence` 发布记录，记录 source event、责任依据、artifact/ledger digests、evidence version、arrival index 和 supersession lineage。该记录可以在未来任务 read cut 被看见，但发布不调用 `policy.observe_feedback`，不增加 `policy.updates`，也不改变持久 `θ`。

原生 ledger 只有在 source terminal outcome 完成后才登记 `RoleEvidenceUpdate`；尚未完成 terminal 的临时可见信息只能存在于 auxiliary offer/trace，不能伪造 evidence 或 `LaterAssignment`。

用于 assignment 的公开视图必须使用独立的 `RoleEvidenceOffer` schema：它以 native
`evidence_id` 为主键，并绑定 delivery、judgment、action、outcome、artifact digest、producer
candidate/version 和 source task。旧 `AssignmentEvidenceOffer` 仍只表示 policy feedback
channel，不能把其中的 `source_event_id` 当成 native role evidence id。offer builder 必须从
canonical ledger 派生 subject；evidence 属于 producer B 时，assignment 选择 C 必须拒绝。

### 2.3 `policy_update_allowed(j)`

对未来 assignment `j`，只有以下条件同时成立时为真：

1. assignment 在目标 selection/task start 之前写入，并引用 source episode 已登记的 evidence；
2. selection 消费同一 read cut，agent 和 propensity 与 assignment 一致；
3. later task 的 delivery、judgment/action 和 terminal outcome 完整、绑定且通过 replay gate；
4. assignment 尚未被 credit（幂等 key 为 assignment id + later outcome lineage）。

此时 `L_j` 只评价“该未来选择/被选 peer 在 later task 中的质量、完整成本和使用结果”。它不能修改 source episode 的 `Q_p`/`Y`，不能把 recipient repair 变成 producer credit，也不能读取 later outcome 后重算已封存的 selection。

## 3. 事件时序和可重放合同

```text
source selection → delivery → Qp/J/A/Y
  → attribution gate → evidence publication
  → assignment (before target selection/start)
  → target selection/read cut → target task outcome
  → delayed selected-only credit
```

`UNKNOWN` 和 `INVALID` 是 no-op；重复 feedback 按 feedback id/lineage 幂等；late correction 只能产生 superseding version，影响 correction 到达后的未来 snapshots。每个阶段都写 state digest、版本、arrival/read cut、propensity、service lag 和成本。Ledger replay 必须先通过，失败链不得更新。

## 4. 选择器与更新器接口

```text
publish(source_episode) -> {published_evidence | UNKNOWN | INVALID}
choose(x, C, public_snapshot) -> (selected_peer, propensity, decision_digest)
validate_later(assignment, later_episode) -> {credit | UNKNOWN | INVALID}
update(credit) -> {updated_once | NOOP}
snapshot()/restore() -> versioned state
```

`publish` 和 `update` 必须是两个可独立消融的接口。临时 public evidence 可以改变未来 assignment 的输入，但在 `validate_later` 返回前持久状态 digest 必须不变。具体表示（计数/均值、上下文线性状态或冻结表示加小 head）和 updater（RLS、online logistic/SGD、periodic refit 或新 updater）仍作为正交实验条件，不预先宣称创新。

由于 native ledger 要求 `LaterAssignment` 先于目标 selection，而普通 selector API 在
`choose_and_seal` 内部采样，执行必须采用 preview→assignment→commit：preview 在事务快照上
生成并封存 chosen candidate、完整概率和 propensity，恢复 policy/RNG；assignment 记录后以
固定选择重放，不得重新采样。assignment 的 agent、role、propensity 和 evidence subject
均由 canonical records 校验。

## 5. 必须证明的实时性、时效性和稳定性

- **实时性**：source publish、assignment read 和 delayed update 分别报告 p50/p95、service lag、状态字节、CPU/GPU/token/tool/人工成本；不能用批量 refit 冒充逐条更新。
- **时效性**：预注册 drift 后，发布证据对未来 assignment 的 propensity/quality 变化和 later-use 增量在窗口 `W` 内出现；later outcome 不得泄漏到早期 read cut。
- **稳定性**：旧 root/task holdout 的峰值与平均遗忘、恢复窗口、UNKNOWN 率、correction/replay 一致性独立报告。

## 6. 必须比较的 baseline 与消融

在相同 `φ`、信息、propensity、预算和历史可见性下比较 uniform、no-update、raw acceptance、terminal-only、contextual trust/bandit、pooled controller 和 RARE。方案 A 至少做正交四格：

1. no evidence / no update；
2. public evidence only（assignment 输入变化，持久 `θ` 不变）；
3. delayed update only（无新的 public evidence）；
4. public evidence + delayed update。

训练方式再正交比较 RLS、online logistic/SGD、periodic refit 与候选增量 updater。主结果必须报告 assignment-level future quality/regret、完整成本、UNKNOWN 分母和 95% interval；源 producer score 改善不能替代闭环结果。

### 6.1 2026-10-05 same-information comparator amendment

静态审计发现原有 `contextual_trust` 只使用 context×candidate 的 Beta 统计，而 RARE
使用 64 维 `captured_features`，且 RARE 曾丢弃 `base_scores`。因此原有 contextual
不能作为 strongest same-information control。现新增一个**候选** comparator
`contextual_trust_linear`：固定使用 `hash64-v1`、64 维 bounded `phi`、同一 candidate
menu、base-score 项、selected-only `recipient_judgment`、propensity、arrival 和成本
合同，采用普通 diagonal ridge/RLS 更新；它不使用 RARE 的 protected anchor、fast
window、correction queue 或 responsibility gate。原 Beta `contextual_trust` 保留为
context-only diagnostic。零调用 qualification 见
[`20261005_feature_contextual_baseline_qualification.md`](../../../coordination/task_reports/20261005_feature_contextual_baseline_qualification.md)。

这只关闭输入合同的工程缺口，不锁定最终 updater，也不改变七臂 active manifest。只有
`contextual_trust_linear` 通过 canonical manifest、独立 namespace 和真实 live parity
后，才可把它写入正式 baseline matrix；在此之前 baseline 仍是 `NOT_FROZEN`。

## 7. 当前仍未锁定的实现项

最终 backbone、表示维度、updater、遗忘保护阈值、漂移窗口、assignment policy、evidence capacity/淘汰和跨 context 泛化仍未锁定。它们必须由 benchmark qualification、离线数学检查和强 baseline 的真实瓶颈共同决定；本文件不把 Laya、AnyJev 或 Qwen 直接指定为最终答案。

## 8. 实现顺序

1. 先完成 CPU two-stage qualification：责任反例、发布不更新、assignment 顺序、later credit 幂等和 replay。
2. 再用同一 root 做四格信息价值/闭环诊断；不把零调用资格结果写成方法收益。
3. 通过 benchmark、baseline、independent live history 和确认 split 后，才选择一个 backbone/updater 开 A800 challenger。
4. 所有真实 API、GPU、失败和 UNKNOWN 记录在 append-only raw/processed/summary 日志中；不回写历史 receipt。

2026-10-05 implementation-status amendment：候选 `DelayedPolicyAdapter` 已在真实
`FeatureContextualTrustPolicy` 上通过 7 格零调用资格。它把 `RoleEvidenceOffer` 的
publication 与 later target feedback update 分开，并补充 assignment-level alternate-outcome
拒绝、candidate/channel/namespace 绑定、容量与回滚；这只是方法接口的工程资格，不是
最终 updater、live PIPE3 replay 或 scientific result，也不改变本节的实现顺序和未锁定项。

## 9. 对照标准

方法审查使用 [`method_v1.2_20260930_eval.md`](../evaluation/method/method_v1.2_20260930_eval.md)。故事边界见 [`storyline_v1.1_20260928.md`](../storyline/storyline_v1.1_20260928.md)，可执行实验卡见 [`benchmark_baseline_v1.1_20260930.md`](../benchmark-baseline/benchmark_baseline_v1.1_20260930.md)。
