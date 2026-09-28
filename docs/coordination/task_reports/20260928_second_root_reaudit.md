# 2026-09-28 第二 root 独立复审

## 任务

复核 PIPE3 与 MULTI3 是否具有可归因的 producer delivery、recipient 自有工作、实际 artifact adoption 和可分离评分。任务只做 pinned TeamBench 源码的零 API 组合审计，不调用 LLM、真实 scorer 或 GPU。

## 证据

- 复审报告：[n03_second_root_reaudit_20260928.md](../../research/n03_second_root_reaudit_20260928.md)
- MULTI3 直接组合原始记录：[n03_multi3_direct_composition_audit_20260928](../../../experiments/logs/n03_multi3_direct_composition_audit_20260928/)
- TeamBench pin：`d185aef1916fd86a9ba554d581fd256319a973af`

PIPE3 的 producer.py、processor.py 和 downstream sink 构成了可分离的责任候选，已有 Qp/Qr/adoption 控制矩阵和 seed-0 sidecar fixture；但 fixture 是手工构造，尚未证明 root-specific live runner 能产生完整事件链。

MULTI3 的 native tests 使用预先构造的 `correct_wire`/`correct_envelope`，没有把 backend `serialize_batch` 输出交给 frontend `process_envelope`。seed 0/1/2 的直接组合均失败，因此不能把 native pass 或其结构当作 adoption 证据。

## 决策与边界

- PIPE3：`conditional GO`，只进入下一道最小零 API runner qualification。
- MULTI3：`confirmation root NO-GO`，保留为 fallback candidate。
- benchmark freeze、baseline freeze、真实 API 和 A800：均未获准启动。
- sidecar fixture 的 PASS 不足以证明完整 responsibility lineage；下一道 gate 必须把 `delivery_id`、`producer_id`、`recipient_id`、`action_id`、artifact digest 和 canonical ledger event 逐一绑定，并验证延迟/乱序/UNKNOWN replay。

## Goal 对照

| Goal 要求 | 状态 | 说明 |
|---|---|---|
| 故事线与责任归因 | PARTIAL | PIPE3 的责任候选更清晰，MULTI3 不能承担确认 root；真实因果 runner 尚未完成 |
| benchmark 权威性与可检验性 | OPEN | 仍是 TeamBench-derived candidate，不得写成已冻结 benchmark |
| baseline 公平性 | OPEN | 同信息 snapshot/propensity/成本口径尚未接入 PIPE3 live runner |
| 真实协作闭环与学习效果 | OPEN | 零 API 审计，没有 label、update 或效果证据 |
| Goal 变更 | UNCHANGED | 没有提出降级或修改 |

下一步只修复 PIPE3 资格门，不为 MULTI3 直接重写 adapter，也不启动真实 API。该任务的 `real_api_calls=0`、`gpu_jobs=0`、`scientific_claim_allowed=false`。

`goal_change_requested=false`。
