# 2026-10-02 图稿确定与多轮迭代任务汇报

## 任务

根据当前故事线、三份论文验收标准、AAMAS 版式要求和本地 Top-Conf Figure Gallery，确定正文所需图稿，绘制多个版本，保存历史结果，并在故事线和视觉两个视角下独立审查后选出正文版本。

## 调研依据

直接检查了 `/Users/jingwu/Documents/Codex/2026-09-27/new-chat/topconf-paper-figure-gallery/data/figures.json` 及高分 framework、pipeline、architecture 样例。当前 gallery 有 3,516 张图，其中 framework 288、pipeline 400、architecture 523。可复用的规律是：单一阅读方向、浅层分面板、≤5 个语义色、箭头连接有名字的 artifact/state/assignment/outcome、灰度可读、caption 自洽；方法内部结构不能用普通流程图替代。

本轮还使用了两位独立 Codex 协作者：一位审查故事线与方法可证伪性，一位审查实际 PDF 的可读性、箭头语义、字体和版式。审查意见保存在：

- `docs/coordination/task_reports/20261002_figure_story_audit.md`
- `docs/coordination/task_reports/20261002_figure_visual_review_v1.md`

## 图稿决策

当前正文采用三张图：

1. **Figure 1 — Earning-roles loop**：全宽六阶段闭环，表达 delivery → recipient judgment → responsibility-safe evidence → future assignment → target outcome → delayed credit。
2. **Figure 2 — Evidence-to-role state**：全宽三泳道方法图，明确 episode、public evidence、local decision，以及 ownership/UNKNOWN gate、read-cut state、sealed assignment 和 selected-only update。
3. **Figure 3 — Benchmark/baseline experiment map**：全宽三栏图，区分 ArtifactRole 主轨、PeerSelect 机制副轨、matched policy arms 和四个 RQ。

独立事件时间线仍保留为 `figures/timeline.pdf` 和版本快照，但由于当前正文 8 页预算，暂不单独占用主文图位；Figure 2 已经在方法结构中显式呈现 read cut、after-seal outcome 和 delayed update。真实实验完成后再绘制 Figure 4 结果图，不提前画任何提升曲线。

活跃计划为 [`docs/paper/aamas2027/FIGURE_PLAN_v2.md`](../../paper/aamas2027/FIGURE_PLAN_v2.md)，入口为 [`FIGURE_PLAN.md`](../../paper/aamas2027/FIGURE_PLAN.md)。

## 版本迭代

所有历史版本保存在 `article/aamas2027/figures/versions/`，未覆盖旧文件：

- `v0_baseline_20261002`：原 7 页稿使用的三张图；
- `v1_feedback_target_and_fonts_20261002`：反馈终点和 TrueType 字体修复候选；
- `v2_outer_feedback_route_20261002`：反馈路径移到外侧；
- `v3_outer_right_grey_feedback_20261002`：反馈路径改为灰色虚线，从外侧进入 future assignment；
- `v4_method_state_added_20261002`：加入方法内部结构图；
- `v5_method_readability_20261002`：增大方法图正文标签、缩短长标题并把 after-seal 语义放入节点。
- `v6_update_to_future_read_cut_20261002`：根据故事线终审修正方法图的关键时序语义；selected-only update 的蓝色虚线现在真正回到 **future read cut**，不再指向已经封存的 assignment。
- `20261002_v1/`, `20261002_v2_candidate/`, `20261002_v3_candidate/`：独立协作者生成的未选中候选，保留 PDF 与说明供后续复核。

最终正文选择 v6 的方法图与 v3 的闭环/实验图视觉方案。所有 PDF 都由 `scripts/build_aamas_figures.py` 重新生成；`pdffonts` 已确认嵌入 CID TrueType，未使用 Type 3 字体。

## 排版验证

- Figure 1、Figure 2、Figure 3 在正文实际双栏页面逐页检查；图注位于图下，`\Description{}` 齐全，未出现越界或文字覆盖；
- 主稿保持 7 页，官方正文上限为 8 页；
- 最终编译使用官方 AAMAS class/bst/by.pdf，结果单元仍为空；
- TeX 官方 balance pass 曾报告 1.326pt 的最终页 vbox 舍入诊断。该值低于 1.5pt 的 `\\vfuzz` 仅警告阈值，不改变排版几何；没有可见裁切或溢出。更大的 overflow 仍会被编译检查拦截；
- `python3 scripts/check_aamas_documents.py --sync-gate --check-gate` 通过，科学 submission gate 仍关闭。

## 对目标的影响

这轮关闭了“核心方法没有可视化”和“反馈箭头语义与法律时序冲突”两个图稿风险。论文现在能分别展示故事闭环、方法内部状态和 benchmark/baseline 结构，同时保留了真实结果图的明确位置。它没有替代 benchmark authority、baseline parity、独立 live histories 或科学效能证据；这些门槛仍按 active Goal 执行。
