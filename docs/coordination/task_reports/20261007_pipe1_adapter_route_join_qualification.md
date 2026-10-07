# PIPE1 adapter–route join qualification — 2026-10-07

状态：`QUALIFIED_ZERO_CALL_JOIN_GATE`。本轮增加一个很窄的 join validator，把已经通过
native binding 的 offline adapter 与独立 route receipt 接起来；它只检查两者是否描述
同一个 task 和 allocation，不执行 route、不读模型、不运行候选代码，也不打开策略更新。

## 为什么需要 join

adapter 和 route receipt 各自结构合法，并不保证它们描述同一个选择。若只按顺序调用
两个 validator，adapter 可能选择 `peer-b@v1`，receipt 却记录 `peer-c@v1`，两个局部
检查都会通过，归因仍会脱钩。join 因此要求：

- adapter 必须是 `READY_FOR_ROUTE`，native selection binding、schedule 合法且
  `policy_update_allowed=false`；
- route receipt 自身通过既有 `validate_pipe1_route_receipt`；
- source/target task id 与 adapter 的唯一 task id 一致；
- route registry 顺序、allocation permutation、chosen candidate、probabilities 和
  chosen propensity 与 adapter selection input 一致。

通过后状态是 `READY_FOR_PREFLIGHT`，不是 `COMPLETE`、`attribution_ready` 或科学结果；
任意不一致统一返回 `UNKNOWN`，不产生 label、assignment 或 policy update。native
material binding、provider/timezone、真实 message/artifact/Executor/Verifier lineage、
selected-only 实际输入、精确 scoring、成本和 later-use 仍由独立 preflight/live runner
负责。

## 验收

配置在最终检查前冻结于
[`config.json`](../../../experiments/logs/n03_pipe1_adapter_route_join_qualification_20261007_v1/config.json)。
新增 `scripts/peerrolebench_pipe1_adapter_route_join.py` 及五个正负 join case，联合
adapter、route receipt 和 PIPE3 contract 回归：

- `38 passed`；
- `py_compile` 与 scoped `git diff --check` 通过；
- chosen candidate、task id、selected-only 声明和 adapter update flag 的篡改均
  fail-closed；
- 完整回执见
  [`summary.json`](../../../experiments/logs/n03_pipe1_adapter_route_join_qualification_20261007_v1/summary.json)。

计数为 0 API、0 generator、0 candidate、0 GPU、0 policy update，
`scientific_claim_allowed=false`。本轮只关闭了 adapter/receipt 之间的结构错配风险，
没有打开 PIPE1 benchmark 或投稿 gate。
