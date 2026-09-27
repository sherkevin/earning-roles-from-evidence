# 2026-09-28 baseline bridge audit

## 对应 Goal

本任务对应 Goal v1.0 的 baseline 信息公平、版本绑定、延迟反馈和 selected-only 归因要求。

## 实际执行

冻结输入为历史 N02 v3 ledger；没有修改它，没有真实 API/GPU。执行了 bridge audit 单测和 qualification：

```text
python3 -m pytest -q tests/test_peerrolebench_baseline_bridge_audit.py
python3 scripts/peerrolebench_baseline_bridge_qualification.py \
  experiments/logs/n02_peerrole_dev_v3_20260926/ledger.json \
  --out-dir experiments/logs/n03_baseline_bridge_audit_20260928
```

10 项相关单测通过（包含 baseline policy 回归）；qualification 对 15 条历史事件返回 `NOT_MAPPABLE`，`policy_update_allowed=false`。原始 config/raw/summary 已记录。

## 发现

旧 ledger 没有 candidate version、context/base score、state/model/schema version、selected time，也没有 judgment/terminal feedback 的 arrival/delay/disposition/provenance 或预注册 label mapping。consumer action 仅作为责任/成本证据，不能被误当成 feedback。若强行映射，必然补默认值或混淆 hidden scorer 信息，因此 bridge 现在明确拒绝更新。

## Goal 对照

| 标准 | 状态 | 原因 |
|---|---|---|
| situated judgment→role evidence 主线 | `MAINTAINED` | 只审查数据映射，不改故事/创新点 |
| baseline 可公平比较 | `BLOCKED_BY_EVIDENCE` | 旧 ledger 缺 policy 所需公开 sidecar |
| benchmark freeze | `OPEN` | PIPE3 runner 尚未形成 sidecar + ledger 完整链 |
| 科学效果/实时训练/A800 | `OPEN` | 本任务无新 API/GPU，不能支持 efficacy |
| Goal 变更 | `UNCHANGED` | `goal_change_requested=false` |

## 下一步

为 PIPE3 runner 增加 sidecar schema，并将 sidecar digest 与 selection/feedback ledger 绑定；先做离线无损映射和乱序/版本/UNKNOWN 回放，再考虑新的真实 episode。无需用户决定。
