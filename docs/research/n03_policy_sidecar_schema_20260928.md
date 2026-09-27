# N03 public policy sidecar schema

日期：2026-09-28  
状态：`IMPLEMENTED_FOR_OFFLINE_QUALIFICATION / NOT_RUNNER_INTEGRATED`  
依据：[`n03_baseline_bridge_audit_20260928.md`](n03_baseline_bridge_audit_20260928.md)。

旧 N02 ledger 无法无损映射到 BaselinePolicy。为避免用默认值掩盖缺失信息，本任务增加一个版本化、公开、带 hash 绑定的 sidecar schema。它不改旧 ledger，也不改变 RARE 的方法合同。

## Decision sidecar

`DecisionSidecar`（[`scripts/peerrolebench_policy_sidecar.py`](../../scripts/peerrolebench_policy_sidecar.py)）绑定一个 sealed ledger `record_hash`，并保存：

- `event_id`、`selector_id`、`context_key`；
- 每个候选的 `candidate_id` 和 `candidate_version`；
- 冻结 `base_scores`、完整行为概率、实际 `propensity` 和 `chosen_index`；
- `state_version`、`encoder_version`、`feature_schema`、`selected_at`；
- 可选 captured features。

构造时检查菜单唯一性、概率和 propensity 一致性、版本非空、时间非负和 record hash 格式。sidecar digest 对 canonical payload 计算，runner 必须把它写入同一事件的公开 provenance。`bind_to_ledger_record` 还要求 `protocol_event_type`、`protocol_event_id` 与 ledger 的事件类型及 `selection_id`/`judgment_id`/`outcome_id` 一致，并可由 runner 传入 expected type/id 做额外检查。

## Feedback sidecar

`FeedbackSidecar` 绑定反馈 ledger `record_hash`，保存 `feedback_id`、`source_event_id`、`selection_event_id`、`producer_id`/`producer_version`、`source`、`arrived_at`、`delay`、`action`、`disposition`、`provenance` 和 `label_mapping_version`。只有 `disposition=eligible` 且 `provenance=public` 时才允许携带 label，并能转换为 BaselinePolicy 的 `Feedback`；UNKNOWN/pending/rejected 或非公开反馈只能保留审计记录，转换结果为 `None`。

这使 hidden scorer 与 policy 分离：scorer/责任审查先在 runner 外部完成公开边界判定，policy 只接收已声明的 public sidecar。缺失 label mapping、隐藏 label、错误 record hash 或不支持的 action/source 会直接失败。

## 离线资格结果

测试：

```text
python3 -m pytest -q tests/test_peerrolebench_policy_sidecar.py
```

sidecar qualification：

```text
python3 scripts/peerrolebench_policy_sidecar_qualification.py \
  --out-dir experiments/logs/n03_policy_sidecar_qualification_20260928_v3
```

结果为 `passed=true`、`sidecar_version=peerrole-policy-sidecar-v2`、eligible feedback 可转换、UNKNOWN feedback 不转换，且三类事件的 event type/id 绑定检查通过；`real_api_calls=0`、`gpu_jobs=0`、`scientific_claim_allowed=false`。提交 `3b6644e` 的 config/raw/summary 已记录。该 qualification 使用简化 record，只证明单事件 bridge 边界。

完整 canonical stream qualification：

```text
python3 scripts/peerrolebench_policy_sidecar_stream_qualification.py \
  --out-dir experiments/logs/n03_policy_sidecar_stream_qualification_20260928_v4
```

提交 `631f2b0` 后的 v4 日志覆盖 strict ledger replay、feedback permutation、duplicate sidecar、truncated ledger UNKNOWN 和 wrong selected producer/version 五个 case；规则是 selection 按 canonical ledger index 注册，feedback 按 `(arrived_at, protocol_event_id)` 重放，并验证独立 manifest root。该运行仍是工程资格，不是 benchmark 效果。

## 尚未通过的门

sidecar 目前已能在离线 canonical replay 中接入 BaselinePolicy，但尚未接入 PIPE3 live runner，也没有从真实候选输出生成字段。当前绑定检查覆盖同一 record hash、event type、event id、sidecar digest、时间一致性和 selected producer/version；runner 仍需证明 sidecar manifest 与 append-only ledger 的 attestation、真实延迟/乱序可重放、producer/action/artifact 责任一致、UNKNOWN 禁止 update，以及所有 baseline 共享同一公开信息和成本预算。

因此 benchmark、baseline freeze、RARE/RLS 接入、backbone/training 选择和 A800 仍保持开放，`goal_change_requested=false`。
