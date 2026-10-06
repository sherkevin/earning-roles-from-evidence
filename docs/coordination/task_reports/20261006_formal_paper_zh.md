# 2026-10-06 正式论文中文 Markdown 任务汇报

## 任务目标

把当前 AAMAS 正式英文主稿翻译成可以直接阅读的中文 Markdown，覆盖摘要、故事线、方法、benchmark、baseline、实验矩阵、结果边界、讨论和结论；不改动英文主稿，也不把尚未确认的实验写成结果。

## 本次决策

- 唯一生效的中文正文阅读稿是 [`docs/paper/aamas2027/FORMAL_PAPER_ZH.md`](../../paper/aamas2027/FORMAL_PAPER_ZH.md)。
- [`article/aamas2027/main_zh.md`](../../../article/aamas2027/main_zh.md) 只保留为指针，避免出现两份可能漂移的中文正文。
- 英文 [`article/aamas2027/main.tex`](../../../article/aamas2027/main.tex) 仍是内容、科学状态和结果边界的唯一权威来源。
- 本次交付格式是 Markdown；没有把 LaTeX 译稿作为正式交付物。公式仍以 Markdown 可渲染的 `$$...$$` 数学块保留。

## 完成内容

- 逐节翻译摘要、引言、相关工作与定位、问题形式化、责任感知协议、benchmark 与 baseline、实验问题与矩阵、结果与证据边界、讨论与局限、结论。
- 保留 RARE、ArtifactRole、PeerSelect、责任门、读取截点、仅选中项更新、H1–H4、RQ1–RQ4、结构根、成本和“未知”等关键术语及信息边界。
- 补回 Markdown 转换中容易丢失的 6 个表格标题、3 个图注和 8 条正文引用，并附正文实际引用的参考文献链接。
- 结果表的空单元和“待定”保持为空，不新增数字、不改变主张边界；图形继续链接当前英文矢量资产。
- 将结构核查写入 [`experiments/logs/chinese_paper_translation_20261006/translation_checks.json`](../../../experiments/logs/chinese_paper_translation_20261006/translation_checks.json)。

## 核查结果

源稿与中文稿均有 22 个正文 section/subsection 标题、9 个显示数学块、3 张图和 6 张表；中文稿包含 8 条正文引用对应的参考文献，未发现 HTML 残留或 `TBD` 字面残留。结果单元仍按源稿保留为空或“待定”。本次是文档翻译，不是实验运行，LLM API 调用数和 GPU 作业数均为 0。

机器可读核查同时记录了源稿和中文稿的 SHA-256，便于后续英文源稿变化后重新生成并比较，而不是继续手工维护两套正文。

## 解释边界

中文稿的用途是中文阅读、共同审阅和后续写作讨论；它不替代英文投稿源文件，也不证明 benchmark 已合格、方法已锁定或角色学习已经有效。若英文主稿后续发生实质修改，应先修改英文源，再重新生成中文稿并更新核查记录。
