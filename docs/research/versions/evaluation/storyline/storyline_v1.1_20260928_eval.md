# 故事线评价标准 v1.1

- **状态**：`ACTIVE`
- **类别**：evaluation/storyline
- **评价对象**：[`storyline_v1.0_20260928.md`](../../storyline/storyline_v1.0_20260928.md)
- **生效日期**：2026-09-28
- **前一版本**：`storyline_v1.0_20260928_eval.md`
- **用途**：投稿前的严格故事线预检，不是 AAMAS 官方评分表，也不保证录用。

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

## H. 一票否决

预设专家身份；脚本指定角色后声称涌现；没有真实 recipient action；没有 future assignment；同一 owner 直接评价后继续选择却声称公共角色形成；把 consumer 自身错误记作 producer 失败；把 UNKNOWN 当负例；只报一次成功；结果看完后改主指标、split 或 claim；近邻方法可以解释收益而论文不承认；论文范围超出实验范围。

## 来源边界

官方要求与本项目化标准的来源见 [`docs/research/20260928_evaluation_criteria_provenance.md`](../../../20260928_evaluation_criteria_provenance.md)。AAMAS 官方要求支持 originality/significance/soundness/reproducibility/clarity/relevance；责任链、P0 门、novelty table 和 claim 分级是本项目的严格操作化，不是官方逐字规则。
