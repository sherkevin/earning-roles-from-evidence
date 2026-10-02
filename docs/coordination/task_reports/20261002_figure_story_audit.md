# 2026-10-02 图稿故事线与 Top-Conf Figure Gallery 独立审查

## 审查范围

本审查只检查论文图稿是否把故事线、方法边界和实验可证伪性讲清楚，不替实验填结果，也不修改主稿。检查对象是：

- `article/aamas2027/figures/overview.pdf`
- `article/aamas2027/figures/timeline.pdf`
- `article/aamas2027/figures/experiment_map.pdf`
- `article/aamas2027/main.tex` 中的图题、`\Description{}` 和图表位置；
- 本地 Top-Conf Figure Gallery（直接检查 `data/figures.json` 和高分图样例）。

Gallery 当前记录 3,516 张图，其中 `framework` 288 张、`pipeline` 400 张、`architecture` 523 张。其自身的模式定义把多智能体系统总览归为 `framework`，把端到端阶段数据流归为 `pipeline`，把模型内部模块与张量连接归为 `architecture`。这三个模式正好对应本项目的系统闭环、事件时序和在线状态更新三个不同叙事任务，不能用一张普通流程图代替全部任务。

## Gallery 得出的可复用规则

抽查高分 `framework`、`pipeline`、`architecture` 图后，稳定出现以下结构：

1. 图有一个明确的阅读方向，主路径只有一条；反馈或旁路用虚线并写清它改变的对象。
2. 每个面板只承担一个语义层：输入/观测、方法模块、输出/评价不能混在同一个大面板里。
3. 颜色表达语义，编号和文字同时表达语义；灰度打印时仍能区分阶段，不依赖红绿颜色。
4. 箭头连接的是可解释的对象（artifact、state、assignment、outcome），不是无标签的圆点。
5. 文字很少，但每个框都能回答“谁产生了什么、谁读取了什么、何时可读取”。细节放在 caption 或正文。
6. 内部结构图通常用 2--3 个浅层面板展开一个关键机制，而不是继续堆叠更多阶段框。
7. 图注可以独立说明输入、反馈和测量对象；图本身不放未验证的提升数字或结论性词语。

## 当前三张图的审查

### Figure 1：`overview.pdf`

**结论：故事线基本成立，作为 Figure 1 可用，但还不是最终的机制图。**

它已经表达了六个必要阶段：版本化交付、接收方判断、责任安全证据、未来分配、独立结果和延迟 credit；顶部虚线也说明反馈不能修改已经封存的 assignment。这正好对应论文的核心因果链。

仍有三个缺口：

- 没有显示“局部 peer 候选集/图结构”，读者还看不出这是局部选择问题，而是一般 workflow；
- 没有显示 public evidence 如何变成一个可读 state、selector 如何读取它、updater 在什么地方写回；
- producer、recipient、selector 的身份只隐含在文字中，缺少最小 actor 标记。

**保留内容：** 六阶段和橙/绿/蓝的语义层。
**下一版应补：** 在“future assignment”框中加入小型局部候选图，在“public role evidence”与“future assignment”之间加入 `read-cut state`，并在交付/判断/选择框顶端标出 producer、recipient、local selector。每个阶段仍只保留一个最小 ledger payload。

### Figure 2：`timeline.pdf`

**结论：时序边界清楚，适合作为 protocol figure；它不能代替内部方法架构图。**

上下两行的事件顺序和延迟路径适合解释 no-leakage 约束。当前顶部虚线从第一框上方穿过并回到发布位置，缩小后可能被误读为同步边；应把虚线旁的文字靠近它，并明确标注 `delayed evidence → later read cut`。如果版面紧张，可将这张图并入 Figure 2 的一个 panel，而不是单独占用一个主文图位。

图内字号应以最终 PDF 实际打印大小检查；当前若继续增加文字会使单栏图过密。不要把 wall-clock 数字、实验结果或模型名称放入该图。

### Figure 3：`experiment_map.pdf`

**结论：实验结构可读，但当前更像目录图，尚未充分证明 baseline parity。**

两条轨道、匹配 policy 和四个 RQ 的关系已经可见，适合留作实验总览。当前中间 policy 列与右侧 RQ 的映射是概念性的，读者看不出每个 arm 读取哪些字段、哪些 arm 只改变 update、哪些 arm 只改变 evidence。下一版可在中间列底部加入一个小的统一合同条带：`same menu | same read cut | same opportunity | same complete cost`，并用简短标记区分 `history`, `judgment`, `terminal`, `update` 四种信息条件。

不要在这张图里放空的百分比、箭头式“提升”或模拟结果曲线；实验矩阵和数值结果应由表格及真实运行图承担。

## 建议的最终正文图清单

### F1：Earning-roles loop（必须）

一句话目的：让读者在 30 秒内看到 situated judgment 经过责任门变成 evidence，改变下一次 assignment，并由未见的后续结果延迟检验。

版式：全宽 framework/teaser；六阶段浅层闭环；只保留最小 ledger 字段。
审查门槛：一个单向阅读主路径、一个明确的 delayed edge、actor 身份可见、无结果数字。

### F2：Evidence-to-role state（必须，当前缺失）

一句话目的：说明核心方法到底怎样把接收方判断投影成 typed evidence、经过 ownership/UNKNOWN gate、进入局部 selector state，并在未来结果到达后只更新对应 responsibility opportunity。

推荐画成三个泳道：

1. `Episode`：producer artifact → recipient action/judgment；
2. `Evidence`：typed projection → responsibility gate → versioned row/read watermark；
3. `Decision`：local candidate menu/read cut → sealed assignment → selected-only delayed update。

右侧放最小 state/update 接口，标出可替换的 representation/updater 位置，但不要画成已经确定的 backbone。该图是本文方法贡献的主要视觉证据，优先级高于单独的 timeline 图。

### F3：Event-time and responsibility boundary（建议保留，版面不足时并入 F2）

一句话目的：证明 future outcome 在 assignment seal 时不可见，late/duplicate/UNKNOWN 不能回写既有决策。

版式：单栏上下双行时间轴，六节点，虚线只回到 later read cut。它主要服务于 protocol validity 和审稿人的 no-leakage 检查。

### F4：Benchmark and baseline map（必须）

一句话目的：说明 ArtifactRole 是主科学轨道，PeerSelect 是机制副轨道；所有 policy 在相同 menu、feedback schedule、opportunity 和 complete-cost contract 下比较。

版式：全宽三栏 `tracks → matched information arms → RQ/endpoints`。中间列要显示信息条件标签，底部合同条带固定出现。两条轨道不能合并成一个分数。

### F5：真实结果图（实验通过后必须）

目前只预留图位，不填任何数字。最终建议采用一个两面板结果图：

- (a) future quality--complete-cost utility 的 stream-level 点估计和区间；
- (b) online update latency/state bytes 与 forgetting/drift recovery 的关系。

每个点必须绑定 root、seed、policy 和完整成本；不使用只展示最好 seed 的曲线，也不把源 judgment 分数替代 future assignment outcome。若结果不能支持闭环收益，F5 应如实展示 trade-off 或 null，而不是绘制“自进化成功”视觉。

## 不能出现在图里的内容

- 未经真实运行支持的提升百分比、胜率、收敛曲线或“更智能”等结论性文字；
- 未确定的 backbone、模型规模、训练算法或伪造的内部层结构；
- 将 recipient integration 直接画成 producer defect 的箭头；
- 把 ArtifactRole 和 PeerSelect 的指标合成单一总分；
- 将 evidence publication 画成即时 policy update，或让 target outcome 反向进入已封存 assignment；
- 依赖红/绿颜色的唯一编码、过多小字、无标签交叉箭头、截图式 UI 和装饰性 agent 图标；
- 在图内写“planned”, “not a result”, “internal draft”等提交过程文字。边界说明放 caption 或正文。

## 版本与评审要求

当前三张 PDF 作为 `v0` 基线保留。每轮绘制必须同时保存：源脚本或 HTML、自然语言结构说明、SVG/PDF、渲染 PNG 和评审记录，不覆盖旧版本。每一轮至少做以下三项检查：

1. **故事线审查：** 只看图和图题，能否复述 delivery → judgment → attribution → assignment → outcome → credit；
2. **方法审查：** 是否能定位 read cut、责任门、局部候选集、selected-only update 和 UNKNOWN；
3. **版式审查：** AAMAS 双栏实际尺寸下文字可读、图注位于图下、灰度可分、无越界/裁切/不可解释箭头。

选择最终版本前保留 v0、v1、v2 的差异和拒绝理由；只有通过三项检查的版本才替换 `main.tex` 中的图引用。

## 审查结论

现有三图已经关闭“正文没有图”的排版风险，但尚未关闭“核心方法不可视化”的审稿风险。下一轮最有回报的动作不是继续装饰 Figure 1，而是绘制并评审 F2 `Evidence-to-role state`；若页数不允许四张独立图，应将 timeline 作为 F2 的 panel 保留，同时维持 F1 和 F4。真实结果到来后再绘制 F5，并把所有结果图绑定到冻结 manifest。

## 当前版本评分（仅图稿验收，不是论文录用概率）

评分维度为：故事线可辨识度、方法边界可验证性、实验设计可读性、AAMAS 双栏可读性；每项 0--2 分，共 8 分。

|对象|故事线|方法边界|实验可读性|版式|合计|判断|
|---|---:|---:|---:|---:|---:|---|
|Figure 1 overview v0|2|1|0|2|5/8|可作 teaser，补局部候选集和 actor 标签|
|Figure 2 timeline v0|1|2|0|2|5/8|可作 protocol 图，不能承担方法架构|
|Figure 3 experiment map v0|1|1|2|2|6/8|可作实验总览，需强化 information/cost parity|
|完整图组（当前）|2|1|2|2|7/8|缺少 F2，暂不能称为方法视觉闭环|

只有新增 F2 并通过“只看图和图题复述方法”的审查，完整图组才可进入正文最终版候选。该分数不评价实验效果，也不替代 benchmark、baseline 或真实结果验收。
