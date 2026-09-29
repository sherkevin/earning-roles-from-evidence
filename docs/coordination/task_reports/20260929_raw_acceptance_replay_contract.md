# 2026-09-29 raw acceptance versioned replay contract

## 任务

把已经通过的 `RawAcceptanceSidecar` public projection 接入 canonical sidecar replay，
使 raw comparator 使用同一 selection、arrival/delay、manifest 和 ledger identity
边界，同时不要求 responsibility-aware attribution gate。

## 实现

- `SidecarRow` 和 `replay_policy_sidecars` 现在接受 `RawAcceptanceSidecar`。
- raw sidecar 先通过 canonical `recipient_judgment` record、selection identity、
  selected producer 和 arrival/delay 校验，再由 `project_raw_acceptance` 生成
  `source=raw_acceptance` 的 typed `Feedback`。
- `require_responsibility_lineage=True` 时 raw sidecar 不伪装成 attributed feedback；
  它跳过责任 gate，而普通 `FeedbackSidecar` 仍必须通过 v3 lineage 校验。
- raw policy 未订阅时计入 `ignored_channel_count`，不会隐式更新其它 comparator。

## 资格运行

运行前写入：
`experiments/logs/n03_raw_acceptance_replay_20260929_v1/config.json`。

命令：

```text
python3 scripts/peerrolebench_raw_acceptance_replay_qualification.py \
  --out-dir experiments/logs/n03_raw_acceptance_replay_20260929_v1
python3 -m pytest -q \
  tests/test_peerrolebench_raw_acceptance_replay.py \
  tests/test_peerrolebench_policy_projection.py \
  tests/test_peerrolebench_baseline_policies.py
```

结果：replay qualification **passed=true**，canonical raw update、canonical decision
mutation、wrong producer、duplicate sidecar 4 个 case 全部符合预期；回归测试
**30 passed**；`real_api_calls=0`、`gpu_jobs=0`、`scientific_claim_allowed=false`。
已有 terminal/lineage replay qualification 也各自通过 5 个 case，未观察到回归。

## 边界

这是 versioned replay/sidecar contract，不是 PIPE3 live runner 或 benchmark effect。
ledger 与 sidecars 是 hand-authored fixtures；还没有证明真实 API actor、scorer、
consumer action 和 root split 能在同一 runner 中产生这些事件，也没有 RARE adapter 或
closest published comparator。

## Goal 对照

| 目标 | 状态 | 说明 |
|---|---|---|
| raw baseline public projection/replay | `PARTIAL_PASS` | projection 与 canonical replay 子门通过 |
| 六 comparator 完整 runner parity | `OPEN` | 真实 PIPE3 runner 和所有 policy cell 尚未完成 |
| benchmark/root/label 资格 | `OPEN` | 不因 fixture replay 通过而改变 |
| 科学效果、实时训练、A800 | `OPEN` | 零 API/零 GPU，无效果数字 |
| Goal/故事线/创新点 | `UNCHANGED` | 没有降级或改写 |

## 下一步

把 raw replay 接到真实 PIPE3 versioned runner；在 runner 内固定 event visibility、
完整成本、fault/UNKNOWN 分母和六 policy parity。RARE 的 feature/selection adapter
仍未实现，完成前 baseline 继续 `NOT_FROZEN`。
