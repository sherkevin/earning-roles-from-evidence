# Task report — gallery-audited Figure 1 round v25–v27 (2026-10-06)

状态：`PARTIAL`（图形表达门通过；科学证据门仍开放）

## 目标对应

本任务对应故事线标准中的 Figure 1 叙事主张、写作标准中的 30 秒理解测试，以及图形
标准中的“对象化表达、短标签、单一主轴、最小视觉噪音”。没有修改 Goal 或降低科学标准。

## 样例库审查

直接读取本地 `topconf-paper-figure-gallery`，查看了 CollabLLM（ICML 2025 oral/best）、
DPO（NeurIPS 2023 honorable）和 VideoPoet（ICML 2024 oral/best）。共同规律是：
用具体对象讲一个动作，分组服务于语义，连接线承担叙事，文本只作短锚点，颜色有固定职责。
详细记录见 `docs/paper/aamas2027/GALLERY_FIGURE_STYLE_AUDIT_20261006.md`。

## 冻结与操作

- v25 以 v19 和样例库图作为参考；v26 以 v25 为输入；v27 以 v26 为输入。
- 每次编辑的提示词、输入/输出 PNG、PDF 和哈希均保存在对应版本目录。
- 本轮没有调用 LLM/API、GPU 或 Nebula；使用 Codex 内置 image-generation tool，之后用
  `sips` 将 PNG 转为论文 PDF。

## 结果

- v25：加入 producer、artifact、recipient use、judgment、ledger、quality/cost 等对象，
  但背景分组仍偏卡片化，中心事件偏小。
- v26：移除大块背景卡片，形成连续开放主轴；正文缩放后小标签偏小。
- v27：收紧空白并放大中央事件和阶段标签，作为当前 Figure 1。

使用 v27/v22/v24 图组构建：`article/aamas2027/build/figure_set_v27_v22_v24_review_20261006/main.pdf`。
结果为正文 8 页、参考文献从第 9 页开始、引用解析、`overfull_boxes=0`。同时修正主稿
Figure 1 caption，使其描述当前蓝/橙/绿/紫配色。

## 标准对照

- 已满足：样例库溯源、风格规则落文档、对象化主轴、版本可回退、纸面版心验证、图文配色一致。
- 部分满足：AI 栅格图的字体仍需最终投稿 PDF 和打印尺寸再核验；视觉相似不等于科学质量。
- 未满足/不适用：benchmark 资格、baseline parity、真实结果、方法效果和科学投稿门。

## 下一步

在没有新的具体视觉缺陷前不继续盲目生成 v28；当前回到 benchmark/baseline 和科学证据
主线。若机制语义变化，只对 v27 做定点编辑。

`goal_change_requested=false`
