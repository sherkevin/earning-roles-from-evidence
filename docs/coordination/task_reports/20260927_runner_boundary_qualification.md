# Task report：runner exception/retry 与 scorer 边界资格检查 / 2026-09-27

状态：`PARTIAL`。`goal_change_requested=false`。本任务只推进 Goal v1.0 的 ER-G3、ER-G4
工程门，不把诊断结果写成 benchmark 或方法效果。

## 目的与冻结条件

本轮回答一个窄问题：真实 runner 在 producer、delivery、recipient judgment 或
scorer 阶段异常时，是否会把中断误当成负标签；retry 是否会被当成第二个样本；
scorer 的超时、权限错误、缺失回执和非法 JSON 是否会绕过 evidence/update。

冻结输入是 N02 v3 的完整 15-event ledger：
[`ledger.json`](../../experiments/logs/n02_peerrole_dev_v3_20260926/ledger.json)。执行脚本为
[`peerrolebench_runner_boundary_qualification.py`](../../scripts/peerrolebench_runner_boundary_qualification.py)。
脚本不调用 LLM、native scorer 或 GPU；所有输出写入
[`n03_runner_boundary_qualification_20260927_v3`](../../experiments/logs/n03_runner_boundary_qualification_20260927_v3/)。

## 结果

- 完整 v3 ledger：`PASS` 且允许 update（仅表示账本可重放）。
- 在 selection、delivery、judgment 后截断并标记为 runner exception：均为显式
  `UNKNOWN`，缺失阶段被列出，`learning_update_allowed=false`。
- 插入 `producer_retry` 事件：`INVALID / unsupported_retry`，不会形成第二个样本。
- scorer `timeout`、`permission`、`transport_error`、`invalid_json`、`missing_coverage`：
  全部为 `UNKNOWN`，且 `update_allowed=false`。
- `pass` scorer 分支是唯一可产生 terminal label/evidence update 的诊断分支；本轮
  没有真正启动 hidden scorer。

本轮边界与 replay 集成测试通过。运行摘要的
`all_expectations_met=true`、`scientific_claim_allowed=false`。

## Goal 对照与边界

| Goal | 状态 | 支持的结论 | 尚不能支持 |
|---|---|---|---|
| ER-G3 causal ledger/UNKNOWN | `PARTIAL` | 父端对中断、非法 retry 与 scorer transport failure 的 disposition 已有可执行矩阵 | 未验证真实 runner 中的 hidden scorer/operator 独立进程与 IPC；未证明网络重试实现遵守该合同 |
| ER-G4 reproducibility | `PARTIAL` | config/raw/summary、fixture hash、case-level verdict 均落盘 | 没有 agent output、terminal score 或学习结果 |
| ER-G1 scientific chain | `OPEN` | 只排除了部分错误标签路径 | 没有 judgment 的信息价值、责任归因或未来任务收益 |
| ER-G2 online update | `OPEN` | 不完整/错误链不会进入 update | 没有实时性、稳定性、遗忘或性能证据 |

## 根因与下一步

当前 runner 的 retry policy 是“阶段尝试不重试”；异常只写 `stage_error`/`stop`，账本
保留已发生前缀。这一政策在父端 replay 下是安全的，但它不是 hidden scorer 的实现，
也没有把 scorer 回执通过独立 IPC 注入实际 runner。

下一步应在一个新冻结的、仍然零 LLM 的 runtime fixture 中实现独立 scorer worker：
candidate 只收到公开评分回执，不可读取 expected/score payload/operator ledger；父端记录
worker 的 response digest、退出码、超时与权限错误，并把合法回执接入真实 ledger replay。
这一步通过后，才有理由冻结 PIPE3 的真实 API 小流。Goal 不变。
