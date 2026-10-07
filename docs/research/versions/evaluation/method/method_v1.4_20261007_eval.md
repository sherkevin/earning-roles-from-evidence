# 方法论评价标准 v1.4

- **状态**：`ACTIVE`
- **类别**：evaluation/method
- **评价对象**：[`method_v1.3_20261007.md`](../../method/method_v1.3_20261007.md)
- **生效日期**：2026-10-07
- **前一版本**：[`method_v1.3_20261006_eval.md`](method_v1.3_20261006_eval.md)
- **用途**：审查两阶段 role-evidence 方法是否真正新、可运行、可验证、实时且稳定；不保证录用。

## A. 观察、归因、发布与更新硬门

方法必须把以下状态分开记录并可重放：

- `observation_eligible/observation_publish_allowed`：评价绑定真实交付与责任对象，J 在行动前封存，源任务完整后才可发布独立 typed observation。固定合法 lineage 后，accept/rework/reject 必须同等准入；Qp 正负不能作事后选样规则。完整 recipient/mixed 交接只可保留为 noisy observation，不是 producer reward。

- `attribution_eligible`：源 producer contract、recipient judgment、实际 action、terminal outcome 和 digest 唯一绑定；later outcome 不能单独制造源归因；recipient-only/mixed/UNKNOWN 必须拒绝。
- `evidence_publish_allowed`：可发布不可变 public evidence，供未来 read cut 使用；发布阶段持久 policy digest 和 update count 不变。
- `policy_update_allowed`：只有 assignment 在 selection/start 前成立、selection 消费同一 evidence snapshot、later task 完成后，才允许一次 selected-only delayed credit。

Noisy observation、attributable role evidence 与 policy feedback 必须类型分离；新观察视图不冒用 native evidence 身份。Role evidence offer 必须与 policy feedback offer 分离；native `evidence_id`、producer/version、delivery/artifact lineage 和 target assignment subject 必须可从 canonical ledger 重放。必须有 preview→assignment→selection 的 exact chosen/propensity 检查，禁止把 source selection id 当 evidence id，或用错误 peer 消费别人的 evidence。

任何把 diagnostic ELIGIBLE 直接当训练标签、把 later outcome 回填成旧 producer 标签、或在早期 selection 读取未来结果的实现均不通过。

结构化 owner 与 judged role 必须分开验收：`structural_owner_role` 只能由冻结 contract/registry、changed paths、独立 producer check 和预注册 defect/quality 事件推导；模型生成的 `target_role`/`target_paths` 只能作为带噪声的 calibration observation。producer owner 与 judged recipient 的 disagreement 应保留并计入 judge calibration，不能单独 censor 合法观察。producer 输入→交付 diff 与 recipient 交付→最终 diff 必须分开；recipient-only/mixed 在 producer credit 通道 fail closed；unknown、资源失败和 contract mutation 在观察发布和训练通道均 fail closed。

现有 ledger-credit 校验只是 lineage/时序前提，不能替代 reward 验证。目标任务的 Qp、独立 Y、实际动作和完整成本须分别记录，更新目标与标签规则须预注册；不得直接把 target J 的 rework/reject 当作 producer 奖惩。实际运行后且完整合法才更新，发布时持久状态必须不变。

## B. 形式完整性与事件顺序

独立读者必须能从 source selection → Qp/J/A/Y → gate → publication → assignment → later selection/outcome → delayed update 重放出结果。文档和测试必须定义：输入、公开/私有状态、read cut、arrival index、UNKNOWN/INVALID、版本、supersession、重复/乱序、snapshot/restore、容量/淘汰和停止规则。原生 ledger 的 assignment 必须在目标 selection/task start 前写入并保持 agent/propensity 一致；无 assignment 的 task_start 是否允许需单独遵守底层协议，不能误写成方法必然约束。

## C. 创新与正交消融

必须完成 closest-method audit，并证明收益不能由普通 contextual trust/bandit、RLS、online SGD、periodic refit 或现成 JEV wrapper 在同信息/同预算下复现。至少报告四格：no evidence/no update、public evidence only、delayed update only、public evidence + delayed update；再做责任门、延迟 credit、遗忘保护和 correction/replay 的去除消融。不能把组件堆叠本身作为充分创新。

## D. 在线性质与成本

分别测 publish、read/assignment、delayed update 的 p50/p95、service lag、吞吐/backlog、状态字节、CPU/GPU/RAM、token/API/tool/人工成本。实时训练必须说明冻结与更新参数、每次读写数据、是否 full-model forward/backward、并发、限流、恢复和 checkpoint。批量 refit 不能冒充逐条更新。

## E. 时效性与稳定性

在预注册 drift 后，报告 evidence 对未来 assignment 的 propensity、future quality/regret 和完整成本的响应窗口；later outcome 不得泄漏到 source read cut。报告旧 root/task 的平均和峰值 forgetting、恢复时间、UNKNOWN 率、late correction/replay 一致性。source FAIL→later PASS 不得被解释为 source 被修复。

## F. 统计与可识别性

主 estimand 是 assignment-level future quality/regret 或 team quality–complete-cost utility，而不是 source producer score 自身。使用独立 streams/root split、selected-only propensity、missing-label/UNKNOWN 分母、judge reliability/calibration 和 95% interval。四格中的公开证据与持久更新必须能分开估计，confirmation split 的 updater、阈值、词表和停止规则必须在看到结果前封存。

## F.1 Few-shot 任务泛化硬门

如果论文声称系统能把历史交接经验迁移到新任务，必须显式证明“相似任务支持”而不是
仅仅证明候选累计次数增加。合格实现需要：

- 在 query read cut 前封存可复现的任务/角色表示和相似度版本；
- 只从过去可见的 edge-local evidence 检索 support，禁止当前或 later outcome 泄漏；
- 报告 0/1/K-shot、leave-one-root-out、时间切分、角色/候选版本漂移和组合漂移；
- 与 no-memory、uniform、strong same-information linear/RLS、最近邻/加权检索和主候选
  在同一菜单、propensity、成本和 history visibility 下比较；
- 报告检索延迟、记忆容量、跨 root 质量/regret、校准、旧任务遗忘和 UNKNOWN 分母。

固定哈希特征上的在线 RLS、随机行切分、或只在同一任务的后续 episode 上变好，都不能
单独通过该门。没有这些结果时，最多声称“在线候选分数更新”，不能声称 few-shot
任务泛化或跨任务角色学习。

### F.2 融合方法的可识别性硬门

若方法同时使用 profile、episodic memory 和 online head，必须为每条输入记录 information
cut、source event、profile version、memory delta version 和 head state digest。profile
不得和当前 delta 重复包含同一 evidence；`y^J` 与 `y^L` 必须分别进入预注册的更新路径。
必须有 profile-only、memory-only、head-only、full fusion、no-memory、RLS/SGD 以及
profile/prototype permutation 对照。融合权重、刷新周期、Top-K、更新步长和 reservoir
规则只能在 development split 冻结，不能按 confirmation 结果回调。否则无法把收益归因
到方法机制，方法门不通过。

## F.3 评价支持度与增量信息硬门

必须报告准入前后 J/Qp/动作的支持度、UNKNOWN 与完整分母。若源发布 J 恒定且
scorer 只读其类别，则 source overlay 的效果只能先解释为事件数；不能写成评价
内容的增量。增加 Qp PASS 分支但仍只保留 accept，不算解决此缺口。

至少提供 count-only/J-masked、合法 Qp-only、terminal-only、raw-J 与同表示
contextual 对照；字段、机会数、read cut、探索和预算对齐。公开不合法的 Qp/Y 只能
作为标明信息差异的上界，不可混入公平 baseline。先在交付/Qp/Y/owner 固定条件下
比较三种合法 J–action 配对，再在各配对内改变合法路径；违反 native 决策–动作配对的
输入必须拒绝。真实自然支持度与未来执行效益必须另行测量。

从 auxiliary observation 到 native LaterAssignment 必须有真实注册回执和类型明确的
适配器，不能只把 observation_id 改名。原生每组 J/A 唯一 update 的约束不能绕开；
旧 attributable offer、最终 assignment 与 credit 都须拒绝观察回执冒充独立责任证明。
Native replay PASS 不能替代这些门或 reward 验证。

任何观察通道收益都不能只靠降低责任标准、把接收方自己的工作记给 producer，
或在确认集上挑选标签/seed 得到。拆通道本身既不证明创新，也不通过有效性门。

## G. 反驳与停止

以下任一情况时方法主张不通过：

1. public evidence 发布已隐式改变持久 policy；
2. later outcome 重写源 label 或给 recipient repair 计 producer credit；
3. assignment/selection/read cut 顺序不合法，或 propensity 被修改；
4. assignment 引用 producer B 的 evidence 却选择 producer C，或 preview 后重采样；
5. UNKNOWN、重复、乱序或 correction 没有 no-op/幂等语义；
6. contextual trust/bandit 在同信息和成本下解释全部收益；
7. 只有 zero-call fixture 或单次 API 链，没有独立 live histories 和 confirmation split。
8. 检索使用了 query 之后的 evidence，或跨 root 的相似任务泛化只由随机行切分支持。

9. 只凭完整 ledger credit 就把 target J 当 producer reward，或 J 恒定时仍声称内容增量。

## H. 两档交付门

`Findings-ready` 至少需要可复现的 two-stage CPU/live 机制、四格消融和负结果解释；`Proceedings-ready` 还需要独立 confirmation、closest-method 对照、future assignment 效果、负迁移/遗忘分析和 clean-environment replay。两档都要求原始事件、失败、成本和 digest 可追溯。

2026-10-06 structural-owner amendment：A1--A8 zero-call mutation/replay qualification 已通过，覆盖 producer owner/judged-role disagreement、recipient-only、mixed ownership、缺少注册、重复回放与 contract mutation；这只证明责任门的工程行为，不构成 live efficacy 或 scientific result。

2026-10-05 qualification note：candidate `DelayedPolicyAdapter` 的 8/8 zero-call
receipt 已覆盖真实策略上的 publish/update 接缝、canonical replay/history binding、
assignment-level 幂等和 fail-closed lineage。它仍不能满足 `Findings-ready` 的 live
two-stage、四格消融、future assignment effect 或 independent history 门；这些门仍保持
未通过。

## 来源边界

本标准保留方法评价 v1.3 的 soundness、reproducibility、创新、成本、稳定性与统计要求。依用户确认的 ADR0049 分开 noisy observation 与可归因收益，并增加支持度/计数对照及 reward 语义审查；不把任何原有效果要求删除或降级。
