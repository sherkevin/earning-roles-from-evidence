# Task report：runner 的 producer-score 边界接入 / 2026-09-27

状态：`PARTIAL`；`goal_change_requested=false`。本轮把已经通过协议测试的 producer
scorer 接到真实 closed-loop runner 的可选 delivery 后边界，但没有启动新的真实 API
episode，也没有允许它驱动 controller。

## Goal 对照

- **ER-G3**：部分满足。card 声明 `producer_scorer` 时，runner 在 delivery 封存后、
  judgment 请求前，对 producer-owned digest 运行 scorer，并把 response 作为独立
  `ProducerScore` 写入 ledger；旧 `TerminalOutcome`/recipient score 未被覆盖。
- **ER-G4**：部分满足。新增路径有 source-hash freeze、worker config/raw response、
  response digest 和 replay gate；本轮没有 LLM/GPU，因此没有科学效果证据。
- **ER-G1/ER-G2**：未开始。controller 仍只使用既有 integration-action update，
  producer score 暂不作为训练标签。

## 实现与验证

runner 新增 `producer_interface_names` 和 `append_producer_score`；只有 card 明确设置
`producer_scorer` 才会调用
[`scripts/peerrolebench_producer_scorer.py`](../../scripts/peerrolebench_producer_scorer.py)。
adapter 只把 `queue.py`、`priority.py` 和 operator support 文件放进 private worker，
不会把 `consumer.py`、ledger 或 native grader 传给 producer scorer。完整结果必须满足
artifact digest、schema、check inventory、label/coverage 和 response digest；否则保持
UNKNOWN。

`tests/test_peerrolebench_runner_producer_score.py` 验证了接口类名来源、UNKNOWN score
写入和完整 replay；目标回归共 `112 passed`，py_compile 与 diff check 通过。旧 N02 v3
仍未重跑，当前配置没有 `producer_scorer` 字段。

## 未完成、原因与下一步

| 门 | 状态 | 原因 |
|---|---|---|
| live scorer invocation | `PARTIAL` | 代码路径可调用，尚无新的 API episode 记录 |
| producer score 驱动 role update | `OPEN` | 必须先定义同信息 baseline、延迟/UNKNOWN 规则和训练目标 |
| scorer qualification 完整性 | `PARTIAL` | seed 0 五格通过；P5/P6/P7 near-miss 与 transport mutation 仍需补齐 |
| benchmark qualification | `OPEN` | 单 structural root、任务文本泄露和 native scorer 边界未关闭 |
| A800/实时更新 | `OPEN` | 尚无有效 producer/judgment signal，按 Goal 禁止启动 |

下一步扩展 scorer qualification matrix，并在新 runner card 中做一条极小真实链路；先只
验证 response/ledger/UNKNOWN，不让 producer score 进入 controller。只有在这条链路和第二
structural root 都合格后，才讨论 N04 baseline 与 A800。
