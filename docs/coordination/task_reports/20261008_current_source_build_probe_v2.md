# Current-source TeX input diagnostic

日期：2026-10-08
状态：`DIAGNOSTIC_PREAMBLE_OR_ENVIRONMENT_BLOCKER`

在上一轮隔离构建超时后，本轮分别对当前 `main.tex` 和仅把两张正文图替换成占位框的 `probe_nofig.tex` 做 20 秒级直接 `pdflatex` 诊断，并把工作目录固定为 `article/aamas2027`。

两种输入都没有进入正文，也没有读到图片；日志在 AAMAS 类加载 `totpages.sty` 附近停止。因而当前证据不能支持“Figure 1/2 导致构建失败”，也不能支持任何页数结论。诊断源、完整日志和失败回执保存在：

`experiments/logs/n03_paper_current_source_build_probe_20261008_v2/`

canonical `artifacts/aamas2027/main.pdf` 没有修改，API/GPU 均为 0，科学 gate 不变。下一步应先用最小 AAMAS 文档复现 preamble/package 环境问题，再恢复主稿构建；不要继续盲目改图。
