# 原 EDO 代码在当前问题中的可复用边界

2026-09-23，源码审查；未运行新模型或声称方法有效。当前研究问题依照[决议 0006](../../user/decisions/0006-study-peer-judged-role-formation.md)：真实接收者的判断和使用如何成为被评 agent 的角色证据，并改变以后的局部职责。先从这个信息流出发，再决定复用旧实现的哪些部分。

| 旧组件 | 可直接借的工程骨架 | 不能直接继承为科学机制 |
|---|---|---|
| [`task_tree.py`](../../../workspace/idea04_core/task_tree.py) | 有上限的父子任务、owner/executor、状态和 JSONL 序列化，可作递归 do/outsource/split 的任务载体 | 当前字段只保存一个 `audit_status` 和自由文本结果；不含接收者实际采用、返工、逐项来源、可见证据集合或因果依赖 |
| [`audit_runtime.py`](../../../workspace/idea04_core/audit_runtime.py) | `AuditEvent` 已有评价者/被评者/任务 ID、决策、返工成本、时间等结构与缓冲写盘 | 默认规则据长度、拒答词和文本存在性验收，`value_gain` 是估计量；不能当真实使用、独立质量或终局归因 |
| [`persona_model.py`](../../../workspace/idea04_core/persona_model.py) | 邻居私有 `BeliefStore`、版本化持久化与旧日志兼容性值得复用 | 七维固定轴的 EMA 将评价者错误和生产者能力混合；没有“被评价者可分享角色证据”与委派者私有信念的边界，也无选择偏差/不确定性处理 |
| [`action_policy.py`](../../../workspace/idea04_core/action_policy.py) | 三动作枚举、树深/分支/节点上限、每次决策的候选分数和理由可用于运行时审计 | `0.6*neighbor_belief` 等手工效用和固定 tie-break 是原型启发式，未从真实接收者事件学习，也不构成角色形成方法 |
| [`runner.py`](../../../workspace/idea04_core/runner.py) | 串行状态、逐题持久化/恢复、审计和树日志的工程路径可供重写时参考 | 头条 `fixed_peer_calibrated` 只用终局 F1 更新被接受节点的自身标量；Stage-2 的向量更新也未提供已验证的跨任务同伴判断→角色→后续职责链 |

下一步的复用动作是用 `TaskTreeState` 的有界结构和 `AuditEvent` 的身份/任务字段起一个**新版本事件 schema**：先封存交付、接收者行动前判断、真实采用/返工及合法后果，再区分 `local_neighbor_belief` 与 `producer_role_evidence`，最后记录实际未来职责选择。旧日志保持原状，不能把规则生成的 `ACCEPT` 当成独立同伴判断。这个工程骨架可缩短实现时间；它本身不填补当前缺的真实观察与算法证据。

工程烟测：在 AppWorld Python 环境中执行 `python -m pytest -q workspace/idea04_core/test_task_tree.py workspace/idea04_core/test_audit_runtime.py workspace/idea04_core/test_persona_model.py workspace/idea04_core/test_action_policy.py`，88 项通过；这是旧结构的回归测试，不是当前科学机制的验证。
