# AAMAS Figure Plan v3 — active

日期：2026-10-07。依据 ADR 0048，将正文图组从三张收敛为两张。
本计划替代 v2；旧资产与审查原文保留，不改变 Goal 或科学 gate。

## 两张图各自解决什么问题

| 图位 | 读者需要理解的论点 | 画面必须呈现的内部操作 |
|---|---|---|
| Figure 1：责任混淆与 earning-roles 闭环 | 同样的 recipient 负面判断不能说明同样的 producer 责任 | 两个文件责任反例；筛选后的公共证据进入局部未来选择；结果只影响下一次状态 |
| Figure 2：选择与更新的两接口 | 发布证据与训练策略有不同输入、时间和资格 | 上：source 完整资格 → P/D 切分 → 任务/历史表示及公共元数据 → 评分与残差 → 读切后封存；下：同一 assignment 与 outcome → 契约验证 → 一次更新 → next state |

完整实验矩阵、baseline、信息条件、成本和结果位置保留在正文表格。
`experiment_map.pdf` 作为历史候选保存，不再是正文活动图。

## 样例依据与共同视觉规格

深读记录见 [`20261007_gallery_design_and_prompt_analysis.md`](../../coordination/task_reports/20261007_gallery_design_and_prompt_analysis.md)。
直接查看八张原图，选 Agentic Supernet 的紧凑结构与 Snapshot of Influence 的技术
表达作为主参考；DPO 只提供对比构图启发，不混入其插画风格。不是给所有图统一套一个配色。

- 白底、深灰规则线、克制的蓝与青色强调；统一 TeX/Times 风格文字层级。
- 模块内部有信息：文件改动、证据行、P/D 时间切分、表示条、局部候选、封存 ID。
- panel 标题仅比普通标签略大；不用巨型全大写标题、渐变、阴影或装饰性盾牌/锁。
- 每张约 3:1 横幅为设计目标；正文等比例放置，目标高度约 2.2–2.5in。
- 普通标签按最终约 7–9pt 设计；不通过缩小文字塞入额外说明，细节交给 caption。
- 图中案例与选择均为机制示意，无效果数字、优势曲线或排名结论。

## 验收与版本

1. 因果：source judgment 不直接产生 target outcome；选择先封存，target 后执行。
2. 归因：recipient-only/mixed/UNKNOWN 不进入 producer evidence。
3. 更新：source publication 不触发 persistent updater；matching target 只更新一次。
4. 反馈：回写进入 next state，不回改当前 snapshot、assignment 或历史 evidence。
5. 视觉：实际论文宽度下核验字号、内容密度、线条和两图一致性，并与选定样例并看。
6. 版本：生成前保存 prompt/config，生成后保存原图、路径、哈希和逐项审查。

首轮候选为 v35（Figure 1）与 v36（Figure 2），全部迭代原图和提示词保留。
当前内部主稿采用 v51（Figure 1）与 v55（Figure 2），两者均保留原始 AI 栅格，
用无覆盖层的 PDF 容器等比例嵌排。v53 没有产生可观察的微文字改善，v54 因
`Profile P (< κ)` 被改写为错误符号而拒绝；v55 在保留拓扑和标签的前提下修正该符号，
并通过独立图面与实际论文页核查。标题常规字重、图 1 右侧两行布局、图 2 细字段改善
均用于当前内部稿；图 2 最小标签仍偏细小，栅格字形和最终出版质量仍 OPEN，
不称为冻结的投稿资产。实际正文 8 页，总 9 页，References 第 9 页；两图位于第 3/4 页，
约 7.006in 宽，Figure 1 高 2.335in、Figure 2 高 2.342in。构建与审查见
[`本轮标题与密度任务报告`](../../coordination/task_reports/20261007_figure_hierarchy_density_round.md)。
旧 v42/v48、首轮任务报告与稳定 PDF 保留回退；v49/v50 的未落实标题字重也保留原图。
本轮 v49/v50 的四个实际 prompt/image 版本及独立审查位于
`experiments/logs/figure_hierarchy_density_round_20261007_v49_v50/`；之后的
v53/v54/v55 微文字修正、失败原因、候选构建和主版提升回执位于
`experiments/logs/figure_microtype_round_20261007_v53_v55/`。
论文主版固定为 `artifacts/aamas2027/main.pdf`；版本目录中的 PDF 只作候选或历史快照，
通过页面核查后才可覆盖主版，遵循 ADR 0050。
Figure 2 的 O 是完整观察发布资格，不代替责任归因门 G；完整负面判断仍有发布资格。
目标执行由 Figure 1 表达，位于 Figure 2 的两接口之间，不是图 2 中另一条已绘制泳道。
v30/v32/v34 的原生产通过判断被同日
[`counteraudit`](../../coordination/task_reports/20261007_figure_counteraudit_v30_v32_v34.md)
收窄；旧版本继续保留。新图改善不代替三份科学评价标准的验收。
