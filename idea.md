# Idea 04: 局部交互驱动的涌现组织

> HISTORICAL METHOD DESIGN as of the AAMAS redirection on 2026-09-16. The active scientific contract is [REQUIREMENTS.md](docs/paper/aamas2027/REQUIREMENTS.md); gaps, B/M locks and execution are in [AAMAS_TASKS.md](docs/coordination/AAMAS_TASKS.md). Prior role-emergence, scalar-reduction and convergence claims below must not override the new evidence audit. Preserved for provenance, not as an additional active method plan.

## 0. 文档定位

这不是摘要，也不是短提案，而是本项目的主方法设计说明书。

它现在必须同时服务 5 个目标：

1. 让研究者一句话讲清这篇 long paper 真正研究的是什么。
2. 让工程实现者能够按文档直接拆出运行时、状态、日志和实验。
3. 让论文作者能够从这里直接抽取 introduction、method、experiment、limitation。
4. 让当前仓库中的可执行系统找到自己在整条研究线里的准确位置。
5. 让后续工程师知道下一阶段到底该重构什么，而不是继续在旧框架上小修小补。

因此，本文档必须同时回答 6 件事：

- 我们真正研究的问题是什么。
- 新方法的对象到底是什么，不是什么。
- 为什么旧的固定角色硬路由只能算受限原型，而不是最终 idea。
- 完整 long-paper 方法如何定义成可执行、可量化、可复盘的系统。
- 当前仓库怎样映射到这个更大的理论框架里。
- 下一阶段代码、实验、日志到底该怎么升级。

---

## 1. 题目草案

中文备选：

- 局部交互驱动的涌现组织：面向多智能体递归委派与验收的协作框架
- 从同质智能体到涌现分工：基于局部委派与递归验收的多智能体组织方法
- 社会化任务委派：稀疏图上多智能体的涌现人格、递归拆分与价值校准

英文备选：

- `Emergent Organization from Local Delegation and Audit in Multi-Agent Systems`
- `From Homogeneous Agents to Division of Labor via Recursive Delegation and Audit`
- `Emergent Delegation Organization for Sparse-Graph Multi-Agent Collaboration`

本文建议把完整 long-paper 方法总名统一为：

## `Emergent Delegation Organization` (EDO)

其中，当前仓库里的可执行前身保留其旧名字：

## `Terminal-Consensus Peer Backpropagation` (TCPB)

但要明确：

- `EDO` 是完整 long-paper 方法。
- `TCPB` 是当前仓库里已经跑起来的受限原型机制。
- 论文主方法必须是 `EDO`，不是 `TCPB`。

---

## 2. 一句话核心命题

这篇工作的核心不再是：

**在固定角色和固定路由规则下，节点如何更稳地做 accept-or-forward。**

而是：

**在没有中央调度器、没有预设专家身份的前提下，一群初始近似同质的 agent 能否仅凭局部交互、递归委派、递归验收和价值反馈，在稀疏连通图上自发形成稳定且有用的分工组织。**

更白一点地说，我们要研究的是：

- 专长能不能不是先写死，而是后长出来；
- 角色能不能不是先指定，而是后被社会互动塑形；
- 拆分任务本身能不能也被当成任务来继续路由；
- 一个 agent 的“人格”和“社会能力”，能不能定义为它持续为别人创造可验收价值的能力；
- 任务能不能只靠局部邻居信息，一步步流向更适合的位置。

---

## 3. 为什么必须从旧 framing 升级

### 3.1 旧框架的优点必须承认

当前仓库中的 `fixed_peer_calibrated` / `fixed_self_calibrated` / `fixed_static_roles` 路线并不是无效的。

它至少做对了 4 件事：

1. 把“委派失准”从泛泛的多 agent 协作问题里单独拎出来了。
2. 把结构化中间状态、日志、可复盘路径这些研究资产建立起来了。
3. 证明了结果导向的校准信号确实比自我反思更可靠。
4. 给后续 long-paper 留下了一个可以直接对比、直接复现实验的强基线。

### 3.2 但旧框架不能再充当最终 idea

你指出的问题是对的：当前路由机制虽然有效，但它作为最终论文主方法仍然太简单，原因在于：

- 角色名是预先写死的；
- 初始 agent 不是同质的；
- 路由核心仍然带有明显的硬匹配味道；
- 动作空间太小，只有 `accept / forward`，没有真正的递归拆分；
- “下游做完后上游验收”的社会化递归链条尚未成为方法主对象；
- 当前 competence 更像受限路由分数，而不是由互动历史塑造出来的人格结构。

换句话说，旧方案更像：

**一个经过校准的固定流程网络**

而你真正想做的是：

**一个会在社会化协作中长出人格和分工的组织系统**

### 3.3 EMNLP long paper 更需要后者

如果论文仍然把固定角色和硬路由当作主创新，reviewer 很容易给出以下质疑：

- 这是不是只是 hand-crafted routing policy？
- 这是不是 prompt engineering + 一些阈值？
- 这是不是静态角色扮演，而不是 emergent organization？
- 这和已有 orchestrator / role-play MAS 的差异到底够不够大？

而新 framing 的优势在于，它把问题提升到更基础的一层：

## `organization formation under local interaction`

即：

- 在局部可见、全局不可见时，组织如何形成；
- 在没有先验专家目录时，分工如何形成；
- 在拆分、外包、验收递归出现时，信任和人格如何形成；
- 在多步协作里，谁真正为别人创造了价值，如何被系统记住。

这比“再调一个更好的 local router”更像 long paper。

---

## 4. 新的研究对象到底是什么

### 4.1 不是“多 agent 多聊几轮”

本工作不是研究 agent 之间聊得更久会不会更强。

我们不把“多轮自然语言对话堆叠”当成主角。

### 4.2 不是“找一个更聪明的中央调度器”

我们也不想退回到：

- 一个超级 orchestrator 看全局；
- 一个 meta-reviewer 统一打分；
- 一个中心节点帮所有 agent 做拆分、路由和验收。

因为那样会把问题重新退化成：

**一个强 agent 如何管理许多弱 agent**

而不是：

**组织如何在局部互动中自己形成**

### 4.3 不是“预设专家并让他们各司其职”

静态角色系统可以是 baseline，但不能是主方法。

原因很简单：

- 如果专家身份一开始就给定，那么分工不是形成出来的，而是声明出来的；
- 如果 task-to-role 映射一开始就给定，那么路由不是社会化发现，而是规则查表；
- 如果节点只能做固定角色擅长的那一类事，那么“人格”只是 prompt 模板的别名。

### 4.4 我们真正研究的是组织形成

完整 long-paper 方法的研究对象是：

1. **同质起点**：每个 agent 使用同一套基础认知机制与动作语法。
2. **局部信息**：agent 只知道自己的邻居和与邻居相关的局部历史。
3. **稀疏图**：网络不是全连接，而是连通但稀疏。
4. **递归任务**：任务既可以被自己做，也可以被外包，也可以被拆成子任务。
5. **递归验收**：谁把任务外包出去，谁就有责任验收下游结果。
6. **价值标签**：一个 agent 的人格来自它反复被别人验收通过、为别人节省工作、提升最终结果的历史。
7. **涌现分工**：长期下来，不同 agent 会形成不同的优势项、劣势项和组织位置。

---

## 5. 核心洞察

### 5.1 专长不该先验写死，而应在互动中被识别

现实世界里的组织很少从一开始就拥有完美的专家目录。

更常见的过程是：

- 先有一群能力相近但并不完全相同的人；
- 在不断合作和验收中，某些人逐渐被发现更擅长某类事；
- 别人据此更愿意把类似任务给他；
- 于是分工被强化，最后看起来像“天然角色”。

这就是我们要让 agent 系统模拟的机制。

### 5.2 社会能力的本质不是自我评价，而是持续为别人创造价值

这是全文最重要的认知立场之一。

我们不把 agent 的社会能力定义为：

- 它说自己擅长什么；
- 它觉得自己做得怎样；
- 它在 prompt 里扮演了什么角色。

我们把它定义为：

**它交付给别人、并被别人验收通过的价值能力。**

也就是说，一个 agent 的人格标签不是内心独白，而是社会化历史的压缩表示。

### 5.3 递归拆分不是附属动作，而是主动作之一

当前很多 MAS 把 decomposition 当作“上游专属角色”的任务。

这不够自然。

在完整方法里：

- `拆分任务` 本身也是一个任务；
- 它不属于某个预设角色；
- 任意 agent 在局部判断后都可以选择 split；
- split 后的每个子任务再次进入同一套 `do / outsource / split` 决策。

所以整个系统不是线性链条，而是：

## `task tree over a sparse society graph`

### 5.4 稀疏图不是限制，而是社会结构的必要条件

如果图是全连接的，系统几乎退化成：

- 所有人都看得到所有人；
- 每一步都可以直接选全局最优；
- 组织结构和局部信任就不再重要。

而在稀疏连通图里：

- 每个节点只看得到邻居；
- 局部视野会形成真实的中介、桥接、局部簇；
- 某些节点会变成连接不同能力区域的桥；
- 任务会沿着局部更优路径逐步迁移，而不是一次性全局跳转。

这比“全局路由器选全局最优节点”更像真正的组织过程。

### 5.5 终局结果很重要，但不能再是唯一反馈

旧方法的 `TCPB` 做对了一件关键的事：

- 用终局结果而不是自我反思来校准。

但对完整 `EDO` 来说，这仍不够。

因为在递归外包链里：

- `a -> b -> c` 时，`b` 应该评价 `c`；
- `a` 应该评价 `b`；
- 根节点的终局结果还应对整棵任务树产生更慢、更全局的回看。

因此，完整方法的反馈必须分两层：

1. **局部验收反馈**：上游对下游子任务结果的验收。
2. **终局任务反馈**：整题最后是否被正确完成。

`TCPB` 只保留了第 2 层，是一个保守但有价值的前身。

---

## 6. 方法总名与两层结构

### 6.1 完整 long-paper 方法

完整方法统一称为：

## `Emergent Delegation Organization` (EDO)

它由 7 个不可缺少的组成部分构成：

1. `Near-Homogeneous Agents`
2. `Sparse Connected Interaction Graph`
3. `Recursive Task Tree`
4. `Three Primitive Actions: do / outsource / split`
5. `Recursive Upstream Acceptance Audit`
6. `Value-Induced Personality Tags`
7. `Local Utility-Based Delegation`

### 6.2 当前仓库中的受限原型

当前仓库保留为：

## `TCPB Prototype`

它在整个研究线里的角色是：

- `EDO` 的 Stage-1 受限实例；
- 一个已经能稳定产生日志、指标和基线比较的可执行原型；
- 一个证明“结果导向校准确实有价值”的经验起点；
- 后续所有大改版必须超越或至少解释清楚的 baseline。

### 6.3 两层结构为什么必须明确写开

如果不把这两层分开写，论文会陷入两种坏状态之一：

1. **写得太保守**
   - 最终还是像一篇 fixed-role router 论文。

2. **写得太激进**
   - reviewer 一看代码和实验，就会说你并没有真正实现文中声称的完整社会化组织系统。

正确做法是：

- 用 `EDO` 作为理论主方法；
- 用 `TCPB Prototype` 作为当前受限 instantiation；
- 清楚说明“现在已经验证了什么、还没有验证什么”。

---

## 7. 正式问题定义

为了让方法可执行，先把对象定义清楚。

### 7.1 图结构

设多智能体系统为有向图：

`G = (V, E)`

其中：

- `V = {a1, a2, ..., aN}` 为 agent 集合；
- `E` 为允许通信的边；
- `N(i)` 表示 agent `ai` 的可见邻居；
- `G` 必须连通，但应保持稀疏。

完整方法的默认图要求：

- 非全连接；
- 局部度数有限；
- 任意任务从任意起点出发，都有机会通过多跳达到更适合的区域；
- 允许比较不同图族，例如 chain、star、random sparse、small-world、community bridge。

### 7.2 允许的不对称性

你已经明确选择了：

## `轻结构偏置`

即：

- agent 本体相同；
- 初始 prompt 族相同；
- 初始动作语法相同；
- 初始标签分布相同或近似中性；
- 但允许由于图位置不同、接触任务历史不同、局部邻居不同而形成分化。

这一定义非常重要，因为它决定了论文可以主张的是：

**由结构暴露差异和互动历史诱发的涌现分工**

而不是：

**完全无偏、无结构、纯随机起点的绝对对称自组织**

### 7.3 原始任务与任务树

每个原始任务记作：

`x = (q, y, C)`

其中：

- `q` 为输入问题；
- `y` 为 gold answer；
- `C` 为可选上下文集合。

完整方法中，任务不是单一线性对象，而是一棵任务树：

`T_x = (Z, root, parent, children)`

其中每个任务节点 `z in Z` 至少包含：

- `task_id`
- `parent_task_id`
- `root_task_id`
- `task_text`
- `task_type_guess`
- `required_output`
- `input_evidence`
- `current_uncertainty`
- `depth`
- `budget_remaining`
- `status`
- `owner_agent`
- `executor_agent`
- `child_task_ids`
- `candidate_result`
- `audit_status`

### 7.4 为什么必须从 packet 升级到 task tree

旧方法里的 `handoff packet` 对线性 accept-or-forward 足够了。

但对完整 `EDO` 来说不够，因为：

- 一个父任务可能对应多个子任务；
- 子任务完成后需要再被整合；
- 整合结果还要被上游再次验收；
- 同一个 agent 可能同时拥有多个未结子任务；
- 失败后可能需要局部返工，而不是整条链重跑。

所以 long-paper 方法的真实状态对象必须是：

**树状任务状态 + 局部互动日志**

而不是单个线性 packet。

---

## 8. Agent 状态与“人格”定义

### 8.1 每个 agent 的状态

agent `ai` 在时刻 `t` 的状态记为：

`S_i^t = {P_i^t, B_i^t, M_i^t, H_i^t, N(i)}`

其中：

- `P_i^t`：agent `ai` 的公共人格标签向量；
- `B_i^t`：agent `ai` 对邻居的局部信念；
- `M_i^t`：局部记忆；
- `H_i^t`：与历史委派、验收、返工相关的交互摘要；
- `N(i)`：当前可见邻居。

### 8.2 人格不是风格，而是标签向量

为了避免 reviewer 把“人格”理解成写作语气、语调、角色扮演，我们必须给出严格操作化定义。

本文中的人格指的是：

## `value-induced operational persona`

即：

- 由互动历史压缩得到；
- 能影响未来局部任务分配；
- 可以被日志追踪；
- 可以被量化比较；
- 与任务结果和他人验收直接相关。

### 8.3 推荐的人格标签向量

完整方法中，每个 agent 维护一个人格标签向量：

`P_i = [solve, decompose, audit, integrate, explore, efficiency, reliability]`

含义如下：

- `solve`：直接完成当前任务的能力；
- `decompose`：把复杂任务拆成高质量子任务的能力；
- `audit`：验收下游结果、识别错误和不完整性的能力；
- `integrate`：将多个子结果合并成父结果的能力；
- `explore`：在外部证据、线索、候选路径中找出有效信息的能力；
- `efficiency`：以较低 token / hops /返工代价完成工作的能力；
- `reliability`：被上游验收通过、被终局结果支持的稳定性。

### 8.4 为什么这组标签比“固定角色”更好

固定角色的问题在于：

- 它把复杂社会能力压成了单个名字；
- 它默认不同能力之间强绑定；
- 它无法表达“某 agent 擅长拆分但不擅长整合”这类真实差异。

而人格标签向量允许：

- 同一个 agent 同时擅长多类能力；
- 不同标签以不同速度演化；
- 后续路由根据任务结构调用不同维度，而不是按角色名查表。

### 8.5 邻居可见的不是全局真值，而是局部可见信念

完整方法下，节点 `ai` 不应访问任何全局专家目录。

它只维护对邻居 `aj` 的局部可见信念：

`B_i(j) = local belief of ai about aj`

该信念来源于：

1. 自己与 `aj` 的历史交互；
2. `aj` 最近公开发布的人格摘要；
3. `aj` 在局部网络中的可观察信誉；
4. 与 `aj` 相关的最近验收记录。

这一定义保证方法仍然是去中心化的。

---

## 9. 任务签名与局部匹配

### 9.1 不再使用硬角色匹配

新方法里，路由不应再写成：

- 先猜 `preferred_role`
- 再把任务塞给对应角色名

这会让系统重新退化为硬编码角色路由。

### 9.2 改为任务签名

对每个任务节点 `z`，构造一个任务签名：

`phi(z) = [need_decompose, need_verification, need_integration, need_exploration, evidence_breadth, uncertainty, cost_sensitivity]`

其来源可以是：

- 规则特征；
- 轻量 LLM 判断；
- 或未来低维学习模块；

**当前原型的确定性提取规则（无需 LLM 调用）：**

| 维度 | 提取规则 | 数据来源 |
|---|---|---|
| `need_decompose` | `hop_count == 0` 且问题含多跳特征 → 1，否则 → 0 | `HandoffPacket.hop_count` |
| `need_verification` | `hop_count >= 2` → 1 | `HandoffPacket.hop_count` |
| `need_integration` | `len(evidence_so_far) >= 8` → 1 | `HandoffPacket.evidence_so_far` |
| `need_exploration` | `1 - min(1, len(evidence_so_far) / 10)` | `HandoffPacket.evidence_so_far` |
| `evidence_breadth` | `min(1, len(evidence_so_far) / 12)` | `HandoffPacket.evidence_so_far` |
| `uncertainty` | 直接读 `packet.uncertainty` | `HandoffPacket.uncertainty` |
| `cost_sensitivity` | `min(1, hop_count / max_handoff)` | `HandoffPacket.hop_count` |

多跳启发：若问题满足 `_is_multihop_question()` 判定（≥2 大写实体或含 "both"/"and"），则在 `hop_count=0` 时将 `need_decompose=1, need_exploration=0.7` 作为先验。完整定义见 `artifacts/edo_lite_executable_spec.md §1.2`。

但方法论上必须强调：

**核心不是 embedding 最近邻检索，而是任务需求与人格标签之间的局部适配。**

### 9.3 任务签名的研究作用

这一步很重要，因为它让方法同时避免两种误解：

1. 不是固定角色硬匹配；
2. 也不是必须依赖大规模 embedding router。

我们真正要做的是：

**把任务看成一组需求，把 agent 看成一组由社会互动塑造出来的能力标签，然后在局部邻域内比较谁更值得接、外包或继续拆分。**

---

## 10. 三类原始动作

完整方法中，每个 agent 在收到任务节点 `z` 时，必须只在三类主动作中做选择：

1. `do_self`
2. `outsource(neighbor)`
3. `split(subtasks)`

### 10.1 `do_self`

表示当前 agent 认为：

- 自己现在做这件事的收益最高；
- 返工风险在可接受范围；
- 没必要继续把它往外包或者继续拆。

### 10.2 `outsource(neighbor)`

表示当前 agent 认为：

- 在自己的局部邻域里，有人更适合做这件事；
- 外包成本和验收成本值得支付；
- 当前任务还不需要拆成多个子任务。

### 10.3 `split(subtasks)`

表示当前 agent 认为：

- 任务内部存在多个相对独立或弱耦合的子问题；
- 继续整体处理不如拆开；
- 拆开后每个子任务都能重新进入同一套三动作决策；
- 自己可以承担后续整合与验收义务。

### 10.4 这三类动作为什么足够

因为它们已经覆盖了组织里的三种基本分工逻辑：

- 自己做；
- 找别人做；
- 把事拆开再组织别人做。

其它行为，如返工、重审、重路由、超时终止，都属于这三类主动作之上的安全控制，而不应成为主方法定义的中心。

---

## 11. 局部效用估计器

### 11.1 为什么必须有 utility，而不能只比“谁更像专家”

如果系统只根据“谁更擅长”来选动作，会忽略：

- 外包本身有通信和验收成本；
- 拆分本身有整合和协调成本；
- 自己做可能不是最好，但可能最快；
- 某邻居虽然能力强，但返工风险很大；
- 某任务虽然可以拆，但拆分收益并不覆盖协调开销。

因此，完整方法必须显式引入：

## `global value, local utility`

即：

- 全局目标是提升任务完成质量并降低总成本；
- 但每个节点只做局部效用估计，并在局部视野内选动作。

### 11.2 推荐的局部效用形式

对 agent `ai` 和任务节点 `z`，定义：

`U_self_i(z) = Fit(P_i, phi(z)) - lambda_c * Cost_self(z) - lambda_r * Risk_self(z)`

`U_out_i(z, j) = Fit(B_i(j), phi(z)) - lambda_s * SendCost(i, j) - lambda_a * AuditCost(z) - lambda_r * RejectRisk(j, z)`

`U_split_i(z) = SplitGain(z) - lambda_m * MergeCost(z) - lambda_d * DepthPenalty(z) - lambda_a * AuditLoad(z)`

其中：

- `Fit` 表示人格标签与任务签名的适配度；
- `Cost_self` 表示自己直接完成的 token /时间/注意力开销；
- `SendCost` 表示外包的通信和同步成本；
- `AuditCost` 表示后续验收的额外工作；
- `RejectRisk` 表示该外包结果被退回、返工或终局失败的风险；
- `SplitGain` 表示拆分后可能获得的并行收益和结构清晰度；
- `MergeCost` 表示整合多个子任务结果的成本；
- `DepthPenalty` 表示过深递归带来的复杂度惩罚；
- `AuditLoad` 表示拆分后新增的验收负担。

**当前原型实例化（见 `artifacts/edo_lite_executable_spec.md §2.2`）：**

`Fit(P_i, phi(z))` → `competence_i[agent_name]`（标量自我能力）；`Cost_self=0`（均匀假设）；`Risk_self=packet.uncertainty`；`U_split` 未实现（Stage-2）。  
当前原型的具体加权公式（`_score_accept` / `_score_neighbors`）：

```
U_self = 0.55 * self_competence + 0.20 * evidence_sufficiency + 0.10 * (1 - uncertainty) - 0.10 * loop_risk - 0.05 * revisit_risk
U_out_j = 0.60 * neighbor_belief_j + 0.25 * role_match_j + 0.05 * structural_prior - revisit_penalty_j
```

敏感性分析（Session 3）已确认：在 ±2× 范围内调整权重，F1 变化 < 0.003pp。这些权重是定性先验，不是经过调优的超参数。

### 11.3 最终动作选择

定义：

`a_i(z) = argmax{U_self_i(z), max_j U_out_i(z, j), U_split_i(z)}`

若预算、深度或稳定性约束被触发，则走安全规则：

- 限制继续 split；
- 限制重复外包；
- 必要时回退到自己做或终止保底输出。

**当前原型的确定性终止规则（硬规则，无随机性）：**

| 规则 | 触发条件 | 执行动作 |
|---|---|---|
| 最大跳数 | `hop_count >= max_handoff`（默认=4） | 当前节点强制接受 |
| 终点节点 | `neighbor_list == []`（chain 末端 synthesizer） | 接受并输出 |
| 死端 | 目标节点不在 `adjacency[current]` 中 | 当前节点兜底接受 |
| 循环保护 | `next_node in seen_nodes AND next_node != synthesizer` | 跳过，改为转向 synthesizer |

Stage-2 新增的 split 终止规则：`max_subtasks_per_split=3`，`max_tree_depth=3`，`max_total_nodes=12`。完整定义见 `artifacts/edo_lite_executable_spec.md §4`。

### 11.4 为什么这比旧 accept-or-forward 更像组织

旧方法本质上是在回答：

- 我接还是转？

而新方法回答的是：

- 我自己做值不值？
- 在我认识的人里谁更值得接？
- 这件事有没有必要拆成多个子任务再组织起来？

这就是从“局部路由器”升级到“局部组织者”的关键变化。

---

## 12. 递归委派与递归验收

### 12.1 基本流程

对任意任务节点 `z`，其处理过程如下：

1. 当前 agent 读取任务签名 `phi(z)`。
2. 计算 `U_self`、`U_out`、`U_split`。
3. 选出动作。
4. 若 `do_self`，则生成候选结果并提交给父节点验收。
5. 若 `outsource(j)`，则将 `z` 或其重写版本委派给邻居 `j`。
6. 若 `split`，则产生子任务 `{z1, z2, ..., zk}`，对子任务分别重复相同过程。
7. 子结果返回后，当前节点进行整合与验收。
8. 整合后的父结果继续提交给更上游验收。

### 12.2 验收是递归的，不是一次性的

若出现：

- `a -> b -> c`

则：

- `c` 做完自己的任务后，不是直接结束；
- `b` 必须先验收 `c`；
- `b` 把自己的整合结果或修改结果交给 `a`；
- `a` 再验收 `b`；
- 根节点在整题结束后，再看最终正确性和全局代价。

所以完整方法的真正信息流不是简单路由链，而是：

## `delegation tree + recursive acceptance ladder`

### 12.3 验收动作本身也应结构化

上游验收下游时，至少应该能做出以下判断之一：

- `accept`
- `accept_with_minor_fix`
- `reject_and_redo_self`
- `reject_and_reroute`
- `reject_and_resplit`

每次验收都会产生一条社会化标签事件。

### 12.4 为什么验收是方法核心

因为组织中的信誉不是靠自我报告产生的，而是靠别人是否愿意接收你的工作成果产生的。

也就是说：

- 你有没有“完成任务”，不是你说了算；
- 你有没有给组织创造价值，也不是你说了算；
- 只有当上游愿意接纳并继续基于你的结果工作时，这个价值才真正被社会化确认。

这就是人格标签更新的根基。

---

## 13. 人格标签如何由社会互动长出来

### 13.1 局部标签事件

每次上游 `u` 对下游 `v` 的任务结果做出验收后，都生成一个局部标签事件：

`l_(u->v, z) = [accepted, rework_cost, value_gain, timeliness, decomposition_help, integration_help]`

这些分量可以理解为：

- `accepted`：是否被上游直接接纳；
- `rework_cost`：上游为修补该结果额外花了多少工作；
- `value_gain`：该结果是否明显推进了父任务完成；
- `timeliness`：是否在预算与深度要求内返回；
- `decomposition_help`：若该结果是拆分方案，是否让任务结构更清晰；
- `integration_help`：若该结果是子结果，是否便于后续整合。

### 13.2 终局结果事件

局部验收还不够。

因为某次上游“误验收”也可能把坏结果继续传上去。

因此，在根任务完成后，还需产生终局结果事件：

`r_terminal(x) = [quality, total_cost, total_depth, final_accept]`

这个事件用于：

- 矫正局部验收可能带来的短视偏差；
- 给整条任务树上的关键节点更慢、更全局的反馈。

### 13.3 标签更新规则

推荐的人格更新形式为：

`P_i^(t+1) = clip((1 - mu) * P_i^t + mu * (eta_local * LocalValue_i^t + eta_terminal * TerminalValue_i^t - eta_rework * ReworkPenalty_i^t))`

其中：

- `LocalValue_i^t` 来自最近一段时间里别人对它工作的局部验收；
- `TerminalValue_i^t` 来自终局任务质量；
- `ReworkPenalty_i^t` 来自返工、误拆分、低质量外包等负面后果；
- `mu` 为更新速率；
- `clip` 用于抑制暴涨暴跌。

**当前原型的标量实例化（对应 `apply_peer_post_sample_competence()`）：**

原型将 `P_i` 简化为标量自我能力 `competence[i][i] ∈ [0.05, 0.95]`。实际更新步骤：

```
raw_delta = +0.06 if answer_f1 >= 0.5 else -0.10   # 终局信号
raw_delta = clip(raw_delta, -0.06, +0.06)            # 增量上限
target    = clip(prev_self + raw_delta, 0.05, 0.95)
new_self  = 0.5 * prev_self + 0.5 * target           # momentum=0.5，等价于 mu=0.5
```

参数映射：`eta_local=0`（无逐跳验收），`eta_terminal=1`，`eta_rework=1`，`mu=0.5`。Stage-2 完整向量更新见 `artifacts/edo_lite_executable_spec.md §3.3`。

### 13.4 公开人格与私有记忆

完整方法最好区分：

- `public persona`
- `private episodic memory`

前者用于局部委派时的可见信号，后者用于 agent 内部总结。

其中公开人格只能包含：

- 对局部路由确有帮助；
- 可被日志复盘；
- 不依赖全局真值；
- 不把整个系统重新变回全局共享黑板。

### 13.5 为什么这才是“人格”

这里的人格不是文风，而是组织语境中的稳定社会特征：

- 你常不常被别人验收通过；
- 你是不是擅长拆事；
- 你给别人带来的是便利还是返工；
- 你是在降低组织成本还是增加组织摩擦。

从这个定义出发，agent 的人格就和社会学里的“被他人反复识别的稳定行动倾向”更接近。

---

## 14. 什么才算真正的“涌现”

为了防止论文过度主张，必须先把 emergence 的边界写死。

### 14.1 可以主张为涌现的内容

以下现象可以被视为涌现：

- 初始近似同质的 agent 在运行后形成人格标签分化；
- 不同节点的 `do / outsource / split` 选择分布逐渐不同；
- 相同任务家族更频繁流向某些局部区域；
- 某些节点逐渐成为桥接者、审计者、拆分者或整合者；
- 这些分化不是直接由固定角色名强制指定，而是由互动历史和验收结果逐步塑造。

### 14.2 不应主张为涌现的内容

以下内容不能被包装成涌现：

- 预先写死的角色 prompt；
- 预先写死的 task-to-role 查表；
- 预先写死的“某节点只能做某类事”；
- 全局真值支持下的邻居能力读取；
- 中央节点统一审批所有下游结果。

### 14.3 本文允许的固定偏置

我们允许存在以下固定偏置：

- 稀疏图结构本身；
- 安全预算、最大深度、最大子任务数；
- 标签更新的平滑和剪裁；
- 轻量级的 task signature 提取规则；
- 保底终止机制。

这些偏置的地位是：

**组织环境和制度约束**

而不是：

**预先写死的最终分工**

### 14.4 可以提前写进论文的可证伪预测

如果 `EDO` 成立，至少应观察到以下现象：

1. 人格标签从中性初值显著分化。
2. `do / outsource / split` 行为在节点间形成非均匀稳定分布。
3. 局部验收能降低低质量子任务结果向上游继续污染的概率。
4. 在连通稀疏图中，任务会向高适配区域迁移，而不是随机漫游。
5. 去掉验收或去掉人格标签后，组织质量和委派安全会下降。

---

## 15. 当前仓库如何映射到新方法

这一节是整份文档最关键的诚实声明。

### 15.1 当前仓库不是 `EDO` 全量实现

当前代码库中的主运行时只实现了一个受限原型：

- 不是通用稀疏图，而是 `chain / star`
- 不是同质 agent，而是 4 个 role-prior 节点
- 不是任务树，而是线性 `handoff packet`
- 不是 `do / outsource / split` 三动作，而是 `accept / forward`
- 不是递归上游验收，而是终局 `TCPB`
- 不是人格标签向量，而是 role-indexed competence map

### 15.2 但它仍然是有价值的 Stage-1

原因是它已经证明了：

1. 结果导向校准比自我反思可靠。
2. 去中心化局部路由可以被日志化、审计化和定量化。
3. 结构化中间状态是必要研究对象。
4. “任务被留在错误位置”这一 failure mode 可以被真实 benchmark 暴露。

### 15.3 一一映射关系

| 完整 `EDO` 对象 | 当前仓库中的受限对应物 | 代码锚点 |
|---|---|---|
| 稀疏连通图 | `chain / star` | `workspace/idea04_core/runner.py` |
| 同质 agent | 4 个 role-prior 节点 | `workspace/idea04_core/methods.py` |
| 任务树 | 线性 `HandoffPacket` | `workspace/idea04_core/contracts.py` |
| `do / outsource / split` | `accept / forward` | `workspace/idea04_core/methods.py` |
| 递归验收 | 终局后接受节点更新 | `workspace/idea04_core/methods.py` + `runner.py` |
| 人格标签向量 | self-competence 为主的 competence map | `workspace/idea04_core/methods.py` |
| 局部人格信念 | `published_competence` | `workspace/idea04_core/contracts.py` |
| `phi(z)` 提取 | `_build_routing_features()` 的确定性规则 | `workspace/idea04_core/methods.py` |
| 效用函数实例 | `_score_accept()` / `_score_neighbors()` | `workspace/idea04_core/methods.py` |
| 人格更新规则 | `apply_peer_post_sample_competence()`（终局标量更新） | `workspace/idea04_core/methods.py` |

各组件的完整当前实现状态与 Stage-2 扩展需求，见 `artifacts/edo_lite_executable_spec.md §5`。

### 15.4 当前实验到底支持什么，不支持什么

当前实验可以支持：

- outcome-based calibration 有效；
- delegation safety 可以被显著改善；
- route preferences 可以在固定拓扑中稳定下来；
- 当前残余错误很多来自生成瓶颈，而非纯路由瓶颈。

当前实验不能直接支持：

- 真正的同质冷启动人格涌现；
- 递归拆分是否带来收益；
- 局部验收是否优于 terminal-only 更新；
- 一般稀疏图上的组织形成规律；
- 人格标签向量是否比角色路由更优。

这就是为什么旧实验必须降级为：

**完整方法的受限原型证据，而不是最终主张的全部证据。**

---

## 16. 新方法的实验总设计

### 16.1 研究问题

#### Q1. 近似同质起点能否形成可观测的分工组织？

看什么：

- 人格标签是否分化；
- 节点行为是否分化；
- 某些任务家族是否稳定流向某些局部区域。

#### Q2. `split` 是否是必要动作，而不是可有可无的附加功能？

看什么：

- `do+outsource` 与 `do+outsource+split` 的差异；
- 在强组合任务上，split 是否提升质量或降低总返工；
- split 的收益是否高于整合开销。

#### Q3. 局部递归验收是否优于只有终局反馈？

看什么：

- 低质量子结果是否更少向上游传播；
- audit precision / recall；
- 返工深度和组织稳定性是否改善。

#### Q4. 稀疏图中的局部视野是否足以发现更合适的 agent 区域？

看什么：

- 任务是否能从任意起点迁移到高适配区域；
- 图结构差异如何影响组织形成；
- 小世界桥接节点是否带来更好的搜索效率。

#### Q5. 新方法是否不仅提升最终质量，也改变组织过程？

看什么：

- F1 / EM；
- 委派安全；
- token / hop / depth 成本；
- 人格分化、组织稳定性、桥接结构等过程指标。

### 16.2 baseline 体系

最少应包含以下几类 baseline：

1. `Single-Agent`
2. `Central Orchestrator`
3. `Central Orchestrator + Reflection`
4. `Fixed Static Roles`
5. `Fixed Self-Claim`
6. `Fixed Self-Calibrated`
7. `Fixed Peer-Calibrated (TCPB Prototype)`
8. `EDO w/o Split`
9. `EDO w/o Recursive Audit`
10. `EDO w/o Persona Tags`
11. `EDO Full`

### 16.3 benchmark 规划

主 benchmark 应继续保留：

- `HotpotQA`

因为它有利于：

- 与旧系统连续对比；
- 延续已有日志与基线；
- 快速验证委派与验收链条。

第二 benchmark 应优先推进：

- `MuSiQue`

因为它更适合测试：

- 任务拆分；
- 多子问题整合；
- 非线性递归协作。

若 long-paper 时间允许，再考虑：

- 更强组合型 benchmark；
- 更接近真实 agentic workflow 的 benchmark；
- 带工具调用和高不确定性的 benchmark。

---

## 17. 指标体系

### 17.1 结果质量指标

- `Answer EM`
- `Answer F1`

### 17.2 当前已在使用的协作过程指标

- `mean handoff count`
- `dead-end rate`
- `premature accept rate`
- `forward-after-correction rate`
- `token cost per sample`
- `cost-normalized F1`

### 17.3 新方法必须新增的组织指标

- `specialization entropy`
- `persona tag divergence`
- `audit precision`
- `audit recall`
- `subcontract acceptance rate`
- `split usefulness rate`
- `average delegation depth`
- `bridge utilization rate`
- `local-discovery success rate`
- `organization stability across seeds`

### 17.4 每个指标分别回答什么

- `specialization entropy`：组织是否从平均态走向分工态；
- `persona tag divergence`：人格标签是否真的分化；
- `audit precision/recall`：上游是否真的会验收，而不是装饰性打分；
- `subcontract acceptance rate`：外包结果是否经常能直接被上游接纳；
- `split usefulness rate`：拆分是否值得；
- `average delegation depth`：组织是否陷入过深递归；
- `bridge utilization rate`：稀疏图中的桥接节点是否真实发挥作用；
- `local-discovery success rate`：只靠局部信息能否找到更适合的区域；
- `organization stability`：人格和分工是否跨 seed 稳定形成。

### 17.5 当前结果与新指标的衔接

当前仓库尚未支持所有新指标，但现有指标仍然重要，因为它们是：

- Stage-1 的组织安全代理指标；
- 新系统必须至少不退化的底线；
- 证明“过程改善不只是 storytelling”的必要条件。

---

## 18. 日志与可复盘要求

完整 `EDO` 必须比旧系统拥有更丰富的日志，而不是更少。

### 18.1 完整方法至少应新增以下日志

- `task_tree.jsonl`
- `delegation_events.jsonl`
- `audit_events.jsonl`
- `persona_snapshots.jsonl`
- `neighbor_belief_snapshots.jsonl`
- `subtask_results.jsonl`
- `integration_events.jsonl`
- `organization_summary.json`

### 18.2 保留旧系统中的关键日志资产

以下旧日志仍应继续保留或兼容：

- `run_config.yaml`
- `sample_ids.json`
- `routing_traces.jsonl`
- `handoff_packets.jsonl`
- `competence_snapshots.jsonl`
- `parsed_predictions.jsonl`
- `metrics.json`
- `failure_cases.md`
- `case_studies.md`

### 18.3 新日志必须能回答的问题

完整日志必须允许研究者回答：

- 一个任务是在哪里被拆开的？
- 子任务分别外包给了谁？
- 哪个上游接受了哪个下游结果？
- 哪些人格标签因哪些互动而上升或下降？
- 某个节点为什么变成桥接者、整合者或审计者？
- 错误究竟来自拆分失败、外包失败、验收失败，还是最终生成失败？

---

## 19. 当前代码之后的实现路线

这一节直接服务后续工程拆分。

### 19.1 Phase 0: 保留 Stage-1 运行线

当前 `TCPB Prototype` 不应被推翻重写，而应被冻结为：

- 对照基线；
- 回归测试对象；
- 旧方法结果来源；
- 新运行时的 sanity anchor。

### 19.2 Phase 1: 状态层升级

目标：

- 从线性 `HandoffPacket` 升级到 `TaskNode + TaskTreeState`

建议新增模块：

- `workspace/idea04_core/task_tree.py`
- `workspace/idea04_core/audit_contracts.py`
- `workspace/idea04_core/persona_contracts.py`

### 19.3 Phase 2: 动作空间升级

目标：

- 从 `accept / forward` 升级到 `do / outsource / split`

建议新增：

- `workspace/idea04_core/action_policy.py`
- `workspace/idea04_core/subtask_planner.py`

### 19.4 Phase 3: 验收运行时

目标：

- 明确谁负责验收谁；
- 支持 `accept / minor_fix / reroute / resplit`

建议新增：

- `workspace/idea04_core/audit_runtime.py`
- `workspace/idea04_core/integration_runtime.py`

### 19.5 Phase 4: 人格标签与邻居信念

目标：

- 将当前 scalar competence 扩展为 persona tags；
- 区分公开人格与局部信念；
- 让邻居选择基于人格-任务签名适配，而不是固定角色。

建议新增：

- `workspace/idea04_core/persona_model.py`
- `workspace/idea04_core/neighbor_beliefs.py`

### 19.6 Phase 5: 图结构泛化

目标：

- 从 `chain / star` 扩展到通用稀疏连通图。

建议新增：

- `workspace/idea04_core/graph_builder.py`
- `workspace/idea04_core/topology_metrics.py`

### 19.7 Phase 6: 实验与分析脚本升级

目标：

- 支持组织指标、人格轨迹、拆分质量和桥接统计。

建议新增：

- `scripts/collect_organization_metrics.py`
- `scripts/plot_persona_divergence.py`
- `scripts/analyze_audit_quality.py`
- `scripts/analyze_graph_regions.py`

### 19.8 最重要的实现顺序

真正推荐的顺序是：

1. 先把 `TaskTreeState` 做出来；
2. 再实现 `split`；
3. 再实现递归验收；
4. 再引入人格标签；
5. 最后做一般稀疏图和更复杂实验。

原因很简单：

- 没有任务树，就没有完整 split；
- 没有递归验收，就没有社会化标签；
- 没有人格标签，就没有新路由核心；
- 没有这些基础，图结构泛化只会把旧问题复制到更多图上。

---

## 20. 风险、反证与叙事边界

### 20.1 主要风险

- 论文把完整方法讲得太大，但当前代码与证据还停留在 Stage-1；
- 人格标签定义不清，被 reviewer 误解成“换个名字的 competence”；
- split 带来的收益小于整合成本；
- audit 过强导致组织过于保守；
- 稀疏图上的局部搜索找不到真正高适配区域；
- 收益仍然主要来自 token 增加，而不是更好的组织结构。

### 20.2 反证条件

若出现以下现象，应主动缩窄主张：

- 标签长期不分化；
- 分工结构高度不稳定；
- 去掉 audit 几乎没有影响；
- 去掉 split 反而更好；
- 稀疏图下任务多数在局部打转；
- 旧 fixed-role 基线始终全面优于新方法。

### 20.3 叙事边界

当前最安全、也最诚实的写法应该是：

- `EDO` 是完整 long-paper 方法；
- 当前仓库验证的是它的受限原型；
- 该原型已经证明“结果导向的去中心化校准是对的方向”；
- 但真正的同质人格涌现、递归拆分与递归验收仍需 Stage-2 实现与实验。

这不是示弱，而是在主动建立可信度。

---

## 21. 为什么这个版本更像 EMNLP long paper

这个版本比旧版更强，不是因为它更复杂，而是因为它更基础、更统一。

它把多 agent 协作问题提升为：

## `how organization emerges from local interaction`

这使得：

- 中央调度器问题变成组织形成问题；
- 静态角色问题变成人格标签与分工形成问题；
- 路由问题变成局部效用与社会信任问题；
- 中间状态问题变成任务树、验收链和可复盘组织历史问题。

也就是说，整篇论文的主角从：

**一个更好的 fixed router**

升级成：

**一个关于组织如何在语言智能体社会中形成的可执行方法论**

### 21.1 这篇论文最终最该卖什么

最应该卖的不是：

- “我们有 4 个很会配合的专家角色”

而是：

- “我们提出了一种让近似同质 agent 在局部交互中形成分工组织的框架，并给出了一个已经可运行的受限原型与一套可复盘的扩展路线。”

### 21.2 结论性的定位

所以，本项目从现在开始应统一采用以下定位：

- `EDO` 是主方法。
- `TCPB Prototype` 是 Stage-1 restricted instantiation。
- 当前实验是 long-paper 研究线的起点证据。
- 后续工程目标不是继续调 4 个固定角色，而是让组织机制真正长出来。

这才和你的原始设想一致，也更接近一篇有辨识度的 EMNLP long paper。
