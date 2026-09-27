# Task report：producer scorer v2 failure-disposition matrix / 2026-09-27

状态：`PARTIAL`；`goal_change_requested=false`。

## 对应 Goal

本任务推进 Goal v1.0 的 ER-G3（producer contract 可测、UNKNOWN 与负标签分开）和
ER-G4（真实实验前冻结失败规则、保存逐 case 原始证据）。它没有完成 benchmark
qualification、situated judgment 信息价值或在线 role learning，因此没有改变 Goal 标准。

## 冻结与实现

新增 ADR 0035 和 versioned scorer `dist1-producer-objective-v2`。v2 将
`decision_complete` 与 `coverage_complete` 分开：候选文件在已资格化 runtime 中发生
可复现的、traceback 指向 producer-owned path 的 `DATACLASS_FIELD_ORDER` 或
`SYNTAX_ERROR_IN_DELIVERY` 时，返回 `FAIL, label=0, quality_score=0`; 后续行为检查
明确记录为 `UNKNOWN/blocked_by_import_gate`。worker/driver/权限/超时/digest/schema
错误仍然是 `UNKNOWN`。

协议的 `ProducerScore` 事件新增 `decision_complete`，runner 只对新版本识别候选 hard
decision；旧 v1/v2 response、ledger 和 live episode 没有被回写。未知 scorer version
不会静默回退到 v1。

## 实验与证据

运行前写入配置和 case digest，运行中写入 JSONL 事件，运行后保存逐 case response、
transport 和 summary：

[`experiments/logs/n03_producer_scorer_v2_qualification_20260927/`](../../experiments/logs/n03_producer_scorer_v2_qualification_20260927/)

该矩阵为 0 LLM、0 GPU、0 native grader，使用 pinned sandbox 和 fresh worker：

| case | 预期/观察 | 关键证据 |
|---|---|---|
| authored-correct（重复2次） | `PASS/1`, decision+coverage complete，重复一致 | response digest 相同 |
| 候选 dataclass 字段顺序错误（重复2次） | `FAIL/0`, decision complete、coverage incomplete，来源 `mqueue/priority.py` | `DATACLASS_FIELD_ORDER` |
| 候选 SyntaxError | `FAIL/0`, decision complete、coverage incomplete | `SYNTAX_ERROR_IN_DELIVERY` |
| 可导入的 priority near-miss | 完整覆盖 `FAIL/0`, quality `5/7` | 仅 contract checks 失败 |
| trusted-driver TypeError、timeout、digest mutation、incomplete response | 全部 `UNKNOWN`, 无 label | negative-control 回执 |

矩阵执行通过，说明新的标签边界在这些预注册控制上可运行；`scorer_is_qualified` 仍为
false，因为 Python instrumentation 不是 hostile-code 隔离证明，第二结构 root、真实
责任流和同信息 baseline 尚未完成。

## 与 Goal 的对照

已满足：失败规则被写入 ADR；新 schema 可执行；候选失败与测量失败可区分；历史结果
未被重写；控制矩阵和原始日志可复查。

部分满足：producer objective 现在可以形成更干净的标签，但尚未证明它对真实任务的
覆盖、跨 root 稳定性或 recipient situated judgment 有信息价值。

未满足：ER-G1 的完整因果链、ER-G2 的最终在线训练机制、ER-G3 的 benchmark freeze、
ER-G4 的真实独立流和 A800 条件。原因是第二 root/责任测量/强 baseline 仍未过门，不是
因为本次离线矩阵失败。

## 下一步

先把 v2 资格结果并入 N03 gate，补齐 PIPE3 的真实 producer scorer 与两个 root 的同信息
baseline；只有 scorer/ledger/责任证据都通过后，才冻结一张最小真实 API card。这个
任务不触发新的 API 或 GPU，也不重新运行已关闭的 neutral-v2 路线。
