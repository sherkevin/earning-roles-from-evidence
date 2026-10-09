# Figure 2 微文字修正与主版同步报告

日期：2026-10-07。状态：内部论文版式门通过；科学投稿门和栅格字体生产门仍开放。

## 任务目的

Figure 2 在实际 AAMAS 版心中的最小字段仍偏细。本轮只处理已有标签的纸面可读性，
不新增模块、箭头、公式或科学结论，不改变两图计划和 Goal。所有生成和审查事件记录在
`experiments/logs/figure_microtype_round_20261007_v53_v55/`。

## 版本结果

| 版本 | 输入 | 结果 | 状态 |
|---|---|---|---|
| v53 | v52 | 微文字没有足够可观察的改善 | 保留，未采用 |
| v54 | v53 | 文字更大更深，但 `Profile P (< κ)` 发生符号变形 | 拒绝 |
| v55 | v54 | 修正精确符号，保留可读性改善和原拓扑 | 采用 |

v53、v54、v55 的 prompt、原始输出路径、图像哈希和逐版 README 均保留。v54 没有进入
活动稿；这次拒绝是语义正确性门，而不是审美偏好。

## 候选构建与审查

使用 Figure 1 v51、Figure 2 v55 的候选构建命令为：

```bash
python3 scripts/build_aamas2027.py --build-dir build/microtype_20261007_v55 --main-only
```

候选 PDF SHA-256 为
`8b78fb9172eb49003cb6f74e19ae4f5ef45fe5ff53cc4afe2272d6d2775606f2`。机器核验结果：

- 正文 8 页，总 9 页；References 从第 9 页开始；
- 引用已解析，overfull box 为 0；
- Figure 1/2 位于第 3/4 页，宽约 7.006 英寸，高约 2.335/2.342 英寸；
- 两图无裁切、断箭头或顺序漂移；
- v55 的 `Profile P (< κ)`、`Delta D [κ,w]`、P/D 字段、残差、封存 assignment、
  validate、一次 update/No-op 拓扑在纸面核查中保持正确。

独立 Codex gpt-6-sol 审查结论为内部稿 PASS；最小字段仍细小但不阻断整页观察。图像
PDF 容器 `font_count=0`，因此没有把栅格文字误称为可提取字体或最终出版质量。

## 主版治理

依据 ADR 0050，候选已复制为唯一当前主版：

- `artifacts/aamas2027/main.pdf`
- `article/aamas2027/build/main.pdf`

二者与版本快照 `artifacts/aamas2027/microtype_20261007_v55/main.pdf` 字节一致，
均为上述哈希。所有其他子目录仍是候选或历史快照，供回退和审计，不是并列主稿。
主版同步只改变排版资产，未改变论文科学内容、Goal、benchmark/baseline、真实实验结果
或 submission gate。

## 未关闭项目

栅格字体生产门仍 OPEN；科学 Goal 和三份论文验收标准不降级；submission gate 仍未通过。
若后续继续图稿工作，必须先提出可衡量的具体缺陷，并沿同样的版本、版心和独立审查流程
进行，不因本轮内部版式通过而声称论文科学就绪。
