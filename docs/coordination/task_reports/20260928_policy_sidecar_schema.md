# 2026-09-28 public policy sidecar schema

## 对应 Goal

本任务对应 Goal v1.0 的版本归因、延迟反馈、公开 provenance、UNKNOWN no-update 和同信息 baseline 要求。

## 实际执行

实现 `DecisionSidecar`/`FeedbackSidecar` 和 ledger record-hash 绑定，执行：

```text
python3 -m pytest -q tests/test_peerrolebench_policy_sidecar.py
python3 scripts/peerrolebench_policy_sidecar_qualification.py \
  --out-dir experiments/logs/n03_policy_sidecar_qualification_20260928_v2
```

测试通过；qualification `passed=true`，`sidecar_version=peerrole-policy-sidecar-v2`，eligible feedback 可转为 policy event，UNKNOWN feedback 不转，事件类型/ID 绑定检查通过，0 API、0 GPU。原始 JSONL 在 qualification 目录。

## Goal 对照

| 标准 | 状态 | 原因 |
|---|---|---|
| situated judgment→role evidence 主线 | `MAINTAINED` | sidecar 只补公共输入，不改故事或创新点 |
| policy 输入可版本化、可重放 | `PARTIAL` | schema、hash、event type/id 离线检查通过，尚未接 PIPE3 runner |
| benchmark/baseline 公平比较 | `OPEN` | 真实 producer/action/延迟/provenance 尚未生成 |
| 科学效果/实时训练/A800 | `OPEN` | 无 API/GPU，只有工程资格 |
| Goal 变更 | `UNCHANGED` | `goal_change_requested=false` |

## 下一步

在 PIPE3 runner 中生成 sidecar 并把 sidecar digest 写入 ledger 公开 event，随后做离线乱序/版本/UNKNOWN replay。没有该回放通过，不启动新的真实 API。
