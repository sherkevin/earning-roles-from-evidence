# 两图标题层级与结构密度优化

日期：2026-10-07。状态：本轮优化与内部纸面核查完成；最终出版质量仍 OPEN。

## 目的与范围

用户授权继续优化 v42/v48。上轮语义和观察性纸面可读通过，剩余明确差距是 panel
标题略重、图 1 右侧留白较多，以及图 2 细标签接近可读下限。本轮只处理这些问题，
继续使用内置 AI 生图；保持两张正文图，不调整故事线、方法、Goal 或科学标准。

## 操作与衡量

- Figure 1 v49：保留两种责任案例，将右侧选择/执行/反馈序列压成两行，减少低信息留白。
  保留原始 Q 与 use trace 双输入、B:v0 绑定、recipient-only 审计和 future-only 更新。
- Figure 2 v50：保留两接口拓扑，降低标题字重，改善细标签；不删输入或补数学公式。
- 两图仍约 3:1，实际版心宽约 7in；只改变图像中的布局/字形，PDF 容器不加覆盖层。
- 通过条件：独立逐箭头语义不退步；与旧版相比标题层级和密度有可指出的改善；
  实际页面标签可读、无裁切且风格一致。栅格无可提取字体不被冒称嵌字通过。
- 预算：首轮两次生图；只有独立审查指出具体阻断项，才允许每图一次有针对性修正，
  全轮至多四次。不为“更高级”无界增加变体。每版实际 prompt、原图、哈希和失败保留。

## 证据与 Goal 对照

配置与后续 raw events：`experiments/logs/figure_hierarchy_density_round_20261007_v49_v50/`。
上轮 v42/v48 原图、PDF 和纸面证据保留作为回退。只有完成比较与实际版心检查后，
才替换内部主稿资产。ER-G1/G5 的图形呈现是本轮对象；ER-G2/G3/G4 不产生新增科学证据。

## 实际执行与版本选择

本轮真实调用内置 imagegen 四次，达到预先记录的上限。0 科学 LLM 实验、0 GPU job。
模型 ID、seed 和生成 usage 未由服务披露；不把这些图称为 image2.5 输出。
原图直接嵌入 PDF，无 HTML/Python 绘图、像素加工或文字覆盖。

| 版本 | 父版本 | 实际改善 / 未过项 | 采用状态 |
|---|---|---|---|
| v49 / Figure 1 | v42 | 右侧闭环排列为两行，减少留白；标题仍粗重 | 保留，由 v51 替代 |
| v50 / Figure 2 | v48 | record 字段、数学下标等细标签更清楚；标题仍粗重 | 保留，由 v52 替代 |
| v51 / Figure 1 | v49 | 标题匹配普通 `Public evidence` 标签，变为常规字重；next state 用中性 before/after | 内部主稿采用 |
| v52 / Figure 2 | v50 | 标题匹配普通 `Local menu` 标签；保留细标签改善与完整两接口连线 | 内部主稿采用 |

第一轮“减小/减轻标题”的文字要求没有落实；指定图内已有普通标签作为字形参照后才成功。
这一轮复用了原有对象、箭头合同和图库的文字层级，没有通过新增文字或模块填满空白。
每个版本的实际 prompt、原图、父版本、原返回路径和 SHA-256 均已保存。

- [Figure 1 v51 提示词](../../../article/aamas2027/figures/ai_versions/v51_overview_regular_titles_20261007/prompt.md)
- [Figure 1 v51 原图](../../../article/aamas2027/figures/ai_versions/v51_overview_regular_titles_20261007/figure1_v51.png)
- [Figure 2 v52 提示词](../../../article/aamas2027/figures/ai_versions/v52_method_regular_titles_20261007/prompt.md)
- [Figure 2 v52 原图](../../../article/aamas2027/figures/ai_versions/v52_method_regular_titles_20261007/figure2_v52.png)

## 独立审查与论文嵌排

Codex gpt-6-sol 审查员复核原图以及论文第 3/4 页，结论如下；这是观察性图面核查，
不是方法有效性或最终出版验收。

| 指标 | 结果 | 证据与限制 |
|---|---|---|
| 责任 / 时间语义不退步 | PASS | 原始 Q 与 use trace 绑定 B:v0；recipient-only 仅审计；先封存再执行；matching outcome 经 validate 后只更新一次 |
| 标题层级 | 改善 | 常规 serif 字重替代粗标题，与对象标签更协调 |
| 图 1 密度 | 改善 | 右半区两行闭环减少低信息留白，封存记录连至 target；无新增长解释 |
| 实际版心裁切 / 连线 | PASS | 图框、箭头与文字无裁切或断线 |
| 观察性可读与两图协调 | PASS，用于内部稿 | 主要标签清楚，蓝/青/灰、文件/表格、细线一致；图 2 最小标签在整页观看时仍偏细小 |
| 栅格文字最终出版门 | OPEN | 两个图像容器 font_count=0；清楚的栅格外观不能作为矢量字形或嵌字证明 |

图库仅提供 JPEG 视觉依据，未验证样例源 PDF 的字体嵌入；不据此推断作者使用的软件。

隔离构建命令：
```bash
python3 scripts/build_aamas2027.py --build-dir build/hierarchy_density_20261007_v51_v52 --main-only
```

编译成功：正文 8 页、总 9 页，References 单独从第 9 页开始，引用已解析、0 overfull。
两图位于第 3/4 页，各为 7.0057in × 2.3352in，实际栅格约 310dpi。全部九页已渲染并查看；
没有发现此次图稿替换引入的版面故障。原有结果空位和第 8 页留白仍保留待真实结果填充。
官方模板哈希一致；已有 incomplete-ifx 兼容性警告保留，不隐瞒也不误称新失败。

本轮版本稿：`artifacts/aamas2027/hierarchy_density_20261007_v51_v52/main.pdf`。
SHA-256：`0815b36b7a24c89af29bb7d00aaa78db627c8acffa368f8c73fbc9e7f9c11342`。
`receipt.json`、`independent_review.json`、`paper_scale_measurements.json`、编译日志及实际
源码快照在本轮日志目录。旧 v42/v48 与上一轮稳定 PDF 保留，可回退。
按照 ADR 0050，该版本已提升为唯一当前主版
`artifacts/aamas2027/main.pdf`；父目录主版与本轮版本稿哈希一致。其他版本目录只作历史/回退，
不再作为并列主稿。
最终检查确认四版 prompt/image 哈希、活动图稿、编译源码快照和稳定 PDF 一致，正文恰有
两个 figure 块且无旧图 3 引用；`git diff --check` 无输出。Codex 打开稳定稿返回 queued，
未把排队状态写成已显示。

英文 Figure 1 图注仅增加对 Figure 2 验证过程的引用，中文阅读稿同步：延迟反馈须通过
检查才影响未来状态。没有改动数学机制、实验矩阵或结果单元。

## Goal 对照与剩余工作

ER-G1/G5 的方法图解释和论文呈现取得具体改善；ER-G2/G3/G4 没有新增科学证据。
Goal 文件哈希与执行前相同；三份科学标准没有降级。期间 scientific gate 的索引哈希
被刷新，本轮图稿流程没有写入或提升该 gate，十五个要求仍全部 pending。

下一步只针对可指出的剩余问题处理：图 2 最小标签的纸面字形，以及两图最终印刷质感。
应保持已核查的对象与连线，采用局部文字规格修正，并在实际版心比较；没有明确改善
目标时不追加变体。最终生产未过，不能把内部候选称为冻结投稿图。

## 后续微文字修正与主版提升：v53–v55

在上面的 v49–v52 记录之后，用户指出 Figure 2 的最小字段在论文版心仍偏细。
因此单独开启受限微文字轮次，配置、原图、哈希、失败和审查均保存在
`experiments/logs/figure_microtype_round_20261007_v53_v55/`。本轮没有科学 API 调用、
GPU 作业或正文科学内容变更。

| 版本 | 处理 | 结论 |
|---|---|---|
| v53 | 尝试放大既有微文字并保持拓扑 | 视觉改善不足，保留但不采用 |
| v54 | 进一步加深微文字 | `Profile P (< κ)` 被生成器改成错误符号，语义审查拒绝 |
| v55 | 只修正上述符号，继承 v54 的可读性改善 | 独立图面和实际版心核查通过，采用 |

v55 的原图为 1627×544；无覆盖 PDF 容器哈希为
`70b3ef829f7a272cd7f84ab748dfd18d8b851d3d1f72b38823aa6c9a53396777`，容器没有可提取
字体。以 Figure 1 v51 + Figure 2 v55 构建的候选 PDF 哈希为
`8b78fb9172eb49003cb6f74e19ae4f5ef45fe5ff53cc4afe2272d6d2775606f2`，正文 8 页、总 9 页、
参考文献从第 9 页开始、引用已解析、overfull 为 0；Figure 1/2 实际版心高度分别约
2.335/2.342 英寸，均无裁切。独立 Codex gpt-6-sol 审查确认 Figure 2 的关键符号、
P/D 字段、残差、封存、验证、一次更新/No-op 拓扑没有漂移，纸面观察性可读通过。

依据 ADR 0050，候选已提升为唯一当前内部主版
`artifacts/aamas2027/main.pdf`，工作区 `article/aamas2027/build/main.pdf` 与其字节一致；
版本快照保留在 `artifacts/aamas2027/microtype_20261007_v55/`，不得当作并列主稿。
这次提升只关闭了内部版式/图面核查，不关闭栅格字体生产门，也不改变科学 submission
gate、Goal 或三份论文验收标准。
