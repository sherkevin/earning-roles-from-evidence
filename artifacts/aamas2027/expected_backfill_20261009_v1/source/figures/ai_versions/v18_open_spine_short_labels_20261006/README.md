# Figure 1 v18 — open spine, short labels

状态：历史候选，未直接晋升。

本版本是在 v16 基础上的一次完整 AI 编辑。目标是把 Figure 1 从解释性卡片布局收敛为一条可读的因果主轴：situated delivery → recipient use/judgment → responsibility gate → public evidence/read cut → sealed assignment → later outcome → delayed selected-only feedback。

- 工具：Codex 内置 image-generation tool；服务端未披露模型标识，因此不把它标为 image2.5。
- 输入：`v16_open_spine_20261005/candidate_builtin.png`。
- 输出：`candidate_builtin.png`，1983×793，SHA-256 `f2f558e8fd49075b62fc888c3765dad5d5ba0c538d251e83c3f4af147dd22c26`。
- 通过项：单一开放主轴、短语义标签、UNKNOWN 仅审计分支、sealed assignment 之前的 read cut、延迟反馈只回到下一次 read cut。
- 遗留项：最左侧灰色 task 节点没有标签。该问题在 v19 以一次精确编辑修复；v18 保留用于回退和比较。

该候选只验证图形表达，不构成角色学习、benchmark 或方法效果证据。
