# 2026-10-04 图稿参照图复核与问题定位

## 目的

本次只复核“投稿参考 best paper 架构/框架图在哪里，以及当前图为什么显得不够像顶会论文图”。不修改正文图稿，不把视觉问题误判成需要继续堆文字或装饰的问题。

## 已定位的主参照

最匹配当前论文 Figure 1 的参照是 ICML 2025 Best Paper：

- 论文：*CollabLLM: From Passive Responders to Active Collaborators*；
- venue/year：ICML 2025；
- gallery id：`icml2025-0242`；
- gallery pattern：`framework`；
- gallery tier/award：`oral` / `best`；
- 本地图像：`/Users/jingwu/Documents/Codex/2026-09-27/new-chat/topconf-paper-figure-gallery/images/icml/final/icml2025-0242.jpg`；
- gallery metadata：`/Users/jingwu/Documents/Codex/2026-09-27/new-chat/topconf-paper-figure-gallery/data/figures.json`；
- 论文页面：[PMLR 页面](https://proceedings.mlr.press/v267/wu25i.html)；
- PDF 原始地址：[PMLR raw PDF](https://raw.githubusercontent.com/mlresearch/v267/main/assets/wu25i/wu25i.pdf)；
- PDF 第 1 页 Figure 1：`COLLABLLM Framework`；
- 本次核验 PDF SHA-256：`4ab60e94f9d644efa742fed7ed977dba93beec4f35e1bf3ba432c3498c9ebe60`。

这不是“内部模型层结构”参照，而是与我们最接近的 **best-paper 级系统框架图**。它对应的是我们的 Figure 1；若要画内部状态/更新机制，还需要另找 architecture 级参照，不能把 framework 图直接当作方法细节图。

## 参照图的可复用骨架

CollabLLM Figure 1 的有效性来自结构，而不是插画：

1. 画面只有一个主阅读方向：左侧 context，右侧 response/policy，中间是唯一的核心创新模块；
2. 中央模块使用一个大而浅的虚线容器，把方法的新增机制包起来，读者一眼知道“论文到底新在哪里”；
3. 顶层只有四个带编号的动作：context、response、simulation、reward；编号和箭头共同建立阅读顺序；
4. 外部参与者、输入输出、训练/更新对象各自处在清晰的层级，不把所有概念放进同一排等权卡片；
5. 文字只标注 artifact、state、reward、policy 等可追踪对象，解释放在 caption；
6. 颜色只承担语义分组，箭头、边界、编号和文字同时提供冗余编码；
7. 闭环不是把六个步骤排成环，而是明确“什么进入核心模块、核心模块改变什么、结果回到哪里”。

## 与当前三张图的直接对照

当前文件：

- `article/aamas2027/figures/overview.pdf`；
- `article/aamas2027/figures/method_state.pdf`；
- `article/aamas2027/figures/experiment_map.pdf`。

### Figure 1 `overview.pdf`

它的信息合同是正确的，但视觉语法仍是“六个等权流程卡片”：每个卡片的标题、正文和 ledger 字段占据相近权重，读者看不出哪个模块是核心机制；外围虚线把画面包成一个大框，却没有一个中心方法容器。结果是它更像协议清单或产品流程图，而不是论文的核心发现图。

具体缺口：

- producer、recipient、local selector 没有成为可见的角色层；
- `typed evidence → read-cut state → sealed assignment` 没有在 Figure 1 中形成一个中心机制块；
- 六个阶段的文字偏多，图承担了本应由 caption 和正文承担的解释；
- 外围反馈虚线表达了“回到后续 read cut”，但视觉重心仍停留在卡片排列，未突出“证据如何改变未来责任”。

### Figure 2 `method_state.pdf`

它试图补足方法内部结构，但把 episode、evidence、decision、after-seal outcome、future read cut 放在三条泳道和多条交叉虚线中，导致阅读路径同时存在多条：横向主链、斜向责任投影、右上 outcome 回落、底部 delayed update。信息是全的，层次却不够强；这正是“工程协议图”而不是“方法架构图”的观感来源。

### Figure 3 `experiment_map.pdf`

它适合作为实验地图，但不能承担 Figure 1 的说服任务。`tracks → matched policies → RQ/endpoints` 是目录式映射，缺少一个明显的“核心比较对象”和一个示例 episode，因此不会产生 best-paper 图常见的“一眼理解问题与解决方式”的效果。

## 结论

用户对当前图稿“显得垃圾”的判断有客观依据，但问题不是颜色不够漂亮，也不是再加图标。根因是：当前 Figure 1 把所有阶段画成同等重要的流程节点，没有像 best-paper framework 图那样把一个核心机制置于中央并围绕它组织输入、输出和闭环；当前 Figure 2 又把所有协议约束同时暴露在一张图中，造成交叉关系过多。

下一轮绘图的必要改变是结构性改变：

1. Figure 1 改成 `context / situated episode → central Evidence-to-Role mechanism → future assignment / later outcome` 的单一骨架；
2. 中央机制用一个视觉上占主导的浅色容器，内部只放三步：`judgment → responsibility gate → public role state`；
3. 把 delayed credit 画成一条带标签的外部回路，明确它更新 future read cut，而不是把六个节点都围起来；
4. producer、recipient、selector 用小型角色标签标出，避免靠读者从正文猜身份；
5. 详细的 ownership/UNKNOWN、字段和实验 arm 移到 Figure 2/3 及 caption，不在 Figure 1 争夺视觉重心。

本报告只完成参照定位和问题诊断。未把任何候选新图替换进主稿；现有 v0–v7 历史版本继续保留。

## v8 候选的第一次实现

根据上述诊断生成了隔离候选：

- 源脚本：`scripts/build_aamas_figure_v8_candidate.py`；
- 候选目录：`article/aamas2027/figures/versions/v8_collabllm_framework_20261004/`；
- 输出：`overview.pdf`、`overview.png`、同目录 `README.md`；
- 当前状态：候选，未被 `main.tex` 引用。

第一次渲染发现右侧 selector 的角色标签发生重叠，已在同一候选版本内修复，并重新检查：

- 右侧局部 peer menu 的 A/B/C 标签不再与说明文字重叠；
- `evidence → decision` 标签移到中央机制上方，避免压住 selector 标题；
- PDF 字体改为嵌入 CID TrueType，避免原脚本的 Type 3 字体问题；
- 未修改活动图、主稿页数或任何实验结论。

这一版仍需独立审查员复核后，才能决定是否继续做 v9 或保留 v8。候选图的目的只是验证“中央机制容器”是否比六卡片流程更能承载我们的故事，不代表方法或结果已被验证。

## 独立审查结果

Codex 独立审查员在只看候选图、PNG/PDF 和 CollabLLM 参照图后给出 **8.2/10，建议保留，不返工**：

| 维度 | 分数 |
|---|---:|
| 30 秒可读性 | 8.8 |
| 核心机制视觉中心 | 8.5 |
| 单一阅读方向 | 8.3 |
| 角色/责任语义 | 7.5 |
| 时序/延迟反馈 | 8.8 |
| AAMAS 正文可读性 | 7.8 |
| 论文图而非流程图 | 8.0 |

审查员指出的局部问题已经在当前候选源中修正：`ownership?` 改为 `producer-owned? / UNKNOWN if ambiguous`，`path diff` 改为 `changed paths`，`evidence row / watermark` 改为 `versioned evidence + watermark`，并在 Observe 框中显式写出 `Recipient use`。另外，延迟反馈箭头已经改为从 later outcome 回到 selector 内的 `future read cut`，不再回到中央 evidence 容器。

剩余限制是正文缩放后内部文字接近可读下限，因此不再向图中添加字段。v8 仍是候选，不自动替换主稿；若要进入正文，下一步只需要在 AAMAS 最终双栏尺寸下做一次打印大小检查和 caption 对齐。

最终 v8 PNG/PDF 的快速复核结论为 **PASS，约 8.6/10**。审查员未发现新的重叠或严重语义误读；责任语义约 8.7、时序约 8.8、正文可读性约 8.0。唯一非阻塞问题是 `future read cut` 标签靠近 selector 下边界，进入最终双栏尺寸时需要再做一次打印大小检查。中心容器下部的留白保留，因为它让核心机制成为视觉中心，而不是继续塞入字段。

## AI 生图 v1

按照用户要求，v1 不再使用 HTML/Matplotlib 作为最终视觉来源，而是使用内置 Codex image generation 工具生成位图候选。提示词和版本说明已保存在：

- [`prompt.md`](../../../article/aamas2027/figures/ai_versions/v1_collabllm_style_20261004/prompt.md)
- [`README.md`](../../../article/aamas2027/figures/ai_versions/v1_collabllm_style_20261004/README.md)
- [`overview_ai.png`](../../../article/aamas2027/figures/ai_versions/v1_collabllm_style_20261004/overview_ai.png)

v1 输出尺寸为 `2172 × 724`，宽高比约 `3:1`，SHA-256 为 `6ba51ff9aba2b737685a7989f40c5689b3fda4d5213d2fb6308c5f72d21deee3`。初步检查显示：

- 文本标签基本完整，未出现明显乱码；
- 中央 `EARNING ROLES` 机制容器成为主要视觉中心；
- `delivery → evidence → decision → after seal → later outcome → delayed credit → future read cut` 的方向可追踪；
- 颜色、编号和留白比程序绘制版本更接近参考 best-paper framework 图；
- 当前仍是位图候选，尚未替换主稿，也未宣称达到投稿图最终质量。

独立审查员复核后给出总体 **8.3/10**：文字准确性 9.0、箭头/时序 8.7、30 秒可读性 8.8、视觉质感 8.2、正文缩放可读性 7.4。结论是需要 v2，但只做生产质量修订，不改变结构和语义：不能把 PNG 直接放入论文，应将准确文字和布局转成 SVG/PDF 矢量版本，并稍微拉开 `future read cut` 与 selector 下边界及灰色箭头头部的距离。

## v2 与 v3 的迭代状态

v2 已按照“提高分辨率、拉开反馈标签间距”的提示词生成，但工具仍输出 `2172 × 724` 的 PNG；独立对比确认 v2 与 v1 没有可感知的印刷级改善，因此 v2 不作为论文资产保留，只作为失败迭代记录。

为了验证 AI 是否能直接解决小字问题，又生成了最后一次针对性 v3：只放大正文标签、减少中心空白、拉开 `future read cut` 与箭头，保持 v1 的全部文字和语义。v3 目录为：

- [`v3 prompt`](../../../article/aamas2027/figures/ai_versions/v3_large_type_20261004/prompt.md)
- [`v3 image`](../../../article/aamas2027/figures/ai_versions/v3_large_type_20261004/overview_ai.png)

v3 仍输出 `2172 × 724`，当前等待独立审查员检查是否产生新的局部伪影。原计划在默认生图通道上停止继续迭代；该计划已被用户随后要求“明确使用 image2.5”所覆盖。新的 v4 只通过显式模型 API 路由尝试，结果见下文；这不是修改故事线，而是核实指定生图模型是否真的可用。

独立复核已完成：v3 拒绝保留。虽然小字略有放大，但 `C` 圆圈内字形被破坏，C 下方出现橙色竖线，`future read cut` 覆盖 selector 下边框并压近灰色箭头；仍然是 `2172 × 724` RGB PNG。默认通道因此停止；后续只尝试用户指定的显式 image2.5 路由。

## v9 矢量生产候选

在不再调用图像模型的前提下，基于 v8 的精确矢量源制作了 v9：

- 源脚本：`scripts/build_aamas_figure_v9_vector_production.py`；
- 候选图：`article/aamas2027/figures/versions/v9_vector_production_20261004/overview.pdf`；
- 只做三类生产修复：增大必要正文、将 `UNKNOWN if ambiguous` 拆成可读的三行、把 `future read cut` 放回 selector 内部并让延迟箭头从 outcome 顶部返回；
- PDF 字体为嵌入 CID TrueType，未引用主稿。

v9 仍需一次独立审查和 AAMAS 双栏缩放检查后，才决定是否替换主稿 Figure 1。AI v1 保留为视觉风格底稿，v2/v3 保留为失败迭代记录；它们都不会直接进入论文。

独立审查已通过 v9：中心三模块无文字挤压，`future read cut` 位于 selector 内且避开 A/B/C 和边框，`delayed credit` 从 later outcome 顶部返回且不穿过 outcome 内容或中央 evidence。v9 因此被选为当前主稿 Figure 1；删除顶部总标题是有意的版式取舍，主句由图内底部说明和正文 caption 承担。v7/v8 以及 AI v1–v3 均保留在版本目录中，便于回退和比较。

## 主稿集成验证

已将 v9 复制为 `article/aamas2027/figures/overview.pdf` 并重新编译主稿。验证结果：主稿 7 页、正文内容最后页为第 7 页、引用解析通过、overfull box 为 0；主稿 PDF SHA-256 为 `e63545900e204e44f2d3ac581ec5874fb65cdb8babff62c5`。主稿仍保持 `submission_ready=false`，因为实验结果和科学投稿门尚未开放；本次只替换 Figure 1 的视觉资产。
## GPT Image 2.5 路由核查（2026-10-04）

用户随后明确要求直接使用最新的 image2.5，并禁止继续用 HTML 或 Python
绘图。此前的 AI v1–v3 使用的是内置默认生图通道，无法从返回结果证明具体
模型，因此不能把它们称为 GPT Image 2.5。

为满足该要求，新增了隔离版本
`article/aamas2027/figures/ai_versions/v4_gpt_image_2_5_edit_20261004/`，其中
保存了完整提示词、原生 multipart 请求脚本和每次失败响应。实际核查结果：

1. 捆绑 CLI 在本地 SDK 层因 `edit()` 不接受 `quality` 参数而失败，未发出
   网络请求；该错误保存在 `api_call.log`。
2. 直接调用已授权的内部 IdeaLab OpenAI 兼容入口，并明确传入
   `model=gpt-image-2.5`，服务返回 HTTP 400：
   `PRE-006: gpt-image-2.5模型的配置不存在`。
3. 随后的只读模型清单请求返回 HTTP 200，但仅列出
   `qwen3-coder-plus`，没有任何 image 模型。

因此 v4 没有生成图像，也没有被拿来评审或替换主稿。当前阻塞是服务端没有
可调用的 image2.5 配置，而不是提示词或图稿内容问题；在获得可用的
image2.5 端点/凭证前，不会把 gpt-image-2、内置未知模型或其他模型冒充为
image2.5。

## 内置生图工具 v5（2026-10-04）

用户要求在无法调用 IdeaLab image2.5 时，实际试用 Codex 内置生图工具。已
新增并保留：

- 提示词：`article/aamas2027/figures/ai_versions/v5_builtin_tool_revision_20261004/prompt.md`；
- 图像：`article/aamas2027/figures/ai_versions/v5_builtin_tool_revision_20261004/overview_builtin.png`；
- 尺寸：`2172 × 724`；
- SHA-256：`18300541e014e00f325239d41950e1dd5c330bc4931fadd1009ab7019dd42c85`。

该次调用真实返回图像，并已在对话中展示。工具只返回图像 URL 和
`output_hint`，没有模型名称，因此记录为“Codex 内置生图工具，模型未披露”，
不宣称它是 image2 或 image2.5。v5 没有替换主稿 Figure 1；它是新的视觉
候选，等待独立审查后再决定是否继续修改提示词。

## 样例库对比后的减法重构（v6）

v5 的核心问题不是清晰度，而是把方法说明塞进架构图：三步机制被写成多行
规则，导致流程和文字同等抢占视觉层级。对照已定位的 ICML 2025
CollabLLM best-paper framework 图后，确定 Figure 1 只保留四类对象和五个动作：

`DELIVER → USE → JUDGE → CREDIT → SELECT → OUTCOME`。

责任边界、字段、UNKNOWN 条件、版本水印和完整性规则移到正文与 caption；图中
只留下 `artifact`、`evidence`、`local peers`、`quality + cost` 这些能改变
阅读路径的对象。新增 v6 提示词：

`article/aamas2027/figures/ai_versions/v6_image2_5_minimal_flow_20261004/prompt.md`

该提示词要求 image2.5 从白底重新生成，不再以旧的密集图为布局输入，只把
一张 best-paper framework 图作为视觉语法参考。v6 目前是交给用户使用的提示词，
尚未生成图像，也没有替换主稿。

## 第二次样例库核对：为什么 v6 仍会显得过于简单

本次直接读取 gallery 的 `figures.json`（3516 条记录）并查看了多张高层级
framework/architecture 图，包括：

- ICML 2025 best-paper `CollabLLM`（`icml2025-0242`）；
- ICML 2025 oral `Multi-agent Architecture Search via Agentic Supernet`
  （`icml2025-0960`）；
- ICLR 2024 oral `Efficient Episodic Memory Utilization of Cooperative Multi-Agent
  Reinforcement Learning`（`iclr2024-0306`）；
- ICLR 2025 oral `From Exploration to Mastery`（`iclr2025-0758`）；
- NeurIPS 2023 oral `ToolkenGPT`（`neurips2023-1225`）。

这些样例的共同结构不是“少画几个框”，而是同时有四个层级：

1. **参与者与输入对象**：谁产生什么 artifact，谁接收什么 context；
2. **方法内部结构**：核心模块中还有可辨识的子模块、状态或中间表示；
3. **决策输出**：方法如何产生 policy、assignment、tool path 或下一步动作；
4. **闭环证据**：结果如何回到 state、reward、memory 或下一轮决策。

v5/v6 只有第一层的简化对象和第四层的一条回路，缺少第二、三层，所以看起来
像流程示意，而不是方法架构。问题不应通过增加解释性句子解决，而应通过增加
少量可视化的数据对象和模块边界解决。

## 下一版架构规格（暂不替换主稿）

下一版应恢复以下结构，但仍控制图内文字：

`local peer graph → situated delivery/use → judgment + path evidence → attribution gate → role ledger → sealed peer selection → later outcome`

其中：

- 左侧画 A/B/C 的局部 peer graph 与当前 task；
- 中央大容器内部画 artifact、recipient execution、judgment/path diff 三类
  中间对象，再经过 attribution gate 写入 versioned role ledger；
- 右侧画 role ledger 读切、assignment probability、sealed assignment 和
  exploration 分支；
- 底部画 later outcome 的延迟反馈，只回到 role ledger/selector state；
- 图中文字只用对象名和模块名，责任条件、UNKNOWN 规则、字段定义和训练细节
  放入 caption 与正文。

这会比 v6 更像样例库中的 architecture/framework 图，同时不把未经最终
方法锁定的公式或新原始概念硬塞进图中。旧版本继续保留，下一版需要独立审查
后才进入主稿。

## v9 原图定点编辑提示词（2026-10-05）

用户明确希望在现有架构图上直接编辑，而不是重新生成一张布局相近的图。为此
新增：

`article/aamas2027/figures/ai_versions/v9_image2_5_edit_original_20261005/prompt.md`

该提示词以用户提供的
`/Users/jingwu/Downloads/本地协作与角色账本流程图.png` 为编辑输入，要求保持
画布、布局、配色、字体、模块位置和未列出的文字不变，只做以下定点修正：

1. 将 `EARNING ROLES ENGINE` 改为 `EARNING ROLES PROTOCOL`，避免图中把尚未
   锁定的实现称为 engine；
2. 将 `LOCAL PEERS` 改为 `PEER CONTEXT`，保留 A/B/C/task 作为上下文，并把左侧
   内部连线降为灰色虚线。右侧 `PEER SELECTOR` 唯一承担候选集与选择决策，避免
   左右出现两个候选菜单；
3. 将 `accept / revise` 改为 `recipient signal`；
4. 增加 `path diff` 到 `ATTRIBUTION` 的独立灰色 `path evidence` 连线，并将
   `owned / unknown` 改为 `producer-owned / UNKNOWN`；
5. 在 `ROLE LEDGER` 加入微小的 `v_t` 版本标记，在 `STATE READ` 加入
   `read-cut`，在选择器到结果的连线附近加入 `assignment`；
6. 删除结果回写历史 `ROLE LEDGER` 的虚线，将其改为唯一指向 `STATE READ` 右下
   方、且与 `read-cut` 分离的 `future state` 标记，并标注 `delayed credit`，明确
   延迟反馈用于未来选择状态而不是改写历史证据；同时规定 `path evidence` 沿
   `JUDGMENT` 下方绕行后进入 `ATTRIBUTION`，不得穿越模块或主箭头。

v9 是编辑提示词，不是新的实验结果，也没有覆盖主稿 Figure 1。生成前保留原图
和全部历史版本；生成后需检查文字、箭头终点和原图布局是否被模型擅自改变。独立
审查给出的当前版本评分为：科学语义 8.0/10、顶会图结构 8.2/10、原图定点编辑
可执行性 6.3/10；因此 v9 适合作为受控编辑规格，不能把生成结果未经检查直接放入
正文。图注仍需解释 producer contract、ownership rule、selected-only delayed
credit 和 `recipient signal` 的精确定义。
