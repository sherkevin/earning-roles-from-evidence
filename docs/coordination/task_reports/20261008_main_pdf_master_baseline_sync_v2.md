# Canonical main PDF synchronization — baseline sync v2

日期：2026-10-08
状态：`PARTIAL / INTERNAL_REVISION_MASTER`

## 目的

把当前论文源的已完成文字、引用和两图版本做一次隔离构建，并在通过排版审查后同步到上一层唯一主版。版本目录不覆盖；主版 provenance 与复制回执必须同步。

## 构建与证据

- 源：`article/aamas2027/main.tex`、`article/aamas2027/references.bib`；
- 构建命令：`python3 scripts/build_aamas2027.py --main-only --require-content-pages 8 --build-dir baseline_sync_20261007_v2`；
- 版本快照：`artifacts/aamas2027/baseline_sync_20261007_v2/main.pdf`；
- 构建日志：`experiments/logs/n03_paper_baseline_sync_20261007_v2/`；
- PDF SHA-256：`9092c81938e12a9bcf8b234bc28c7fe758c6f3fa3e55b70bfc9ac224da671edc`；
- 总页数 9，正文 8 页，References 从第 9 页开始；
- 未解析引用 0，overfull box 0，官方模板文件未改动；
- 已渲染并复核第 1、8、9 页，页面可读，边界正确。

## 主版

通过上述检查后，版本 PDF 已同步到：

`artifacts/aamas2027/main.pdf`

`artifacts/aamas2027/main_pdf_master.json`、版本 `verification.json` 与
`promotion_receipt.json` 记录同一来源和哈希；版本 PDF 与主版字节一致。此前版本继续保留，可用于回退和审计。

## 已知质量债务

第 8 页正文只占左栏，右栏留白明显。当前同步只保证了正文页数和可编译性，没有用无实质依据的填充内容掩盖该问题。后续密度修订必须增加真实方法、实验设计或必要图表，并重新隔离构建；不能直接改写主版。

## 科学边界

这是内部修订主版，`submission_ready=false`。本轮没有调用 LLM API、没有启动 benchmark、没有启动 GPU，也没有产生科学效果结论。它只更新论文 artifact 身份和排版快照。
