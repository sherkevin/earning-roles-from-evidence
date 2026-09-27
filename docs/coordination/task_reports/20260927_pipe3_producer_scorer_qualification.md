# Task report：PIPE3 producer scorer qualification / 2026-09-27

状态：`PARTIAL`；`goal_change_requested=false`。

## 对应 Goal

本任务推进 ER-G3 的第二 root 评分边界和 ER-G4 的失败可复现性。它只资格化了
PIPE3 的 producer objective `Q_p`，没有把 PIPE3 冻结为 benchmark，也没有启动真实
API、Nebula 或 GPU。

## 先失败、后修正

第一次 v1 运行使用独立 PIPE3 scorer，但把“原始 JSONL 字节必须含 literal 非 ASCII”
当成 producer 条件。正确 producer 的 `json.dumps` ASCII escaping 因此被误判为
`UNKNOWN`/不完整；完整回执保留在
[`v1`](../../experiments/logs/n03_pipe3_producer_scorer_qualification_20260927/)。

这不是数据失败，而是责任边界错误：processor 的 UTF-8 读写属于 recipient/adoption
目标。ADR 0036 将规则改为“文件字节可按 UTF-8 解码，JSON 解码后字段语义保真”，并保留
严格时间戳 `T` 分隔符、记录数量/顺序和 producer API 检查。

## v3 冻结矩阵与结果

[`experiments/logs/n03_pipe3_producer_scorer_qualification_20260927_v3/`](../../experiments/logs/n03_pipe3_producer_scorer_qualification_20260927_v3/)

运行前冻结了 scorer/worker hash、TeamBench pin、seed 0/1、case digest、请求 schema、
失败规则和 negative controls；使用 pinned sandbox fresh worker，0 LLM、0 GPU、0 native
grader。结果：

| case | 结果 | 解释 |
|---|---|---|
| authored-correct，seed 0/1 | `PASS/1`, decision+coverage complete | 两个同 root domain 变体均通过 |
| original delivery，seed 0/1 | 完整 `FAIL/0`，质量为 `2/3` | 只命中 producer 的空格时间戳问题；不测 processor 缺陷 |
| producer SyntaxError，seed 0/1 | `FAIL/0`, decision complete、coverage incomplete | candidate-origin `SYNTAX_ERROR_IN_DELIVERY` |
| trusted-driver TypeError、timeout、digest mutation、decision incomplete | `UNKNOWN`, label null | 不可观测或回执不可信 |

v3 通过了这张 producer 控制矩阵，但 `scorer_is_qualified=false` 仍然成立：它是一个
TeamBench-shaped、非对抗 Python worker，尚未覆盖 recipient-self、sink adoption、真实
runner root adapter、完整 ledger replay 或第二结构 root。

## 与 Goal 的对照

已满足：PIPE3 producer 责任边界有独立 versioned scorer；候选失败和 scorer UNKNOWN
可区分；两个 seed 的字段重命名和非 ASCII 语义值通过；v1/v2 测量错误和日志未被覆盖。

部分满足：第二 root 的上游 `Q_p` 现在有可复用的封存/digest/scorer seam，但还没有
完整的三元责任指标 `(Q_p,Q_r,adoption)` 或真实 agent 流。

未满足：benchmark freeze、同信息 baseline、recipient situated judgment、未来 assignment、
在线训练效果和 A800。原因是 runner 仍以 DIST1 路径和接口为中心，且 recipient/adoption
评分尚未实现；不是 Goal 降级。

## 下一步

实现 root-specific 的 PIPE3 recipient-self/adoption preflight，先用四格零 LLM 控制和
完整 `selection → delivery → ProducerScore → judgment → action → TerminalOutcome → evidence`
回放验证边界；Qp 必须在 judgment 前，UNKNOWN 不得更新。通过后再考虑一条极小真实 API
链，暂不修改旧 DIST1 runner、旧日志或 N03 API 预算。
