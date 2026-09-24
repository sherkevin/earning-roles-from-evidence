# 面向 peer-judged role formation 的 agent benchmark 与 baseline 调研

**日期：** 2026-09-24  
**性质：** 文献与公开仓库的工作性调研，不是正向实验结果，也不等同于 benchmark lock。  
**目标：** 判断“producer artifact → recipient judgment/use/repair → role evidence → future responsibility”是否已有可直接使用的 benchmark，以及一篇可发表的论文通常如何组织 benchmark、scorer 和 baseline。

本报告与[近年 benchmark 补充审计](../../../references/aamas/benchmark_survey_recent_20260924.md)互相引用：本报告强调科学识别和最小实验协议，补充审计展开了 TeamBench、AWS collaboration scenarios 和 Dynamic Role Assignment 等近期近邻。

## 结论先行

截至本次调研，没有一个公开 benchmark 同时提供下面这条完整、可审计的因果链：

```text
producer 交付具体 artifact
→ 实际 recipient 在看到终局结果前作出 accept / reject / repair 判断
→ recipient 真正使用、返工、拒绝或独立重做
→ 判断的来源、上下文和终局修正形成 producer 的 role evidence
→ 没有直接参与原判断的第三方在后续机会中改变 producer 的 responsibility
→ 用 native objective scorer 衡量 team quality、rework 和 total cost
```

现有工作大多只覆盖其中一到两段：

| 工作 | 已经解决的部分 | 没有解决的部分 | 对本项目的价值 |
|---|---|---|---|
| [CooperBench](https://arxiv.org/abs/2601.13295) / [代码](https://github.com/cooperbench/CooperBench) | 真实代码仓库、相互依赖的 feature、冲突、solo/coop/team、native tests 和协作成本 | feature owner 预先分配；没有 recipient judgment/use/repair，也没有跨任务 role update | **最适合做主 substrate**，我们增加薄协议层 |
| [MultiAgentBench / MARBLE](https://arxiv.org/abs/2503.01935) / [代码](https://github.com/ulab-uiuc/MARBLE) | 多域任务、预设角色、拓扑、milestone、协调指标、协议对照 | 角色是 preset；主要协调分数由 LLM evaluator 给出；没有 earned role | 借 milestone、graph 和配置方式，不承担主结论 |
| [τ-bench](https://arxiv.org/abs/2406.12045) / [最新代码](https://github.com/sierra-research/tau2-bench) | 有限状态、隐藏数据库、用户/工具轨迹、规则化终局、pass^k | 没有 producer-consumer artifact 和第三方角色分配 | 借隐藏状态、任务唯一性、重复试验和规则 scorer |
| [ToolSandbox](https://arxiv.org/abs/2408.04682) / [代码](https://github.com/apple/ToolSandbox) | stateful tool、可见性、snapshot、intermediate/final milestones | 没有 peer role learning | 借 visibility、checkpoint、milestone evaluator |
| [LifelongAgentBench](https://arxiv.org/abs/2505.11942) / [代码](https://github.com/caixd-220529/LifelongAgentBench) | 有序、依赖、跨 episode 的长期任务，replay/no-replay baseline | experience 是自身轨迹，不是 recipient judgment；无第三方 assignment | 借 sequence split、persistent identity、历史预算和负迁移分析 |
| [AgentBoard](https://arxiv.org/abs/2401.13178) / [代码](https://github.com/hkust-nlp/AgentBoard) | 中间进度指标，并用多名人工标注者验证 | 不研究角色形成 | 借 intermediate metric 的人工一致性验证 |
| [AgentBench](https://arxiv.org/abs/2308.03688) / [代码](https://github.com/THUDM/AgentBench) | 多环境、固定 dev/test、统一评测、模型对照、公开 evaluator | 主要是单 agent，不含 peer judgment | 借“多环境 + 固定 split + 可复现 evaluator”的发表范式 |
| [SWE-bench](https://arxiv.org/abs/2310.06770) / [SWE-agent](https://arxiv.org/abs/2405.15793) | 真实 issue、repo-level patch、programmatic tests、pass@1 | 不是 multi-agent，也没有交付采用过程 | 借真实任务与独立测试的可信度 |
| [TeamBench](https://arxiv.org/html/2605.07073) / [代码](https://github.com/ybkim95/TeamBench) | Planner/Executor/Verifier 的角色边界、solo/restricted/full-team、role violation 和 verifier disagreement | verifier 只评价当前提交，不形成跨任务公共 role evidence | 借 role-violation、judge–grader disagreement、compute-matched solo 和按难度分层的报告方式 |
| [AWS multi-agent collaboration scenarios](https://arxiv.org/abs/2412.05449) / [代码](https://github.com/aws-samples/multiagent-collab-scenario-benchmark) | 企业场景、结构化 payload、Coder→Test/Review handoff、assertion evaluator | 角色和责任预设，未记录 recipient 采纳如何改变未来责任 | 借 payload/artifact schema 和多角色 assertion 设计 |

因此，我们不能把已有工作简单改名为“role-learning benchmark”。合理定位是：**在真实协作代码任务上构建一个 peer-judged role-formation protocol benchmark extension**。它的科学贡献是新增 judgment-to-role protocol 和可识别的对照，而不是重新发明代码环境或 agent runtime。

## 1. 别人是如何把 benchmark 论文做成可发表结果的

从 AgentBench、τ-bench、ToolSandbox、LifelongAgentBench、SWE-bench 和 CooperBench 可以归纳出一套稳定结构。它不是“任务数量足够多”这么简单，而是下面七件事同时成立：

1. **能力问题边界单一。** 论文先声明一个可证伪的能力缺口，例如长期依赖、工具状态、真实代码修复或协作冲突，而不是同时宣称 planning、memory、role、workflow、emergence 都被解决。
2. **任务可以执行，结果可以复核。** 任务要有隐藏状态或真实仓库，有明确的 action/API/patch 接口，终局由 native tests、数据库状态、inventory 或其他独立规则判定。LLM judge 可以做辅助标签，不能独自承担主结论。
3. **数据划分阻断泄漏。** τ-bench 按任务设计隐藏 state 和唯一目标；SWE-bench 按 issue/repository 留出；LifelongAgentBench 保留任务顺序。我们的 split 至少要按完整 task root，最好按 repository 留出。
4. **baseline 和方法信息、预算匹配。** CooperBench 的 solo/coop/team 对照之所以有解释力，是因为同一任务和 native evaluator 下比较不同协作组织。τ-bench 的多次 trial 和 pass^k 说明单次成功率不足以描述 agent 行为。我们的每个控制必须拿到相同模型、工具、机会、存储和 API/test budget。
5. **指标和科学问题一一对应。** 终局 task success 只能回答任务是否完成；它不能回答 artifact 是否被采用，也不能回答 role 是否学会。中间指标必须有人工或独立程序验证，AgentBoard 对进度标签报告了多人一致性，这正是我们需要为 recipient judgment 做的事。
6. **报告失败与成本。** 真实 agent 工作有 timeout、merge conflict、重复调用、返工和不稳定性。论文需要报告每个样本的轨迹和成本，而不是只给一个平均成功率。
7. **公开到能复现。** 公开 task manifest、source commit、启动命令、scorer、raw event log、模型/seed/budget 和失败分类，才能把“看起来有效”变成可审查结果。

这也解释了为什么“加入一个角色标签”不能成为我们的 benchmark：没有前行动作、后续责任和独立终局，审稿人无法判断它是 role learning、普通 trust、随机分配还是 prompt effect。

最近的 [Dynamic Role Assignment / Meta-Debate](https://arxiv.org/abs/2601.17152) 已经把“peer review → role assignment”作为概念性问题来研究，因此这是我们必须正面比较的近邻，而不是可以忽略的空白。它的 peer review 发生在同一题的角色选择前，审查的是候选 proposal；它没有真实 artifact 的后续采用/返工、终局校正和跨 episode 的第三方责任转移。它应作为可选的 B5 或 novelty threat，且只有在信息、预算和任务粒度都忠实时才有比较意义。

## 2. 逐项判断最接近的工作

### 2.1 CooperBench：最好的主基底，但不是现成答案

CooperBench 用真实仓库里的 cooperative coding tasks 比较 `solo`、`coop` 和 `team`。公开数据覆盖多个仓库、语言和 feature pair；它保留 patch、conversation、claims、时间、通信和测试结果，并以 feature tests 和 merge 状态评估。论文还给出 expectation failure、communication failure 和 commitment failure 的失败分类，说明 benchmark 不只是“跑一次 agent 得分”。

它与我们的故事最接近，因为 patch 是可归属的 artifact，recipient 可以在另一个依赖 feature 中真正使用或修改它，最终可由 native tests 检查。但是原生设置预先把 agent 分配到 feature，且冲突时存在 `solo-agent` fallback。因此 `both tests pass` 不能证明 recipient 采用了 producer 的 patch；也不能证明 role evidence 改变了下一次责任。

主线应当复用其仓库、task root、patch sandbox 和 scorer，额外实现：

- `ArtifactReceipt`：记录 producer、parent task、文件、diff/hash、recipient 可见字节范围；
- `JudgmentGate`：首次集成或修改前封存 accept/reject/repair/independent-redo、置信度和拟使用 artifact；
- `ConsumerExecutor`：区分实际采用、局部返工、拒绝后独立重做；
- `RoleEvidenceLedger`：保存 judge、context、provenance、outcome 和 cost，并把公共 role evidence 与 judge 的私有 trust 分开；
- `ThirdPartyAssigner`：让没有直接参与原判断的 owner 在下一责任机会中选择 producer；
- `CostLedger`：token、调用、tool actions、wall time、通信和 rework 全部入账。

### 2.2 MultiAgentBench / MARBLE：能证明“协作协议可评估”，不能证明“角色被学出来”

MARBLE 提供 research、Minecraft、database、coding、bargaining、Werewolf 等场景，用 star/chain/tree/graph 拓扑、milestones、task score、communication/planning score 做对照。它的优点是多域、预定义 KPI、协议图和多模型结果齐全，展示了怎样把一个大而模糊的“协作”拆成可跑的评测。

但 roles、profiles 和 graph 往往在配置里预先写死；协调分数还依赖 LLM evaluator。它回答的是“已知角色和拓扑下的协作效果”，不是“recipient 的 situated judgment 是否形成了未来 role”。我们最多借 task/config/milestone 结构或把它作为 fixed-workflow comparator。

### 2.3 τ-bench：任务少也可以有说服力，前提是状态和 scorer 足够干净

τ-bench 把一个任务定义为隐藏数据库状态、用户目标、policy 和可调用工具上的有限状态过程，终点由数据库状态比较确定；它还用多次 trial 报告 pass^k，暴露 agent 的不稳定性。任务设计包含人工 schema/policy 设计、模型生成候选和人工验证，重点不是堆样本数量，而是保证每个任务有唯一、可检查的成功状态。

我们应借它的三个原则：把 recipient 的可见性和状态写成协议；为每个 episode 定义唯一的 downstream objective；重复 seed/trial 并报告 reliability。不能借它的 user simulator 替代我们的 peer，因为我们的 peer 必须实际拥有依赖任务并执行 artifact use/repair。

### 2.4 ToolSandbox：把“看到了什么、何时能行动”做成一等公民

ToolSandbox 把工具、对话和世界状态放在可快照的执行上下文中，支持角色级消息可见性、隐含状态依赖和 intermediate/final milestones。对我们最有用的不是具体工具，而是它证明了 observation boundary 和 snapshot 可以被严格记录并复现。

我们的 judgment 必须发生在 terminal tests 之前，而且事件只能读取 receipt 声明的内容；一旦 recipient 已经读取终局 evaluator，那个判断只能被标成 post-outcome control，不能再当作前行动机。

### 2.5 LifelongAgentBench：为“后续责任”提供最清楚的时间结构

LifelongAgentBench 在 Database、Operating System 和 Knowledge Graph 中组织有技能依赖的任务序列，比较 no replay、不同 replay window 和 self-consistency。它固定 container snapshot、seed 和任务顺序，结果显示无关历史可能伤害后续性能。这是我们最应借鉴的 longitudinal 设计：role evidence 必须跨 episode 传播，且必须验证它在新 task/root 上是否有帮助或产生负迁移。

它仍然不是我们的 benchmark，因为它保存的是 agent 自己的成功轨迹，没有 recipient 的 situated judgment，也没有“第三方 owner 不看私有评价仍改变责任”的检验。

### 2.6 AgentBoard：中间判断必须验证，不能靠方法作者自说

AgentBoard 用细粒度 progress rate 记录 agent 在长轨迹中的进展，并用四名人工评审和一致性指标验证该中间指标。我们的 accept/use/repair/reject 不是天然真值：必须在小批量中用人工或独立规则检查它是否真的对应“采用了 artifact”“只做了局部修复”“完全重做”。如果无法验证，就只能把它当作模型自报信号，不能作为核心机制证据。

## 3. 对我们任务的 benchmark 判断

### 3.1 是否已有自己的 benchmark？

**没有。** 目前公开 benchmark 没有同时提供 peer judgment、artifact use/rework、source-aware evidence 和 third-party future assignment。已有 CooperBench 等工作能提供客观执行底座，但不包含我们的科学干预。

这不是坏消息：它给了清晰的创新边界。我们不应宣称“提出了一个通用 multi-agent benchmark”，而应先做一个小而干净的 **CooperBench peer-judged role-formation extension**。只有在多个 repository/task-root、独立 scorer、固定 split 和外部有效性通过后，才考虑把它升级为独立 benchmark 名称。

### 3.2 推荐的最小 benchmark 形状

第一阶段只做一个完整 vertical slice：

1. 按完整 task root 选择 4–8 个 development episodes，每个 episode 有 producer feature、dependent recipient feature 和一个后续 responsibility opportunity；
2. 先运行 recipient-redo，再运行 artifact-handoff，二者使用相同模型、工具、预算、任务状态和 seed 协议；
3. recipient 在任何修改、测试或查看终局结果前写 judgment seal；
4. 记录实际采用的 artifact、文件/行级变更、repair delta、独立重做和 native test；
5. 将 judgment 和终局结果写入 source-aware ledger；下一 episode 由没有直接评价该 producer 的 owner 选择责任；
6. 把确认集按 repository 留出。若样本不足，明确写成 task-root development evidence，不冒充跨域泛化。

这个规模足以先验证协议是否能跑通，但不足以支持“大规模 benchmark”或普遍性结论。确认阶段至少需要更多 task roots、多个 seeds，并报告按 root 的置信区间，而不是把同一仓库的 feature pair 当作独立组织。

### 3.3 量级：benchmark 池、论文样本和 baseline 要分开

“好论文的 benchmark 有多大”没有一个固定数字。公开工作的量级差异很大：CooperBench 报告 652 个 feature-pair、30 个 task roots、12 个仓库；TeamBench 是 851 个模板扩展成 931 个 seeded instances；WebArena 有 812 个 web tasks；SWE-bench 原始版有 2294 个 issue instances，但也使用 300/500 个严格筛选子集。换句话说，任务数量从几十个高质量独立场景到上千个公开实例都能发表，决定可信度的是独立性、难度覆盖、objective evaluator、split 和 baseline，而不是单纯的总行数。

对本项目可以先冻结下面这个**分层量级方案**，但要把“全量 benchmark 池”和“论文确认样本”明确区分：

| 层级 | 规模 | 用途 | 是否可作为主结果 |
|---|---:|---|---|
| benchmark inventory | CooperBench 全部 30 个 task roots、12 个 repositories、652 个 feature-pairs | 公开任务池、难度/语言/冲突分层、后续复现 | 是，但不要求第一轮全部调用模型 |
| protocol smoke | 4–6 个 roots，每个 1–2 个 pair，1 seed，7 个 arms | 检查 receipt、judgment seal、use/rework、scorer 和 assignment 是否可重放 | 否 |
| development pilot | 6–10 个 roots，至少 12–20 个 pair episodes，2 seeds，7 个 arms | 只估计成本、失败率、judgment 可用性和方差；冻结实现和分析规则 | 否 |
| confirmation minimum | 至少 20 个互不重叠的 task roots，约 40 个 pair episodes，2 seeds，7 个 arms | 论文主分析的最低可辩护规模；按 root 做 block bootstrap/置信区间 | 可以，但只支持中等或较大效应 |
| confirmation target | 尽可能覆盖全部 30 个 roots，约 60 个 pair episodes，2 seeds，7 个 arms | 跨仓库/语言/冲突类型的稳健性与失败边界 | 最理想 |

这里的“7 个 arms”是 `B0–B5 + P`，所以 confirmation minimum 大约是 `40 × 2 × 7 = 560` 个 arm-episodes；每个 arm-episode 内还有 producer、recipient 和 assignment 的多次 API 调用。这个数字看起来大，但它不是 560 个独立组织：主要独立单位仍是 task root，pair 和 seed 是 root 内的重复观测，分析时必须按 root 聚类，不能把 560 当成样本量。

如果实际 API 成本只能支持 12–14 个 confirmation roots，就只能称为 development/limited confirmation，不能声称跨仓库的稳定 role-learning 效果。反过来，也不应为了凑到 1000 个调用而重复同一 root、同一 pair 或同一身份；重复不会创造新的独立证据。

baseline 的合理量级是 **5–8 个对照臂（包含 proposed arm 后总共 6–9 个 arms）**。少于 4 个通常无法区分 pooled upper bound、固定协作、artifact 边际价值和普通 contextual trust；超过 8 个若没有新的识别问题，容易变成成本很高的 baseline 展示。我们的核心矩阵定为 6 个 baseline 加 1 个 proposed arm，已经足够干净：

- `B0` pooled single-agent / centralized selector；
- `B1` fixed-coop / no-role update；
- `B2` recipient-redo / no-handoff；
- `B3` raw acceptance；
- `B4` same-information contextual trust/bandit；
- `B5` terminal-only feedback；
- `P` source-aware peer-judged role ledger。

Closest peer-feedback 或 Meta-Debate 只有在实现忠实、信息/预算匹配且确实覆盖额外威胁时才加入，不能为了让 baseline 数量更大而加入。

因此现在可以确定的是：**benchmark 身份和 baseline 家族可以冻结；confirmation 的最终 task-root 数量要等 scorer、handoff adapter 和 development pilot 的成本/方差门通过后再冻结。** 这是实验设计上的必要顺序，不是继续拖延。

### 3.4 主指标

核心 endpoint 应该是 **future responsibility utility**，而不是 role label 数量：

- future assignment quality：后续 owner 是否给更匹配的 responsibility；
- objective quality：native tests、merge status、独立验证和任务完成；
- recipient fidelity：artifact 被采用、局部修复、拒绝或独立重做的比例；
- correction：错误 judgment 被终局事实修正的延迟和成功率；
- cost：LLM/API、tool、communication、sandbox、wall time 和 rework；
- calibration：若 judgment 输出概率/置信度，报告 Brier/ECE 或可靠性曲线；
- generalization：在未见 task root/repository 上的 role evidence 是否仍有用；
- failure taxonomy：conflict、misattribution、premature judgment、leakage、timeout、fallback 和 wrong assignment。

milestone/coordination score 可作诊断指标，但不能代替 future responsibility utility。role label 变化而后续责任、任务质量或总成本不变，不算 role learning。

## 4. 推荐 baseline：必须做成可识别的最小矩阵

所有 arm 使用相同 task roots、初始 agent/model/tool、任务机会、合法可见信息、持久化容量和总 API/test budget。控制臂不能继承 proposed arm 已经学到的实际 memory 或 workflow。

| ID | baseline | 它回答的问题 |
|---|---|---|
| B0 | pooled single-agent / centralized selector | 多 agent 协作是否还值得？给能力和成本上界 |
| B1 | fixed-coop / no-role update | 普通固定分工和通信本身能做到什么 |
| B2 | recipient-redo | producer artifact 是否带来边际价值，而不是 recipient 自己重做 |
| B3 | raw acceptance | 只累计 accept 比例是否已经足够 |
| B4 | local trust | 只有当前 owner 的私有信任能否解释收益 |
| B5 | same-information contextual trust/bandit | proposed update 是否只是一个普通在线 contextual selector |
| B6 | terminal-only | 只看终局成功是否已经足够；前行动 judgment 是否有额外价值 |
| B7 | random/fixed assignment | 下限和 assignment gain 的最小 null |
| P | source-aware peer-judged role ledger | 完整 proposed mechanism |

最关键的可识别比较是：

- P vs B2：交付 artifact 的边际价值；
- P vs B3：use/repair/provenance 是否超过 raw acceptance；
- P vs B5：source-aware situated judgment 是否超过普通同信息在线学习；
- P vs B6：前行动 judgment 是否超过 terminal-only update；
- P vs B0/B1：全局质量、成本和协作稳定性是否改善。

如果 B5 与 P 持平，应收窄或放弃“peer judgment 是必要机制”的主张；如果 B3 与 P 持平，则 use/repair/provenance 复杂度没有被实验支持；如果 P 只改变角色标签而不改变未来 responsibility 或 utility，则不是 role-learning 结果。

## 5. 评审人会怎样审查这篇论文

AAMAS 审稿人很可能逐项追问：

1. recipient 判断是否早于终局结果，还是作者把 outcome 泄漏进了 label？
2. recipient 是否真的使用/返工了 artifact，还是两份 patch 独立通过了测试？
3. 下一次 assignment 是否真的改变，且选择者是否独立于原 judge？
4. P 是否只是在换名字的 reputation/trust/bandit？
5. 各 baseline 的信息、模型、预算和工具是否严格匹配？
6. 结果是否跨 task root、repository、model 和 seed，还是单个仓库的 feature pair？
7. scorer 是否独立、可运行、不会把 `solo fallback` 计为协作成功？
8. 是否报告 rework、通信、token、时间和失败，而不是只挑成功率？
9. judgment 中间指标是否经过人工/独立程序校验？
10. 代码、task manifest、source commit、raw JSONL 和 replay 是否足以复现？

这些问题也构成我们当前的 acceptance gates；它们比“再多找几个 baseline”更优先。

## 6. 项目当前的执行建议

当前的条件性基础设施选择仍然合理：CooperBench 做主 substrate，OpenHands SDK 只做 runtime，AgentWorld 作为第二阶段外部有效性候选。它们的详细复用边界和现有 gate 见 [peer-role assembly plan](../../paper/aamas2027/PEER_ROLE_IMPLEMENTATION_ASSEMBLY_PLAN_20260924.md) 和 [benchmark reuse audit](../../../references/aamas/reuse_design_20260924/benchmarks/README.md)。

接下来按以下顺序推进：

1. 先冻结 CooperBench task-root manifest、split、license/scorer note；
2. 用零模型 fixture 完成 F4–F9：receipt、pre-action judgment、use/rework、terminal correction、public ledger、third-party assignment；
3. 用确定性 fixture 证明 B2/B3/B5/B6 与 P 的事件 schema 和预算能公平运行；
4. 只在上述协议和 scorer 通过后，用 Idealab 的“内部”真实模型跑 2–4 个 development roots，并把配置、每次请求、原始响应、错误、token、seed、commit 和每条样本结果写入 JSONL；
5. 冻结独立确认集，再扩展到更多 roots 或 AgentWorld。若 CooperBench 不能提供可归属的交接顺序，就把它降级为代码集成底座，不包装成角色学习 benchmark。

本调研没有得到“现成 benchmark 可以直接跑出论文结论”的结果；它得到的是一个更干净的可发表边界：**用已有真实任务和独立 scorer，新增并验证 peer-judged role-formation protocol，再用严格同信息 baseline 证明它不是普通 trust、终局反馈或单人上界。**
