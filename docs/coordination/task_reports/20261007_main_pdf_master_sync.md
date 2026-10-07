# Main PDF 主版同步 — 2026-10-07

状态：`INTERNAL_MASTER_SYNCED`。本轮只整理论文产物，不改变故事线、方法、benchmark、
baseline 或科学 gate。

## 目的

版本构建目录持续保留每次迭代，上一层目录只保留一个可引用的主版 PDF，避免用户或
审阅者误拿到旧版、失败版或未核验版。主版必须是某个已经完成页数与版式核验的版本的
逐字节副本，不能手工修改 PDF。

## 当前主版

- 主版：[`artifacts/aamas2027/main.pdf`](../../../artifacts/aamas2027/main.pdf)
- 来源版本：[`microtype_20261007_v55/main.pdf`](../../../artifacts/aamas2027/microtype_20261007_v55/main.pdf)
- provenance：[`main_pdf_master.json`](../../../artifacts/aamas2027/main_pdf_master.json)
- promotion receipt：[`canonical_pdf_promotion_v55.json`](../../../experiments/logs/figure_microtype_round_20261007_v53_v55/canonical_pdf_promotion_v55.json)
- SHA-256：`8b78fb9172eb49003cb6f74e19ae4f5ef45fe5ff53cc4afe2272d6d2775606f2`
- 页数：正文 8 页；总计 9 页；参考文献从第 9 页开始；无 unresolved reference；无 overfull box
- 状态：`submission_ready=false`。结果表仍为空，主版是内部 pre-results 审阅稿。

## 维护规则

1. 每次迭代在新的版本目录中编译和核验，历史目录不可覆盖。
2. 只有通过页数、引用和 overfull 检查的版本，才允许同步到上一层的 `main.pdf`。
3. 同步时更新 `main_pdf_master.json`，记录来源目录、两份 SHA-256、页数和投稿状态。
4. 若新版本未通过核验，主版保持不变；不能用复制或改名掩盖失败。

本轮使用 `pdf` skill 的产物维护规则完成复制和 metadata 核对；没有重新生成或篡改 PDF
内容。`pdfinfo` 与来源 verification JSON 对主版页数和标题做了交叉检查。`article/aamas2027`
只保留 LaTeX 源和工作区构建，不再提供第二份主版。
