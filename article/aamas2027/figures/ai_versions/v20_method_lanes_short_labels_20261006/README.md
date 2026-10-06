# Figure 2 v20 — three method lanes

状态：当前 Figure 2 候选，已晋升到正文资产 `article/aamas2027/figures/method_state.pdf`。

本版本把方法图改为三条开放泳道，分别隔离 episode、public evidence 和 local decision。图中只保留模块名和关系标签，不用段落卡片解释机制。

- 工具：Codex 内置 image-generation tool；服务端未披露模型标识，不标为 image2.5。
- 输入：`v17_ai_draft_20261006/figure2_draft_v2.png`。
- 输出：`candidate_builtin.png`，1672×941；`method_state_v20.pdf` 与正文资产字节一致。
- SHA-256：PDF `821783c3ee24ab7ed1a53bdac09d63e45e9d731c48817f72ce9333c3bd517150`。
- 语义复核：`ARTIFACT → JUDGMENT → TARGET`；`PROJECT → GATE → ROW`；`PEERS → READ CUT → SEALED ASSIGNMENT → SELECTED-ONLY UPDATE`；跨泳道箭头分别标注 `BEFORE SELECTION` 与 `AFTER SEAL`，UNKNOWN 保持审计分支。

本版本验证的是方法边界的图形表达，不是 updater/backbone 的科学锁定或效果证据。
