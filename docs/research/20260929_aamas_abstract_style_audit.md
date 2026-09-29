# AAMAS 高水平摘要风格审查与当前摘要修订依据

- 日期：2026-09-29
- 状态：`SUPPORTING_AUDIT_UPDATED_OFFICIAL_ABSTRACT`
- 用途：为当前 proposal/pre-results 摘要提供证据化的结构、语气和 claim 边界；不改变 Goal、故事线、方法或 benchmark 选择。
- 研究对象：当前生效的 `article/aamas2027/research_proposal.tex` 与 `article/aamas2027/mainline_pre_results.tex`。

## 1. 语料范围与证据边界

AAMAS 的公开页面通常公布主会论文、获奖论文和 finalists，但不会在 proceedings 页面为每篇论文稳定标注 “oral”。因此本审查不把 “oral” 当作可观测标签，而采用可复核的近似语料：AAMAS 2025 Best Paper、Best Paper finalists，以及同届主会研究论文；再用 AAMAS 2026 的本地归档论文作跨年度风格复核。这个替代口径是为了避免把不存在的 oral 标签写成事实。

主要一手来源如下：

| 论文/来源 | 选择理由 | 摘要中可核验的特征 |
|---|---|---|
| [Soft Condorcet Optimization for Ranking of General Agents](https://www.ifaamas.org/Proceedings/aamas2025/pdfs/p1253.pdf) | AAMAS 2025 Best Paper | 先说明跨任务 agent 比较的具体困难，再给出 SCO、最大似然解释、三个算法和三层量化验证；报告 `0--0.043`、`59%`、`52,958/31,049` 等尺度。 |
| [Leveraging Large Language Models for Effective and Explainable Multi-Agent Credit Assignment](https://www.ifaamas.org/Proceedings/aamas2025/pdfs/p1501.pdf) | AAMAS 2025 主会方法论文 | 把 credit assignment 重写为 sequence improvement + attribution 两个可识别问题；随后给出 LLM-MCA/LLM-TACA、多个 benchmark 和结果范围。 |
| [Compositional Shielding and Reinforcement Learning for Multi-Agent Systems](https://www.ifaamas.org/Proceedings/aamas2025/pdfs/p399.pdf) | AAMAS 2025 主会方法/理论论文 | 从指数规模与全局安全/局部 shield 的冲突切入，以 assume-guarantee 作为单一关键操作，并给出“hours to seconds”和收敛结果。 |
| [Curiosity-Driven Partner Selection Accelerates Convention Emergence in Language Games](https://www.ifaamas.org/Proceedings/aamas2025/pdfs/p1282.pdf) | AAMAS 2025 Best Paper finalist | 将 partner selection 的历史信息与可观察行为限制说清，再给出选择规则、random matching 对照和网络演化结果。 |
| [AAMAS 2025 Best Paper and Demo Awards](https://aamas2025.org/index.php/conference/awards/best-paper-and-demo-awards/) | 官方奖项页面 | 证明 SCO 是 Best Paper，且 partner-selection 论文是 finalist；不据此推断所有论文的 oral 状态。 |
| [AAMAS 2025 Call for Papers](https://aamas2025.org/index.php/conference/calls/call-for-papers-main-technical-track/) | 官方评价范围 | 明确 originality、significance、soundness、reproducibility、clarity、relevance 和 state-of-the-art engagement 是整体审查维度。 |

本地全文/摘要缓存见 `references/aamas/papers/2025_soft_condorcet.txt`、`2025_partner_selection.txt`、`2026_partner_selection.txt`、`2026_reputation.txt` 与 `2026_human_llm_teams.txt`。它们用于段落行为分析，不替代上表的一手 URL。

## 2. 反复出现的摘要行为

### 2.1 摘要不是组件目录，而是一条可验证论证链

优秀样本普遍按以下顺序压缩全文：

```text
协作现象/实际后果
  → 一个具体且可反驳的限制
  → 一个中心机制或形式化对象
  → 方法如何解除该限制
  → 与机制一一对应的 benchmark/baseline/尺度
  → 量化结果或清楚的证据边界
  → 结果意味着什么、在哪些范围内成立
```

SCO 的第一句不是泛泛说“agent 很重要”，而是指出 general agent 的跨任务比较必须聚合多种任务表现；随后每一句都服务于 ranking objective、优化方法或三层验证。Compositional Shielding 先给出指数规模与全局安全/局部约束的冲突，再只引入 assume-guarantee 这一核心操作。两者都避免把表示、运行时、数据处理和实现库并列成贡献。

### 2.2 sharp gap 是一条具体的观察/归因/时序限制

样本中的 gap 具有“如果去掉这个假设，现有方法会在什么地方失效”的形式：

- SCO：评价数据可能跨任务、不完整且有噪声，简单 Elo 不保证 Condorcet winner 的性质；
- Partner Selection：已有工作假设 agent 在第一次交互前知道其他 agent 的历史行为；
- LLM-MCA：全局奖励不能直接说明每个 agent 的动作贡献；
- Shielding：局部 shield 需要共同保证全局安全，但直接合成会指数扩张。

这类句子比“现有方法不能很好地适应动态环境”更有用，因为审稿人可以直接问：输入是否真的缺失、方法是否真的补上、实验是否真的隔离了这个限制。

### 2.3 方法句只做一个动作，但动作必须可复述

高质量摘要会在一到两句内说清楚“我们引入什么操作”：SCO 把 noisy comparisons 看作 votes 并做最大似然 ranking；LLM-MCA 把 credit assignment 重写成 sequence improvement 与 attribution；Shielding 用 assume-guarantee 把 global obligation 分解到 local shields。名称后面紧跟对象、输入和目的，而不是只说“提出一个新框架”。

### 2.4 结果句必须让读者知道规模、对照和指标

有结果的样本至少给出一种可核验尺度：误差范围、缺失比例、数据集数量、玩家/对局规模、计算时间、收敛速度、相对 baseline 的方向。SCO 的摘要尤其完整：`865` 个 preference profiles、`59%` 缺失、`52,958` 名玩家和 `31,049` 局 Diplomacy。没有最终结果的摘要也应给出明确的证据边界，不能用“有效”“高效”“实时”替代证据。

### 2.5 语气是确定但可审计的

正式论文使用 “We propose / We formulate / We show / We evaluate”，不使用宣传式形容词堆叠。真正尚未完成的结果则必须显式降格为 “we study / we specify / we will evaluate”，而不是为了模仿 oral 风格伪造 “we show”。过程信息（内部版本、编译、API 探针）不应占据摘要主体；它们应放在正文首段、脚注或项目记录中。

## 3. 当前两个摘要的审查

### 3.1 `mainline_pre_results.tex`

当前摘要约 155 词、7 句，长度和总体顺序合格：问题 → 窄问题 → 协议/更新 → 评价 → baseline → 证据边界。但有三个可修复问题：

1. 开头的 “static role, a global score, or a pooled controller” 是近邻目录，尚未马上给出它们共同遗漏的可识别信息；
2. “candidate responsibility-aware role-evidence update” 没有在同一句说明它改变了什么可观察决策，`candidate` 和 `lawful delayed feedback` 使方法像内部接口说明；
3. 最后一句一次性列出 API traces、scorer、attribution、efficacy、specialization、real-time training，过程与科学结论混在一起，削弱主线。

当前摘要没有科学越界；问题是论证密度与中心对象还不够干净，而不是缺少更多术语。

### 3.2 `research_proposal.tex`

当前摘要约 211 词、11 句，proposal 信息完整但偏长。它重复定义 role、transfer 和 central question，并把 “backbone and update rule remain to be determined” 放进摘要，使读者先看到工程未决项，而不是研究对象。Proposal 可以保留 prospective 语气，但应把中心问题、闭环和预注册比较压缩到约 160--190 词；当前证据边界移到文档正文。

### 3.3 当前内部评分（不是录用预测）

| 维度 | mainline | proposal | 判断 |
|---|---:|---:|---|
| 问题切口 | 4/5 | 3/5 | mainline 已指出 recipient 的具体使用；proposal 仍偏“协作需要分工”。 |
| gap 可反驳性 | 3/5 | 3/5 | 需要直接写出 raw acceptance/terminal reward 为什么不能归因。 |
| 中心机制可复述性 | 3/5 | 2/5 | role evidence 有了，但责任归因、未来 assignment 和更新动作未压缩成一句。 |
| 评价与证据边界 | 4/5 | 4/5 | 没有把协议证据冒充功效；这是当前最稳的部分。 |
| 语气与密度 | 3/5 | 3/5 | mainline 末句过载；proposal 句数较多且包含工程未决项。 |
| 总体 | **17/25** | **15/25** | 可作为内部稿摘要；距离有真实结果的提交版还差 benchmark、baseline 和结果句。 |

这个分数只衡量摘要是否把当前研究说清楚，不能替代三份生效评价文档，也不代表论文录用概率。

## 4. 当前修订原则

当前没有闭环功效、专长形成或实时训练增益，因此不能照抄有结果论文的 “outperforms” 句式。修订只做三件事：

1. 把 `recipient 使用/修改/拒绝 → producer 可归因 evidence → future assignment` 作为一个动作写出来；
2. 把 raw acceptance、terminal-only 和 contextual trust/bandit 明确成替代解释，而不是方法清单；
3. 将内部运行状态压缩成一句诚实的证据边界，保留所有失败和 UNKNOWN，不提前填入数字。

目标结构为：

```text
具体协作失败（1句）
→ sharp attribution gap（1句）
→ Earning Roles 的中心机制（2句）
→ benchmark/baseline/指标（1--2句）
→ 当前证据边界（1句）
```

未来提交版只有在 H1/H2/H3 证据齐备后才能把最后一段替换成数值结果；不能因为摘要风格要求而提前升级 claim。

## 5. 可复用的最终提交版骨架

下面是结果完成后的句法骨架，不是当前结果：

```text
Multi-agent systems [具体协作后果]. Existing [近邻] cannot [具体观察/归因/时序限制].
We propose [唯一机制], which turns [输入事件] into [可用状态] before [未来决策].
The mechanism [说明责任过滤、延迟/在线更新和第三方 assignment 的必要动作].
Across [根/任务规模], against [同信息强 baseline], it [主指标、区间、成本或延迟结果].
Ablations show [机制必要性] and [失败/适用边界].
These results establish [严格范围内的系统性质], rather than [未测量的泛化 claim].
```

该骨架要求结果句与实验矩阵逐字对应：没有对应 cell、分母、区间和成本记录，就不能填入 “improves”“real-time” 或 “self-evolving”。

## 6. 结论与后续动作

摘要层面的下一步不是继续增加术语，而是保持中心机制和证据边界一致。提交版摘要可以先使用研究设计层面的陈述；最终完整论文若获得结果，必须用主指标、区间和成本结果替换设计性句子，不能补写未经实验支持的效果。

## 7. 官方摘要版修订（2026-09-29）

根据作者对内部过程语句和方法章节式语气的进一步纠正，当前两个 LaTeX 源的摘要已统一为可直接提交的 184 词研究摘要。摘要中删除了 `internal`、`pre-results`、`current traces`、`no efficacy` 以及“在约束下形式化”式过程表述，改为直接突出机制相对于 global reputation/terminal-only selector 的信息保留、责任归因和后续修正优势。保留以下可证实的研究设计陈述：

```text
问题：具体交付是否真正帮助了使用它的 recipient；
机制：recipient 的 situated judgment 经责任检查后成为 producer 的 role evidence；
闭环：延迟证据在下一次执行前影响 future assignment，并可被后续独立结果修正；
验证：held-out task roots、独立检查、selected-only feedback 和 matched cost/baselines；
在线性质：测量 drift adaptation、update latency 与旧能力 retention。
```

这版摘要没有虚构 headline result，也没有把未完成的实验写成正面效果；它直接描述待提交论文的研究对象、方法和验证设计。正式结果提交时，只需将评价设计句替换为与冻结实验矩阵逐字对应的 effect size、uncertainty 和成本结果。
