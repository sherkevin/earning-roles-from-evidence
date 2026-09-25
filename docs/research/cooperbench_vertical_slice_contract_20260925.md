# CooperBench 角色形成 Vertical Slice 契约

> 日期：2026-09-25  
> 状态：工程契约；不是 benchmark 结果  
> 目的：把本项目的 producer → recipient judgment/use/rework → later assignment 链条接到 CooperBench，而不把原生 `both_passed` 误当成角色学习证据。

## 固定输入

每个 episode 以完整 task-root 为单位，不按 feature pair 随机拆分：

```text
root_id, repo_name, base_sha, feature_specs, persistent_agent_ids
```

同一 task-root 内的 producer 身份必须可交换。原始 `coop` runner 将排序后的 feature 直接绑定到 agent，因此原始 assignment 不能作为 role-learning 标签；适配层必须自己产生 `assignment_event`，并记录候选集合、chosen producer、propensity、policy/state version。

## 必须按顺序产生的事件

### 1. Producer delivery

```json
{
  "event_type": "producer_delivery",
  "delivery_id": "d-001",
  "root_id": "click-task-2800",
  "producer_id": "agent-a",
  "recipient_id": "agent-b",
  "feature_id": "feature-1",
  "base_sha": "...",
  "artifact_sha256": "...",
  "patch_sha256": "...",
  "source_event_id": "..."
}
```

交付物是 patch 加 provenance metadata。producer 不可读取隐藏测试或 terminal outcome。

### 2. Recipient judgment

recipient 在 terminal scorer 结果可见前封存：

```json
{
  "event_type": "recipient_judgment",
  "judgment_id": "j-001",
  "delivery_id": "d-001",
  "consumer_id": "agent-b",
  "decision": "accept|accept_with_rework|reject_redo|reject_reroute",
  "observed_artifact_sha256": "...",
  "confidence": 0.7,
  "rationale": "...",
  "terminal_outcome_available": false
}
```

`accept` 不能直接写成成功；它只是 consumer 的 situated judgment。`rework` 和 `reject` 也必须保留，不能只保留正例。

### 3. Consumer action

```json
{
  "event_type": "consumer_action",
  "action_id": "a-001",
  "delivery_id": "d-001",
  "consumer_id": "agent-b",
  "action": "use|repair|reject|independent_redo",
  "used_artifact": true,
  "input_artifact_sha256": "...",
  "output_artifact_sha256": "...",
  "repair_cost": {"tokens": 0, "seconds": 1.2, "calls": 1}
}
```

是否真正使用 producer artifact 必须由 hash lineage、changed paths/hunks 和 recipient trajectory 证明，不能由最终测试通过反推。

### 4. Terminal scorer

```json
{
  "event_type": "terminal_outcome",
  "delivery_id": "d-001",
  "merge_status": "clean|conflict|missing_input",
  "strategy": "two_party|solo_agent1|...",
  "feature_tests": {"feature-1": true, "feature-2": false},
  "both_passed": false,
  "scorer_version": "native-v1"
}
```

CooperBench 原生 scorer 在 conflict 或 missing input 时可能运行 agent1 的单独 patch；此路径必须禁用或单列为 diagnostic。`both_passed=true` 且 `strategy=solo-agent1` 不能计入双人交付成功。

### 5. Public role evidence update

更新器只能读取已封存的 recipient judgment、consumer action 和合法到达的 terminal correction，并记录 `feedback_delay`、`update_version`、`update_latency`。隐藏 truth、未选 producer 的标签和 evaluator 私有字段不能进入 pre-action state。

### 6. Later assignment

下一 task-root 必须重新产生可交换候选集合：

```json
{
  "event_type": "later_assignment",
  "assignment_id": "as-002",
  "root_id": "click-task-2810",
  "task_index": 2,
  "candidate_ids": ["agent-a", "agent-b"],
  "chosen_agent_id": "agent-a",
  "role": "citation-review",
  "evidence_ids": ["j-001"]
}
```

只有当 assignment 引用先前证据且其选择与 no-role-update 对照不同，才有资格声称“判断影响了未来职责”。

## 最小 matched baseline

- B0 pooled single-agent / centralized selector；
- B1 fixed cooperation，无 role update；
- B2 recipient redo/no handoff；
- B3 raw recipient acceptance；
- B4 same-information local contextual trust/bandit；
- B5 terminal-only feedback；
- B6 closest reproducible dynamic-role control；
- P proposed evidence update。

每个 arm 使用相同 task-root、模型、工具、预算、身份初始化和可见信息。role evidence 的写入和 future assignment 是唯一允许变化的核心因素。

## 当前缺口与 gate

1. 原生 CooperBench 没有 structured receipt/judgment/action/later-assignment 字段；
2. 原生 `coop` 预分配 feature owner；
3. scorer fallback 会把单人 patch 当成双人成功；
4. 需要按 task-root/repository 分组留出确认集；
5. 需要独立 scorer/许可证决定；
6. 需要先用 2 个 task-root 做 zero-LLM protocol smoke，再做 held-out roots 和真实模型。

本项目的[peer-role protocol module](../../references/aamas/peer_role_protocol_20260925.py)和对应测试只验证上述事件顺序、artifact attribution、terminal isolation 和 later-assignment 引用关系；它不产生科学结果，也不替代 CooperBench 的真实 runner。
