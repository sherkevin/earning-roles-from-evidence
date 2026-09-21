# 论文审稿意见汇总（OpenReview）

> **论文**：《Earning Roles from Evidence in Multi-Agent Reasoning》（EDO / EDO-Frame）
> **投稿渠道**：EMNLP 2026 Long Paper Track（via ARR），匿名评审
> **OpenReview Submission**：11746
> **评审周期**：2026-07-01 ~ 2026-07-27
> **来源**：OpenReview（审稿意见由作者从论文页面取得）

---

## 一、评审总览

| 审稿人 | Soundness | Excitement | Overall Assessment | Confidence |
|---|---|---|---|---|
| Reviewer F61c | 3 | 3 | 3（Findings） | 3 |
| Reviewer vJUA | 2.5 | 2.5 | 2.5（Borderline Findings） | 3 |
| Reviewer 2sxq | 1 | 1 | 1（Do not resubmit） | 4 |
| Reviewer Dz77 | 1 | 2 | 1.5（Resubmit after next cycle） | 2 |
| **Area Chair（元审稿）** | — | — | **2（Resubmit next cycle）** | — |

**总体结论**：4 位审稿人一致认可核心想法值得研究，但写作可读性是最大共识问题；实验仅有 2Wiki 上显著增益、骨干模型偏小、成本不对等；作者未参与讨论期回应。**AC 最终判定：下一轮 ARR 周期需大幅修改后重投（2 = Resubmit next cycle）**。

---

## 二、Meta Review（Area Chair jU7U）

- **时间**：27 Jul 2026, 19:50（modified: 31 Jul 2026, 23:58）
- **链接**：https://openreview.net/revisions?id=i5lVMg49ag
- **可见范围**：Senior Area Chairs, Area Chairs, Authors, Reviewers Submitted, Program Chairs, Area Chair jU7U

### 元审稿意见（Metareview）

本文提出 **Evidence-Derived Organization（EDO）**——一种多智能体 LLM 框架，其中角色不预先分配：智能体在任务树上求解、委派、拆分、审计、记忆、使用标签门控工具，只有被接受的下游证据会更新未来的路由。框架实例化为 **EDO-Frame**，在三个多跳 QA 基准（HotpotQA、MuSiQue、2WikiMultiHopQA）上以 Qwen2.5-3B 为骨干评估，协议固定骨干、上下文构建与评分器，使"组织方式"成为唯一的变更变量。

### 值得发表的理由（Summary Of Reasons To Publish）

- 四位审稿人都认为核心想法值得研究：将多智能体组织视为"由被接受证据赚取的可测量状态"，而非提示词或管理者预先固定的角色，针对的是一个真实且研究不足的变量。
- 方法比辩论式多智能体工作更结构化（任务树、递归审计、persona 标签更新、记忆、工具门控）。
- 受控评估协议是隔离"组织方式"变量的合理努力；附录提供跨 8 个框架族的对比矩阵。
- 2Wiki 结果明确为正（F1 .555 vs 最强匹配基线 .469）。

### 建议修改项（Summary Of Suggested Revisions）

- **写作（最严重、被反复提出的问题）**：两位审稿人独立指出论文密集且难以跟进——缩写和记号在引入前就被使用（TCPB 出现在 line 151 却在 line 186 才定义，且其展开与所述含义不符）；定义依赖后文才引入的记号；多次阅读仍难以重构实际所做工作。
- **数据不一致**：HotpotQA F1 在 lines 474–479（~.76）与 Table 1（~.43）之间无法解释的不一致。
- **实验侧**：明显增益仅限 2Wiki；HotpotQA 与 MuSiQue 增益边际；所有头条结果只用单个小骨干（Qwen2.5-3B），更强模型下效应是否保持未知；评估仅覆盖多跳 QA，与"通用组织框架"的定位不符。
- **成本不对等**：Stage-2 每任务最多可用 72 次 LLM 调用，而 TCPB 最多 4 次；未报告总调用次数与墙钟时间。
- **对比缺失**：未直接对比动态角色分配方面最接近的 prior work。
- **超参数**：方法含大量常数，无调参流程或敏感性分析。
- **作者未回应**：讨论期作者未响应，上述问题未得到回应。

### 其他

- **Overall Assessment**：2 = Resubmit next cycle（需在下一 ARR 周期前完成实质性修改）
- **Reported Issues**：No
- **Publication Ethics Policy Compliance**：使用了符合 PEC 政策的隐私保护工具（仅用于语言润色等获批用途）

---

## 三、Official Reviews

### 3.1 Reviewer F61c

- **时间**：09 Jul 2026, 23:12（modified: 12 Jul 2026, 23:39）
- **链接**：https://openreview.net/revisions?id=jCAIqwGeEb

**论文摘要（Paper Summary）**

提出 EDO / EDO-Frame，多智能体推理框架，智能体没有预先固定的角色，而是从被接受的证据中"涌现"角色：智能体求解、委派、拆分、审计、使用标签门控工具，并基于下游证据更新本地 persona/可靠性标签。

**优点（Strengths）**

- 核心想法相当有趣：不给智能体固定角色（如"planner / critic / retriever"），而是让角色从被接受的工作与审计结果中涌现。
- 方法比常规辩论式多智能体论文更结构化：含任务树、局部路由、递归审计、persona 标签更新、记忆、标签门控工具访问。
- 报告结果强，尤其在 2Wiki：EDO 达到 .555 F1 / .497 EM，对比 MAD .469 / .401、单智能体 .330 / .275。

**缺点（Weaknesses）**

- 方法描述非常抽象：大量公式与设计术语，但缺少真实 agent 轨迹、失败委派、审计决策、记忆更新的具体示例。
- 成本问题严重：Stage-2 每任务最多 72 次 LLM 调用，TCPB 最多 4 次；需要与成本匹配的基线对比，但论文未完全做到。
- 最大增益在 2Wiki，HotpotQA 增益极小（+0.0045 F1，vs 最强匹配基线）。

**评论、建议与笔误（Comments Suggestions And Typos）**

见 Weakness。

**评分**

| 项目 | 值 | 说明 |
|---|---|---|
| Confidence | 3 | Pretty sure（可能遗漏某些细节） |
| Soundness | 3 | Acceptable（主要主张有充分支持） |
| Excitement | 3 | Interesting |
| Overall Assessment | 3 | Findings（可被 Findings of the ACL 接受） |
| Reproducibility | 3 | 可复现但有难度（参数设置不全/主观，数据不广泛可得） |
| Datasets | 1 | 未提交可用数据集 |
| Software | 1 | 未发布可用软件 |

**伦理与身份**：无伦理关切，无需伦理复审；对作者身份无知晓/猜测；PEC：未使用生成式 AI 工具撰写评审。

---

### 3.2 Reviewer vJUA

- **时间**：08 Jul 2026, 12:13（modified: 12 Jul 2026, 23:39）
- **链接**：https://openreview.net/revisions?id=7tJlePQrdW

**论文摘要（Paper Summary）**

提出 EDO，一种基于证据的多智能体 LLM 推理组织机制。不在提示词中分配固定角色，智能体应答、外包、拆分、审计、记忆、使用标签门控工具；被接受的下游证据更新 persona 标签与未来路由决策。

**优点（Strengths）**

- 框架清晰有趣：角色被处理为可测量的组织状态而非提示标签。
- 方法组合了任务树、递归审计、persona 标签更新、记忆、工具门控。
- 在 HotpotQA、MuSiQue、2Wiki 上评估；附录提供完整 8 框架对比矩阵及额外消融。

**缺点（Weaknesses）**

- 新颖性可能被高估：未直接对比动态角色分配、资源分配、可逆多智能体 QA、自适应算子选择等最接近的 prior work。
- 附录提升了透明度，但许多对比基线是宽泛的编排框架，而非最接近的概念替代方案。
- 计算对等性不清晰：附录报告 EDO token 均值，但未报告 EDO 总调用次数或墙钟时间。
- 部分消融削弱机制主张：selector 变体在 Qwen 下几乎中性，部分 Phi-4 对照组为负。

**评论、建议与笔误（Comments Suggestions And Typos）**

- 请更清晰地说明术语与证据层级：论文使用 EDO、EDO-Frame、TCPB、Stage-2、focused EDO、adaptive-router EDO，这些区分有用，但正文需要一张紧凑表格帮助读者理解每个实验行激活了哪些组件。
- 建议把附录中框架广度矩阵的浓缩版移入正文：附录通过列出 24 个框架族对比大幅提升透明度，但正文目前总结得过于紧凑。

**评分**

| 项目 | 值 | 说明 |
|---|---|---|
| Confidence | 3 | Pretty sure |
| Soundness | 2.5 | — |
| Excitement | 2.5 | — |
| Overall Assessment | 2.5 | Borderline Findings |
| Reproducibility | 3 | 可复现但有难度 |
| Datasets | 2 | Documentary（新数据集对复现研究有用） |
| Software | 3 | Potentially useful |

**伦理与身份**：无伦理关切；对作者身份无知晓/猜测；PEC：使用了隐私保护工具（仅语言润色等获批用途）。

---

### 3.3 Reviewer 2sxq

- **时间**：04 Jul 2026, 01:10（modified: 12 Jul 2026, 23:39）
- **链接**：https://openreview.net/revisions?id=kr8bsyKXW0

**论文摘要（Paper Summary）**

提出 Evidence-Derived Organization（EDO），一种使多智能体系统的组织与角色自动涌现的框架。作者将其实例化为 EDO-Frame，并在三个多跳 QA 基准上评估。

**优点（Strengths）**

- 从性能证据中自动推导多智能体组织与协调的想法原则上很有趣。

**缺点（Weaknesses）**

- 整篇论文的呈现令人困惑。缩写与记号常在引入前就被使用：如 TCPB 在 line 151 使用、line 186 才定义；Decentralization invariant 定义（line 203）使用的记号在 line 212 和 276 才引入。部分缩写与其表述含义不符（如 line 186 将 TCPB 展开为 "Topology Calibration Reduction"）。
- 大量依赖技术含义晦涩且未加澄清的行话；方法论与实验评估都极其不清楚。

**评论、建议与笔误（Comments Suggestions And Typos）**

见 Weaknesses。

**评分**

| 项目 | 值 | 说明 |
|---|---|---|
| Confidence | 4 | Quite sure（仔细核对过要点） |
| Soundness | 1 | Major Issues（不足以发表或与 ACL 无关） |
| Excitement | 1 | Not Exciting |
| Overall Assessment | 1 | Do not resubmit（需彻底重做，或与 *ACL 社区无关） |
| Reproducibility | 1 | 无论如何努力都无法复现 |
| Datasets | 1 | 未提交可用数据集 |
| Software | 1 | 未发布可用软件 |

**伦理与身份**：无伦理关切；对作者身份无知晓/猜测；PEC：未使用生成式 AI 工具撰写评审。

---

### 3.4 Reviewer Dz77

- **时间**：01 Jul 2026, 20:30（modified: 12 Jul 2026, 23:39）
- **链接**：https://openreview.net/revisions?id=vxdRsiuU8A

**论文摘要（Paper Summary）**

提出 Evidence-Derived Organization（EDO），一种多智能体 LLM 框架：智能体的角色、路由与工具使用不预先分配，而是通过任务树上的递归委派与审计，从被接受的下游证据中"赚取"，而非由管理者或角色提示固定。

**优点（Strengths）**

- 想法值得研究：将多智能体组织框定为"从被接受证据中赚取"而非预先分配，瞄准了一个真实且研究不足的变量。

**缺点（Weaknesses）**

- **写作**：密集、缠绕、确实难以跟进；多次阅读仍难以重构作者究竟做了什么、各部分如何组合。
- **模型规模**：仅在相当小的模型（Qwen2.5-3B）上评估。编排与脚手架方法已知对弱基座模型有帮助（补足模型自身做不了的推理），而随模型变强（内部自行完成推理）增益会缩小甚至消失——这削弱了泛化性论断。
- **单一基准**：仅 2Wiki 有实质提升，另外两个（HotpotQA、MuSiQue）边际。感觉该方法可能只在单一基准上有优势。
- **单一任务类**：所有数据集都是 QA，只探测了一个任务族。对于定位为通用多智能体推理组织机制的方法，应跨不同任务类验证，证明效应不局限于单一基准或单一类别。
- **超参数无依据**：方法引入大量常数与超参数，无推导、无引用、无调参流程、无敏感性分析，直接断言数值（如 Section 3.8）。读者无法判断结果对这些设置是否稳健，还是依赖手工调参的选择。

**评论、建议与笔误（Comments Suggestions And Typos）**

- 写作是核心弱点：密集、缠绕、难以跟进；且存在具体不精确处——未定义缩写（如 TCPB 全文使用但从未展开）、结果不一致（lines 474–479 HotpotQA F1 ~.76 与 Table 1 ~.43 同一基准差异悬殊，无调和）。
- 单小骨干损害泛化性（同上）。
- 增益仅在单一基准真实（同上）。
- 仅测试一类基准（同上）。
- 超参数无依据（同上）。

**评分**

| 项目 | 值 | 说明 |
|---|---|---|
| Confidence | 2 | 愿意为评估辩护，但可能遗漏细节/误解核心点 |
| Soundness | 1 | Major Issues |
| Excitement | 2 | Potentially Interesting |
| Overall Assessment | 1.5 | Resubmit after next cycle（需下一轮后的大幅修改） |
| Reproducibility | 1 | 无法复现 |
| Datasets | 1 | 未提交可用数据集 |
| Software | 1 | 未发布可用软件 |

**伦理与身份**：无伦理关切；对作者身份无知晓/猜测；PEC：使用了隐私保护工具（仅语言润色等获批用途）。

---

## 四、共性问题归纳（修改优先级参考）

**① 写作可读性（最严重、审稿人共识度最高）**

- 缩写/术语先使用后定义：TCPB（line 151 使用，line 186 定义，且展开 "Topology Calibration Reduction" 与含义不符）。
- 记号先使用后引入：Decentralization invariant（line 203）依赖 line 212/276 的记号。
- 数据不一致：HotpotQA F1 正文 lines 474–479（~.76）vs Table 1（~.43），需调和。
- 建议：全文术语统一表、实验行组件对照表、补充具体 agent 轨迹/审计/记忆更新示例。

**② 实验支撑不足**

- 明显增益仅 2Wiki；HotpotQA（+0.0045 F1）与 MuSiQue 边际。
- 单一小骨干 Qwen2.5-3B，需验证强模型下效应是否保持。
- 仅评估多跳 QA 单一任务类，与"通用组织机制"定位不符，需扩展任务类。
- 部分消融结果中性/负向（selector 变体、Phi-4 对照），削弱机制主张。

**③ 成本与公平性**

- Stage-2 最多 72 次 LLM 调用 vs TCPB 4 次；需成本匹配基线、报告总调用次数与墙钟时间。

**④ 对比不足**

- 未直接对比动态角色分配/资源分配/自适应算子选择等最接近 prior work；正文基线应聚焦概念最近方案，而非宽泛编排框架。

**⑤ 可复现性**

- 大量超参数无推导、无调参流程、无敏感性分析；未提交数据集与软件（多数审稿人 Datasets/Software 打 1 分）。

**⑥ 过程问题**

- 作者在讨论期未回应审稿人，负面印象未能挽回（AC 明确提及）。

---

*文档由 OpenReview 页面审稿意见整理生成；评分与评语为原文忠实转录，未改动审稿人表述。*
