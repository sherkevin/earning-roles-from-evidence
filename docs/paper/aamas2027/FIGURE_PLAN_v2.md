# AAMAS Figure Plan v2 — active

更新时间：2026-10-06（v27、v22、v24 AI 图组晋升）

本版本吸收了故事线审查和视觉审查。v1 保留为历史计划；本文件是当前有效的正文图配置。

## 当前正文配置

1. **Figure 1 — Earning-roles loop**：全宽连续叙事主轴，当前资产为 `article/aamas2027/figures/overview.pdf`，对应 AI 版本 v27。它以对象化的 producer、artifact、recipient use、judgment 和 role ledger 讲清闭环，阶段标签和正文配色已同步。
2. **Figure 2 — Evidence-to-role state**：全宽开放三泳道方法图，当前资产为 `article/aamas2027/figures/method_state.pdf`，对应 AI 版本 v22。彩色竖线和水平规则取代大色块，三条泳道分别显示 episode、public evidence、local decision 的边界。
3. **Figure 3 — Benchmark/baseline experiment map**：全宽开放实验结构图，当前资产为 `article/aamas2027/figures/experiment_map.pdf`，对应 AI 版本 v24。三个开放列区分 ArtifactRole/PeerSelect 轨道、政策臂和 RQ1–RQ4 终点；policy label 不再包在卡片中。

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
- 版式测试：全宽图约 7in，嵌入 TrueType，灰度仍可读，正文标签不小于约 7pt；不出现越界、交叉穿框或未经验证数字。当前 AI 图组仅通过版心/溢出检查，因其仍是单张 JPEG 栅格图，**尚未通过 TrueType/矢量生产门**。
- 版本测试：v0、v1、v2、v3、v4、v5、v6、v7 的 PDF、脚本和评审记录全部保留，不能覆盖历史版本。

本轮及前轮 AI 版本和提示词保存在 `article/aamas2027/figures/ai_versions/` 下的 v18–v27 目录。当前正文晋升的是 v27、v22、v24；v19、v20、v21、v23、v25、v26 保留为可回退的中间候选。样例库风格审查见 `GALLERY_FIGURE_STYLE_AUDIT_20261006.md`。AI 工具的模型标识未披露，不能把这些资产标注为 image2.5 结果。

当前图组质量审查见 [`20261006_figure_quality_audit_v27_v22_v24.md`](../../coordination/task_reports/20261006_figure_quality_audit_v27_v22_v24.md)。在矢量/字体门关闭前，三张图是内部候选，不是最终投稿图。

## 结果图预留

真实实验通过 benchmark、baseline parity、独立 histories 和 complete-cost 资格门后，才绘制 Figure 4：quality--cost utility 与 online latency/forgetting 的结果图。结果图必须绑定 root、seed、policy、完整成本和 stream-level interval；如果结果是 null 或 trade-off，就按事实绘制。
