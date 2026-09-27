# Task report：neutral DIST1 real episode / 2026-09-27

状态：`UNKNOWN`（协议/评分覆盖不足）；`goal_change_requested=false`。

## 运行前冻结

使用 [`n03_peerrole_dev_neutral_v1.json`](../../configs/aamas2027/n03_peerrole_dev_neutral_v1.json)，
TeamBench pin `d185aef1916fd86a9ba554d581fd256319a973af`，`dist1-neutral-v1` material adapter，
provider `内部` / `qwen3.8-max`，thinking disabled。只尝试 episode 0；episode 1 未启动。
旧 v1 prepare 在请求前因 source snapshot 过期被拒绝，随后新建 v2 prepare；两次状态均保留。

## 真实 API 与原始证据

完整三次请求和所有 SSE/parsed response/cost/raw ledger 保存在
[`n03_peerrole_dev_neutral_prepare_20260927_v2`](../../experiments/logs/n03_peerrole_dev_neutral_prepare_20260927_v2/)。

| stage | HTTP | wall(s) | input | output | stop |
|---|---:|---:|---:|---:|---|
| producer | 200 | 15.471 | 824 | 839 | end_turn |
| judgment | 200 | 7.651 | 1,874 | 282 | end_turn |
| consumer | 200 | 5.795 | 2,146 | 364 | end_turn |

producer 返回了 queue/priority 交付；recipient 的 judgment 是 `accept_with_rework`，明确
指出 consumer 需要解包 receipt/message、成功后确认、失败后 nack，并只修改自己的
`consumer.py`。producer scorer 返回 `UNKNOWN`（20 秒 RPC timeout）；完整原始结果仍在
`episode_0/producer_score.json`。

## 为什么不能把它当作模型失败或学习结果

中性 v1 任务文本只说“receipt-based acknowledgement”与“空队列行为”，没有固定：

- `get()` 返回 `(message, receipt)` 还是 `(receipt, message)`；
- 空队列必须立即返回 `None` 还是等待；
- 确认方法叫 `ack`、`acknowledge` 还是其他公开方法。

producer 采用 `(receipt, message)`、阻塞式 `get(timeout=None)` 和 `acknowledge`；recipient
按同一交付自洽地修复。现有 hidden scorer 却要求 `(message, receipt)`、空队列非阻塞和
`ack/nack`，因此 producer scorer 在压力边界超时；consumer scorer 的第一项也超时，
其余三项未运行。runner 将 episode 正确标为 `UNKNOWN`，没有 terminal outcome、role
evidence、future assignment 或 controller update，state 分数保持 `0.5`。

这暴露的是 benchmark contract 与 scorer contract 不一致，而不是 situated judgment 的
正/负效果。当前 episode 只能支持“真实 API、recipient 实际读交付并提出具体修复”的
工程事实，不能支持 producer label、RARE 学习、peer specialization 或 baseline 胜负。

## 修复与下一步

保留 v1 失败和全部成本；不修改历史结果。下一版 `dist1-neutral-v2` 必须在公开材料中
固定 `get() -> None | (message, receipt)`、非阻塞空队列、`ack(receipt)`、`nack(receipt)`
及 `put` 的容量异常语义，并让 hidden scorer 使用同一接口。完成零 LLM contract regression
后，才决定是否再跑一条 v2 episode；若仍出现 UNKNOWN，停止该 card，不扩充样本或启动 A800。
