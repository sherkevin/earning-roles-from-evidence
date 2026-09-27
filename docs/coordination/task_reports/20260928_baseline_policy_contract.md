# 2026-09-28 baseline policy contract qualification

## 对应 Goal

本任务对应 Goal v1.0 的 baseline 可执行性、同信息公平比较和 selected-only 更新边界。它承接 2026-09-27 的 baseline implementation audit。

## 冻结与实际执行

在运行前固定了四个实现条件、versioned candidate schema、公开反馈 disposition/provenance、重复事件规则和“不启动真实 API/GPU”的范围。执行了：

```text
python3 -m pytest -q tests/test_peerrolebench_baseline_policies.py
python3 scripts/peerrolebench_baseline_policy_qualification.py \
  --out-dir experiments/logs/n03_baseline_policy_contract_20260928
```

单测结果为 `8 passed`；qualification summary 为 `passed=true`、`real_api_calls=0`、`gpu_jobs=0`。原始配置、逐事件 JSONL 和 summary 在 `experiments/logs/n03_baseline_policy_contract_20260928/`。

## 结果

新增 `BaselinePolicy` 实现草图：uniform、no_update、terminal_only、contextual_trust。选择快照现在保留 selector、候选版本、模型/特征 schema、决策时间和可选 features；反馈只引用 source decision，并区分公开/未知 disposition。测试覆盖频道隔离、版本隔离、菜单置换、propensity、UNKNOWN no-update、重复幂等和 snapshot/restore。

## Goal 对照

| 标准 | 状态 | 原因 |
|---|---|---|
| 故事线与 RARE 主线 | `MAINTAINED` | 只实现强对照接口，没有修改故事或创新点 |
| baseline 具备统一可运行入口 | `PARTIAL` | 四个离线 policy 可运行；尚未接入真实 root/ledger/scorer |
| 公平、责任归因和完整成本 | `OPEN` | runner 尚未提供 producer/action/version/延迟的完整公开事件 |
| 科学效果、实时训练、A800 | `OPEN` | 本任务无真实 API/GPU，qualification 明确不支持科学 claim |
| Goal 与创新点 | `UNCHANGED` | `goal_change_requested=false` |

## 下一步

先把 PIPE3 runner 的公开事件映射到该接口，并在离线 ledger replay 中验证同一 candidate set、propensity、延迟和成本输入；随后才决定 Beta comparator 的 propensity/label mapping，并接入 RLS/RARE。通过这些门之前不启动新的真实 API 或 A800。
