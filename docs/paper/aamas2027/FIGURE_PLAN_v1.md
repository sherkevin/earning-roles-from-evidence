# AAMAS Figure Plan v1

更新时间：2026-10-02

这份文件先确定论文需要什么图，再决定每一张图的绘制版本。它不记录实验结果；图中的数值、曲线和“提升”结论必须等真实实验完成后才能进入正文。

## 设计目标

论文的中心命题不是“又一个 agent workflow”，而是：一个下游 agent 对已交付产出的情境化判断，经过责任归因后，成为下一次执行前可读取的角色证据，并由后续未见结果检验其是否真正改变了角色分配。图稿必须让审稿人沿着这条因果链阅读，而不是把它看成普通 reputation、静态 router 或 terminal reward。

统一视觉语义：蓝色表示未来选择/可更新状态，绿色表示责任安全的公开证据，橙色表示情境观察与判断，灰色表示冻结组件或对照；不用红绿作为唯一编码。所有图使用同一字体、箭头、圆角框、线宽和语义颜色，并且在灰度打印下仍能依靠编号、线型和文字区分。

## 正文图清单

### Figure 1 — Earning-roles loop（全宽 teaser / architecture）

**一句话目的：** 30 秒内说明“situated judgment 如何跨越责任门，改变未来 assignment，并由未来结果延迟回写”的闭环。

**结构：** 左到右、再由下方回到左方的六个编号阶段：

1. versioned producer delivery；
2. recipient use and judgment；
3. responsibility-safe public evidence；
4. future local assignment；
5. independently scored target outcome；
6. delayed selected-only credit。

上方虚线箭头表示 evidence 只进入更晚的 read cut，不能修改已经封存的 assignment。每个阶段只显示一个最小 ledger payload，避免把图变成 schema 表。

**版式：** `figure*`，约 `7.0in × 2.7–3.1in`。图题必须独立说明 delayed feedback 和 planned-field boundary；图中不得出现真实结果数字。

**参考范式：** Top-Conf Gallery 中高分 framework/architecture 图的浅层分组、编号阶段和单一阅读方向；尤其借鉴 SwiftSage 的多阶段流程分栏和 Online Stabilization 的“冻结/在线”视觉区分，但不复制其领域图标或文字。

### Figure 2 — Evidence-to-role state（全宽 method schematic）

**一句话目的：** 展开 Figure 1 中“公开证据如何进入 selector”的内部结构，明确 private execution、public projection、responsibility gate、local state 和 updater 的边界。

**结构：** 三个横向泳道：

- **Episode lane（橙色）：** producer artifact → recipient action/judgment → terminal outcome；
- **Evidence lane（绿色）：** typed projection → ownership/UNKNOWN gate → versioned evidence row → arrival watermark；
- **Decision lane（蓝色）：** local candidate menu/read-cut → selection probability → sealed assignment → later outcome → selected-only update。

右侧放一个小的 state box，显示 `state_{t+1}=Update(state_t,e_t,y_{t+1})` 的接口关系，而不承诺具体 backbone。用灰色虚线框标示 frozen encoder/strong baselines 的可替换位置。

**版式：** `figure*`，约 `7.0in × 2.4–2.8in`。这是方法图，不放 benchmark 名称和结果数。

**参考范式：** Gallery 的 SAM 式多面板分解和 Agent Planning with World Knowledge Model 的“模块—数据流—输出”层次；每个泳道只表达一种语义。

### Figure 3 — Event-time and responsibility boundary（单栏 protocol timeline）

**一句话目的：** 证明“先观察/发布，再选择/封存，最后才有目标结果”的时序，解释 late、duplicate、UNKNOWN 为什么不能更新既有决策。

**结构：** 六个事件节点按时间排列：source selection → recipient judgment → evidence publication → future selection → target outcome → delayed credit；一条虚线回到 later read cut。节点旁只标 `t`, `t+d`, `t+1` 等相对时间，不放具体 wall-clock。

**版式：** 单栏 `figure`，约 `3.35in × 1.6–1.9in`，文字保持 8–9pt，caption 负责解释责任门与不可见信息。

**参考范式：** Gallery 中 online-learning/temporal pipeline 图的上下双行时间轴和虚线 delayed path；保持一条主时间方向，避免交叉箭头。

### Figure 4 — Benchmark, baseline, and result endpoints（全宽 experiment map）

**一句话目的：** 让审稿人看清 ArtifactRole 是主科学轨道、PeerSelect 是机制副轨道，所有 arm 在同一信息/机会/成本合同下进入四个 RQ，而不是把两个 benchmark 的分数混在一起。

**结构：** 三个面板：`tracks` → `matched policies` → `RQ/endpoints`。左侧列 ArtifactRole 与 PeerSelect，中间列 uniform/no-update/raw acceptance/terminal-only/trust-bandit/pooled/RARE，右侧列 information、assignment、latency/cost、safety/drift。底部注释统一 candidate menu、lawful feedback schedule、task opportunity 和 complete-cost budget。

**版式：** `figure*`，约 `7.0in × 2.2–2.6in`。在没有结果前只画实验映射；有结果后再在同一图位替换为结果面板，避免提前画没有数据的曲线。

**参考范式：** Gallery 的 framework map 和 multi-panel benchmark overview；使用三栏浅底色而非复杂网络图。

## 不放入正文的图

- 不绘制“自进化成功”的结果曲线，直到 benchmark、baseline parity、独立 history 和真实结果全部通过验收。
- 不绘制一个伪造的 backbone 结构图；最终 representation/updater 仍由瓶颈诊断决定。
- 不把 recipient integration 与 producer defect 画成同一条因果箭头；责任边界必须可见。
- 不把 ArtifactRole 与 PeerSelect 合并成单一分数图。

## 版本和评审流程

- 当前已存在的 `article/aamas2027/figures/*.pdf` 作为 **v0 baseline** 保留。
- 每轮输出放入 `article/aamas2027/figures/versions/vN/`，同时保存生成脚本、自然语言结构说明、PDF/SVG 和评审报告；不覆盖历史版本。
- 每轮至少经过两个视角：故事线/因果审查和视觉/版式审查。评审需要检查 one-sentence test、30-second test、颜色/灰度、文字尺寸、caption 自洽和是否引入未经验证的科学主张。
- 选定版本后才替换正文引用，并重新运行 AAMAS 编译、`git diff --check` 和逐页目视检查。
