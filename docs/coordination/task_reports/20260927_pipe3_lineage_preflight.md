# Task report：PIPE3 三元评分与 UNKNOWN lineage preflight / 2026-09-27

状态：`PARTIAL`；`goal_change_requested=false`。

## 对应 Goal

本任务推进 ER-G3 的责任可测性、评分隔离和因果账本边界，也为 ER-G1 的
`交付 → situated judgment → role evidence` 链条提供可回放的工程前置证据。它没有
冻结 benchmark/baseline，没有产生 role-learning 或实时训练效果，也没有启动真实 API
或 A800。

## 失败版本与修正

第一次 v1 运行因 recipient worker 的参数位置错误而全部返回 `UNKNOWN`；完整回执保留在
[`v1`](../../experiments/logs/n03_pipe3_lineage_preflight_20260927/)。修复参数传递后，v2
暴露了一个更有意义的边界：processor 使用 `latin-1` 写入包含 `€` 的 JSON 时，候选处理
异常被错误记成 scorer `UNKNOWN`。worker 随后把 traceback 指向 `processor.py` 的候选处理
失败、以及可观测的非法输出，区分为确定性 `FAIL`；真正的 transport/权限/覆盖异常仍然
保持 `UNKNOWN`。v2 的完整结果也保留在
[`v2`](../../experiments/logs/n03_pipe3_lineage_preflight_20260927_v2/)。

## v5 控制矩阵

最终回执在 [`v5`](../../experiments/logs/n03_pipe3_lineage_preflight_20260927_v5/)；运行
前写入 config，运行中写入 JSONL，运行后保存每个 scorer 的 request/response、digest、
sandbox evidence 和 ledger。该运行 0 LLM、0 GPU、未调用 native grader，使用 seed 0/1，
并分别调用 producer `Q_p`、recipient-self `Q_r` 和 producer→processor→sink adoption。

| case | 预期 `(Q_p,Q_r,adoption)` | 观察（seed 0/1 一致） |
|---|---:|---:|
| all_correct | `(1,1,1)` | `(1,1,1)`，terminal success |
| producer_bad | `(0,1,0)` | `(0,1,0)`，processor 自有工作与 producer 质量分离 |
| recipient_envelope_bad | `(1,0,0)` | `(1,0,0)`，Qp 不惩罚 processor envelope |
| recipient_encoding_bad | `(1,0,0)` | `(1,0,0)`，Qp 不惩罚 processor encoding |
| both_bad | `(0,0,0)` | `(0,0,0)` |

每个完整 case 都回放为 `ledger_status=PASS`，并将 Qp 放在 recipient judgment 之前。
另有 `unknown_scorer_no_update` 控制：只记录 `UNKNOWN ProducerScore`，回放为
`UNKNOWN/incomplete`，没有 judgment、action、outcome 或 role evidence，明确
`update_allowed=false`。因此未知测量不会被转成负例或学习更新。

## 与 Goal 的对照

已满足：PIPE3 的 producer/recipient/adoption 三元责任边界在两个 seed 的受控结构变体
上可分离；Qp、Q_r 和 adoption 不共用一个终局标签；完整 lineage 可以被严格 replay；
UNKNOWN 的 no-update 语义有可审计回执；失败版本未覆盖。

部分满足：这是 root-specific zero-LLM qualification，worker 仍是非对抗式 Python
instrumentation，尚未接入正式 runner，也未证明真实 agent 生成的交付能稳定落入该契约。

未满足：第二独立结构 root、same-information baseline、正式 benchmark freeze、真实
API judgment 流、未来 assignment 的质量/成本后果和在线训练效果。原因是这些证据门仍
未完成，不是 Goal 降级。

## 下一步

先把 recipient/adoption scorer 的控制语义纳入回归测试，接着做一个不复用 DIST1 硬编码
的 PIPE3 runner adapter 和 candidate/hidden scorer process-separation 审查；通过后再决定
是否值得消耗一条真实 API 小流。仍不启动 A800，直到第二 root、强同信息 baseline 和真实
可学习信号同时成立。
