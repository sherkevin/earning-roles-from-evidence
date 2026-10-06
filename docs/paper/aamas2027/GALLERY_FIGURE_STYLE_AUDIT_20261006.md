# Gallery figure style audit — 2026-10-06

本审查使用本地 `topconf-paper-figure-gallery`，不是凭印象评价。画廊收录 3,516 张
ICLR、ICML、NeurIPS、CVPR、ACL、AAAI 设计型主图，并对候选图做规则筛选和人工复核。
本轮重点查看三张与当前论文最相关的高等级样例：

| 样例 | 画廊条目 | 视觉模式 | 借鉴点 |
|---|---|---|---|
| CollabLLM | ICML 2025 oral/best，`images/icml/final/icml2025-0242.jpg` | framework | 用真实用户/agent/交互对象讲清闭环；中心机制有视觉重量，外围只作上下文 |
| DPO | NeurIPS 2023 honorable，`images/neurips/final/neurips2023-02.jpg` | conceptual | 左右或阶段对照服务于一个核心论点；标签短，颜色和区域职责明确 |
| VideoPoet | ICML 2024 oral/best，`images/icml/final/icml2024-1103.jpg` | pipeline | 连续主轴、对象化输入/输出、连接线承担叙事，避免每个节点都变成卡片 |

## 从样例提炼的可检验规则

1. **图先讲一个动作**：读者先看到“谁把什么交给谁、经过什么机制、产生什么后果”，
   再读模块名；图不是模块清单。
2. **只在语义需要处分组**：面板或背景色必须对应一个可解释的阶段/对照关系；每个小
   模块不再单独套一层框。
3. **文本是锚点而非正文**：使用短标签，解释放进 caption；标签层级应明显区分标题、阶段和对象。
4. **对象化表达**：agent、artifact、recipient action、ledger、outcome 用图形对象表示，
   而不是用更多句子描述。
5. **一条主轴、一条反馈路径**：主数据流只有一个方向；延迟反馈用一条独立的曲线/虚线，
   不穿越已经封存的状态。
6. **颜色有责任**：同一语义保持同一颜色，颜色数量受控，并用形状/线型冗余编码；颜色不
   单独承担科学结论。

## 对当前图组的应用

- v25 首次加入对象化叙事，但仍有大块背景卡片；因此不晋升。
- v26 移除背景卡片，形成连续开放主轴；版心标签偏小。
- v27 收紧空白并放大中央事件与标签；随后 v28 进一步去掉巨型标题，统一 peer/artifact/judgment/evidence/read-cut/seal/outcome glyph，作为 Figure 1 当前正文候选。
- Figure 2 v22 和 Figure 3 v24 已分别采用开放泳道和开放三列；随后 v23/v26 统一使用 v28 的对象化 glyph，作为当前正文候选。

这份审查只规定视觉表达质量，不把“像 best paper”当成科学贡献或录用保证。
