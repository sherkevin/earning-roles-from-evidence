# AI figure long-goal production round — v30/v32/v34 (2026-10-07)

状态：`PARTIAL`（三图已通过本轮嵌入字体、版心、纸面缩放和灰度检查；最终独立审查与投稿资产冻结仍开放）。

## 与 Goal 的对应关系

本任务对应 [`GOAL.md`](../GOAL.md) 的 ER-G1：图稿必须把 situated judgment → attributable role evidence → future assignment → later outcome 的因果链在版心内讲清楚，并满足可复现生产要求。图稿工作不替代 ER-G2–ER-G4 的方法、benchmark、baseline 或真实效能证据，Goal 未修改，`goal_change_requested=false`。

## 运行前冻结与真实操作

本轮冻结了 v28/v23/v26 的语义结构和图位，不改变正文 caption、图间颜色语义或方法状态合同。Figure 1 使用已保留的 v29 textless AI base，Figure 2 使用新生成的 v31 textless AI base，Figure 3 使用新生成的 v33 textless AI base；每张底图均保留完整 prompt、生成输出副本和 SHA-256。三张底图之后只通过 LuaLaTeX picture overlay 添加短标签，字体使用系统 Arial Bold 并嵌入 PDF；没有用 HTML 或 Python 绘制图形。

真实生成与生产证据见：

- `article/aamas2027/figures/ai_versions/v29_textless_vector_base_20261007/`
- `article/aamas2027/figures/ai_versions/v30_vector_typeset_refined_20261007/`
- `article/aamas2027/figures/ai_versions/v31_method_textless_vector_base_20261007/`
- `article/aamas2027/figures/ai_versions/v32_method_vector_typeset_refined_20261007/`
- `article/aamas2027/figures/ai_versions/v33_experiment_textless_vector_base_20261007/`
- `article/aamas2027/figures/ai_versions/v34_experiment_vector_typeset_refined_20261007/`
- `experiments/logs/figure_ai_long_goal_round_20261007_v30_v32_v34/receipt.json`

## 本轮结果

| 图 | AI 底图 | 生产 PDF | `pdffonts` | 当前判断 |
|---|---|---|---|---|
| Figure 1 | v29 | v30 | Arial-BoldMT，CID TrueType，embedded/subset/unicode | 通过本轮生产门 |
| Figure 2 | v31 | v32 | Arial-BoldMT，CID TrueType，embedded/subset/unicode | 通过本轮生产门 |
| Figure 3 | v33 | v34 | Arial-BoldMT，CID TrueType，embedded/subset/unicode | 通过本轮生产门 |

每个生产 PDF 均保留一张 AI raster base，但可见标签不再是 JPEG 字形；`pdfimages -list` 与 `pdftotext` 记录在同一轮日志中。Figure 3 的标题改用 Arial Unicode bullet，已消除先前的 CMSY10 Type 1 依赖。

将 v30/v32/v34 放入真实正文图位后，隔离编译命令为：

```bash
python3 scripts/build_aamas2027.py --main-only \
  --build-dir build/figure_set_v30_v32_v34_fresh_20261007 \
  --require-content-pages 8
```

得到 10 页 PDF，正文内容 8 页，参考文献从第 9 页开始，引用未解析数为 0，overfull box 为 0；完整 verification 和 PDF SHA-256 在 `article/aamas2027/build/figure_set_v30_v32_v34_fresh_20261007/`。第 3、4、7 页的真实版心截图已保存到 `experiments/logs/figure_ai_long_goal_round_20261007_v30_v32_v34/fresh_paper/`。

1050 px 纸面缩放和 `pdftocairo -gray` 灰度副本显示：Figure 1 的长轴和 delayed update、Figure 2 的三泳道和 before/after seal、Figure 3 的 tracks/policies/endpoints 及 RQ1–RQ4 仍可辨认；没有出现越界或正文分页漂移。

## 对 Goal 标准的核对

- **已满足（本轮局部）**：三张图都存在完整 AI prompt、原始/文本无关底图、生产源文件、PDF、渲染图和哈希；可见标签使用嵌入式 TrueType；正文保留 8 页内容、参考文献第 9 页起、0 overfull；灰度和版心检查通过；历史候选 v28/v23/v26、v27/v22/v24 仍可回退。
- **部分满足**：图稿在开放主轴、泳道、三列实验图和短标签上已接近样例库风格，但 Figure 3 左侧仍使用抽象人物 token，Figure 1/2/3 的 raster base 仍不是纯矢量；最终是否达到 topconf 质感还需独立审查员依据样例库复核。
- **未开始/不由本轮证明**：benchmark 与 baseline 资格、真实任务结果、在线更新效果、实时性、遗忘、A800 训练和科学 submission gate 均保持原状态；本轮没有新增 LLM/API/GPU 科学实验。

## 未完成原因与修复

剩余问题属于**审查证据不足和科学范围未完成**，不是编译失败。下一步只做一次独立的三图质量审查，检查语义、版心小字号、灰度、样例库风格、标签与正文 caption 一致性；若某一张被判不通过，则保留 v30/v32/v34，基于完整新 prompt 生成新的 AI 底图版本，不覆盖历史资产。科学主线仍按 ER-G1–ER-G4 另行推进，不因图稿通过而提前宣称论文完成。

## Goal 变更

`goal_change_requested=false`。本轮没有降低“最终投稿图”的标准，也没有把工程版心通过写成科学投稿通过。
