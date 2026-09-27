# Task report：diagnostic-card controller update gate / 2026-09-27

状态：`PARTIAL`；`goal_change_requested=false`。

新的 N03 neutral card 声明 `producer_scorer.controller_update_allowed=false`。审查发现旧
runner 会在 recipient outcome 后无条件更新 legacy score，可能把未资格化 producer scorer
的诊断链误写成在线学习。已加入向后兼容的 `controller_update_is_allowed(card)`：历史
没有该字段的 N02 card 保持原行为；新 diagnostic card 跳过 score mutation，但仍记录
`controller_update_skipped` 和 later-assignment 计算使用的旧分数。

单元测试覆盖默认 legacy、显式 false 和显式 true 三种路径；没有调用 LLM/GPU，也没有
重跑历史 episode。该 gate 只防止错误更新，不证明 RARE 学习或 scorer 资格。新的真实
card 仍需在 scorer/ledger/UNKNOWN 门通过后才允许请求。
