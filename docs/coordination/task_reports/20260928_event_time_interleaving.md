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
decision schedule。`ContextualTrustPolicy` 是会读取 situated evidence 的实现条件，
`NoUpdatePolicy` 接收同一 offer 但明确不消费 bundle。两者的 candidate menu、RNG、
预算和 event-time schedule 完全相同。这个小 runner 只验证协议时序，不把 toy label
当作任务质量，也不锁定 active method。

配置在运行前写入
`experiments/logs/n03_event_time_interleaving_20260928_v1/config.json`；加入 append-only
manifest sealing 后，以新源码重跑的 v2 证据保存在
`experiments/logs/n03_event_time_interleaving_20260928_v2/`。每个目录都有结构化
`raw.jsonl` 和 `summary.json`；源码哈希、Python 版本、git commit、seed、
decision/arrival indices 均在 config 中保存。

## 结果

v2 `summary.json` 状态为 `QUALIFIED_OFFLINE`，10 个时序/绑定检查全部通过：

1. 早到 feedback 在 decision 1 前被消费，并产生一次 state update；
2. 晚到 feedback 在 decision 1 不可见，在 decision 2 才被消费；
3. 早到条件的 decision-1 probability 与 `NoUpdate` 不同；
4. 晚到条件的 decision-1 probability 与 `NoUpdate` 相同，历史决策没有被回写；
5. 早、晚到只把同一影响向后平移一个 decision；
6. 每个 decision 都有独立 consumption attestation，更新前后 state digest 改变；
7. comparator 看到与条件组相同的公开 evidence offer。
8. offer operator binding 和 consumption attestation 被同一条 append-only manifest
   hash-chain 覆盖，manifest root 可复算。

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
  consumption attestation 以及离线 append-only manifest sealing 现在有一个可执行
  的非 LLM 时序资格层。
- **部分满足**：F 因素的最小行为语义和 manifest 形状得到验证；当前 offer
  `offer_record_hash` 仍是 adapter 提供的绑定值，尚未由 PIPE3 canonical protocol
  event 生成，仍没有真实 runner 的 event-time sealing、producer responsibility
  scorer 和后续 assignment 的真实 lineage 接入。
- **未开始**：真实 benchmark episode、LLM API、A800、强 same-information
  baseline、完整 `2^4` scientific cells、统计功效和 unseen-root 评估。

## 未完成原因与下一步

本任务前的主要问题是 replay 拓扑造成的识别缺陷，属于实现/测量边界缺陷，不是
实验失败，也不是 Goal 降级理由。下一步必须把 `AssignmentEvidenceOffer` 和
`DecisionConsumptionAttestation` 接到 PIPE3 runner 的真实 append-only manifest，
并让同一份 offer 同时进入 proposed policy 与强 baseline；在该 runner 通过
乱序、延迟、UNKNOWN 和恢复测试前，不启动真实 API 或 A800 factorial。
