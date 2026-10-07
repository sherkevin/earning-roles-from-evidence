# 方法论与训练合同 v1.3

- **状态**：`ACTIVE`
- **生效日期**：2026-10-07
- **类别**：method
- **前一版本**：[`method_v1.2_20261006.md`](method_v1.2_20261006.md)
- **目标约束**：[`docs/coordination/GOAL.md`](../../../coordination/GOAL.md) ER-G2

`ACTIVE` 只表示当前唯一的方法合同，不表示算法或 backbone/updater 已验证。
v1.3 依 [ADR0049](../../../user/decisions/0049-separate-judgment-observation-from-credit.md)
区分有噪声的交付评价观察、可归因的 producer evidence 与后续任务的合法 credit。
ADR0047 的结构化 owner 原则保留。实际实现仍含旧 accept-only source gate 和
诊断性 target-J 更新；下面是需实现并验证的合同，不能把版本生效当成实现完成。

## 1. 最小数学问题与信息边界

每个 episode 给出任务上下文 `x_t` 和合法候选 producer 集合 `C_t`。执行前选择一个 `a_t ∈ C_t`，producer 产生交付 `o_t`，recipient 读取并采取动作 `m_t`。独立 contract/later-use 检查产生结果 `y_t`；不可归因、不可见或资源失败的事件为 `UNKNOWN`。

$$
a_t \sim \pi_\theta(\cdot\mid x_t,C_t,R_t),
\qquad
R_t = \operatorname{Snapshot}(E_{\le w_t}),
$$

其中 `E_{≤w_t}` 是该决策 read cut 前已发布的有类型观察/证据；每条显式声明为 noisy observation 或 attributable evidence，二者不能暗中互换。隐藏 gold、未来 later outcome、private scorer 和其他 policy 的 realized memory 不能进入本轮决策。

### 1.1 符号、来源和最小实例

下面的表把公式中的原始量绑定到一次具体的 PIPE3 episode；它是语义实例，不把当前
qualification fixture 当作科学结果。没有出现在表中的量是由这些原始量计算出的状态或
操作，而不是额外的环境输入。

| 符号 | 来源与权限 | 最小实例 |
|---|---|---|
| `x_t` | 执行前公开的任务上下文 | `task_id=PIPE3_stream_processing, task_index=1, role=producer` |
| `C_t` | 执行前冻结的候选菜单 | `("peer-b@v1", "peer-c@v1")`，由 candidate registry 解析版本 |
| `a_t` | selector 在执行前抽样的候选 | `peer-b@v1`，同时保存完整 probability 与 propensity |
| `o_t` | producer 交付及其 artifact digest | `producer.py` 的 sealed source snapshot 与 `delivery_record_hash` |
| `m_t` | recipient 对该交付的实际动作 | `use`、`repair`、`reject` 或 `redo`，绑定 changed paths |
| `Q_p,J,A,Y` | 分别来自 producer contract、recipient judgment、recipient action、terminal outcome 的独立事件 | `Q_p=FAIL`、`J=accept_with_rework`、`A=repair`、`Y=PASS/FAIL/UNKNOWN` |
| `E` | 通过对应类型准入门、可公开读取的不可变事件集合 | `evidence_id` 绑定 delivery/judgment/action/outcome/artifact/version |
| `w_t` | assignment 读取 evidence 的事件时间 read cut | 目标 selection 前的 `read_cut=1`；更晚到达的 correction 不可见 |
| `R_t` | policy 读取的 evidence snapshot | `Snapshot(E_{≤1})`，不含 target outcome 或 private scorer 字段 |
| `g_t` | 在 arrival index `τ_t` 到达的 public evidence 记录 | `g_0` 为 source role evidence，`τ_0=1` |
| `B_k` | 同一 arrival index 的 evidence batch | `B_1={g_0}`；没有合格 evidence 时为空并保持 no-op |
| `L_j` | target assignment `j` 完成后的 delayed credit | `assignment_id`、chosen candidate、later outcome 与合法 feedback channel 的绑定记录 |
| `\theta` | policy 的持久可更新状态 | feature-aware arm 的 `a_diag,b` 数组，或其他预注册 updater 的状态；publish 前后 digest 必须相同 |

因此一次合法最小路径是：`x_1,C_1` 冻结菜单，`R_1=Snapshot(E_{≤1})`，先记录
`LaterAssignment`，再封存 `a_1`；target 完成后才构造 `L_1` 并调用 `U_delay`。若
`m_t` 修改的是 recipient 自有路径，不得据此生成 producer 负标签；完整且绑定的
原始评价仍可作为 noisy observation。缺字段、资源失败或绑定未知的事件不能发布或训练。

episode index `t` 与 feedback-arrival index `k` 分开。每个 arrival batch 为 `B_k={g_t:τ_t=k}`，但更新不再直接由源 episode 触发：

$$
R^{(k+1)} = U_{\mathrm{pub}}(R^{(k)}, B_k),
\qquad
\theta^{(k+1)} = U_{\mathrm{delay}}(\theta^{(k)}, L_j),
$$

其中 `U_pub` 只登记不可变 public evidence，`L_j` 只有在后续 assignment `j` 已经执行并有完整 later-use outcome 后才存在。发布阶段不改变 `θ`；`U_delay` 对一个 assignment 最多生效一次，且只对未来 assignment/use 的 credit 生效。

## 2. 观察、归因、发布与更新的独立状态

### 2.1 `observation_eligible(i)`：谁对哪次真实交付作了什么评价

由 canonical ledger 唯一绑定 producer/version、delivery digest、recipient judgment、
实际 action、独立 Qp 及完整 terminal outcome；对应 contract/registry 在执行前冻结。
J 在 action 前封存，observation 在源任务完成后才发布。当前或未来读切之外的信息
不可提前可见。Qp/terminal 的正负、J 的 accept/rework/reject 都不能单独决定准入。
UNKNOWN、缺字段、错误摘要、非法顺序和版本错配 fail closed。

producer 输入→交付的变化与 recipient 收到交付→最终产物的变化分开保存。
前者说明交付来源，后者说明使用与加工；不能把两者都叫 action changed_paths。
观察绑定的对象是 producer 的交付物，但不因此证明所述缺陷由 producer 导致。
recipient-only/mixed 动作可作为完整交接观察保存，必须带类型与范围警示，不能
进入 producer reward。judged role 与结构化对象不同须保留差异，不按措辞删样本。

对固定交付、Qp、Y、owner 和注册条件，设 A(J) 为原生协议要求的合法动作，
G_obs 为观察准入布尔量，则在各输入均通过原生验证时应满足：

$$
G_{\mathrm{obs}}(0,A(0))=G_{\mathrm{obs}}(\tfrac12,A(\tfrac12))
                       =G_{\mathrm{obs}}(1,A(1)).
$$

Case：固定 B 的同一 `producer.py`、Qp 与 Y，分别构造 accept/use、rework/repair、
reject_redo/independent_redo 三条合法协议链，按各自动作实际绑定摘要与 used_artifact。
三个合法配对应有同样观察资格；不能在准入时只保留 accept。路径变化在各配对内单独
检验。固定 use 却改成 reject 不是合法输入，必须拒绝。这里只构造零调用合同反例，
不在已完成真实日志中重写评价；非法时序或损坏记录仍拒绝。

### 2.2 `attribution_eligible(i)`：该结果可以归因给 producer 吗

这是比 observation 更强且独立的判断。结构化 owner 只能来自冻结 contract、registry、
producer 交付来源、recipient 实际修改路径、独立 producer check 和预注册 defect/quality
事件；模型 target_role/target_paths 仅为 noisy calibration observation。
事件规则和候选注册必须先于 selection，Qp PASS/FAIL 只实例化规则，不能事后挑选
哪些 actor 算数。Qp 完整不等于 terminal utility，terminal PASS 不等于 producer 合规。

recipient-only、mixed、unknown 或缺独立责任依据不能生成 producer 奖惩。
后续 outcome 也不能单独创造源归因。若需要边际贡献，必须使用单独注册且有效的
反事实设计；仅绑定到 B 并不证明结果由 B 因果造成。

Case：B 正确交付序列化，A 评价 rework 并只改自己负责的 processor。A 的评价能被
记录、其错误解释能被研究，但 `rework→B错误` 不成立；也不能用最终 PASS 反写原评价。

### 2.3 `observation_publish_allowed(i)` 与 `evidence_publish_allowed(i)`

完整 noisy observation 可在未来合法 read cut 被公开读取，类型与 attribution flag
必须保留；producer attributable evidence 则额外要求 2.2。二者都不可在发布阶段调用
`policy.observe_feedback`，不可改变持久 θ 或增加 update count。

native RoleEvidenceUpdate/RoleEvidenceOffer 与 policy feedback offer 继续分开；新
observation 使用独立 schema/auxiliary view，不能冒用 native evidence id 或把
`source_event_id` 改名为有归因证据。完成前的临时 J 仅在 auxiliary trace；不提前生成
native evidence 或 LaterAssignment。旧 evidence 路径的 subject、版本、digest、arrival、
supersession、read cut 以及 preview→assignment→commit 校验保留；新观察路径须有等价
但类型明确的绑定资格，未经实现审查不可接入旧接口冒充已满足。

**当前桥接缺口：** native LaterAssignment 必须引用已登记的 native evidence id，
单有 auxiliary observation_id 尚不能完成这条路径。可复用原生 RoleEvidenceUpdate
作为带专用版本的真实完成回执，由同一回执承载分别校验的观察与归因投影；原生协议
每组 J/A 只准一条 update，不能先发观察回执再追加第二条 attribution update。
所有 offer/assignment/credit 消费边界须按版本与独立责任证明做类型隔离；native
replay PASS 仅证明 lineage。该桥须通过完整零调用链再接 selector，当前尚未完成。

### 2.4 `policy_update_allowed(j)`：未来分派的收益经过实际验证了吗

assignment 必须先于目标 selection/start，选择消费同一快照，agent/propensity 一致，
later task 真正执行，delivery/action/outcome 完整，更新按 assignment/lineage 幂等。
这些是必要条件；`derive_later_credit_from_ledger` 现有实现只提供 lineage 前提，
不检查目标修改责任、独立质量或完整成本，因此不是充分的训练标签校验。

还必须有预注册的 reward 语义：明确训练目标是未来分派质量/完整成本，或经过独立
责任识别的 producer 能力。两者不可混同；source/target J 都不是默认真值。
任何把 recipient 集成或 mixed 修改直接映射成 producer 正负标签的更新不合格。
独立 Y、Qp、实际使用和完整成本须分开记录，缺少合法 label 时不更新且保留分母。
不能根据后来结果重采样先前选择、修改 source Qp/J/Y 或补写当时不存在的 assignment。

Case：A 的 source 评价让未来任务选择 B，B 的未来任务实际运行完成。只有未来任务
存在且 label 规则通过后才能产生 L_j。A 曾说 rework 不会直接产生 L_j；仅改变选择概率
或运行更新函数也不是未来效益。当前 C1 的 target J→Feedback 更新与 post-update preview
仍属于开发诊断，不能作为符合本合同的训练结果。

## 3. 事件时序和可重放合同

```text
source selection → delivery → Qp/J/A/Y
  → typed observation / attribution gates → versioned publication
  → assignment (before target selection/start)
  → target selection/read cut → target task outcome
  → delayed selected-only credit
```

`UNKNOWN` 和 `INVALID` 是 no-op；重复 feedback 按 feedback id/lineage 幂等；late correction 只能产生 superseding version，影响 correction 到达后的未来 snapshots。每个阶段都写 state digest、版本、arrival/read cut、propensity、service lag 和成本。Ledger replay 必须先通过，失败链不得更新。

## 4. 选择器与更新器接口

```text
publish(source_episode) -> {typed_observation / attributable_evidence | UNKNOWN | INVALID}
choose(x, C, public_snapshot) -> (selected_peer, propensity, decision_digest)
validate_later(assignment, later_episode, reward_contract) -> {credit | UNKNOWN | INVALID}
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

### 5.1 2026-10-05 few-shot 任务泛化合同

新任务通常不会与历史任务完全相同，因此“从历史反馈更新一个候选分数”不能替代任务
泛化。未来选择器必须在严格的历史 read cut `M_{<t}` 内，先形成当前任务/角色条件的
表示，再检索相似的历史交接证据，并把相似证据对候选 Agent 的支持度与全局先验、风险、
成本和探索项合成为选择分数。候选抽象为：

$$
z_t=f(x_t, r_t),\qquad
N_t=\operatorname{TopK}_{e\in M_{<t}}\operatorname{sim}(z_t,z_e),\qquad
U_t(c)=b_t(c)+\beta\,\widehat q(c\mid N_t)-\lambda\,\operatorname{cost}_t(c)+\xi_t(c).
$$

其中 `f`、相似度、`K`、时间衰减和跨角色匹配均为待验证组件；`M_{<t}` 只能包含在
该决策前已经发布的 edge-local judgment/later outcome，不能读到当前或未来结果。
当前 `contextual_trust_linear` 只有固定 64 维特征上的在线 RLS，尚未实现这个显式
检索器，不能把它当作 few-shot 泛化结果或最终方法。

方法验收必须增加：0/1/K 条 support 的泛化曲线、leave-one-root-out 与时间切分、候选
版本/角色/任务组合漂移、旧任务遗忘、检索延迟与记忆容量；随机行切分和 later outcome
泄漏均不合格。延迟反馈中心负责把通过责任门的交接证据原子地追加到记忆，并在 future
assignment/use 完成后进行一次 selected-only 更新；它不自动解决相似任务检索本身。

## 6. 必须比较的 baseline 与消融

在相同 `φ`、信息、propensity、预算和历史可见性下比较 uniform、no-update、raw acceptance、terminal-only、候选 `contextual_trust_linear`、诊断 `contextual_trust`、pooled controller 和 RARE。方案 A 至少做正交四格：

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

2026-10-05 composition-status amendment：`pipe3-two-stage-composition-v1.8` 已将相同的
`hash64-v1` / `matrix-features-v1` 64 维 bounded qualification feature map 传入 source
selection 和 target `preview→assignment→commit`，`contextual_trust_linear` 的 3-control
zero-call composition 通过。它只关闭 canonical composition 缺少 feature 输入的工程门，
不是 learned representation、独立 live history、质量或实时成本证据；详见
[`feature composition report`](../../../coordination/task_reports/20261005_pipe3_feature_composition_qualification.md)。

### 6.2 2026-10-05 profile/evidence fusion self-audit

对候选“文字 profile + episodic evidence + delayed residual head”的方法审查没有通过
当前有效性/创新性门：v0.1 可能重复计算同一批 `y^J`、没有完全固定 `y^L` 的输入快照，
也没有证明 embedding 相似度等价于下游效用。修订候选 v0.2 将 profile snapshot、其后
的 evidence delta 和 later-outcome residual head 分成不重叠的时间区间，并要求
profile permutation、task-only、identity-prior、topic-matched 和 component-isolation
controls；详见 [`fusion self-audit`](../../../coordination/task_reports/20261005_fusion_method_self_audit.md)
和 [`candidate v0.2`](../../candidates/few_shot_delayed_role_selector_v0.2_20261005.md)。
这只是候选修正，不锁定最终方法、backbone 或创新 claim；在 CPU temporal gate 通过前
不启动新的 API/A800 efficacy 流。

## 7. 当前仍未锁定的实现项

最终 backbone、表示维度、任务检索器、updater、遗忘保护阈值、漂移窗口、assignment policy、
evidence capacity/淘汰和跨 context 泛化仍未锁定。它们必须由 benchmark qualification、
离线数学检查和强 baseline 的真实瓶颈共同决定；本文件不把 Laya、AnyJev 或 Qwen 直接
指定为最终答案。

## 8. 实现顺序

1. 先完成 CPU two-stage qualification：责任反例、发布不更新、assignment 顺序、later credit 幂等和 replay。
2. 再用同一 root 做四格信息价值/闭环诊断；不把零调用资格结果写成方法收益。
3. 通过 benchmark、baseline、independent live history 和确认 split 后，才选择一个 backbone/updater 开 A800 challenger。
4. 所有真实 API、GPU、失败和 UNKNOWN 记录在 append-only raw/processed/summary 日志中；不回写历史 receipt。

2026-10-05 implementation-status amendment：候选 `DelayedPolicyAdapter` 已在真实
`FeatureContextualTrustPolicy` 上通过 8 格零调用资格；严格路径复用 canonical replay、
`derive_later_credit_from_ledger` 和 history binding，把 `RoleEvidenceOffer` publication
与 later target feedback update 分开，并补充 assignment-level alternate-outcome 拒绝、
candidate/channel/namespace 绑定、容量与回滚。这只是方法接口的工程资格，adapter 自身
尚未接 preview→assignment→commit、independent histories 或 live PIPE3，不能当作最终
updater、实时训练收益或 scientific result，也不改变本节的实现顺序和未锁定项。

### 8.1 2026-10-06 structural-owner gate amendment

ADR 0047 将责任资格从模型生成的 `target_role` 硬条件改为结构化 owner gate。当前实现版本为 `pipe3-responsibility-label-v2-structural-owner` 与 `two-stage-role-evidence-v3-structural-owner`；A1--A8 zero-call mutation/replay qualification 已通过，receipt 位于 `experiments/logs/n03_structural_owner_gate_qualification_20261006_v2/`。该 receipt 只证明 typed gate、反例拒绝、重复幂等和 contract mutation fail-closed，不产生 LLM/GPU 或科学效能结论。

这段为历史资格记录，不证明本次 observation/reward 分离已实现。下一张 live card 必须携带 explicit structural-owner registration、observation schema、合法 reward 规则，并报告 judged-role disagreement；历史 C1 receipt 不回写。

### 8.2 2026-10-07 评价支持度与训练标签前提

当前 strict source gate ⇒ J=1，其 assignment overlay 退化为合格事件计数。
[可复算的 2592 个符号输入审计](../../../../experiments/logs/n03_judgment_support_audit_20261007_v1/summary.json)
及九组 count-only 对照只证明此代码性质，0 API/0 GPU，不是否定评价理论。
新通道必须先通过三类 J × recipient 动作、迟到/重复/绑定的零调用资格；随后小流
检查自然支持度与真实更新后执行。比较至少包含 count-only/J-masked，以及部署可得的
Qp/terminal/raw-J/contextual 强对照。所有值同为 1 的 shuffle 不应产生变化。

现有 C1 target J 可以变化，但它直接作为 producer 更新标签的责任/质量/成本语义
尚未成立；不能用源 gate 的安全性代替目标 label 审查。此缺口关闭前，不启动新训练
收益实验；数学资格通过也不替代两根、完整基线、实时/遗忘与独立确认要求。

## 9. 对照标准

方法审查使用 [`method_v1.4_20261007_eval.md`](../evaluation/method/method_v1.4_20261007_eval.md)。故事边界见 [`storyline_v1.1_20260928.md`](../storyline/storyline_v1.1_20260928.md)，可执行实验卡见 [`benchmark_baseline_v1.1_20260930.md`](../benchmark-baseline/benchmark_baseline_v1.1_20260930.md)。
