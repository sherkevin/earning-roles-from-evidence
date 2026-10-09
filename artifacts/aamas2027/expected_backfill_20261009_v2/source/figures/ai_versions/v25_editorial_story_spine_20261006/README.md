# Figure 1 v25 — editorial story spine

状态：历史候选，未晋升。

本版本是对样例库风格审查后的第一次叙事型重构。它借鉴了 CollabLLM/VideoPoet 等
顶会主图的视觉语法：用具体 agent、artifact、recipient action、ledger 和 outcome
作为视觉锚点，用阶段分组组织一个故事，而不是把每个模块单独框起来。

- 参考样例：本地 gallery 的 ICML 2025 oral/best CollabLLM、NeurIPS 2023 honorable
  DPO、ICML 2024 oral/best VideoPoet；具体审查记录见 `docs/paper/aamas2027/GALLERY_FIGURE_STYLE_AUDIT_20261006.md`。
- 输入：Figure 1 v19 与两张样例库图片。
- 工具：Codex 内置 image-generation tool；模型标识未披露，不标为 image2.5。
- 输出：`candidate_builtin.png`、`overview_v25.pdf`。
- PDF SHA-256：`f044a041ff2fe8bc55631a1fe38a8ed2509949394bf11a12339ce3d6b87172c4`。

v25 已解决“只有流程箭头、没有叙事对象”的问题，但版心预览显示背景分组仍有卡片感，
且中心事件偏小；后续 v26/v27 针对这两个问题定点修订。
