# 2026-09-28 event-time interleaving qualification

- 状态：`PARTIAL`
- 对应 Goal：ER-G1（future assignment 箭头可识别）、ER-G2（实时更新方法可验证）、ER-G4（主张与证据一致）
- `goal_change_requested=false`
- 真实 LLM API：0；GPU：0；科学效果主张：不允许

## 本任务要解决的具体问题

旧的 replay 先注册整段 episode 的 selections，再统一回放 feedback。即使最终
state 发生变化，也不能证明某条 feedback 在当时到达并影响了尚未执行的下一次
selection。此次新增 `scripts/peerrolebench_event_time_interleaving.py`，把三个
decision cut 固定为 `0,2,4`，把同一条 selected-only situated judgment 分别安排在
arrival index `1`（早到）和 `3`（晚到），并在每次 decision 前只 flush
`arrival_index <= read_cut` 的公开 evidence offer。

## 冻结的输入和对照

qualification 使用固定候选菜单 `agent-a@v1/agent-b@v1`、context、base score、
NumPy PCG64 seed 41、同一 label（首个被选 peer 的公开 accept judgment）和相同
decision schedule。`ContextualTrustPolicy` 的 F1 条件消费公开 rows，另有同一 policy
在 F0 条件下不消费；`NoUpdatePolicy` 作为冻结 comparator 接收同一 offer 但不更新。
两者的 candidate menu、RNG、预算和 event-time schedule 完全相同。这个小 runner 只
验证协议时序，不把 toy label 当作任务质量，也不锁定 active method。

配置在运行前写入
`experiments/logs/n03_event_time_interleaving_20260928_v1/config.json`；加入 append-only
manifest sealing 后，以新源码重跑的 v2 证据保存在
`experiments/logs/n03_event_time_interleaving_20260928_v2/`。随后仅改进原始事件粒度
并以相同条件重跑 v3，证据在
`experiments/logs/n03_event_time_interleaving_20260928_v3/`；v3 的 `raw.jsonl` 按
每个 run/decision 单独记录 9 条 trace，再记录 qualification summary。独立审查随后
发现 native sidecar manifest 的 exact-coverage 不能混入 auxiliary offer/consumption
event；因此保留 v1--v3 历史日志，并以分离的 auxiliary manifest 实现重跑 v4。随后
又增加同 policy 的 F0/F1 隔离、未选 candidate 的篡改拒绝、hash-chain 前置哈希篡改
测试，并将 auxiliary manifest records 与 F0 run 写入 raw evidence；最终 v5 证据在
`experiments/logs/n03_event_time_interleaving_20260928_v5/`。每个目录都有结构化
`raw.jsonl` 和 `summary.json`；源码哈希、Python 版本、git commit、seed、
decision/arrival indices 均在 config 中保存。

## 结果

v5 `summary.json` 状态为 `QUALIFIED_OFFLINE`，以下 12 个时序/绑定检查全部通过：

1. `same_seed_initial_decision`：同一 seed 的初始 decision 在 early/late/F0/comparator
   条件下保持一致；
2. `early_feedback_consumed_before_next_decision`：早到 feedback 在 decision 1 前被
   消费并产生一次 state update；
3. `late_feedback_not_available_at_decision_one`：晚到 feedback 在 decision 1 不可见；
4. `late_feedback_consumed_at_decision_two`：晚到 feedback 在 decision 2 才被消费；
5. `early_changes_next_policy_distribution`：早到条件的 decision-1 probability 与
   `NoUpdate` 不同；
6. `late_does_not_rewrite_decision_one`：晚到条件的 decision-1 probability 与
   `NoUpdate` 相同，历史决策没有被回写；
7. `latency_only_shifts_effect`：早、晚到只把同一影响向后平移一个 decision；
8. `attestations_are_distinct_per_decision`：每个 decision 有独立 consumption
   attestation；
9. `state_digest_changes_after_update`：更新前后 state digest 改变；
10. `append_only_manifest_seals_offer_and_consumption`：offer operator binding 和
   consumption attestation 被独立 auxiliary append-only manifest hash-chain 覆盖，
   manifest root 可复算，且不污染 native sidecar manifest；
11. `same_policy_f0_f1_isolated`：同一 policy 的 F0 与 F1 分开记录，F0 的输入 digest
    不含 evidence bundle，且 F1 的概率变化不出现在 F0；
12. `manifest_previous_hash_mutation_rejected`：auxiliary manifest 的
    `previous_hash` 篡改被拒绝；

此外，未选 candidate 的 evidence mutation 在更新前被拒绝，并有独立 pytest 断言；
它是 runner 防护测试，不计入上述 12 个 summary checks。

所有 run 的 manifest records、decision traces 和 qualification summary 都落在 v5
的 raw JSONL 中；这是证据完整性，而不是额外的 scientific cell。

## 代表性轨迹

```text
early: d0=(0.5,0.5), d1=(0.41743,0.58257), d2=(0.41743,0.58257)
late:  d0=(0.5,0.5), d1=(0.5,0.5),   d2=(0.41743,0.58257)
```

概率变化只说明已有 `ContextualTrustPolicy` 的状态转移遵守 event-time 约束；它不
说明实时训练有效、不说明 peer role learning 有收益，也不说明任何 benchmark 任务
上的准确率提升。

## 对 Goal 的逐项判断

- **满足（工程子门）**：pre-decision offer、read watermark、state digest、
  consumption attestation 以及离线 auxiliary append-only manifest sealing 现在有
  一个可执行的非 LLM 时序资格层。
- **部分满足**：F 因素的最小行为语义和 auxiliary manifest 形状得到验证；当前
  `offer_record_hash` 仍是 adapter 提供的绑定值，尚未由 PIPE3 canonical protocol
  event 生成，且 toy runner 中 policy 的 evidence consumption 仍由 orchestrator
  分支调用 `observe_feedback`，不是隔离进程内可证明的 policy-read trace。因此这
  只能作为协议资格，不能证明 policy 实际读取了真实 offer。仍没有真实 runner 的
  event-time sealing、producer responsibility scorer 和后续 assignment 的真实 lineage
  接入。offer/attestation 不能写入 native `PeerRoleLedger`，真实 runner 必须做
  native/auxiliary 双回放。
- **未开始**：真实 benchmark episode、LLM API、A800、强 same-information
  baseline、完整 `2^4` scientific cells、统计功效和 unseen-root 评估。

## 未完成原因与下一步

本任务前的主要问题是 replay 拓扑造成的识别缺陷，属于实现/测量边界缺陷，不是
实验失败，也不是 Goal 降级理由。下一步必须把 `AssignmentEvidenceOffer` 和
`DecisionConsumptionAttestation` 接到 PIPE3 runner 的真实 auxiliary append-only
manifest，同时保留 native sidecar manifest 独立验证，并让同一份 offer 同时进入
proposed policy 与强 baseline；在该 runner 通过
乱序、延迟、UNKNOWN 和恢复测试前，不启动真实 API 或 A800 factorial。
