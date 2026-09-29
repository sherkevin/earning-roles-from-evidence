# 2026-09-29 baseline executable parity audit

## 任务目的

本任务回归主线，检查候选 benchmark manifest 中列出的 baseline 是否真的能由同一套 policy factory 构造。它只审查工程可执行性，不产生 benchmark 效果，不改变 active benchmark 计划，也不改变 Goal、故事线或方法论。

## 冻结范围与命令

运行前写入了配置：
`experiments/logs/n03_baseline_parity_audit_20260929/config.json`。

固定输入：

- manifest：`configs/aamas2027/n03_benchmark_baseline_candidate_v2.json`；
- policy factory：`scripts/peerrolebench_baseline_policies.py:policy_from_name`；
- RARE candidate state：`scripts/peerrolebench_raresafe_candidate.py:RareAnchorState`；
- 当前代码提交：`ca8e5402c7dde8fa2a69d429d54b8c6de14c2e62`；
- real API calls：0；GPU jobs：0；scientific claim：禁止。

执行了：

```text
python3 scripts/peerrolebench_validate_manifest.py \
  configs/aamas2027/n03_benchmark_baseline_candidate_v2.json
python3 - <<'PY'  # 对 manifest 的 7 个名称调用 policy_from_name
...
PY
python3 -m pytest -q \
  tests/test_peerrolebench_baseline_policies.py \
  tests/test_peerrolebench_candidate_registry.py \
  tests/test_peerrolebench_baseline_bridge_audit.py \
  tests/test_peerrolebench_raresafe_candidate.py \
  tests/test_peerrolebench_policy_projection.py \
  tests/test_peerrolebench_policy_sidecar.py \
  tests/test_peerrolebench_event_time_schedule.py
```

逐项原始调用结果在 `raw.jsonl`，汇总在 `summary.json`。

## 结果

manifest 的结构检查为 `PASS`，它确认了两个 root、七个名称和共享信息字段，但这不等于 baseline 已经可执行。

| baseline | 统一 `policy_from_name` | 当前状态 |
|---|---:|---|
| `uniform` | PASS | `UniformPolicy` |
| `no_update` | PASS | `NoUpdatePolicy` |
| `raw_acceptance` | FAIL | 没有 policy adapter |
| `terminal_only` | PASS | `TerminalOnlyPolicy` |
| `contextual_trust` | PASS | `ContextualTrustPolicy` |
| `pooled_controller` | FAIL | 没有 policy adapter |
| `RARE` | FAIL | factory 不支持；另有 `RareAnchorState` candidate state |

定向测试为 **44 passed**。这些测试证明已有四个 policy 的 choose/feedback/snapshot、版本身份、selected-only、UNKNOWN no-update、事件时序和副作用边界；它们没有证明七个 baseline 的 parity。

## 科学含义

当前状态必须写成：

```text
manifest structurally valid
but executable baseline matrix NOT_READY
```

不能把 `raw_acceptance` 当成 `contextual_trust` 的别名，因为两者要区分责任过滤的增量；它们需要不同的公开 feedback projection。也不能把 `RareAnchorState` 当成 RARE baseline：它目前只是 CPU candidate updater，尚未绑定 candidate menu、selection snapshot、propensity、arrival schedule、policy feedback 和统一 runner。

因此本次审计不启动真实 API、不启动 A800、不冻结 benchmark/baseline，也不修改历史结果。Goal 保持不变。

## 下一小步

在新实验前完成三个可审计 adapter：

1. 明确定义 `raw_acceptance` 的公共输入通道，使它读到合法 recipient accept/reject，但不读取 responsibility-aware producer eligibility；
2. 定义同一 candidate menu 和同一公共历史下的 `pooled_controller`，禁止读取 private scorer 或其他 policy state；
3. 把 `RareAnchorState` 包成统一 `BaselinePolicy` adapter，明确 selected-only、版本、延迟、UNKNOWN 和 snapshot 语义。

每个 adapter 先通过零调用 contract/replay qualification，再进入 full-chain runner。若这些 adapter 不能在同一信息与成本合同下运行，baseline 仍保持 `NOT_FROZEN`。

## Goal 对照

| 目标 | 状态 | 说明 |
|---|---|---|
| benchmark/baseline 选择足以识别主张 | `OPEN` | 名单虽完整，统一可执行 parity 未完成 |
| 同信息公平比较 | `OPEN` | raw/pooled/RARE 的公共字段合同尚未落地 |
| 实时更新与稳定性科学证据 | `OPEN` | 本次为零调用工程审计 |
| 故事线、方法论和创新点 | `UNCHANGED` | 没有用工程缺口降级目标 |
| 是否允许新 API/A800 | `NO` | 先补齐可执行 baseline 和 runner parity |
