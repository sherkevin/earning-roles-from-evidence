# 近年 Agent / Multi-Agent Benchmark 调研：对 peer-judged role formation 的支撑关系

**调研日期：2026-09-24**  
**目标：**判断当前论文能否直接复用公开 benchmark，别人通常如何把 benchmark 论文发表出来，以及我们应如何确定主 benchmark 和最小 baseline 套件。

## 结论先行

截至本轮审计，没有发现一个公开 benchmark 原生覆盖下面的完整因果链：

```text
依赖任务 → producer 交付可归因 artifact
→ recipient 在终局结果可见前作出 situated judgment
→ recipient 实际 accept / use / repair / reject
→ objective terminal outcome 对判断进行可能的纠正
→ producer 获得 source-aware role evidence
→ 后续任务在判断影响下改变责任分配
```

因此不能声称“我们直接在某个现成 benchmark 上评估了角色学习”。更准确的论文定位是：**在真实可交付任务 benchmark 上加一层薄的、可审计的 peer-judgment / future-assignment protocol**。现有 benchmark 只提供底层任务、执行环境和终局验证；F5–F9（判断、采用归因、终局校正、角色证据、后续责任）必须由我们实现并验证。

对本项目的推荐顺序：

1. **主 benchmark：CooperBench 派生的代码交付/集成任务。**它最自然地形成 producer patch → owner 接收/修复/重做 → 原生测试和 merge 状态 → 下一次责任机会。当前项目已有固定提交和 native-test 审计，但需完成薄适配层、官方/独立 scorer 说明和 held-out vertical slice。
2. **状态化评估组件：AppWorld 或 ToolSandbox 的 evaluator 思路。**AppWorld 的 state-diff/unit-test 和 scenario consistency 适合开发协议；ToolSandbox 的 milestone/minefield DAG 和 on-policy user simulator 适合设计中间事件审计。二者默认是单 agent / user-agent，不能直接充当主多 agent benchmark。
3. **外部有效性：AgentWorld。**其多 agent、黑箱、资源转移、多轮环境可以验证方法是否只对代码 patch 有效；但角色和能力预先写进任务，不能代替主链条。
4. **评估方法参照：TeamBench。**它说明多 agent 论文不能只报 pass rate，必须报告角色违规、verifier–grader disagreement、compute-matched single-agent、按 Solo 难度分层的 team uplift。它不提供 peer judgment 的未来学习，但应作为我们的审稿自检标准。
5. **不把 MARBLE/MultiAgentBench 当主 benchmark。**它适合固定 workflow/topology 对照和 adapter，角色、图结构、milestone/LLM judge 多数是预先指定的，不能支持“角色由 situated peer judgment 形成”的核心因果主张。

## 论文级 benchmark 通常怎样成立

近年的高质量 agent benchmark 论文不是只发布一个任务列表，而是同时交付四个层次：

- **可复现环境：**固定版本、独立 reset、工具/工作区、执行轨迹和失败恢复边界。
- **任务与 split：**真实或高保真任务、公开开发集与隐藏/未见测试集，避免把同一任务族的变体当成独立组织样本。
- **可验证 evaluator：**优先终局 state diff、unit tests、database goal state 或程序化 grader；有多条正确路径时不能简单比 reference trajectory。
- **基线与诊断：**单 agent 上界、无通信/固定角色、计算匹配的 prompt-only 控制、强模型/开源模型、人工或 judge 校准、消融和失败模式。

发表时真正有说服力的不是“我们的 workflow 得分更高”，而是：

1. 任务确实要求所声称的能力，单 agent 或去掉关键信息后明显变难；
2. evaluator 对等价路径、附带损害和错误判断有明确处理；
3. proposed intervention 与同信息、同预算的 controls 区分开；
4. 过程信号（角色边界、artifact 使用、返工、判断顺序）和终局成功同时报告；
5. 结果在 held-out task roots / seeds 上成立，成本、失败、judge disagreement 和不确定性完整披露。

## 公开 benchmark 与我们任务的匹配矩阵

| 工作 | 发表/来源 | 任务与验证方式 | 论文中实际使用的 baseline / 对照 | 对本项目可复用的部分 | 对核心故事的缺口 |
|---|---|---|---|---|---|
| **AgentBench** | ICLR 2024；[paper](https://arxiv.org/abs/2308.03688)；[repo](https://github.com/THUDM/AgentBench) | 8 个 code/game/web 环境，27 个模型；OS/DB 用 success rate，KG 用 F1，游戏有 win/progress；Dev 公布、Test 保留 | 27 个 API/OSS LLM；统一 user–agent 交互、Docker 隔离和加权总分 | 环境隔离、服务化 runner、公开 dev/隐藏 test 的组织方式 | 单 agent 为主；没有 producer artifact、recipient judgment、实际采用归因或跨任务角色形成 |
| **WebArena** | [paper](https://arxiv.org/abs/2307.13854)；[repo](https://github.com/web-arena-x/webarena) | 812 个长程 web 任务、4 类自托管网站；按目标状态程序化验证，多路径可行；人类 78.24% | text-bison、GPT-3.5、GPT-4，direct/CoT/UA-hint；与人类比较 | 真实工作流、目标状态而非动作序列、人工上界 | 浏览器单 agent；user 不是 peer judge；没有后续责任变化 |
| **SWE-bench** | [paper/repo](https://github.com/SWE-bench/SWE-bench) | 真实 GitHub issue→patch；隐藏测试验证；任务级 pass rate | SWE-agent、mini-swe-agent 等不同 harness/model，通常配合 pass@1/成本 | 真实软件交付、隐藏测试和 contamination 讨论；CooperBench 可借鉴其 task-root discipline | 单 agent patch resolution；不会记录接收者是否使用某个 producer patch，更没有 role update |
| **AppWorld** | ACL 2024 Best Resource；[paper](https://arxiv.org/abs/2407.18901)；[repo](https://github.com/StonyBrookNLP/appworld) | 9 个模拟日常 app、457 API、750 任务/250 scenario；最终数据库 diff + unit assertions；TGC 与跨变体 SGC | ReAct、Plan&Execute、FullCode+Reflexion、Iterative Parallel Function Calling、ToolLLaMA、CodeAct；GPT-4o/4-Turbo/Llama3/DeepSeek 等 | 最适合实现 artifact/use/repair 的 state-based evaluator；SGC 可借鉴“同一责任情境跨变体的一致性” | 默认单 agent；producer–consumer 边界和公共 role evidence 都是新增层；不能把 evaluator 通过当作 peer use |
| **τ-bench** | [paper](https://arxiv.org/abs/2406.12045)；[repo](https://github.com/sierra-research/tau-bench) | 用户模拟器 + 领域 API + 数据库；终局 DB state 对比；`pass^k` 测一致性和可靠性 | function-calling agent（GPT-3.5/GPT-4o 等）和多次 rollout；比较 pass^1 与 pass^k | 真实用户反馈、政策约束、数据库 goal-state 和多次试验协议 | user simulator 是任务对话方，不是评价 producer 的独立 peer；没有 artifact attribution / future duty |
| **ToolSandbox** | [paper](https://arxiv.org/abs/2408.04682)；[repo](https://github.com/apple-aiml-research/ToolSandbox) | 1032 场景、34 工具；stateful tool、on-policy user simulator；milestone DAG + minefield DAG，支持中间/终局动态评估 | proprietary/OSS 模型；user-simulator prompt ablations；与 BFCL/ToolEval/ToolTalk 对比 | milestone/minefield 可表达“判断前可见信息”“禁止 premature action”“终局纠正”；轨迹匹配允许多路径 | 仍是 user–agent tool use；LLM user/judge 可能有误差；无跨 episode 的公共角色证据和后续 assignment |
| **OSWorld** | NeurIPS 2024；[paper](https://arxiv.org/abs/2404.07972)；[repo](https://github.com/xlang-ai/OSWorld) | 369 个真实桌面任务，VM snapshot/reset，跨应用状态，任务特定 execution evaluator；含人类实验 | GPT-4V、Claude-3、不同 observation/action setting；human performance | 跨 app、长程、初始中间状态、程序化 evaluator 与人工校准 | 单 agent computer-use；artifact producer/recipient 和 role learning 不存在 |
| **MultiAgentBench / MARBLE** | ACL 2025；[paper](https://aclanthology.org/2025.acl-long.421/)；[repo](https://github.com/MultiagentBench/MARBLE) | research、Minecraft、DB、coding、bargaining、Werewolf；角色和 graph topology 预设；milestone KPI、communication/planning score、task score | 5 个模型；star/tree/chain/graph；vanilla/CoT/group discussion/cognitive-evolving planning；部分任务 rule-based，部分 LLM judge | 可借 agent graph、coding workflow、task config 和 topology controls；MIT 代码便于 adapter | 角色由 profiles 固定，milestones/CS 大量依赖 LLM evaluator；没有 situated recipient acceptance/use/repair 和后续责任 |
| **AgentWorld** | [paper PDF](https://ryanzhumich.github.io/files/AgentWorld.pdf)；项目当前固定 commit `df5237da96a3ef00f602950baa362d14d3a618fe`，MPL-2.0；见本项目 [source manifest](reuse_design_20260924/benchmarks/SOURCE_MANIFEST.json) | 100 human-annotated + 100 augmented tasks；3–20 agent、25–55 rounds、黑箱、非对称角色/能力；程序 verifier + Causal Collaboration Effectiveness (CCE) | random、single-agent、no-communication、shared-plan-only、oracle-communication | 资源转移、长程协作、黑箱信息限制、CCE/causal trace、现成 no-role/no-communication controls | 角色、能力、资源和 username 由任务先验指定；最终成功不能证明 recipient 使用某个 artifact；跨任务 identity/role update 需自行加 |
| **TeamBench** | 2026 preprint；[paper](https://arxiv.org/html/2605.07073)；[repo](https://github.com/ybkim95/TeamBench)，MIT，commit `d185aef1916fd86a9ba554d581fd256319a973af` | 851 templates/931 instances；Planner 读 full spec，Executor 改 workspace，Verifier 只读证据并判定；OS sandbox 强制角色边界；deterministic grader | Solo、Restricted、Full Team、Team-No-Plan、Team-No-Verify；Solo CoT/2Pass；27 种跨 provider role mixing；人类 study | 直接借用 role-violation rate、verifier false-accept/reject、compute-matched solo、按 Solo 难度分层的 team uplift；提醒 pass rate 不足 | Verifier 只对当前提交给出 verdict，未形成跨任务 public role evidence；没有 producer artifact 的 recipient adoption history |
| **AWS MAC scenario benchmark** | technical report 2024；[paper](https://arxiv.org/abs/2412.05449)；[repo](https://github.com/aws-samples/multiagent-collab-scenario-benchmark)，MIT-0，commit `cb82575c0846bb147423bebacc8597bc24196142` | 3 个企业域、90 场景；user/action simulator；assertion-based evaluation；Software 域有 Coder→Test/Review 的 payload referencing | single agent vs hierarchical multi-agent；routing；payload referencing ablation；LLM judge 与人类抽查 | 最接近“artifact handoff”工程：结构化 payload、监督者/专家/测试/审核链；可借 scenario/assertion schema | 场景和 role 预设，assertion judge 仍是外部评价；没有“接收者先判断、再采用、判断影响未来角色” |
| **Dynamic Role Assignment / Meta-Debate** | 2026 preprint；[paper](https://arxiv.org/abs/2601.17152) | 每题先生成 role-specific proposals，再用 peer review 给候选 agent 打 role-specific score；GPQA、MathVision、RealWorldQA 用 accuracy | homogeneous same-model、empirical random assignment、MAD/DMAD；报告 dynamic vs static role assignment | 是当前最接近“others’ judge → role assignment”的概念先例；应作为 B5/威胁重叠审查 | 角色在同一道题的 debate 前选择；peer review 不是接收者对真实 artifact 的 situated judgment，没用/返工/终局纠正/跨任务责任链；未找到可核验的官方代码仓库 |

## 最小可发表 baseline 套件

所有 arms 必须使用相同 task roots、初始 agent/workflow 状态、合法可见信息、模型/工具、机会流、API 与总预算。不能让 proposed arm 把自己的 realized memory 免费复制给 control。

| ID | baseline | 必须回答的问题 |
|---|---|---|
| **B0** | pooled single-agent / centralized selector | 多 agent 的提升是否只是一个拥有全部信息的 agent 就能得到的上界？ |
| **B1** | fixed/no-role self-organization | 普通协作但没有 learned role，是否已经解释结果？ |
| **B2** | raw recipient acceptance | 只累计 accept/reject 的简单比例是否足够；repair/use 机制是否真的有增益？ |
| **B3** | contextual trust / bandit | 在同样看到 producer、recipient、task context、uncertainty、outcome 的条件下，普通上下文分配器是否能达到同样效果？这是最强同信息 control。 |
| **B4** | terminal-only feedback | 只用最终测试/任务成功，不看 situated peer judgment，是否已经足够？ |
| **B5** | closest peer-feedback / Meta-Debate-style control | 防止把“有 peer review 的动态分配”包装成新颖性；只在实现忠实、信息和预算匹配时加入。 |
| **P** | proposed source-aware judgment → role evidence → later assignment | 判断、实际 use/repair/reject、合法终局校正和后续责任变化是否共同带来 team utility / cost 改善？ |

必须同时做这些 diagnostic，而不把它们算作新的主 baseline：

- **No-handoff / independent redo：**recipient 永远不使用 producer artifact，测试“只增加第二个 agent”是否足够。
- **Prompt-only role assignment：**对照 TeamBench 的结构性角色边界，记录角色越权，而不是只比较成功率。
- **Compute-matched Solo CoT/2Pass：**确保团队增益不是多了两三倍 token/calls 的简单结果。
- **Terminal/judge disagreement：**任何 LLM judge 指标都与独立 grader、unit tests 或人工抽查并列报告。
- **Task-root/identity permutation：**交换 producer/recipient identity、context 或 evidence ownership，检验模型是否学到了 source-aware evidence，而不是 identity prior。

## 对本项目 benchmark 决策的具体判断

### 为什么 CooperBench 仍应作为主 benchmark

当前项目已经审计并固定了 CooperBench commit `63b9d44d9f39a02fccf5bf0052db48a917a011fd`，它提供真实 repository roots、分离 feature、patch、merge conflict 和 native tests。它最自然地支持：

```text
producer patch + provenance
→ owner 在测试结果可见前封存 accept/reject/repair/independent-redo
→ 记录哪些行/文件真正被采用、返工和测试
→ native tests / merge status 提供终局事实
→ 新 task root 产生后续 owner 责任机会
```

现有审计也暴露了必须写进论文的风险：原生 `coop` 预先分配 feature，`test_merged` 可能使用 `solo-agent1` fallback；两个 agent 各自独立完成 feature 也可能 `both_passed=true`。因此不能把最终 tests pass 直接当成 recipient 使用了 producer 交付。主实验必须报告 `merge.status`、`merge.strategy`、artifact contribution、实际 use/rework、独立重做成本和 scorer provenance。

### 为什么不直接把 MARBLE 当主 benchmark

MARBLE 有 role/graph/milestone 词汇和多场景代码，但它是预先配置的角色 workflow；communication/planning score 主要由 LLM evaluator 给出，不能区分“角色真的由历史证据形成”与“prompt 里已经指定了角色”。它适合作为 fixed-workflow comparator 或工程 adapter，不能独立支撑主创新。

### 为什么 AgentWorld 应放到第二阶段

AgentWorld 是最有真实多 agent 味道的外部验证环境，但 task YAML 中的 username、skill、spawn、resource 和成功条件会先验定义职责；`no_roles` 只去掉提示，不会消除能力/资源不对称。完整 server/scorer 也更难先做小批量的可控因果实验。只有 CooperBench vertical slice 先证明 judgment 改变了后续责任，AgentWorld 才有价值作为 external validity。

## 我们应从这些工作中明确放弃的伪命题

- “communication score 高，所以角色学习有效”：MARBLE 已说明 CS 与 task score 可能脱钩，TeamBench 还显示 pass rate 相同的系统可能有完全不同的越权行为。
- “最终通过测试，所以 recipient 使用了 producer”：CooperBench/软件协作中存在独立重做、merge fallback 和多条合法路径，必须记录 adoption/use。
- “LLM judge 说 accept，所以 artifact 可靠”：TeamBench 发现 Verifier 会接受大量 deterministic-grader 失败的提交；必须报告 judge–grader disagreement。
- “角色 prompt 写成 expert/tester 就是角色形成”：固定 profile 或 role assignment 是 workflow 配置，不是 evidence-conditioned learning。
- “更多 agent 或更多 token 就是协作收益”：必须加入 pooled single-agent、compute-matched Solo、no-handoff 和成本/延迟。
- “同一个 task family 的很多变体就是很多独立组织”：AppWorld 的 scenario-level SGC、AgentWorld 的 task structure 和当前 AAMAS requirements 都要求按 task root / organization stream 处理独立性。

## 可执行的下一步

1. 在 CooperBench 上完成一个 held-out 两 agent vertical slice：receipt、judgment seal、use/rework/reject attribution、native scorer、future assignment 全链路可 replay。
2. 先实现 B0–B4；只有 B3 与 P 的信息/预算完全对齐后，再决定是否加入 Meta-Debate-style B5。
3. 把 ToolSandbox 的 milestone/minefield 与 AppWorld 的 expected/allowed state-diff 转化为本项目 F5–F7 的 evaluator contract，避免使用 reference trajectory。
4. 用 TeamBench 的 role-violation、judge–grader disagreement、Solo-stratified uplift 和 human-audit 作为实验表格的固定列。
5. 只有当 P 相对 B3 在后续责任、team utility 或全成本上有稳定差异，且 effect 在 held-out roots/identity permutations 上保留，才把“peer-judged role formation”作为主结论；否则应降级为 artifact-aware allocation/control 结果。

## 复用清单（来源、提交、许可证）

| 来源 | 固定提交 | 许可证/使用说明 |
|---|---|---|
| [MARBLE](https://github.com/MultiagentBench/MARBLE) | `8892e9cfb69282db568e6b018f2b1cd8eec31ba6` | MIT |
| [τ-bench](https://github.com/sierra-research/tau-bench) | `59a200c6d575d595120f1cb70fea53cef0632f6b` | MIT |
| [τ²-bench](https://github.com/sierra-research/tau2-bench) | `b7ea9074c1cba482b30687fecdb5c8425fd6f619` | MIT |
| [AppWorld](https://github.com/StonyBrookNLP/appworld) | `42b5bcf3cd334fee33f0c37c02070a9f5807add5` | Apache-2.0 |
| [ToolSandbox](https://github.com/apple-aiml-research/ToolSandbox) | `c8571d7854316d2e1c5f288e59fe1e34e53f6dd1` | GitHub API reports `NOASSERTION`; do not copy code until license is clarified |
| [AgentBench](https://github.com/THUDM/AgentBench) | `d1e4a10db08c87075c78972e48ecc182be03e2d5` | Apache-2.0 |
| [WebArena](https://github.com/web-arena-x/webarena) | `dce04686a56253aefba7b18a4fa0937cf1dc987b` | Apache-2.0 |
| [OSWorld](https://github.com/xlang-ai/OSWorld) | `b138d348256078fa634fc3b73567a7337c793e6b` | Apache-2.0 |
| [SWE-bench](https://github.com/SWE-bench/SWE-bench) | `02e7a74ffd0b707aab73d203fe87bdc7c76afc8e` | MIT |
| [TeamBench](https://github.com/ybkim95/TeamBench) | `d185aef1916fd86a9ba554d581fd256319a973af` | MIT |
| [AWS MAC scenario benchmark](https://github.com/aws-samples/multiagent-collab-scenario-benchmark) | `cb82575c0846bb147423bebacc8597bc24196142` | MIT-0 |
| AgentWorld | `df5237da96a3ef00f602950baa362d14d3a618fe` | MPL-2.0; local source manifest: `references/aamas/reuse_design_20260924/benchmarks/SOURCE_MANIFEST.json` |

## 证据边界

本报告是文献/代码审计和 benchmark 设计建议，不是新的 agent/API 实验结果。当前项目的 scientific readiness 仍由 `REQUIREMENTS.md` 和 `AAMAS_TASKS.md` 控制；在 F5–F9 vertical slice 和同信息 baseline 通过前，不应写“方法已验证”。
