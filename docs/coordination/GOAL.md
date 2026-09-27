# earning-roles 项目 Goal v1.0

日期：2026-09-27。状态：ACTIVE。Goal 变更授权：`false`。

这份文档定义项目要做成什么样。实验失败、数据不准、接口超时、成本过高或当前
方法效果不显著，都只能产生 task report 和修复任务，不能自动降低这里的标准。
只有用户明确同意修改/降级，并用新的 ADR 记录旧目标、新目标、证据、理由和后果，
Goal 才能改变。

## 1. ER-G1：最终科学链条与论文产出

项目最终要形成一篇符合 AAMAS 审稿标准的论文和可复现实验包。论文必须把以下四
件事连成一个可审计的因果链，而不是只展示一个选择器或一次终局成功：

```text
真实交付物
  → 实际接收并使用交付物的 recipient 的 situated judgment
  → 可归因的 producer role evidence
  → 下一次执行开始前的责任/peer assignment 改变
  → 未见任务上的团队质量与完整成本变化
```

中心科学问题是：在没有预先指定专家身份的协作流中，真实 recipient 对具体交付物
的接受、修改、返工或拒绝，能否被安全地转成 producer 的角色证据，使未来责任分派
更合适，并在相同信息、探索、模型调用和完整成本下改善预先声明的质量—成本目标。

“角色”必须是可归因、可追溯、能影响未来执行的状态。接受率、角色熵、终局成功、
自我评价或 prompt 中的角色名都不能单独满足目标。

## 2. ER-G2：方法与在线训练标准

最终方法不能只是把 AnyJev、Laya、RLS、online SGD、周期性 refit 或普通 contextual
bandit 拼接起来。它可以复用这些项目的表示、运行时或比较器，但论文贡献必须包含
一个我们自己的、可执行并可被反驳的在线更新/训练机制，至少满足：

1. **实时性**：selected-only 的每条合法反馈都能低成本增量生效；测量 update p50/p95、
   端到端延迟、状态大小、token/tool/GPU/人工成本。
2. **时效性**：任务或 peer 能力变化后，未来选择能在预先定义的窗口内响应。
3. **稳定性**：旧任务 holdout、任务漂移和乱序/延迟反馈下，报告峰值和平均遗忘；
   “当前没观察到遗忘”不能替代测量。
4. **责任安全**：recipient judgment、recipient action、producer contract check、
   final outcome 和 `UNKNOWN` 分开记录；正常的 recipient 自有 integration 不自动
   惩罚 producer。
5. **可迁移接口**：底层 selector/update 事件接口可以服务 peer select 和 tool select，
   但两个项目的任务、label、scorer 和科学结论必须分开验证，不能为了共享代码合并
   不同问题。

当前 `RARE` 只是候选方法合同，不是已证明的最终算法；最终 backbone、表示和更新器
必须由真实小流暴露的瓶颈与强基线比较后决定。

## 3. ER-G3：Benchmark 与 baseline 的硬标准

主 benchmark 候选是 TeamBench-derived `PeerRoleBench-TB`，但必须同时满足：

- 至少两个结构不同的 task root；改 seed 或改名不算独立 root；
- producer 有独立可测的交付义务，recipient 有真实依赖、使用/修改/返工行为，sink
  adoption 与 producer correctness 分开计账；
- task text、源码、hidden tests、expected、scorer、operator ledger 和候选 workspace
  的可见性在运行前冻结，不能把答案写进 prompt 或解释性源码注释；
- development/confirmation 按 root 划分，不能看完开发结果后改 split、标签或主指标；
- 缺少责任证据、评分覆盖或可见性证明的流必须记录 `UNKNOWN`，不能补成成功/失败。

首轮至少比较：random/local-uniform、no-update、raw acceptance、同信息 contextual
trust/bandit、terminal-only、pooled controller、RARE，以及相同表示下的 RLS、online
SGD/logistic、periodic refit。所有条件共享信息、探索、预算和独立 stream。

## 4. ER-G4：实验与论文的证据标准

实验必须使用真实 LLM/API；每次实验都要在执行前写 config，在执行中流式记录调用、
token、错误、延迟和原始输出，在执行后保存逐样本结果、UNKNOWN、失败原因、源码/模型/
数据/硬件/seed/hash。任何没有真实调用的 fixture 只能支持协议或工程结论。

论文只有在以下证据齐备后才能填写方法效果数字：

- recipient judgment 对独立 producer contract/later-use 结果有信息价值，并超过明确
  的 raw/terminal 对照，或诚实报告没有增量；
- judgment 进入未来执行前的 assignment，并在未见 root 上产生质量/成本后果；
- 实时更新的速度、时效性、稳定性和遗忘约束均有独立 stream 证据；
- benchmark、baseline、runner、scorer、成本和失败边界可复现；
- 结论、摘要、标题和 LaTeX 结果表与 claim-evidence matrix 一致。

A800 只用于已有真实信号、明确训练瓶颈和冻结实验卡之后的 bounded challenger；GPU
作业本身不能替代 benchmark 或方法证据。

## 5. ER-G5：当前阶段门

| 阶段 | 必须交付 | 未通过时的动作 |
|---|---|---|
| G0 目标/故事 | ER-G1 的 Goal、主线、符号、责任语义、反驳条件 | 修正文档；不改 Goal 标准 |
| G1 资格 | ER-G3 的两个 root、非 oracle 材料、真实 scorer/ledger/IPC 边界 | 修 runner/任务；保留 UNKNOWN |
| G2 方法 | ER-G2 的完整更新伪代码、backbone/表示候选、强 baseline 和成本合同 | 做离线推导/小 fixture；不把现成组件称创新 |
| G3 开发实验 | ER-G4 的冻结 card、真实 API、小批量独立 stream、逐事件日志 | 分析失败原因；不重写成功标准 |
| G4 确认实验 | ER-G1/ER-G4 的独立 root、预注册主指标、确认预算和停止规则 | 根据证据决定支持、否定或用户批准的 scope change |
| G5 论文 | ER-G1–ER-G4 的结果、局限、复现包、AAMAS 模板和审稿自查 | 只修改论文表述，不掩盖未满足的硬门 |

## 6. ER-G6：Goal 变更控制

以下行为禁止自动发生：把无效数据当作有效、把 `UNKNOWN` 当作负例、删除失败记录、
用一次成功替代纵向学习、把工程 fixture 写成方法结果、把 RLS/Laya/AnyJev 直接称为
创新、因为实验贵而减少必要 baseline、因为模型失败而删除实时性/稳定性标准。

如果证据显示原问题不可识别、任务不再承载故事，或者用户决定有意改变研究问题，
必须先写 task report，随后由用户明确同意新的 Goal；新 ADR 需要列出：旧版本、变更
条目、证据、理由、对论文主张/实验/成本的影响，以及未完成的旧目标是否保留为历史
分支。未获得同意前，执行状态只能是 `OPEN`、`UNKNOWN` 或 `BLOCKED_BY_EVIDENCE`，
不能改成“目标已完成”或静默降级。

## 7. ER-G7：当前结论

故事线已经收敛到 situated judgment → attributable role evidence → future assignment
→ quality/cost；协议、日志和部分运行边界已经修复。最终 benchmark、backbone、在线
训练方法、实时性/遗忘效果和 AAMAS 科学结论都尚未完成。当前任务的详细对照见
[`20260927_goal_reconciliation.md`](task_reports/20260927_goal_reconciliation.md)。
