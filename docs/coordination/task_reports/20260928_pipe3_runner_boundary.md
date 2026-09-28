# 2026-09-28 PIPE3 selection runner boundary

- 状态：`DONE`（selection boundary 工程子门；完整 runner 仍未完成）
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
定向集合共 `19 passed`。提交后的 structured qualification
`experiments/logs/n03_pipe3_runner_boundary_qualification_20260928_v4/` 也通过：

- `git_commit=aad3cc2c919a178c0744692594c22889f8fcbec6`，runner 与依赖源码 hash 已写入
  config；
- valid case 两次 native selection、两条 native sidecar row、四条 auxiliary row，
  policy 在第二个 decision 前更新一次；
- native manifest root 和 auxiliary manifest root 均可复算；
- 未选 candidate mutation 被拒绝，policy updates 保持 0，第二次 native selection
  没有被写入。

## 边界

这仍然不是完整 PIPE3 runner：没有 actor LLM、producer/recipient/adoption scorer、
judgment/action/outcome/evidence 阶段，也没有证明隔离进程内的 policy-read。不会把这条
零调用 boundary 写成 benchmark 或学习效果。下一步补全链 UNKNOWN/fault-injection 和
responsibility v3 feedback gate，再决定是否可开一条真实 API 小链。
