# Canonical main PDF baseline synchronization — baseline sync v1

日期：2026-10-07
状态：`PARTIAL / INTERNAL_REVISION_MASTER`

## 目的

把当前论文源中已经完成的 baseline 表述收敛到一个可审计的版本，并维护上一层目录的
唯一主版 PDF。这个任务只处理论文构建与主版同步，不激活 benchmark、API 实验、GPU
训练或任何科学结果。

## 输入与版本

- 源文件：`article/aamas2027/main.tex`、`article/aamas2027/references.bib`；
- 隔离构建日志：`experiments/logs/n03_paper_baseline_sync_20261007_v1/`；
- 隔离构建命令：
  `python3 scripts/build_aamas2027.py --main-only --require-content-pages 8 --build-dir baseline_sync_20261007_v1`；
- 构建版本：`artifacts/aamas2027/baseline_sync_20261007_v1/`。

版本中的论文措辞将历史 context-only trust 保留为诊断比较项，把同信息控制写成
`contextual trust linear`，并把 DIST1/PIPE3 的 development/confirmation 划分留给版本化
parity card 冻结。这样不会在论文排版任务中擅自决定尚未共同确认的 structural-root split。

## 独立校验

- PDF 可打开；总页数 9；正文 8 页；References 从第 9 页开始；
- 0 个未解析引用；0 个 overfull box；官方 `aamas.cls`、bst 与 `by.pdf` 未被修改；
- 版本 PDF SHA-256：
  `3bdfeec42d8ab983c8bcc73fc51642aae2d064bd16e73de997840ff3764aebf8`；
- 独立检查结果保存在该版本的 `promotion_receipt.json`，构建 verification 保存在
  `verification.json`。

## 主版变更

通过校验后，版本 PDF 已复制到上一层唯一主版：
`artifacts/aamas2027/main.pdf`。主版与版本字节一致，provenance
`artifacts/aamas2027/main_pdf_master.json` 已同步到同一版本和 SHA-256。历史版本没有被
覆盖或删除。

## 边界与下一步

这是内部修订版，`submission_ready=false`；它只证明排版和版本链路通过，不能证明
benchmark 已冻结、baseline 已执行、模型有效或科学投稿 gate 已打开。下一步仍须先收敛
候选 structural-root split 与 parity card，再按统一成本、可见信息、later-use 和独立
stream 协议执行真实 baseline 矩阵。
