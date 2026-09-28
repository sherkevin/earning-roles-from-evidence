# 三份验收文档的来源审计

日期：2026-09-28
状态：`PROVENANCE_REPORT`，不是第四份 active 评价标准。
对应 active 文档：[canonical/README.md](canonical/README.md)。本报告支持 v1.1 评价标准的升级说明。

## 结论先行

三份验收文档不是凭空构造的，但也不能称为已经完成了对历届 AAMAS 优秀论文的系统计量研究。它们来自三层材料：

1. **AAMAS 官方底线**：直接读取 AAMAS 2027 Main Track Call、Information about Findings、Submission Instructions 和 Reviewer Guidelines。
2. **本项目的科学操作化**：把官方的 originality/significance/soundness/reproducibility/clarity/relevance 转成我们这个故事必须满足的可观测链条，并吸收此前实验暴露的责任、评分、UNKNOWN、未来 assignment 和成本问题。
3. **优秀论文的定向抽样**：核对了官方 AAMAS 2024 Best Paper Awards 页面和 AAMAS 2026 Awards 页面，并抽查了获奖/提名论文的题目、领域和公开摘要入口。这个样本足以否定“一套固定获奖模板”，但不足以推出统计意义上的普适规律。

因此，P0-1 到 P0-6、三份文档的项目专用检查项、100 分内部评分和 `UNKNOWN`/责任归因规则，都是**我们的审查工具**，不是 AAMAS 官方逐字要求，也不是从获奖论文自动学习出来的定理。

## 一手来源

- [AAMAS 2027 Call for Main Track](https://warwick.ac.uk/fac/sci/dcs/aamas2027/calls/call-for-main-track/)：明确列出 originality、significance、soundness、reproducibility、clarity、relevance、presentation quality 和对 state of the art 的理解/引用；同时要求贡献属于 autonomous agents/multiagent systems，不能只是 generic prompting、generic tool use 或任意生成任务。
- [AAMAS 2027 Information about Findings](https://warwick.ac.uk/fac/sci/dcs/aamas2027/guidelines-and-policies/findings/)：要求 scientific soundness、清晰写作、AAMAS relevance、evidence support、claims justified 和 identifiable contribution；也明确负结果、replication、benchmark、dataset 等可以成为有价值的科学贡献，但取决于 novelty、scope、generality、validation 和 impact。
- [AAMAS 2027 Submission Instructions](https://warwick.ac.uk/fac/sci/dcs/aamas2027/guidelines-and-policies/instructions/)：鼓励 supplementary 提供证明、实验细节、代码和数据；要求为 prompt、AI tool 和版本提供足够信息，并要求作者自己审查偏差和验证结果。
- [AAMAS 2027 Reviewer Guidelines](https://warwick.ac.uk/fac/sci/dcs/aamas2027/guidelines-and-policies/reviewer-guidelines/)：列出 desk-rejection 风险，包括超页数、out of scope、技术内容严重不足、格式、匿名性和 AI 使用违规；这支持我们把“可复现、可验证、范围匹配”当作硬门，但不直接规定我们的 P0 门。

## 优秀论文抽样得到的真实信息

[AAMAS 2024 Best Paper Awards](https://www.aamas2024-conference.auckland.ac.nz/awards/best-paper-awards/) 同时包含合作博弈理论论文、agent-based modeling 论文、强化学习论文、人类目标识别论文和论证/公平等方向。AAMAS 2026 官方 awards 页面又包含 human–LLM team guidelines、合作 MARL、reputation in LLM-based MAS、规划、社会选择和多机器人等不同类型。

这个抽样说明：优秀论文并不共享一个固定算法形式或固定实验 benchmark。可迁移的规律更窄：

- 贡献对象能被一句话明确识别；
- 方法/理论/框架与要回答的问题一致；
- 证据形式与主张匹配（理论主张给推导，经验主张给受控实验，指南/框架主张给系统方法和验证）；
- 论文把范围、比较对象、适用边界和失败情形说清楚；
- 结果不是靠泛化口号替代证据。

这些规律支持三份评价文档的方向，但不能证明我们的具体 `situated judgment → role evidence → future assignment` 机制有效，也不能证明 AAMAS 审稿人一定接受 P0-1 到 P0-6 的具体阈值。

## 三份文档分别是怎样推出来的

### 故事线评价标准

来自官方的 relevance/significance/clarity，加上本项目必须识别的因果链：真实交付、真实 recipient action、责任归属、未来 assignment、未见任务质量/成本。`P_v(c)` 与 `B_u(v,c)` 的区分、第三方 owner、不能用 acceptance rate 代替角色形成，来自项目对旧实验和相关工作的识别风险审查。这是项目化的因果识别要求，不是 AAMAS 明文句子。

### 方法论评价标准

来自官方的 soundness/reproducibility 和 submission 对实验/版本/提示信息的要求，加上在线更新问题的可执行性：事件 schema、信息边界、UNKNOWN、幂等 replay、延迟/乱序、更新延迟、状态容量、遗忘和 drift。`RLS/Laya/AnyJev/SGD` 不能直接称创新，是我们根据当前研究目标和已有项目审查做的 novelty boundary。

### Benchmark + baseline 评价标准

来自官方的 validation、evidence、state-of-the-art comparison 和 scope fit，加上本项目的识别需求：两个结构 root、producer/recipient 真实依赖、独立 contract/adoption、同信息强 baseline、完整成本、development/confirmation split 和 UNKNOWN 分母。`uniform/no-update/raw acceptance/terminal-only/contextual trust/pooled/RARE` 这个矩阵是我们的控制设计，不是官方 baseline 清单。

## 当前应如何表述

可以说：三份验收文档是**基于 AAMAS 官方底线、项目因果与工程审计、以及定向优秀论文抽样形成的项目化审查规范**。

不能说：AAMAS 官方要求必须通过 P0-1 到 P0-6；我们已经统计证明了所有优秀 AAMAS 论文都遵循这些规则；或者三份文档已经验证了我们的 benchmark/method。

下一步若要把“历届优秀论文规律”提高到更强证据，需要预先定义论文样本、按贡献类型编码问题—方法—证据—局限，再由独立复核者复核编码。那会是一个新的 literature audit，不应偷偷改写当前 active 评价标准。

## 新增的正文结构审查

本轮进一步读取了四篇正式 proceedings 全文，并将正文结构与段落功能记录在 [AAMAS 论文结构与段落行为审查](20260928_aamas_paper_structure_audit.md)：

- AAMAS 2025 Soft Condorcet Optimization：方法、定理、在线更新和多层实证如何由同一评价缺口串联；
- AAMAS 2026 Defection at First Sight：如何把 partner-selection 的信息限制写成 sharp gap；
- AAMAS 2026 Reputation as a Solution to Cooperation Collapse：系统机制、场景递进和 ablation 如何对应；
- AAMAS 2026 Best Paper Developing Guidelines for Human–LLM Agent Teams：指南型贡献如何由多 stakeholder、时序框架和专家验证组成。

这次审查得到的是“现实问题 → 默认设定失效 → 锐利切口 → 唯一机制 → 可验证贡献 → 对应证据 → 边界”的样本规律，以及“是否有效 → 为什么有效 → 何时失效 → 代价是什么”的实验叙事顺序。它们被写入 storyline evaluation v1.2，但仍标记为论文样本归纳和项目推断，不是 AAMAS 官方保证，也不是固定段数模板。
