# 用户最新架构图复核记录（2026-10-05）

## 输入

用户提供的最新成图已归档为：

`article/aamas2027/figures/ai_versions/v10_image2_5_patch_20261005/input_latest.png`

SHA-256：
`046cc46c178e7311119fbce124eb19db88a57e2ac405d61436551bc526763c32`

该图不是主稿定稿，只是 v9 原图编辑提示词产生的候选结果。

## 已解决的问题

- 左卡已经改名为 `PEER CONTEXT`，不再和右侧 `PEER SELECTOR` 形成两个候选菜单；
- 中央容器已经改为 `EARNING ROLES PROTOCOL`；
- `recipient signal`、`producer-owned`、`UNKNOWN` 已正确出现；
- `path evidence` 已从 `path diff` 绕行进入 `ATTRIBUTION`，没有穿过
  `JUDGMENT` 模块；
- 主体模块层次、颜色体系、左到右流程和整体留白保持良好。

## 仍存在的硬问题

### P0：延迟反馈仍然错误地回写 ROLE LEDGER

图中仍保留一条灰色虚线，从 `OUTCOME` 底部绕回并以箭头结束在
`ROLE LEDGER` 下方。图中没有 `future state` 或 `delayed credit` 标签。
因此读者仍会把结果理解为直接改写历史角色证据，无法表达“延迟信号只影响
未来选择状态”的方法语义。这是投稿前必须修复的问题。

### P1：PEER CONTEXT 内仍有橙色 A→B 箭头

其他上下文连线已经是灰色虚线，但 A→B 仍是橙色有向边。它会被读成一个额外
的因果/执行路径，与中央 `PRODUCER → artifact → RECIPIENT` 流程重复，且没有
图例说明。应改为灰色虚线、无箭头的上下文边，或明确标记为当前交互；本项目
采用前者以保持图面干净。

### P1：三个状态标记未生成

`v_t`、`read-cut`、`assignment` 均未出现在图中。它们不是核心流程，但缺失后
版本化证据、读取切面和选择输出的语义只能依赖图注，降低了架构图自解释性。

## 质量判断

本版可作为视觉候选，不能直接放入正文。其主要问题不是画质，而是一个会改变
因果解释的反馈箭头。已创建只针对残留问题的补丁提示词：

`article/aamas2027/figures/ai_versions/v10_image2_5_patch_20261005/prompt.md`

补丁提示词要求：删除指向 `ROLE LEDGER` 的整条虚线；唯一新增指向
`STATE READ` 右下方 `future state` 标记的延迟反馈；消除左侧橙色 A→B 边；
补齐三个短标签。生成后必须逐字、逐箭头核验，任何一项失败都不能替换主稿图。

## v10 受控编辑候选

使用 v10 补丁提示词对归档输入执行了一次真实的图像编辑调用。输出归档为：

`article/aamas2027/figures/ai_versions/v10_image2_5_patch_20261005/candidate_builtin.png`

SHA-256：
`ecdcf6926e9fbfc8805640485c7b18cef32a36fbc7e63bd73c4b18a2ff7876e5`

调用工具为 Codex 内置生图工具，模型标识未披露，因此不将其称为 image2.5。

逐项核验结果：

- A→B 已变为无箭头灰色虚线上下文边；
- 旧的 `OUTCOME → ROLE LEDGER` 灰色回写线已删除；
- 新的灰色虚线指向 `STATE READ` 下方唯一的 `future state` 标记；
- `delayed credit`、`v_t`、`read-cut`、`assignment` 均出现且可读；
- `path evidence` 仍然绕过 `JUDGMENT` 后进入 `ATTRIBUTION`；
- 中央主流程、模块边界和已有标签保持不变。

因此，v10 候选已经通过当前的科学语义检查，可以作为主稿 Figure 1 的视觉
候选；但它仍是栅格图，正文定稿前应检查 PDF 缩放后的文字可读性，并在图注中
补充 producer contract、ownership、selected-only delayed credit 和
`recipient signal` 的定义。未经这些检查，不自动替换主稿中的矢量或高分辨率版本。

## 图注责任

即使补丁成功，图注仍需明确：`path evidence` 与 producer contract 和
ownership rule 共同决定 attribution；`delayed credit` 是 selected-only 的
延迟信号，只用于未来 selector state，不修改历史 ledger；`recipient signal`
是接收方对交付使用结果的判断信号，而非简单的二分类 accept/revise。

## v11 语义闭环与 v12 排版候选

针对 PDF 复核暴露的三处剩余歧义，新增 v11：

`article/aamas2027/figures/ai_versions/v11_semantic_patch_20261005/prompt.md`

v11 的真实编辑候选为 `candidate_builtin.png`，SHA-256 为：

`55693f03da04e177ab8262ac7bf51e265d69daed1211fddb3e2f55ad31e00156`

逐项检查确认：

- `future state` 通过 `next read` 短箭头连接到下一次 `STATE READ`；
- `explore` 成为候选菜单的探索输入，只有 `seal` 连接到 `assignment` 和
  `OUTCOME`；
- 绿色账本箭头只从 `producer-owned` 出发，`UNKNOWN` 没有进入账本的路径。

由于 v11 的原始栅格上下白边会把正文推到第 8 页，新增仅裁空白边的 v12：

`article/aamas2027/figures/ai_versions/v12_pdf_crop_20261005/candidate_cropped.png`

SHA-256：
`64a39b1f064ede8de502c3174aade0e2392d07b2a5528b6150c6dad6b4fbdb26`

临时双栏编译结果：7 页、0 个 overfull box、无未解析引用；渲染页面检查确认
图形、连线和标签未被裁掉。v12 是当前最佳候选；当时先保留为候选，等待独立
图表审查完成。

独立审查随后确认：原 active `overview.pdf` 仍是旧的 numbered method-state 图，
与已经同步的 Figure 1 图注和 `\Description` 不一致；这构成语义一致性 P0。因而
已将 v12 cropped PDF 晋升为 active：

`article/aamas2027/figures/overview.pdf`

active 文件与 v12 `overview_v12.pdf` 的 SHA-256 均为：

`666940c307a94a1694a3bfd585a72fead69e23923d3ab9ef9b466985fa59dca9`

旧 active 矢量图仍保存在
`article/aamas2027/figures/versions/v9_vector_production_20261004/overview.pdf`，
没有覆盖历史版本。

独立图表审查的最终结论为 P0=0、P1=2：语义闭环已经成立，剩余意见是把
`explore` 与候选菜单的关系在图注或局部图形中再说清楚，以及在最终印刷尺寸下
复核小标签的可读性。这两项不改变当前协议含义，也没有阻止 v12 晋升为 active。

## Active 主稿验证

主稿 `python3 scripts/build_aamas2027.py` 已重新运行。结果：

- `article/aamas2027/build/main.pdf`：7 页；
- 内容页数：7；
- 未解析引用：0；
- overfull box：0；
- PDF SHA-256：
  `b358a65ed0deac05e4d37118fa415b2f9378d6761c490d1a3c218ee51f36372b`。

因此，当前 active 图、图注和正文的时间语义已经同步；投稿 gate 仍保持关闭，
因为这是内部 pre-results 稿，科学结果尚未回填。
