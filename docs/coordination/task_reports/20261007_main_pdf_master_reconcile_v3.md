# Canonical main PDF reconciliation — reference supplement v3

日期：2026-10-07
状态：`PARTIAL / INTERNAL_REVISION_MASTER`

## 发现

并行论文构建已经生成了 `reference_supplement_20261007_v3/main.pdf`，且父目录
`artifacts/aamas2027/main.pdf` 已经与它相同；但 `main_pdf_master.json` 仍指向 v2，
其记录的 SHA-256 与父目录文件不一致。这会使“主版”和 provenance 分离，不能作为可审计
的唯一入口。

## 收敛

保留 v2 和 v3 两个不可变版本；不覆盖任何版本目录。补齐 v3 的 `verification.json`，
把父目录 master provenance 指向 v3，并验证两份 PDF 字节完全相同：

- SHA-256：`b316464801f9e02c65fa61d9f704c21945679ced1492e897df1749b72425f3be`；
- 正文 8 页，总 9 页；References 从第 9 页开始；0 overfull、无未解析引用；
- `submission_ready=false`，仍是内部 revision，不代表科学投稿 gate 已打开。

版本构建仍放在 `artifacts/aamas2027/<round>/`，唯一主版仍是
`artifacts/aamas2027/main.pdf`。今后如果正文或图片发生新构建，必须先生成新的版本目录
和 verification，再更新这个 parent-level master；不能直接覆盖主版而不更新 provenance。
