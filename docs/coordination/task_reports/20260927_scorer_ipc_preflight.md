# Task report：独立 scorer IPC preflight / 2026-09-27

状态：`PARTIAL`。`goal_change_requested=false`。本任务推进 ER-G3、ER-G4 的隔离与可审计
边界，不把 fixture 判分写成 benchmark 或方法效果。

## 目的与冻结条件

目标是验证 scorer 是否能在独立 sandbox worker 中持有 private expected digest，并通过
只含公开字段的请求返回结构化 `PASS/FAIL`；candidate-side probe 不能读取 scorer 的
trusted worker 路径。冻结输入是 N02 v3 ledger，delivery artifact digest 来自其真实
`producer_delivery` payload。没有 LLM、GPU 或 native grader。

## 实际执行与结果

- v1 失败被保留在 [`n03_scorer_ipc_preflight_20260927`](../../experiments/logs/n03_scorer_ipc_preflight_20260927/)。根因是把 ledger 文件整体 hash 当成 delivery artifact hash；正确 artifact 被误判为 `FAIL`。这不是静默修正，原始 worker/response 记录保留。
- v2 使用修正后的 delivery digest，在 [`n03_scorer_ipc_preflight_20260927_v2`](../../experiments/logs/n03_scorer_ipc_preflight_20260927_v2/) 通过：private scorer 对正确/错误 digest 分别返回 `PASS/FAIL`，响应 digest 落盘；candidate probe 读取 scorer trusted worker 得到 `PermissionError`。
- config 明确记录 `candidate_received_hidden_expected=false`、`independent_hidden_scorer_ipc=true`、`scientific_claim_allowed=false`。v2 不含真实 agent 生成或任务 hidden tests。
- 单元/回归检查共 `100 passed`，新增 worker 与 parent preflight 均 `py_compile` 通过。

## Goal 对照

| Goal | 状态 | 本轮证据 | 仍未满足 |
|---|---|---|---|
| ER-G3 hidden scorer/operator 边界 | `PARTIAL` | 独立 scorer worker、private truth、candidate read denial、结构化 response digest | 真实 hidden scorer 语义、operator ledger IPC、retry/timeout live runner 尚未接通 |
| ER-G4 可审计实验 | `PARTIAL` | v1 失败与 v2 修复分版本保存，config/raw/summary 和 worker hashes 齐全 | 没有真实 API episode 或科学结果 |
| ER-G1 科学链条 | `OPEN` | 只验证了隔离边界 | 没有 producer correctness、situated judgment 信息价值或未来任务收益 |
| ER-G2 在线训练 | `OPEN` | 未触碰 updater/backbone | 没有实时性、时效性、稳定性或遗忘证据 |

## 根因与下一步

v1 暴露了 artifact digest 与 ledger-file digest 的概念混淆，说明 scorer 请求合同必须
明确区分 delivery identity、ledger identity 和 response identity。v2 修复了该实现错误，
但仍只是 fixture truth。下一步把 scorer worker 的 response/exit/timeout/permission
记录接入真实 closed-loop runner，并用实际 producer/recipient payload 做一次新的冻结
开发流；在此之前不启动 A800，也不宣称 benchmark 已合格。Goal 不变。
