# N03 baseline policy contract (implementation stage)

日期：2026-09-28
状态：`IMPLEMENTED_FOR_OFFLINE_QUALIFICATION / NOT_FROZEN`
依据：[`n03_baseline_implementation_audit_20260927.md`](n03_baseline_implementation_audit_20260927.md) 与 Goal v1.0。

这份文档只定义四个候选 baseline 的可执行接口，目的是让它们在同一事件流上接受信息公平检查。它不是 benchmark freeze、不是 RARE 决议，也不是科学结果。

## 接口

代码位于 [`scripts/peerrolebench_baseline_policies.py`](../../scripts/peerrolebench_baseline_policies.py)。

一个选择保存：

- `event_id`、`selector_id`、`context_key`；
- 带 `candidate_id@candidate_version` 的完整菜单；
- 冻结的 `base_scores`、精确行为概率和实际 `propensity`；
- `state_version`、`encoder_version`、`feature_schema`、`selected_at`；
- 可选的 captured feature vectors。

反馈不携带候选 ID，而是引用 `source_event_id`，由选择快照解析被选候选。这避免把未执行候选的标签误写入状态。反馈还必须显式给出：

- `source`：`recipient_judgment` 或 `terminal_outcome`；
- `label`、`arrived_at`、`delay`、`action`；
- `disposition`：`eligible`、`pending`、`unknown` 或 `rejected`；
- `provenance`：`public` 或 `unknown`。

只有 `eligible + public` 的事件才能更新；同一个 `(source_event_id, source)` 只接受一次。`pending`、`unknown`、`rejected`、重复反馈和不可公开事件都不会更新。隐藏 scorer 的判断不能由 policy 自己推断，必须先由 runner 的公开边界与责任/完整性检查产出 disposition。

## 四个实现条件

| policy | 选择规则 | 允许更新的 source | 状态存储 |
|---|---|---|---|
| `uniform` | 忽略 base score，均匀探索 | 无 | 无 |
| `no_update` | 只使用冻结 base score | 无 | 无 |
| `terminal_only` | base score 加 candidate/version 的 Beta trust | `terminal_outcome` | candidate/version 计数 |
| `contextual_trust` | base score 加 context + candidate/version 的 Beta trust | `recipient_judgment` | context/candidate/version 计数 |

两种 Beta policy 会记录 propensity，但当前实现不做 inverse-propensity weighting；这只是有界、可审计的 comparator。正式实验卡必须在看到结果前决定是否保留该更新规则，不能把它直接称为 RARE 或最终 trust/bandit baseline。

## 已执行的离线资格检查

测试：

```text
python3 -m pytest -q tests/test_peerrolebench_baseline_policies.py
```

结果：`8 passed`。覆盖菜单置换、精确 propensity、selected-only 源事件、版本隔离、频道隔离、UNKNOWN/pending/illegal no-update、重复反馈幂等、snapshot/restore。

另有零 API qualification runner：

```text
scripts/peerrolebench_baseline_policy_qualification.py \
  --out-dir experiments/logs/n03_baseline_policy_contract_20260928
```

它写入 config/raw/summary，结果为 `passed=true`、`real_api_calls=0`、`gpu_jobs=0`、`scientific_claim_allowed=false`。该结果只证明接口行为，不证明 baseline 在 PeerRoleBench 上公平或有效。

## 尚未解决的科学门

1. runner 尚未把真实 `producer_id`、责任范围、action/use/rework、延迟乱序和 scorer isolation 转成此接口的公开事件；
2. Beta comparator 的 label mapping、propensity 使用和跨 selector 共享范围还没有进入预注册实验卡；
3. RLS、RARE、pooled controller、online logistic 和 periodic refit 尚未接入这套接口；
4. 因此 benchmark、baseline、backbone 和训练方法继续保持未冻结。

`goal_change_requested=false`。
