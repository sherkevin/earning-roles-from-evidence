# 2026-09-28 PIPE3 global event-time schedule boundary

- 状态：`DONE`（实时顺序工程子门）
- 对应 Goal：ER-G2（实时更新可验证）、ER-G4（主张与证据一致）
- `goal_change_requested=false`
- 真实 LLM API：0；GPU：0；scientific cell：0

## 问题

`FeedbackSidecar` 的 `arrived_at` 和 `delay` 是审计时间戳，不足以构成可复现的在线
更新顺序。若 runner 在回放时按 wall-clock 或 `(arrived_at, event_id)` 重新排序，迟到
反馈可能在离线阶段被错误地提前应用，无法证明它只影响尚未执行的 decision。

## 实现

新增 `scripts/peerrolebench_event_time_schedule.py`：

- `ArrivalAssignment` 为每条 `recipient_judgment` 或 `terminal_outcome` 指定唯一的
  `feedback_id`、protocol event、source decision 和全局整数 `arrival_index`；
- `validate_schedule()` 拒绝重复 feedback、重复 protocol identity、重复时间索引、
  缺少预期 feedback，以及未知事件类型，并返回 frozen arrival order；
- `schedule_digest()` 对 canonical schedule 产生稳定 digest，输入列表顺序不影响结果。

v1 暂时要求 arrival index 唯一，因此没有隐式 tie-break；若后续需要并发到达，必须把
tie-break 字段显式加入新 schema，而不能恢复 wall-clock 排序。

测试 `tests/test_peerrolebench_event_time_schedule.py` 覆盖 canonical order、重复时间、
重复 protocol identity、缺失反馈和 digest 稳定性；candidate registry、schedule、
assignment manifest、event-time qualification 定向集合共 `16 passed`，并通过
`py_compile` 与 `git diff --check`。

## 边界与下一步

该模块只验证时间轴，尚未把 schedule 接到真实 policy loop；因此没有证明实时训练、
准确率或角色学习。下一步的 `peerrolebench_pipe3_real_runner_v1.py` 必须在每次 decision
前按 `arrival_index <= read_cut` flush，构造 offer，再调用 policy；在线应用顺序和最终
双 manifest replay 必须同时通过。任何 schedule 缺失、乱序、重复或 UNKNOWN 都只保留
审计数据，禁止 policy update。
