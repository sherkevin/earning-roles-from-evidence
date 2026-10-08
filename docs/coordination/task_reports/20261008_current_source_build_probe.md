# Current-source LaTeX build probe

日期：2026-10-08
状态：`INCOMPLETE_TERMINATED_TIMEOUT`

## 目的

检查当前工作树中尚未审查的论文与图稿修改是否已经自然改善正文第 8 页右栏留白。构建使用独立目录，不能覆盖 canonical `artifacts/aamas2027/main.pdf`。

## 执行

- 命令：`python3 scripts/build_aamas2027.py --main-only --require-content-pages 8 --build-dir baseline_current_20261008_v1`；
- 输出目录：`experiments/logs/n03_paper_current_source_build_probe_20261008_v1/`；
- `pdflatex` 运行约五分钟后仍未生成 `verification.json`，日志停在处理当前图稿 PDF 的生成阶段；
- 只终止了这次隔离构建进程，canonical 主版没有触碰；
- API、GPU、科学实验：均为 `0`。

## 解释

这次尝试不能支持页数、引用、overfull 或提交状态结论。它只说明当前并行 source/figure 状态不适合直接提升为主版；现有已验证的 [canonical main PDF](../../artifacts/aamas2027/main.pdf) 继续有效。部分 LaTeX 输出和原始日志被保存在同一日志目录，便于定位具体图稿或宏展开问题。

## 下一步

先在隔离目录定位 `pdflatex` 停滞的具体输入，再进行一次小范围修复构建；修复前不覆盖主版，也不把当前并行源文件称为可提交版本。
