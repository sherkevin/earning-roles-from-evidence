# Agent1 ↔ Agent2 书面约定（Session 5+）

**7405 全量**（`hotpotqa_validation_full.jsonl`）：默认 **Agent2 主跑**；**Agent1 不启动 7405** 除非双方在同一版本改本条并互相知会；优先只跑 **三主方法**（`fixed_peer_calibrated` / `fixed_static_roles` / `fixed_self_claim`）以控成本。

**`topology: star`**：与 7405 **分开展**；**Agent1** 负责在获批预算下用 **200 条同批 jsonl** 跑 star×三主方法（新 `run_*`）；**Agent2** 不重复同一配置 unless 对表后另有分工。
