# History 四格 matched replay qualification

日期：2026-10-04
状态：`QUALIFIED_OFFLINE`（工程门通过；不产生科学效果结论）

## 目的与衡量指标

本任务只验证上一项 `delayed credit → HistoryBindingReceipt → PeerHistoryV2` 接缝是否真的能影响下一次执行前选择。它没有调用 LLM、没有提交 GPU，也不改变 active storyline、method、benchmark、baseline 或 Goal。

预注册四个 matched cells：

| cell | E1 到 E2 的 history 状态 | 必须满足 |
|---|---|---|
| `history` | 合法 append 的一条 source→target history | selector input 引用 projection digest，且选择 propensity 与空历史不同 |
| `no-history` | 空 projection | 使用同一菜单、base score、read cut、RNG |
| `shuffled-history` | 将合法 entry 的 arrival 改到 seal 之前 | fail closed 为 `UNKNOWN`，无选择结果、无更新 |
| `reset-history` | 合法 E1 后恢复空 snapshot | 选择字段与 `no-history` 完全相等 |

每个 cell 记录 `input_digest`、projection digests、scores/probabilities、chosen peer、propensity、UNKNOWN reason、selection trace digest、update count、完整 cost schema 和 component SHA-256。任何失败保持 UNKNOWN，不改写为负例。

## 实现

- `scripts/peerrolebench_history_selector.py` 是仅用于资格测试的确定性 comparator，不是论文提出的 learner。它只接受 `PeerHistoryV2.selector_projection()` 的白名单字段，检查 candidate identity、scope count、read cut 和 scope schema；隐藏字段或未来到达的记录直接拒绝。
- `scripts/peerrolebench_history_four_cell_qualification.py` 复用 canonical PIPE3 native ledger、`RoleEvidenceOffer`、`LaterAssignment`、已提交 `DelayedCreditLedger` 和 history adapter。配置先写入 `config.json`，随后写四个 cell 的 `summary.json` 与 `raw.jsonl`；失败的 v1 也保留。
- v1 在第一次运行时暴露 `LaterCredit.build` 调用未使用关键字参数，配置和失败目录完整保留；修正后 v2 通过。selector 增加 public-field fail-closed 检查后，正式回执使用 v3。

## 正式回执

正式结果：`experiments/logs/n03_peer_history_four_cell_qualification_20261004_v3/`。

- `QUALIFIED_OFFLINE`, `passed=true`；0 LLM/API、0 GPU、`scientific_claim_allowed=false`。
- `history`：一条 entry，`history_input_digest=b9f17b40...`; scores `[0.3333333333, 0]`; probabilities `[0.5825702065, 0.4174297935]`; chosen `peer-a@v1`。
- `no-history`：entry count 为 0；scores `[0,0]`; probabilities `[0.5,0.5]`; chosen `peer-b@v1`。
- `reset-history` 与 `no-history` 的 input digest、scores、probabilities、choice、propensity 完全相等。
- `shuffled-history` 返回 `UNKNOWN`，原因是 `history entry must arrive after assignment seal`，没有 selection、credit 或 policy update。
- 四格 `update_count=0`；每格均记录 15 个 fixture ledger events 和 `cost={api_calls:0,gpu_jobs:0,input_tokens:0,output_tokens:0,tool_calls:0,replay_events:15,wall_ms:...,updates:0}`。
- focused tests：selector/history/adapter/binding 共 `18 passed`；`py_compile` 通过。

## 结论与边界

这一步关闭了一个必要的工程前置：history projection 已被执行前 selector 消费，并且 reset/shuffle 的信息边界可审计。它没有证明 peer suitability、角色专业化、质量/成本收益、实时训练速度、遗忘控制，也没有证明当前 comparator 是最终方法。

仍未关闭的科学门：跨 episode 持久 history、selector 的真实 policy/update、独立 live histories、第二 benchmark structural root、七 arm same-information baseline parity、later-use precision、完整成本和真实 API 结果。A800 继续关闭；下一步只能先把四格接口接入独立 live histories，并保持同信息 baseline 与 UNKNOWN 语义。

`goal_change_requested=false`。
