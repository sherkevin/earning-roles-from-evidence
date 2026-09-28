# 2026-09-28 PIPE3 full responsibility-chain qualification

- 状态：`PARTIAL`（工程资格通过；科学资格、真实 runner 和 benchmark 资格仍开放）
- 对应 Goal：ER-G1、ER-G3、ER-G4；当前阶段门 G1
- `goal_change_requested=false`
- 真实 LLM/API：0；GPU：0；`scientific_claim_allowed=false`

## 本次任务

selection boundary 之后缺少一条可审计的 PIPE3 完整链。本任务新增
`scripts/peerrolebench_pipe3_full_chain_qualification.py`，在不调用 API、不执行候选源代码的
条件下构造两个严格 episode，验证：

```text
peer_selection → task_start → producer_delivery → producer_score
→ recipient_judgment → consumer_action → terminal_outcome
→ role_evidence_update → later_assignment → peer_selection
```

每条反馈 sidecar 使用 v3 的 artifact、delivery 和 action record binding。selection sidecar、
native manifest、assignment offer/consumption auxiliary manifest 和显式 arrival schedule 分开
保存；没有把辅助字段塞进原生账本。

## 冻结与证据

运行前写入了配置、Python 版本、Git commit、candidate registry、协议顺序、故障矩阵和
`scientific_claim_allowed=false`。第一个修复前的运行保留在
`experiments/logs/n03_pipe3_full_chain_qualification_20260928_v1/`，修复 sidecar 版本后
通过的运行是：

`experiments/logs/n03_pipe3_full_chain_qualification_20260928_v4/`

其中包含 `config.json`、`raw.jsonl`、`ledger.json`、`native_sidecar_rows.jsonl`、
`native_sidecar_manifest.json`、`assignment_aux_rows.jsonl`、`assignment_manifest.json`、
`candidate_registry.json`、`arrival_schedule.json` 和 `summary.json`。通过回执的关键值为：

- strict ledger：`PASS`，17 个事件；
- native sidecar：6 行，一对一覆盖 selection/judgment/outcome；
- auxiliary manifest：4 行，offer 在 consumption 之前且链完整；
- arrival schedule：4 个 feedback，唯一且覆盖完整；
- responsibility-aware replay：`PASS`，TerminalOnlyPolicy 的 2 次 eligible terminal update；
- UNKNOWN scorer：停在 delivery/score 后，`update_allowed=false`；
- wrong lineage、迟到 offer、缺失 arrival schedule：均被拒绝。

## 与 Goal 的逐项对照

| Goal 标准 | 本次状态 | 证据/原因 |
|---|---|---|
| 真实交付→判断→责任证据→后续 assignment 的链条可表示 | 部分满足 | 两个零调用 episode 在严格账本上闭合；这是 protocol/runner gate，不是实际 agent 行为。 |
| responsibility attribution 安全 | 部分满足 | v3 sidecar 逐跳绑定 artifact、delivery、action；错误 producer lineage 被拒绝。 |
| `UNKNOWN` 不更新 | 满足工程子门 | unknown scorer case 保留 partial ledger，未产生 update。 |
| 真实 scorer/API 与 hidden isolation | 未满足 | 本次零 API，未执行 actor/scorer，也未证明隔离进程中的 policy-read。 |
| future assignment 真正因 evidence 改变 | 未满足 | fixture 只证明 assignment 可在下一 selection 前封存；没有科学因果效果。 |
| benchmark 两个独立 root、强 baseline、公平预算 | 未满足 | 仍是 PIPE3 条件性候选，未冻结 benchmark/baseline。 |
| AAMAS 科学效果 | 未满足 | 没有真实数据、质量/成本结果或实时训练结果。 |

## 发现的问题与下一步

本次修复了一个真实实现问题：v2 feedback sidecar 无法通过责任 lineage gate；不能通过
放宽校验解决，必须使用 v3。它还确认了一个需要防止的解释错误：完整 ledger 和离线
replay 不能证明 policy 在隔离进程中读取了 evidence，也不能证明后续 assignment 的改变
由 judgment 导致。

下一步是把这条边界接到一个新的、版本化的真实 PIPE3 runner：先完成 actor payload、Qp/Qr/
adoption scorer、action snapshot 和 fault stop，再只运行一条真实 API 小链。只有这条链
同时产生可审计的 producer score、recipient judgment、真实 action/cost、later assignment
和 raw usage，才决定是否进入 N03 开发流；在此前不发起 A800 训练，也不把该资格回执写成
方法效果。
