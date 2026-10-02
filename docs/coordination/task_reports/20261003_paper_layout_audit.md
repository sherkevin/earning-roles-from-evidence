# 2026-10-03 AAMAS 主稿与图稿复核

## 结论

独立只读复核确认 `article/aamas2027/build/main.pdf` 为 7 页、letter 双栏，使用官方
AAMAS 类文件；当前构建无 overfull box，引用已解析。主稿实际使用
`overview.pdf`、`method_state.pdf` 和 `experiment_map.pdf` 三张矢量图，图注和
`\Description` 齐全，无裁切、重叠或字体嵌入问题。`timeline.pdf` 仍是候选资产，未放入
主稿，因此没有引入重复图或额外页数。

## 需要保留的限制

当前 PDF 仍明确标为 `INTERNAL PRE-RESULTS`，结果列为空，ArtifactRole、RARE、Qp 和
later outcome 仍是待冻结接口。它是结构和写作骨架，不是可投稿的科学结果稿；不能因
排版通过而打开 submission gate，也不能把工程资格写成方法效果。

Figure 3 和 Table 2 的小字号标签需在最终打印尺寸复核；必要时应压缩文案或把细节移到
补充材料。最终稿还必须逐字段对齐冻结 scorer、ledger 和结果 manifest。若加入
`timeline.pdf`，需要重新检查与 Figure 2 的语义重复和页数。

## 证据与后续

- 现有 `main.pdf` 页数、纸张尺寸和图稿渲染已实际检查；不为凑页数继续堆内容。
- 图稿版本均保留在 `article/aamas2027/figures/versions/`，当前使用的图资产与历史版本
  不覆盖。
- 后续优先级仍是 benchmark/scorer/independent history 与真实确认实验；图稿只在字段
  或结果冻结后做一次最终可读性复核。

`goal_change_requested=false`；本任务没有 API、GPU 或科学结果。
