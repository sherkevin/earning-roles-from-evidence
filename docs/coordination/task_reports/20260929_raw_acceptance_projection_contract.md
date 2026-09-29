# 2026-09-29 raw acceptance public projection contract

## 任务

关闭 N03-next-r4.45 的第一个工程子门：为 `raw_acceptance` 定义独立的 public
projection，使它可以读取合法 recipient `accept/reject`，同时不能读取
responsibility-aware producer eligibility、gate、private scorer 或 producer label。

## 实现

- `RawAcceptanceSidecar` 是独立类型，不复用带 attribution gate 的 `FeedbackSidecar`。
- `project_raw_acceptance` 绑定 canonical `recipient_judgment` ledger record、selection
  sidecar、delivery/producer/recipient identity 和 fixed mapping
  `raw-acceptance-v1`。
- 只允许 `accept → 1.0`、`reject → 0.0`；`rework` 等值直接拒绝，不能被静默映射为负例。
- 输出的 `PolicyFeedbackProjection.source` 为 `raw_acceptance`，public payload 不包含
  `responsibility_status`、`attribution_basis`、`gate_digest` 或 `weight`。
- `PolicyFeedbackProjection` 现在明确允许 `raw_acceptance`，现有 `RawAcceptancePolicy`
  可以消费这个 typed feedback。

## 资格运行

运行前写入 `experiments/logs/n03_raw_acceptance_projection_20260929_v1/config.json`，
执行：

```text
python3 -m pytest -q \
  tests/test_peerrolebench_policy_projection.py \
  tests/test_peerrolebench_baseline_policies.py
python3 scripts/peerrolebench_raw_acceptance_projection_qualification.py \
  --out-dir experiments/logs/n03_raw_acceptance_projection_20260929_v1
```

结果：核心 projection/policy 命令 **29 passed**；projection qualification
**passed=true**，6 个结构化 case
（accept、reject、canonical mutation、rework rejection、unchosen candidate、selection
binding）全部通过；`real_api_calls=0`、`gpu_jobs=0`、`scientific_claim_allowed=false`。
随后补跑 sidecar、registry、event-time 和 candidate 相关回归集合，**49 passed**。

## 边界

这是独立 projection seam 的资格，不是 PIPE3 live runner、benchmark、效果或责任标签
资格。record 是 hand-authored canonical-shape fixture；还没有证明真实 runner 能从
每个 root 产生同样的 public event，也没有证明 raw policy 与 RARE/contextual trust
的质量或成本差异。

## Goal 对照

| 目标 | 状态 | 说明 |
|---|---|---|
| raw baseline 有独立信息合同 | `PARTIAL_PASS` | projection seam 已通过零调用测试 |
| baseline 完整可执行与同信息 parity | `OPEN` | versioned PIPE3 runner、closest published adapter、cost parity 未完成 |
| benchmark 冻结 | `OPEN` | authority、root、clean replay、独立 streams 未通过 |
| 科学效果、实时训练、A800 | `OPEN` | 本任务无真实 API/GPU，不产生效果结论 |
| Goal/故事线/创新点 | `UNCHANGED` | 没有降级或改写目标 |

## 下一步

把 `RawAcceptanceSidecar` 接入 versioned PIPE3 runner，补 canonical event / fault
replay（缺 record、错 producer、错 selection、非 accept/reject、延迟/乱序）后，才可
把 raw comparator 放进六 policy parity runner。RARE adapter 仍单独开放。
