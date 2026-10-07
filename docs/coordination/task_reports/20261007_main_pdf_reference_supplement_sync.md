# Main PDF 主版同步：reference supplement v2 — 2026-10-07

状态：`INTERNAL_MASTER_RECONCILED`。并行论文迭代已经生成并提升了
`reference_supplement_20261007_v2`，但主版 provenance 仍指向上一轮
`microtype_20261007_v55`。本轮只做主版一致性收敛：保留新的版本目录，把其核验文件
归档到版本目录，并更新上一层的 `main_pdf_master.json`。没有手工改写 PDF，也没有
改动故事线、方法、benchmark、baseline 或科学 gate。

## 核验结果

- 主版：[`artifacts/aamas2027/main.pdf`](../../../artifacts/aamas2027/main.pdf)
- 来源版本：[`reference_supplement_20261007_v2/main.pdf`](../../../artifacts/aamas2027/reference_supplement_20261007_v2/main.pdf)
- provenance：[`main_pdf_master.json`](../../../artifacts/aamas2027/main_pdf_master.json)
- source/master SHA-256：
  `36b8dfa7baa2f29a650fe9b51645330603b5afb962f9eb64c7c8e48f694183a3`
- 正文 8 页；总计 9 页；References 从第 9 页开始；0 overfull；无 unresolved reference
- `submission_ready=false`：结果表和科学证据仍未完成，主版是内部审阅稿

`verification.json` 来自对应构建目录，并已复制到版本化 artifact 目录；主版与来源
逐字节一致。旧的 v55 版本保留，可随时回退；以后只有通过页数、引用和版心检查的
版本才可更新上一层 `main.pdf`，未核验版本不得覆盖主版。
