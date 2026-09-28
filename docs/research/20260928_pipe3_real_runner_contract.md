# PIPE3 real runner v1 contract

状态：`implementation contract / method not frozen`

这份文档规定真实 runner 必须提供的可回放边界。它不是 benchmark 结果，也不把
`ContextualTrustPolicy` 或任一 updater 宣布为论文方法。

## 1. 不可变输入

runner 在第一次 API 调用前写出并 hash：

- TeamBench commit、PIPE3 root/seed、train/development/confirmation split；
- candidate registry 完整快照及 `registry_digest`；
- public material/source template digest、material adapter 版本；
- policy family/version、encoder/feature/base-score 版本、RNG 算法与 seed；
- LLM/provider/model、prompt 版本、每阶段 token/请求预算；
- Qp、Qr、adoption scorer 版本与 sandbox 限制；
- 全局 `arrival_index` schedule digest 和每个 arm 的 `consume_evidence` 条件。

candidate registry 是唯一的 ID→version 来源。native `PeerSelection` 保存 ID，
`DecisionSidecar` 用 registry 解析为同序的 `CandidateRef(id, version)`；模型输出不能
改 ID、version、candidate menu 或 source digest。

## 2. 一个 decision cut 的顺序

所有 arm 使用同一 candidate menu、materials、arrival schedule、RNG draws、预算和
外部任务输入；每个 arm 都有独立 policy state、ledger 和 raw output。

1. 从 frozen global stream flush 所有 `arrival_index <= read_cut` 的反馈；重复、缺失、
   未注册或 UNKNOWN 反馈不得进入 policy；
2. 用当前可见 public rows 构造 `AssignmentEvidenceOffer`，不包含 chosen peer 或
   propensity，并先写 auxiliary offer record；
3. policy 读取同一 offer（F1 消费 rows；F0 接收相同 offer metadata 但 policy input
   为空），产生选择概率和 sampled candidate；
4. 写 native `PeerSelection`，从 ledger 刚写入的真实 `record_hash` 构造
   `DecisionSidecar`，校验 native candidate IDs、chosen ID、chosen index、propensity
   与 sidecar 完全一致；
5. 用真实 sidecar/state digest 构造并验证 `DecisionConsumptionAttestation`，再写
   auxiliary consumption record；
6. 写 native sidecar manifest 的 selection row。offer/attestation 永远不能写入 native
   manifest 或 `PeerRoleLedger`。

选择之后才允许 `task_start`。delivery、producer score、recipient judgment、action、
terminal outcome、role evidence 依次进入 native ledger。`UNKNOWN` scorer/transport/
resource/schema 只保存 partial ledger 和诊断结果，停止该 episode，不产生 eligible label、
role update 或 later assignment。

## 3. 责任和反馈时机

Qp 只看 producer-owned `producer.py` 与 read-only `models.py`；Qr 只看 recipient-owned
`processor.py` 与 `models.py`；adoption 看完整 public runtime。actor 不可见 hidden tests、
scorer response、expected output 或 operator ledger。

recipient judgment 在 action 之前写入 native ledger，但只有 action/artifact lineage 已
封存后，才能构造带 responsibility v3 binding 的 eligible judgment sidecar。否则保留为
pending/unknown。terminal feedback 同样必须绑定真实 delivery/action/outcome record。
这防止把“判断过”误当作“对上游负责”。

`FeedbackSidecar.arrived_at` 只作审计字段；online apply 使用 frozen global
`arrival_index`，不能用 wall-clock 或事后 `(arrived_at,event_id)` 排序替代。sidecar 到
arrival schedule 必须一一对应。迟到 feedback 只能进入未来 decision cut，不能回写已经
sealed 的 selection。

## 4. 双回放与输出

每个 arm 至少输出：

```text
config.json                 # pre-call frozen card and source hashes
candidate_registry.json     # immutable entries + registry_digest
event_time.jsonl            # explicit arrival_index assignments
ledger.json                 # native PeerRoleLedger chain
native_sidecar_rows.jsonl
native_sidecar_manifest.json
assignment_aux_rows.jsonl
assignment_manifest.json
raw.jsonl                   # prompts, responses, costs, errors, digests
summary.json
```

完成链必须同时通过：

1. strict `replay_ledger_events`；
2. native sidecar manifest exact coverage；
3. auxiliary assignment manifest exact coverage and offer-before-consumption order；
4. event-time schedule one-to-one and online-order replay；
5. `replay_policy_sidecars(..., require_responsibility_lineage=True)`，并额外确认它
   没有把 offline wall-clock sort 当成 online evidence。

任一回放不通过，summary 为 `UNKNOWN`/`INVALID`，policy state 不得更新。

## 5. 实验准入

在 runner boundary 通过乱序、延迟、重复、缺失、UNKNOWN、恢复和 same-information
baseline parity 测试前，不提交真实 factorial API 或 A800 job。selection boundary 已
依照契约落成 versioned `scripts/peerrolebench_pipe3_runner_v1.py`；随后零调用的
full-chain qualification 已通过两个 episode，覆盖 strict ledger、v3 responsibility
sidecar、native/auxiliary manifest、arrival schedule 和 UNKNOWN/fault rejection（见
`task_reports/20260928_pipe3_full_chain_qualification.md`）。这仍未实现 actor/scorer/
action 的真实进程隔离，也未证明 evidence 对 assignment 的因果影响。下一步只能先接入
一条新的真实 PIPE3 小链，确认 actor payload、Qp/Qr/adoption、judgment lineage 和 raw
usage 均可审计，再决定是否进入完整 benchmark matrix。
