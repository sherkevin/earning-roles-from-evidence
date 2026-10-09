# AAMAS Figure Plan v2 — superseded by v3

历史计划。当前唯一生效版本为 `FIGURE_PLAN_v3.md`（ADR 0048）。本文件保留当时的
设计与判断；其纸面/语义 PASS 已被同日 counteraudit 收窄，不能作为当前通过证据。

更新时间：2026-10-07（v30、v32、v34 AI 底图 + 嵌入字体图组晋升为正文候选）

本版本吸收了故事线审查和视觉审查。v1 保留为历史计划；本文件是当前有效的正文图配置。

## 当前正文配置

1. **Figure 1 — Earning-roles loop**：全宽连续叙事主轴，当前资产为 `article/aamas2027/figures/overview.pdf`，对应 v29 AI 底图 + v30 嵌入字体生产层。它以对象化的 peer context、artifact、recipient use、judgment、role evidence、read cut、sealed assignment 和 later outcome 讲清闭环，阶段标签和正文配色已同步。
2. **Figure 2 — Evidence-to-role state**：全宽开放三泳道方法图，当前资产为 `article/aamas2027/figures/method_state.pdf`，对应 v31 AI 底图 + v32 嵌入字体生产层。彩色竖线和水平规则取代大色块，三条泳道分别显示 episode、public evidence、local decision 的边界，并统一使用 v28 的对象化 glyph。
3. **Figure 3 — Benchmark/baseline experiment map**：全宽开放实验结构图，当前资产为 `article/aamas2027/figures/experiment_map.pdf`，对应 v33 AI 底图 + v34 嵌入字体生产层。三个开放列区分 ArtifactRole/PeerSelect 轨道、政策臂和 RQ1–RQ4 终点；endpoint glyph 与前两图统一。

独立事件时间线仍保存在 `figures/timeline.pdf` 及版本目录中，作为协议图候选；在当前 8 页正文预算下不单独占用主文图位，因为 Figure 2 已经显式标出 read cut、sealed assignment、after-seal outcome 和 delayed update。若正文页数或审稿反馈允许，timeline 可作为 Figure 2 的 panel 或 supplementary 图恢复。

## Figure 2 的方法信息

Figure 2 需要回答审稿人的核心问题：判断如何成为角色证据，而不是普通 retrospective score。三条泳道分别表示：

- **Episode**：producer artifact、recipient action/judgment、after-seal target outcome；
- **Public evidence**：typed projection、ownership/UNKNOWN gate、versioned row/watermark；
- **Local decision**：local peers、read-cut state、sealed assignment、selected-only update。

跨泳道箭头只表示合法的数据关系：判断进入 projection，eligible public rows 进入 read-cut state，after-seal outcome 进入 matching opportunity。Representation/updater 画成可替换接口，不画成已确定的 backbone。
selected-only update 的回写箭头必须落在 **future read-cut state**；它不能回写已经 sealed 的 assignment。当前实现与版本快照为 `v7_future_target_semantics_20261002`。
recipient judgment 到 target outcome 是灰色虚线的 **after seal** 时间关系，不表示判断直接导致结果；目标结果只能在 assignment 封存后到达。

## 验收要求

- 一句话测试：只看图和 caption，能说出“recipient judgment → responsibility gate → public evidence → later assignment → unseen outcome → delayed credit”。
- 30 秒测试：能区分 observed episode、public state、future decision 和 delayed feedback。
- 版式测试：全宽图约 7in，嵌入 TrueType，灰度仍可读，正文标签不小于约 7pt；不出现越界、交叉穿框或未经验证数字。当前图组以 AI textless raster base + 可见标签的嵌入式 Arial Bold TrueType 层生产；`pdffonts`、纸面缩放、灰度与正文版心检查均已通过。本轮仍是内部候选，最终独立审查与投稿资产冻结尚未完成。
- 版本测试：v0、v1、v2、v3、v4、v5、v6、v7 的 PDF、脚本和评审记录全部保留，不能覆盖历史版本。

本轮及前轮 AI 版本和提示词保存在 `article/aamas2027/figures/ai_versions/` 下的 v18–v34 目录。当前正文候选是 v30、v32、v34；v28、v23、v26 的栅格候选与 v29、v31、v33 的 textless AI 底图保留；v27、v22、v24 及更早版本保留为可回退的中间候选。样例库风格审查见 `GALLERY_FIGURE_STYLE_AUDIT_20261006.md`。AI 工具的模型标识未披露，不能把这些资产标注为 image2.5 结果。

当前图组质量审查见 [`20261006_figure_quality_audit_v27_v22_v24.md`](../../coordination/task_reports/20261006_figure_quality_audit_v27_v22_v24.md)。可见字体门已由 v30/v32/v34 关闭；最终独立审查与投稿资产冻结前，三张图仍是内部候选。

长期 AI 重绘目标的最新候选为 Figure 1 v30、Figure 2 v32、Figure 3 v34；三张图都保留 AI 生成的
textless base，只通过 LuaLaTeX 添加短标签。`pdffonts` 证明全部可见标签使用嵌入式 Arial Bold
TrueType，`pdfimages` 证明 AI base 仍保留；真实正文构建保持 10 页总页数、8 页正文、参考文献第 9
页起、引用解析、0 overfull。候选生成、完整 prompt、SHA-256、灰度和版心 receipt 见
[`20261007_ai_figure_production_gate_v30_v32_v34.md`](../../coordination/task_reports/20261007_ai_figure_production_gate_v30_v32_v34.md)
及 `experiments/logs/figure_ai_long_goal_round_20261007_v30_v32_v34/receipt.json`。最终独立质量审查仍开放，
不能把局部生产门通过写成科学投稿通过。

## 结果图预留

真实实验通过 benchmark、baseline parity、独立 histories 和 complete-cost 资格门后，才绘制 Figure 4：quality--cost utility 与 online latency/forgetting 的结果图。结果图必须绑定 root、seed、policy、完整成本和 stream-level interval；如果结果是 null 或 trade-off，就按事实绘制。
