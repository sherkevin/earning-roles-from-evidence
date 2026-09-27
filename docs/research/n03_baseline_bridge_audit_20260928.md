# N03 baseline-to-ledger bridge audit

日期：2026-09-28
状态：`NOT_MAPPABLE / QUALIFICATION COMPLETE`
依据：Goal v1.0、[`n03_baseline_policy_contract_20260928.md`](n03_baseline_policy_contract_20260928.md)。

本次审查不修改历史 N02 ledger，也不为缺失字段填默认值。目标是判断冻结的 peer-role ledger 能否无损地映射到四个 baseline policy 的输入。

## 运行与结果

```text
python3 tests/test_peerrolebench_baseline_bridge_audit.py
python3 scripts/peerrolebench_baseline_bridge_qualification.py \
  experiments/logs/n02_peerrole_dev_v3_20260926/ledger.json \
  --out-dir experiments/logs/n03_baseline_bridge_audit_20260928
```

代码位置：[`scripts/peerrolebench_baseline_bridge_audit.py`](../../scripts/peerrolebench_baseline_bridge_audit.py)。原始输入 ledger、config、逐记录 JSONL 和 summary 均保留在 qualification 目录。

审查了 15 条冻结事件：2 个 selection、2 个 recipient judgment、2 个 terminal outcome 和 2 个 consumer action。action 是责任/成本证据，不被当作 policy feedback；结果为：

```text
status=NOT_MAPPABLE
policy_update_allowed=false
scientific_claim_allowed=false
real_api_calls=0
gpu_jobs=0
```

缺失字段计数：

- 两个 selection 都缺 `candidate_versions`、`context_key`、`base_scores`、`state_version`、`encoder_version`、`feature_schema`、`selected_at`；
- 四个 policy feedback 事件都缺 `arrived_at`、`delay`、`disposition`、`provenance`；
- 两个 recipient judgment 和两个 terminal outcome 都没有预声明数值 label mapping。

## 结论

现有 ledger 证明了 selection→delivery→judgment→action→outcome 的因果链，但不能直接证明 policy 的版本绑定、延迟回放或同信息公平性。任何直接映射都会把不同版本、反馈时序和公开/隐藏来源混在一起，或者隐式制造 label；因此 bridge 必须拒绝更新。

需要由新的 root-specific runner 在 selection/feedback 的公开事件旁记录 sidecar：候选版本、context digest、冻结 base score、state/model/schema version、selected time、反馈到达时间/延迟、action、公开 disposition/provenance，以及 judgment/terminal label mapping 的版本。隐藏 scorer 只用于外部质量与责任检查，不能直接作为 policy 输入。

## Goal 对照

| Goal 标准 | 状态 | 说明 |
|---|---|---|
| 故事线与 RARE | `MAINTAINED` | 只是拒绝不完整映射，没有改变 situated judgment→role evidence 主线 |
| benchmark/双 root | `OPEN` | PIPE3 runner 尚未产生这些 sidecar，benchmark 仍未冻结 |
| baseline 公平可执行 | `BLOCKED_BY_EVIDENCE` | 旧 ledger 缺 policy 输入，必须先修复 runner schema |
| 实时/稳定/准确科学证据 | `OPEN` | 没有 API/GPU，也没有 role efficacy claim |
| Goal/创新点 | `UNCHANGED` | `goal_change_requested=false` |

下一步是给 PIPE3 runner 增加**公开 sidecar schema 和 hash-chain 绑定**，先用离线 fixture 验证无损映射，再考虑新的真实 API episode。旧 N02 ledger 继续作为历史接入证据，不回写。
