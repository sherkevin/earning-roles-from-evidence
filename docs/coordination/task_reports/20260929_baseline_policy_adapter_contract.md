# 2026-09-29 baseline policy adapter contract

## 任务目的

承接 [executable parity audit](20260929_baseline_executable_parity_audit.md)，把两个可以在当前公开反馈合同下定义的 comparator 接入统一 `BaselinePolicy` factory，并用同一零调用 schedule 验证信息边界。RARE 不在本任务中伪装成完整 policy。

## 实现

- `RawAcceptancePolicy`：读取独立的 `raw_acceptance` public channel；沿用 candidate+context Beta 状态，使比较只改变责任过滤，而不同时改变 context capacity。只接受 `accept/reject` action，其他 action 不转成负标签。
- `PooledControllerPolicy`：读取公开 `recipient_judgment`，按 `candidate_id@candidate_version` 共享历史，不区分 context 或 selector，用于集中历史上界对照。
- `FEEDBACK_SOURCES` 增加 `raw_acceptance`；`policy_from_name`、`BaselinePolicy.restore` 和 snapshot contract 已覆盖两个新 policy。
- qualification schedule 增加 raw acceptance event，并为六个可执行 comparator 固定 expected update count。

RARE 仍只有 `RareAnchorState` candidate updater，缺少 feature encoder、selection-boundary binding、captured feature replay 和统一 runner adapter，因此保持未实现状态。

## 证据

运行前由 qualification 脚本写入配置，运行：

```text
python3 -m pytest -q \
  tests/test_peerrolebench_baseline_policies.py \
  tests/test_peerrolebench_candidate_registry.py \
  tests/test_peerrolebench_policy_projection.py \
  tests/test_peerrolebench_policy_sidecar.py \
  tests/test_peerrolebench_event_time_schedule.py \
  tests/test_peerrolebench_raresafe_candidate.py
python3 scripts/peerrolebench_baseline_policy_qualification.py \
  --out-dir experiments/logs/n03_baseline_policy_contract_20260929_v4
```

结果：**44 passed**；六个 policy comparator 的 qualification `passed=true`；`real_api_calls=0`、`gpu_jobs=0`、`scientific_claim_allowed=false`。逐事件 JSONL、配置和 snapshot 在 `experiments/logs/n03_baseline_policy_contract_20260929_v4/`。

## 边界

这只关闭了“六个 comparator 可以共享同一离线接口”的工程子门。它没有证明 raw sidecar 已接入 PIPE3，也没有证明 responsibility-aware gate、root scorer、独立进程、完整成本、later assignment 或效果 parity。当前 `PolicyFeedbackProjection` 和 `FeedbackSidecar` 仍只支持 responsibility-attributed public label，因此 raw channel 还需要独立的 root runner projection；不能把本次 direct `Feedback` qualification 当成 live runner qualification。

## Goal 对照

| 目标 | 状态 | 说明 |
|---|---|---|
| baseline 名称都有可执行 comparator | `PARTIAL_PASS` | 六个已可构造，RARE 仍未接入 |
| 同信息与责任边界公平 | `OPEN` | raw projection、PIPE3 runner 和成本账本仍未完成 |
| benchmark 冻结 | `OPEN` | root、authority、clean replay 和 independent streams 仍未通过 |
| 科学效果、实时训练、A800 | `OPEN` | 本任务零 API/零 GPU，无效果结论 |
| Goal 与创新点 | `UNCHANGED` | 没有降级或改写主张 |

## 下一步

先为 raw acceptance 定义并 qualification 独立 public projection，再将六个 comparator 接入同一个 versioned runner；随后把 RARE 的 feature/selection adapter 接入，做全矩阵 replay 和 fault injection。全部通过前，baseline 仍为 `NOT_FROZEN`。
