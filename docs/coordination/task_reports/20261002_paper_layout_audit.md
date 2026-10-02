# 2026-10-02 AAMAS 主稿排版与版式审计任务汇报

## 任务

核对当前 AAMAS 2027 官方投稿要求，检查主稿是否按官方模板编译，并为后续真实实验结果预留架构图、流程图、实验矩阵和结果表的位置。该任务只处理论文结构与排版，不把尚未完成的实验写成结果，也不修改三份科学验收标准。

## 官方要求核对

本次核对使用 AAMAS 2027 官方页面和项目中保存的官方模板副本：

- [Instructions for Authors](https://warwick.ac.uk/fac/sci/dcs/aamas2027/guidelines-and-policies/instructions/)
- [Call for Main Track Papers](https://warwick.ac.uk/fac/sci/dcs/aamas2027/calls/call-for-main-track/)
- [Reviewer Guidelines](https://warwick.ac.uk/fac/sci/dcs/aamas2027/calls/reviewer-guidelines/)
- [Q&A](https://warwick.ac.uk/fac/sci/dcs/aamas2027/guidelines-and-policies/qa/)
- `references/aamas/template/official/AAMAS_2027_sample.tex`
- `references/aamas/template/official/aamas.cls`

核对结果是：主赛道正文上限为 **8 页**，参考文献不计入该上限；官方没有 7 页硬上限。正文中的 appendix 仍计入 8 页，不能靠 appendix 绕过限制。论文须使用官方 LaTeX 模板并保持双盲；supplementary 可选且不能承载正文必需的核心证据。当前草稿保留 7 页作为自然排版结果，未通过空白或版式参数人为凑页。

官方页面还要求作者对生成式 AI 的使用进行披露并对论文内容负责。该要求会在投稿版的致谢/披露位置按最终作者信息处理；当前内部稿不打开 submission gate。

## 本次修改

- 在 `main.tex` 增加 `\submissionType{Research Paper Track}`，继续使用官方匿名类文件和既有 submission ID 配置。
- 用外部矢量 PDF 替代 TikZ，新增三个可重复生成的图：
  - Figure 1：situated delivery → recipient judgment → responsibility gate → future assignment → downstream outcome → delayed update 的闭环架构图；
  - Figure 2：publish、choose、use/rework、validate/update 的事件时序和责任边界图；
  - Figure 3：ArtifactRole/PeerSelect 两条实验轨道、同信息 baseline 和 RQ 的映射图。
- 每张非装饰图都有位于图下方的 caption 和 `\Description{}`；颜色同时使用灰度可区分的线型/标签语义。
- 新增 headline result table，预留 future quality、完整成本、quality--cost utility、assignment change、judgment calibration、update latency/state size、forgetting 和 UNKNOWN/false-attribution 等列；所有数值单元保持空白。
- 新增 trace table，按 source selection、recipient use、responsibility gate、evidence publication、future assignment 和 delayed credit 六阶段展示应审计的 protocol fields；它是待填的实验审计表，不是实验结果。
- 修正文中 benchmark 名称过长造成的 overfull hbox；避免把本地候选轨道写成已经冻结的公认 benchmark。
- 新增 `scripts/build_aamas_figures.py`，统一生成 `article/aamas2027/figures/{overview,timeline,experiment_map}.pdf`。

## 编译与检查

使用官方模板完成 LaTeX → BibTeX → LaTeX 重编译，并用 `scripts/build_aamas2027.py` 做 PDF 表面检查。最终主稿为：

- `article/aamas2027/build/main.pdf`：7 页，letter 页面，引用已解析；
- 无 `Overfull \\hbox` 或 `Overfull \\vbox`；保留模板本身的 underfull/balance 提示；
- 官方 `aamas.cls`、`.bst` 和 `by.pdf` 与保存的官方副本一致；
- `build/verification.json` 已记录页数、内容页上界、引用和 overfull 检查；
- Figure 1、Figure 2、Figure 3 已在生成的 PDF 页面中目视检查，图题位置、可读性和表图顺序正常。

主稿仍是内部 pre-results draft。空结果表、submission gate 关闭、benchmark/baseline scientific readiness 未改变；这次版式通过不等于论文已经有可投稿的效能证据。

## 对目标的影响

这一步关闭了“主稿没有足够位置承载实验和方法图”的排版风险，并把论文固定在官方 8 页约束内。它没有关闭三份科学验收文档中的 benchmark 权威性、baseline parity、实验执行或结果合理性门槛；下一步仍需先完成这些门槛，再把空表替换为经过审计的真实结果。
