# 2026-09-28 故事线评价标准 v1.2：论文结构与段落行为

- 状态：COMPLETE（标准升级）；不代表论文达到 Findings-ready 或 Proceedings-ready。
- 对应 Goal：ER-G1（sharp、自洽、可证伪故事线）、ER-G4（可审计论文）。
- goal_change_requested：false
- 真实 API/GPU：未运行；本任务是文献正文审查和标准文档升级。

## 完成的工作

1. 直接读取四篇 AAMAS proceedings 全文，而不是只看摘要：
   - AAMAS 2025 Soft Condorcet Optimization；
   - AAMAS 2026 Defection at First Sight；
   - AAMAS 2026 Reputation as a Solution to Cooperation Collapse；
   - AAMAS 2026 Best Paper Developing Guidelines for Human–LLM Agent Teams。
2. 记录 Introduction、Related Work、Problem/Method、Experiment、Discussion/Conclusion 的段落职责、章节之间的输入输出关系，以及结果段落的观察—解释—边界模式。
3. 新建 [AAMAS 论文结构审查](../../research/20260928_aamas_paper_structure_audit.md)。
4. 新建并登记唯一生效的 [故事线与论文写作评价标准 v1.2](../../research/versions/evaluation/storyline/storyline_v1.2_20260928_eval.md)；v1.1 保留并标记为 superseded。
5. 更新 active registry 与 canonical README；补充来源审计。

## 从正文样本得到的可复用规律

- 引言沿“现实协作现象 → 默认设定的失效 → sharp gap → 唯一机制 → 可验证贡献 → 范围/章节路线”推进。
- Related Work 按问题轴或假设分组，每组末尾明确最近邻差异，不写成逐篇摘要列表。
- Method 遵循“最小原语/信息边界 → 性质或目标 → 算法机制 → 可检查预测”。
- Experiment 遵循“是否有效 → 为什么有效 → 何时失效 → 代价与限制”。
- 结果段先陈述图表事实和分母，再解释机制，最后报告替代解释和边界。
- 结论只回收已证实的机制和范围，不能新增贡献。

这些是样本规律，不是录用定理。AAMAS 官方要求仍以官方 Call、Reviewer Guidelines 和 Findings 页面为准。

## 与 Goal 的对照

- 已完成：论文叙事和段落职责现在有独立、可核查、带来源的标准；故事线主链已明确映射到 situated judgment → attributable role evidence → future assignment → unseen-task utility。
- 部分满足：标准规定的写作结构已经形成，但我们尚未拥有完整闭环实验，因此不能把任何段落写成已验证结果。
- 未满足：benchmark freeze、方法 freeze、独立 live confirmation、A800 主实验和闭环 efficacy 仍未完成。
- 具体原因：当前科学证据仍受责任归因、producer 质量计分、持久 peer state 与 independent histories 限制；不是因为写作标准可以降级。
- 下一步：先按 v1.2 把论文提纲和 claim–evidence matrix 对齐，再修复方法/benchmark 的科学资格门，取得 H1/H2/H3 所需证据后再写结果段。
- 是否需要用户决定：不需要新的 Goal 决定；本次只是在已同意的严格标准上增加来源充分、可审计的写作约束。
