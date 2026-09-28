# 故事线与论文写作评价标准 v1.3

- **状态**：`ACTIVE`
- **类别**：evaluation/storyline
- **评价对象**：[`storyline_v1.1_20260928.md`](../../storyline/storyline_v1.1_20260928.md)
- **生效日期**：2026-09-28
- **前一版本**：`storyline_v1.2_20260928_eval.md`
- **用途**：投稿前的严格故事线、创新和论文叙事预检；不是 AAMAS 官方评分表，也不保证录用。

## v1.1 对象修正

本版本评价当前生效的 storyline v1.1。v1.1 将 situated judgment、责任过滤、延迟更新和 future assignment 作为一个有机闭环叙述；本评价仍要求用 matched composition、正交因素消融、全因子主效应/交互和跨 root 证据检验该叙述，不能把更完整的公开包装当作实验证据。

## 使用原则

这是不可补偿的 hard-gate 标准：核心门失败，不能靠漂亮的终局成功率、图表数量或总分补回。标准分为 AAMAS 官方底线、项目科学识别门和强录用目标；三者必须在审查记录中区分。只有“强录用目标”全部有证据时，才可以把故事写成完整方法论文；否则应收窄 claim 或继续实验。

## A. 问题切口：是否 sharp

必须同时满足：

1. 用一段话明确一个中心问题，指出现有方法在哪个具体协作情境下失效；不能把能力学习、信誉传播、workflow 搜索、贡献分配和角色形成并列成五个问题。
2. 给出一个最小反例：没有本方法时，为什么 raw acceptance、终局奖励、固定专家或中央 pooled controller 会做出错误/不可识别的责任选择。
3. 给出成功和失败的预先判定条件，以及一个会让作者停止主张的反驳结果。
4. AAMAS agent/multiagent interaction 是问题本身的必要部分；论文不是 generic LLM、prompt 或工具包装。官方 Call 要求 agent/MAS contribution 与 state of the art engagement。[官方 Call](https://warwick.ac.uk/fac/sci/dcs/aamas2027/calls/call-for-main-track/)

**不通过的表现**：去掉 recipient、future assignment 或 multiagent dependency 后，问题仍然完全成立；这说明切口没有打中协作科学问题。

## B. 创新：是否唯一、可识别、不可被轻易替代

主创新必须写成一个可检验句式：

```text
现有近邻在 [明确观察/归因/时序限制] 下无法识别 [具体目标]；
本方法引入 [唯一机制]；因此可以检验 [预注册后果]。
```

必须提交一张 novelty table，至少列出五个最近邻：它们的问题、输入信息、更新规则、责任/credit 语义、实验对象、与本方法的真正差异。基础模型、运行时、数据适配器、普通 RLS/SGD、缓存和 prompt 模板不能单独算创新。

创新硬门：

- 只能有一个主要机制；新增模块必须说明是必要条件、实现基础还是 baseline。
- 必须有最小消融能移除该机制，同时保持其他信息、预算和模型相同。
- 必须有“等信息替代解释”：若 contextual trust/bandit、raw acceptance 或 pooled controller 可以复现全部收益，主创新不成立。
- 论文必须主动说明创新的适用范围和不适用范围；不能用“自然涌现”“端到端”代替机制。

## C. 因果链：每个箭头都要有证据

```text
交付 → recipient 真实读取/行动 → 可归因判断
→ producer role evidence → 执行前 future assignment
→ 未见任务质量/完整成本
```

每个箭头必须有独立事件、权限边界和 hash/ID 绑定。最低要求：

- recipient 真实看到并采取 `use/modify/reject/redo` 等动作；detached judge 或自评不够。
- producer contract、recipient 自有 integration、sink adoption、最终 outcome 和 `UNKNOWN` 分开记录。
- assignment 在执行/评分前封存；至少一个未来 owner 不是直接评价该候选者的同一 owner。
- later outcome 不能被倒灌到当轮选择；责任归因必须有可审计来源。

## D. Claim–evidence 对齐

建立逐句矩阵：每个摘要、引言、贡献点、结果和结论句子都指向代码、配置、原始日志和统计结果。claim 分四级：

1. **协议级**：接口/隔离/回放通过；不能写成方法有效。
2. **信号级**：判断对 later-use/contract 有信息价值；不能写成团队收益。
3. **闭环级**：判断改变 future assignment 并影响未见任务；需要独立 root/stream。
4. **泛化级**：跨 root、漂移、延迟和完整成本仍成立；需要 confirmation evidence。

任何低级证据支撑高级 claim 都是 hard fail。摘要不得出现没有对应 confirmation evidence 的“显著提升”“实时训练已实现”“形成专长”等词。

## E. 强录用目标

这不是官方硬性阈值，而是我们对高质量 AAMAS 方法论文的目标：至少两个结构不同 root（最好三个及以上）、独立 live histories、同信息强 baseline、预冻结主指标和停止规则、报告 effect size 与不确定性、完整成本、失败/UNKNOWN 分母、局限和可复现包。样本不足时必须给出精度/功效理由，不能只报均值。

## F. 必须预先定义的 estimand

主故事不能只写“效果变好”。在实验卡中预先定义单位、处理、时间窗和结果：

- `H1` 信息价值：在相同可见任务上下文和 propensity 下，保留 responsibility-aware situated judgment 相比 raw acceptance/terminal-only，对独立 producer contract 或 later-use 结果的预测增量。
- `H2` 闭环效果：在下一次执行前允许 future owner 使用封存 evidence，相比同信息对照，未见 root 的质量、完整成本和返工成本变化。
- `H3` 在线代价：在给定 arrival rate、并发和 drift 窗口下，更新延迟、backlog、状态大小和遗忘是否满足预注册预算。

每个假设必须写出 primary endpoint、方向、最小关心差异或精度目标、95% uncertainty interval、对照和停止规则。必须报告 assignment 实际使用率，不能把“有机会读 evidence”当作“证据改变了选择”。要检查 identity、task mix、propensity 和 judge/producer 相关误差造成的替代解释。

## G. 论文档次与证据位置

- **Findings-ready**：可以是一个范围清晰、证据充分但广度有限的贡献；至少完成一个可识别箭头并诚实写局限。
- **Proceedings-ready**：必须完成完整 `judgment → role evidence → future assignment → unseen utility` 闭环，并有独立 root、强同信息 baseline、预冻结主分析和可复现 artifact。

核心定义、主要推导、主实验设置和主结果必须在正文；不能把审稿人必须依赖的核心证据藏进 supplementary。supplement 只能扩展复现细节、附加分析或证明，不能修补正文缺失。

## H. 论文行文的行为逻辑

这一节不是要求所有论文使用固定段数，而是要求每一段在同一条论证链上承担可识别的动作。它来自 AAMAS 论文结构审查（docs/research/20260928_aamas_paper_structure_audit.md）中对四篇正式 proceedings 全文的交叉阅读；样本规律、官方要求和本项目 hard gate 必须在审查记录中分开。

### H.1 全文主链

全文必须能压缩成：

协作现象/后果 → 现有方法的一个具体限制 → 最小反例与可证伪问题 → 唯一机制 → 形式化对象和信息边界 → 与机制对应的实验预测 → 结果、替代解释和适用边界

删掉任一箭头后，不能仍然声称同一贡献。章节不能各自讲一个故事；每节结尾应回答“这一步为下一步提供了什么必要输入”。

### H.2 标题、摘要和引言

- **标题**只包含问题对象、核心机制和必要范围；不能把运行时、backbone 或实现名冒充科学贡献。
- **摘要**按五句组织：问题/后果；现有方法的 sharp 限制；核心机制；最重要的可核验结果；范围和代价。结果尚未确认时写研究问题和证据计划，不能写成已完成效果。
- **Introduction**通常按以下功能顺序推进，每个功能可以是一段或多段，但不能把多个中心问题并列：
  1. 说明 multi-agent 协作现象为什么重要；
  2. 给出一个具体、可复现的失败；
  3. 对最近邻方法按“它们看到了什么、什么时候更新、如何归因”说明限制；
  4. 提出一个单一 sharp gap 和最小反例；
  5. 用一句话给出机制，并解释它为什么直接解除该限制；
  6. 给出与机制一一对应的理论/实验问题和证据层级；
  7. 列出可审计贡献，每项都能定位到后文的定义、算法、定理或结果；
  8. 最后给章节路线图（若篇幅允许）。
- 引言末尾必须说明不解决什么，避免把角色学习、信誉传播、workflow 搜索和训练框架写成四个独立主张。

### H.3 Related Work、问题定义和方法

- Related Work 按失败维度或假设分组，而不是逐篇复述；每组结尾必须明确本文解除的限制。
- 问题定义只引入后文实际使用的原始概念；每个新符号必须有输入来源、权限/可见性和一个具体实例。
- 方法章节按“对象 → 信息边界 → 更新/决策规则 → 实现约束 → 可检验预测”展开。公式后必须给自然语言实例；伪代码、状态转移、版本和迟到反馈语义不能留给读者猜测。
- 每个方法子节只引入一个必要机制。普通 backbone、RLS/SGD/refit、缓存、prompt 和适配器必须标为实现基础或 baseline，不能通过堆模块制造创新。
- 理论或复杂度结果必须回答一个实验会用到的问题；不能添加与中心机制无关的装饰性推导。

### H.4 实验、结果和讨论

- 实验开头先冻结任务根、可见信息、baseline、指标、停止规则和成本；随后按 H1 → H2 → H3 顺序回答信息价值、闭环 utility、实时代价。
- 每个结果段使用同一模板：观察（数值、区间、分母、失败/UNKNOWN）→ 解释（为什么支持或不支持机制）→ 替代解释/边界（控制、责任归因、漂移、选择偏差）→ 下一步。
- 图表在正文中必须先被提出问题，再给读者观察路径，最后说明它改变了哪个判断。不能让 caption 独自承担结论。
- 讨论不得把“可运行”“协议通过”“单一 root 成功”升级成闭环效果；若结果不支持 H2/H3，应收窄 claim 并保留负结果。
- 结论重新回答中心问题，报告机制、代价、失败和可外推范围；未来工作不能用来填补当前论文已经声称的证据缺口。

### H.5 段落和句子风格硬门

每个正文段落必须只有一个主要论证动作，并能标注为 claim / context / evidence / interpretation / bridge 之一或一个明确组合。建议使用：

Topic claim → 必要背景或证据 → 与本文机制的关系 → 解释/限制 → 下一段桥接

硬性检查：

- 段首句告诉读者本段要证明或解释什么；
- 同一段不同时定义新对象、报告结果和宣称泛化；
- 首次出现的术语、符号和缩写在本段或前段给出语义；
- 句子中的因果词（导致、因此、证明、形成）必须有对应设计或统计证据；
- 不使用“显著”“高效”“实时”“涌现”“通用”等无指标形容词；
- 每个表/图都在正文中被引用、解释和限定；
- 贡献列表与正文、代码、配置、原始日志和统计输出逐项可追溯；
- 不用相关性、单个案例或作者自评替代责任归因和 future assignment 证据。

### H.6 与本项目故事线的段落映射

| 论文位置 | 必须回答的问题 | 我们的证据 |
|---|---|---|
| Introduction 的 failure 段 | 为什么 raw acceptance/terminal reward 无法学习角色 | 最小反例、producer/recipient 分离 |
| Introduction 的 gap 段 | 最近邻缺少哪一个可识别的时序/归因关系 | novelty table、同信息替代解释 |
| Method 开头 | situated judgment 如何变成 role evidence | 事件、ID/hash、可见性和更新算子 |
| Method 后半 | evidence 如何在执行前影响 future assignment | assignment freeze、第三方 owner、propensity |
| Experiment H1 | judgment 是否包含增量信息 | 独立 contract/later-use 结果 |
| Experiment H2 | assignment 是否真正改变未见任务 utility | independent live histories、质量/完整成本/返工 |
| Experiment H3 | 实时更新是否可用且不遗忘 | delay/backlog/state/forgetting/drift |
| Discussion | 哪些失败仍会误导角色学习 | responsibility、scorer coverage、UNKNOWN、负迁移 |

## I. 一票否决

预设专家身份；脚本指定角色后声称涌现；没有真实 recipient action；没有 future assignment；同一 owner 直接评价后继续选择却声称公共角色形成；把 consumer 自身错误记作 producer 失败；把 UNKNOWN 当负例；只报一次成功；结果看完后改主指标、split 或 claim；近邻方法可以解释收益而论文不承认；论文范围超出实验范围。

## J. 来源边界

官方要求、样本来源与本项目化标准见 [`docs/research/20260928_evaluation_criteria_provenance.md`](../../../20260928_evaluation_criteria_provenance.md)。AAMAS 官方要求支持 originality/significance/soundness/reproducibility/clarity/relevance；责任链、P0 门、novelty table 和 claim 分级是本项目的严格操作化，不是官方逐字规则。
