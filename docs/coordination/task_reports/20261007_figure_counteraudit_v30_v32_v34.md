# 当前图组复核：可用候选不等于图形验收通过

日期：2026-10-07。对象：当前工作区实际引用的 Figure 1 v30、Figure 2 v32、Figure 3 v34。
结论：**NOT_PASSED_FOR_FINAL_FIGURE_FREEZE**。不改变 Goal 或三份科学标准。

## 目的与证据

回答用户的两个问题：三张 AI 图是否满足现行要求；是否达到所选样例的表达水平。
本次直接渲染活动 PDF、查看本地样例图片、读取活动 main.tex 的 caption/Description，
并将 PDF 字号换算为论文全宽约 7in（504 PDF pt）下的实际大小。
不能以“生成了 1050px 缩略图”“字体已嵌入”或“整篇编译无 overfull”代替纸面字号与语义核验。

证据目录：[`figure_counteraudit_20261007_v30_v32_v34`](../../../experiments/logs/figure_counteraudit_20261007_v30_v32_v34/)。
包含执行前配置、逐标签字号、活动 PDF 哈希、实际渲染和样例来源/哈希。
0 次生图、0 次科学实验 API、0 个 GPU 作业。渲染仅用于检查，不修改图像。

独立 Codex 审查员 `/root/current_figure_semantic_audit` 同时核对了活动 PDF 与正文，
指出下面三项图文冲突；主审随后查看渲染逐项复核。独立审查未修改文件。

## 三张图的阻塞项

| 图 | 实际观察 | 与要求的冲突 | 必要修复 |
|---|---|---|---|
| Figure 1 闭环概览 | outcome 下方的灰色虚线回到紫色锁，即 sealed assignment | caption 明确要求只进入 future state/next read，不能回改已封存 assignment | 把反馈端点明确落到单独的下一次状态/读切对象，并保持当前封存选择不变 |
| Figure 2 方法流程 | JUDGMENT→TARGET 是实线橙色主流程；底部 UPDATE 没有回到 future read 的路径 | 计划要求目标结果在 assignment 之后产生，判断与目标结果不能画成直接因果；需体现未来读切更新 | 区分源 episode 与未来 target，画出 seal→target outcome→matching update→next read |
| Figure 3 实验地图 | MATCHED INFORMATION 横跨所有 arms；只列四个 policy，并未标注为部分示例 | raw/no-update 是信息消融，不能据此断言各臂实际使用相同信息；完整正文还有 terminal-only 等必要对照 | 总标题表达相同机会/预算和完整成本核算；只将 strongest contextual control 与 RARE 标为同信息，完整矩阵另明确引用 |

Figure 3 另有视觉误读风险：只有 RARE 行从浅色圆点变为深绿实心圆，没有图例说明其
含义。当前没有相应效果数据，不应借颜色暗示 RARE 独有的改善。所有臂应用中性图形
表达比较条件，若圆点表示状态而非效果，则需明确状态语义。

## 纸面字号：生产门尚未全部通过

三张图都有嵌入字体，但按当前全宽使用方式换算，字号并未满足 Figure Plan 中
“正文标签不小于约 7pt”的要求：

| 图 | 最小标签字号 | 代表标签 |
|---|---:|---|
| Figure 1 v30 | 约 3.5pt | ARTIFACT、RECIPIENT USE、JUDGMENT、延迟反馈说明 |
| Figure 2 v32 | 约 5.1pt | UNKNOWN / AUDIT、BEFORE SELECTION、AFTER SEAL |
| Figure 3 v34 | 约 5.4pt | ADAPTER、STREAM COMPARISON |

Figure 1 的阶段标题也仅约 5.8pt。Figure 2/3 多数对象标签约 6.6pt。
这是 PDF span size × placement width / source width 的可复算结果，不是屏幕缩放印象。
字体矢量化并不会自动放大纸面字号；必须收紧无效留白、改变构图比例或减少次要标签后
提高实际字号，再按放入正文后的大小检查。

## 与样例库到底差在哪里

本轮实际查看 CollabLLM（icml2025-0242）、DPO（neurips2023-02）和 Agentic Supernet
（icml2025-0960）的本地图片。样例库不具有一种统一画风；这些图包含容器、图标、
背景色，CollabLLM 甚至有完整的对话示例。因此过去把共同规范简化为“白底、少框、
少字、无图标”的判断并不充分。

- CollabLLM 展开了核心模拟机制：从一次候选交互到多条后续轨迹，再到奖励构造与 policy。
  读者看到的是方法如何工作，而不只是模块名称。
- DPO 用左右结构直接表达方法差异；图本身就承载一个论点。
- Agentic Supernet 展示构建块、搜索空间和不同任务产生的不同结构，抽象对象都有明确用途。

当前图组有统一色系、短标签和较清楚的阶段排列，这是改进。但盾牌表示 gate、
文档表示 evidence、眼睛表示 read、锁表示 assignment，仍主要是在以图标替代名词。
图中尚未直观展现：哪些观察能成为 producer evidence，哪些只属于 recipient 的工作；
这两类观察如何造成不同的未来责任分配。这个差距属于方法表达深度，不能仅靠换配色解决。

没有单独的概念对比 panel，因此不能说“概念图已通过”。可在 Figure 1 内用一个短的
示意实例突出“recipient 修复自己的模块≠producer 有缺陷”，再让合法证据进入未来选择；
实例应明确是机制示意，不加入虚构的效果数字。是否增加 panel 需服从现有论文篇幅，
不必另加第四张图。

## 对此前审查结论的修正

保留此前 [`independent_final_figure_audit`](20261007_independent_final_figure_audit.md)
的原文，但本次不接受其中“主要语义门、纸面门已通过”的判断：其遗漏了反馈箭头端点，
也没有量化实际论文宽度下的字号。此前“只需改 caption、不需要动图”的建议不足以修复
图形拓扑；图注不能抵消指向错误对象的箭头。

不能据此称此前 8.6–8.8 分是客观通过证据。本轮采用逐项门槛，不再用平均分遮盖关键
错误。当前唯一可保留的正面结论是：字体已嵌入，历史候选已保存，整体配色更统一。

## 最小有效下一步与验收

1. 先修 Figure 1/2 的时间关系和反馈端点；通过“结果无法流回已封存选择”的逐箭头审查。
2. 把字号按最终全宽做到约 7pt 以上，并明确区分机制示意与结果证据。
3. Figure 1 用一个具体观察→归因→未来选择的可视化实例解释核心机制；Figure 3 修正
   信息对照标注和圆点含义，完整 baseline 名单服从现行实验矩阵。
4. 新版本保留 prompt、原图和变更说明；重新做独立语义、纸面与样例对照审查。

本轮只作检查和留档，未改动活动图或论文。即使上述图形门通过，也不能代替论文的
novelty、benchmark/baseline 和真实实验门。继续推进科学投稿目标时，这次复核应防止
图稿错误掩盖或歪曲待验证的研究机制。
