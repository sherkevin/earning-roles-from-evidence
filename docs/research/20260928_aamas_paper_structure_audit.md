# AAMAS 论文结构与段落行为审查

- 日期：2026-09-28
- 状态：LITERATURE_AUDIT
- 用途：为故事线与创新点评价标准补充写作脉络；不是新的 active 研究定义，也不是录用保证。
- 审查对象：AAMAS 正式 proceedings 中的四篇公开全文。它们覆盖方法/理论、经典 MAS 学习、LLM-MAS 系统和 Best Paper 级的人机协作指南，不能代表全部 AAMAS 论文。

## 一手正文样本

| 论文 | 类型 | 正文证据 | 本地保存 |
|---|---|---|---|
| Lanctot et al., “Soft Condorcet Optimization for Ranking of General Agents”, AAMAS 2025 | 方法 + 定理 + 多层实证 | Introduction 明确评价难题、现有 ranking 的缺口、SCO 机制和四项可核验贡献；Background 先定义 AvT/AvA 与 baseline；方法给出损失、在线更新和定理；实验按 PrefLib、噪声 tournament、held-out Diplomacy 递进 | [2025_soft_condorcet.txt](../references/aamas/papers/2025_soft_condorcet.txt)，原文 [PDF](https://www.ifaamas.org/Proceedings/aamas2025/pdfs/p1253.pdf) |
| Russell et al., “Defection at First Sight: Learning Partner Selection in Optional Social Dilemmas without Prior Information”, AAMAS 2026 | MARL + partner selection | Introduction 从社会困境的公共问题进入，指出已有工作依赖“新伙伴已有历史信息”，构造去掉该假设的 sharp gap；Contribution 明确学习策略和观察限制；Preliminaries 定义游戏/Q-learning；实验再解释 emergent co-evolution | [2026_partner_selection.txt](../references/aamas/papers/2026_partner_selection.txt)，原文 [PDF](https://www.ifaamas.org/Proceedings/aamas2026/pdfs/IBSZ1473.pdf) |
| Ren et al., “Reputation as a Solution to Cooperation Collapse in LLM-based MASs”, AAMAS 2026 | LLM-MAS 系统 + 多场景实验 | Introduction 依次建立 cooperation collapse、已有证据、解决方案缺口、双层 RepuNet 机制和三类场景；方法先 formalize network/reputation，再分 direct encounter、gossip、network evolution；结果按现象、相关性、网络结构、ablation 解释 | [2026_reputation.txt](../references/aamas/papers/2026_reputation.txt)，原文 [PDF](https://www.ifaamas.org/Proceedings/aamas2026/pdfs/UEHN4980.pdf) |
| Yurrita et al., “Developing Guidelines for Human-LLM Agent Teams: A Multi-Stakeholder Lens”, AAMAS 2026 Best Paper | 指南/框架 + 专家验证 | Introduction 定义人机团队和新能力，指出 guideline 缺口，说明多 stakeholder/temporal framework 和迭代来源；Related Work 按概念对象组织；Guidelines 按 teaming stages 展开；验证分别报告 relevance、clarity、coverage 和 limitation | [2026_human_llm_teams.txt](../references/aamas/papers/2026_human_llm_teams.txt)，原文 [PDF](https://www.ifaamas.org/Proceedings/aamas2026/pdfs/JOWO4591.pdf) |

## 反复出现的行为逻辑

这些规律来自正文样本的交叉阅读，而不是从标题或摘要推测：

1. 先让读者知道为什么现在必须解决这个协作问题，再谈方法。Introduction 的第一段通常建立 MAS 现象、任务或社会后果；随后缩小到一个可操作的 failure，而不是一开始罗列模块。
2. gap 不是“没人做过”，而是一个可定位的限制。典型形式是已有方法拥有某能力，但依赖一个不现实的信息、时序、规模、目标或参与者假设。Partner Selection 论文用“新伙伴没有 prior information”作切口；SCO 用 incomplete/uneven comparison data 作切口。
3. 机制紧跟 gap，并且能在一句话中复述。机制不是系统组件清单，而是解除该限制的单一操作。随后贡献列表把机制拆成可检查的理论性质、算法性质和证据性质。
4. 每个章节都在推进同一条论证链。定义只引入后文实际使用的对象；方法解释对象如何产生；实验测试机制预测；讨论回到边界、替代解释和失败条件。优秀论文不会把一个章节变成独立的技术说明书。
5. 证据按难度或外部有效性递进。SCO 由已知数据集/优化问题到稀疏噪声模拟再到真实 held-out 数据；RepuNet 由经典困境到更接近现实的场景；Human–LLM Teams 由 workshop/literature synthesis 到额外专家验证。递进的每一步都对应一个新的 claim。
6. 结果段落先给观察，再给解释，再给边界。主结果通常先报比较和不确定性，然后解释为什么与机制一致，最后说明适用范围、失败或仍需验证的部分。图表不是结论本身，正文必须解释图表改变了哪个判断。
7. 贡献列表是可审计承诺，不是宣传口号。每一项贡献都能在后文找到定义、定理、算法、实验或用户研究证据；不会把“使用 LLM”“搭建运行时”“换 prompt”单独列为科学贡献。
8. 结尾回到问题和边界。结论重新回答中心问题，说明机制实际解释了什么、没有解释什么；讨论或 limitations 保留反例、规模限制、测量误差和未来工作，而不是只重复最优数字。

## 可复用的段落级模型

样本中最稳定的不是固定段落数量，而是一个段落只承担一个论证动作：

Topic claim → necessary context/evidence → mechanism or comparison → interpretation → bridge to next claim

- Introduction 段：只推进“现象 → 已知限制 → sharp gap → 机制 → 可检验结果”中的一个动作。
- Related Work 段：先按限制/假设分组，再指出该组与本文机制的差异；不能逐篇列摘要。
- Method 段：先定义对象和信息边界，再给更新/决策规则，再解释实现约束和可检验预测。
- Experiment 段：先说明问题、控制和指标，再给结果；一个结果段只回答一个预注册问题。
- Discussion 段：把结果翻译回 mechanism-level claim，同时写明替代解释、失败和外推边界。

## 对本项目的直接含义

我们的稿件必须把以下顺序写成一条不可跳跃的链：

1. 多 agent workflow 中，producer 交付质量与 recipient 的真实使用结果不一致，单次 acceptance 或终局 reward 不能识别“谁适合未来承担哪类工作”。
2. 现有 reputation/trust/partner-selection 方法的具体信息、归因或时序限制，造成一个可复现的最小反例。
3. 我们的核心机制只解决一个问题：把 recipient 的 situated judgment 变成可归因、延迟可处理、能在执行前影响 future assignment 的 role evidence。
4. 方法章节证明它如何在有限信息和有限状态下更新；实验先验证 judgment 的信息价值，再验证 assignment 和未见任务 utility，最后测实时成本、漂移和遗忘。
5. 讨论只宣称实验覆盖的范围，并保留 producer 责任误归因、recipient 自身 integration、scorer coverage 和 UNKNOWN 的限制。

这意味着不能把“JEV/backbone/在线训练框架/图结构/benchmark 适配器”平行写成五个创新点；它们只有在证明上述核心机制所必需时才进入正文。

## 边界和反例

- 四篇样本不是完整语料库，不能推出“所有录用论文都必须采用七段 Introduction”。
- 论文类型不同：定理型、系统型和指南型的证据形式不同，不能强迫我们的实证故事加入无关定理。
- 样本中的某些论文可能仍有测量或统计不足；这里提取的是写作和论证行为，不等于替它们背书。
- 这些规律不能把当前项目的协议资格、v3 链路或零概率更新伪装成科学效果。

## 结论

v1.2 将采用“行为逻辑硬门 + 段落职责模板 + claim/evidence 对齐”的组合。它约束论文是否能让审稿人沿同一条因果链读完，而不宣称存在能保证录用的写作模板。
