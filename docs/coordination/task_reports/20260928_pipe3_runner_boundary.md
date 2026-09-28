# 2026-09-28 PIPE3 selection runner boundary

- 状态：`PARTIAL`
- 对应 Goal：ER-G1、ER-G2、ER-G4
- `goal_change_requested=false`
- 真实 LLM API：0；GPU：0；scientific cell：0

## 完成内容

新增 versioned `scripts/peerrolebench_pipe3_runner_v1.py`，把真实 runner 最容易漂移的
selection boundary 变成可复用代码：

1. `make_offer()` 对不含 chosen/propensity 的 public offer 计算 bundle digest 和不含
   自身的 canonical operator record hash；
2. `Pipe3SelectionBoundary` 从 candidate registry 解析 versioned `CandidateRef`，按
   offer 的 candidate 顺序调用 policy，随后写入真实 `PeerRoleLedger.record_selection`；
3. `DecisionSidecar.ledger_record_hash` 绑定刚写入的 native selection record，native
   sidecar row 与 auxiliary offer/consumption row 分别落链；
4. `DecisionConsumptionAttestation` 在 native selection 封存后构造并验证；
5. feedback 只有在 `source_event_id` 和实际 selected candidate 都匹配时才能更新 policy，
   未选 candidate 变异会在 native selection 前拒绝；
6. `validate_selection_manifests()` 同时验证 native manifest 与 auxiliary manifest，
   两条链不互相污染。

## 验证

`tests/test_peerrolebench_pipe3_runner_v1.py` 与 registry/schedule/manifest/event-time
定向集合共 `19 passed`。覆盖真实 native record hash 绑定、两次 decision 的 selected
feedback 更新、未选 candidate 拒绝和双 manifest root。尚需运行提交后固定源码 hash 的
structured qualification log。

## 边界

这仍然不是完整 PIPE3 runner：没有 actor LLM、producer/recipient/adoption scorer、
judgment/action/outcome/evidence 阶段，也没有证明隔离进程内的 policy-read。不会把这条
零调用 boundary 写成 benchmark 或学习效果。下一步在提交后重跑 qualification，随后补
全链 UNKNOWN/fault-injection 和 responsibility v3 feedback gate，再决定是否可开一条真实
API 小链。
