# Task report：producer scorer seed 1/2 与 transport regression / 2026-09-27

状态：`PARTIAL`；`goal_change_requested=false`。本轮检查 scorer 没有把 seed-0 的类名写死，
并验证 timeout/permission/malformed response 不会制造 label。

## 运行前冻结与证据

冻结同一 TeamBench pin、DIST1 generator、producer-only 文件和 scorer schema；seed 1 的
class pair 是 `EventQueue/PriorityEvent`，seed 2 是 `JobQueue/PriorityJob`。脚本为
[`scripts/peerrolebench_producer_scorer_seed_regression.py`](../../scripts/peerrolebench_producer_scorer_seed_regression.py)，
完整配置、raw、private worker response 在
[`experiments/logs/n03_producer_scorer_seed_regression_20260927/`](../../experiments/logs/n03_producer_scorer_seed_regression_20260927/)。
全程零 LLM、零 GPU、未调用 native grader。

seed 1 原始 source 返回 `FAIL, 0.2857`；seed 2 在完整压力检查中触发 worker-exit，保守
返回 `UNKNOWN`。两者都没有意外 `PASS`。单元注入的 TimeoutError、PermissionError、
malformed response 均写出 `UNKNOWN`，response.json 仍记录 transport/result。

## Goal 对照

- **ER-G3**：部分满足。seed-dependent interface、digest 和 UNKNOWN 语义通过；完整压力
  resource outcome 仍说明 scorer 不是稳定 benchmark label。
- **ER-G4**：部分满足。配置/raw/response 和 9 项 transport/scorer tests 可重现；无真实
  API episode。
- **ER-G1/ER-G2**：未开始。没有 judgment calibration、future assignment、baseline 或
  online update。

## 下一步与限制

scorer 仍只对当前 TeamBench DIST1 source shape 做诊断；P2 forced-race、P7 资源上限和
Python instrumentation 的 non-adversarial 边界不能被写成通用安全或 benchmark 资格。
下一步是冻结第二 structural root 与 same-information baseline，再决定是否值得用新 card
跑一条真实 API 链；如果 scorer 返回 UNKNOWN，只记录诊断，不更新 controller。Goal 不变。
