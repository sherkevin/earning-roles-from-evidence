# 2026-09-28 故事线与方法论严格复评

- 状态：`PARTIAL`
- 对应 Goal：ER-G1、ER-G2、ER-G4
- `goal_change_requested=false`
- 评价对象：当前 active storyline v1.1、active method v1.0，以及待验证 method v1.1-candidate
- 本报告是内部 gate audit，不是 AAMAS 录用预测。

## 评价口径

采用当前生效的 storyline evaluation v1.3 和 method evaluation v1.1。分数分成两层：

1. **合同覆盖度**：文档是否把需要定义、比较和测量的对象写出来；
2. **科学证据准备度**：是否已有真实、独立、可复现的结果支持论文主张。

后者是不可补偿硬门；协议 fixture、零调用 replay 和候选状态测试不能替代真实协作流。

## 故事线结果

| 维度 | 合同覆盖度 | 证据准备度 | 主要原因 |
|---|---:|---:|---|
| sharp 问题与范围 | 75/100 | 34/100 | 主问题已收紧到 situated judgment→role evidence→future assignment，但最小反例和独立 later-use 增量尚未取得 |
| 有机整体创新 | 70/100 | 0/100 | v1.1 已给出整体机制和 matched-composition/全因子检验；当前 scientific cell 仍为 0/16 |
| 因果链 | 65/100 | 20/100 | ledger 能记录四段事件，但 policy 消费 evidence、A gate 和后续 utility 尚未被证明 |
| 论文行文逻辑 | 80/100 | 30/100 | v1.3 已对齐当前 storyline；正文仍不能填入未验证效果数字 |

**故事线当前严格状态：`NOT_READY`（证据硬门失败）。** 这次复评不是降级；它把“对外叙事已收敛”和“实验尚未证明”分开。

## 方法论结果

| 维度 | active method v1.0 | candidate v1.1 的新增覆盖 | 科学状态 |
|---|---:|---:|---|
| 形式可重放 | 45/100 | 70/100 | candidate reference 已通过 14 项零调用不变量，但尚未接入真实 runner |
| 创新可识别性 | 40/100 | 45/100 | 有 bounded anchor/window 候选；closest RLS/trust/refit 尚无对照结果 |
| 实时/时效/稳定合同 | 48/100 | 65/100 | candidate 定义了 O(d)、窗口、半径和 interleaving；没有真实延迟、吞吐、漂移或遗忘结果 |
| 训练/系统可复现 | 25/100 | 40/100 | candidate 明确小状态和 snapshot，但 A/F projection、并发、恢复和 scorer 隔离仍开放 |
| 目标/统计 | 36/100 | 45/100 | M=quality−cost 与全因子 contrast 已定义；没有独立 root、CI、功效和预注册执行结果 |

**方法论当前严格状态：`NOT_READY`（active method 尚未锁定，candidate 不能直接当最终算法）。** 合同覆盖提升不等于方法有效。

## 距离目标的最短路径

1. 完成 typed policy projection：J/A/U/F 四因素必须只改变输入投影或 state transition；scorer payload 不得泄漏到 policy。
2. 完成 event-time interleaving runner：反馈在下一 decision watermark 前到达时才可影响下一 choice；迟到、重复、correction 和 version replacement 必须可重放。
3. 用同一表示、初始化、探索和 event stream 比较 candidate、RLS/linear associative、contextual trust、terminal-only、no-update 和 periodic refit。
4. 通过零调用 16-cell qualification 后，才冻结一条真实 API 小流；随后用独立 root/stream 测 H1 信息价值、H2 闭环 utility、H3 在线代价与遗忘。

## 停止条件

在上述 evidence gate 未通过前，不能停止长任务，也不能把标题、摘要或贡献列表写成“实时训练已实现”或“形成角色专长”。如果 full mechanism 与 matched composition 无差异，保留负结果并由用户决定是否修改研究问题；失败本身不改变 Goal。
