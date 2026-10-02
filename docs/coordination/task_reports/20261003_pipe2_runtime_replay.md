# PIPE2 真实 runtime 回执责任门回放

日期：2026-10-03  
状态：`PARTIAL / EVIDENCE-GAP CONFIRMED`；旧 sandbox 回执可重放，但不能形成
producer role evidence。

## 任务目的

把已完成的真实 PIPE2 derived-root runtime qualification 接入当前 responsibility
gate，检查旧回执是否真的包含 situated recipient judgment、consumer action 和独立
terminal outcome 所需字段。该任务禁止从 producer/adoption 分数反推缺失字段，也不
执行候选代码或调用 LLM。

## 实现与冻结输入

新增 `scripts/peerrolebench_pipe2_runtime_replay.py`。它读取冻结的：

```text
experiments/logs/n03_pipe2_derived_root_runtime_qualification_20261003_v3/summary.json
```

并绑定当前派生 root recipe digest。每个 producer control × recipient control 只映射
真实存在的 producer `status/label/artifact_sha256`、recipient adoption status 和
artifact digest；`recipient_judgment`、`consumer_action`、`terminal_outcome` 保持空值，
缺失字段作为显式列表写入 raw JSONL。配置记录输入 summary SHA256、root digest、argv、
git commit、Python/platform 以及 0 API/0 GPU/0 candidate execution。

## 结果

命令：

```bash
python3 scripts/peerrolebench_pipe2_runtime_replay.py \
  --output experiments/logs/n03_pipe2_runtime_replay_20261003_v3
```

结果：`REPLAY_QUALIFIED_UNKNOWN`，40/40 组合通过保守回放，
`ELIGIBLE=0`、`PENDING_ATTRIBUTION=0`、`UNKNOWN=40`、`label_count=0`，
`policy_update_allowed=false`。每一行都明确缺少：

1. recipient 对该交付的结构化 judgment；
2. consumer 是否直接使用/返工/重做及 changed paths；
3. 独立 terminal outcome 与完整性/责任绑定。

这不是失败的模型结果，而是对旧 runtime scorer 可识别性的直接证据：它能证明
producer contract/adoption 维度，却不能证明 situated judgment→attribution。

## Goal 对照

| Goal 要求 | 状态 | 证据 |
|---|---|---|
| 真实交付和 producer correctness | `PARTIAL` | 旧 runtime receipt 有 producer status/label/digest |
| recipient situated judgment | `OPEN` | 40/40 回放均缺该字段 |
| 可归因 role evidence | `BLOCKED_BY_EVIDENCE` | gate 不发 label，避免从 adoption 反推责任 |
| future assignment 与后续质量/成本 | `OPEN` | 没有 source evidence，不能进入 assignment |
| 实时更新与 A800 | `NOT_RUN` | 输入识别门未通过，不启动 GPU |

## 下一步

不改写旧回执、不把 UNKNOWN 当负例。下一步复用已有 PIPE3
`evaluate_source_gate`、`build_role_evidence_from_ledger`、`make_role_evidence_offer`
和 preview→commit seam，设计一个真实小链：在同一真实执行中分别记录 recipient
judgment、action/ownership、independent terminal outcome，再做责任门和 later assignment。
完成这一步前不进入 baseline effect comparison，也不启动 A800。

`goal_change_requested=false`；Goal 与 benchmark/baseline 选择未修改。
