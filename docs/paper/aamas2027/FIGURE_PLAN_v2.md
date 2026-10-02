# AAMAS Figure Plan v2 — active

更新时间：2026-10-02（v7 语义修订）

本版本吸收了故事线审查和视觉审查。v1 保留为历史计划；本文件是当前有效的正文图配置。

## 当前正文配置

1. **Figure 1 — Earning-roles loop**：全宽 teaser，保留六阶段闭环。
2. **Figure 2 — Evidence-to-role state**：全宽方法图，新增三条泳道，显示 episode、public evidence、local decision 的边界。
3. **Figure 3 — Benchmark/baseline experiment map**：全宽实验结构图，区分 ArtifactRole 主轨与 PeerSelect 副轨。

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
- 版式测试：全宽图约 7in，嵌入 TrueType，灰度仍可读，正文标签不小于约 7pt；不出现越界、交叉穿框或未经验证数字。
- 版本测试：v0、v1、v2、v3、v4、v5、v6、v7 的 PDF、脚本和评审记录全部保留，不能覆盖历史版本。

## 结果图预留

真实实验通过 benchmark、baseline parity、独立 histories 和 complete-cost 资格门后，才绘制 Figure 4：quality--cost utility 与 online latency/forgetting 的结果图。结果图必须绑定 root、seed、policy、完整成本和 stream-level interval；如果结果是 null 或 trade-off，就按事实绘制。
