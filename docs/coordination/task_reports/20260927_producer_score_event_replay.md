# Task report：producer-score event 与 replay causal order / 2026-09-27

状态：`PARTIAL`；`goal_change_requested=false`。本轮完成了 producer 质量观测的独立
协议事件和外层 replay 支持，仍没有把该事件接入真实 runner 或 role update。

## Goal 对照

- **ER-G3**：部分满足。`ProducerScore` 只绑定 delivery artifact digest，且必须出现在
  recipient judgment 之前；PASS/FAIL/UNKNOWN 的 label/coverage 约束由协议和 replay 同时
  校验。旧 N02 ledger 仍能原样回放。
- **ER-G4**：部分满足。新增 protocol/replay 测试和旧 ledger 回归通过；没有新的 LLM、GPU
  或 benchmark inference，因此不支持效果结论。
- **ER-G1/ER-G2**：未开始。事件目前只保存可审计信号，不驱动 situated judgment 学习或
  在线训练。

## 冻结、实现与证据

新增 `ProducerScore`：`producer_score_id`、`delivery_id`、producer artifact digest、
scorer version、`PASS|FAIL|UNKNOWN`、label、quality score、response payload digest 和
coverage。完整 PASS/FAIL 必须有一致 label、quality 和 response digest；UNKNOWN 不能携带
label/quality，也不能满足 coverage。

外层 replay 新增 `producer_score` constructor 和顺序检查：delivery 之前的 score、digest
不匹配、重复 score 或 judgment 之后的 score 都拒绝。保存的 N02 v3 15-event ledger 在新
协议下仍 `PASS`，producer score count 为 0；带 producer score 的完整 synthetic chain
与 status/digest mutation 测试通过。相关代码在
[`references/aamas/peer_role_protocol_20260925.py`](../../references/aamas/peer_role_protocol_20260925.py)、
[`scripts/peerrolebench_ledger_replay.py`](../../scripts/peerrolebench_ledger_replay.py)；
测试为 [`tests/test_peerrolebench_ledger_replay.py`](../../tests/test_peerrolebench_ledger_replay.py)。

## 仍未满足与根因

| 门 | 状态 | 原因 |
|---|---|---|
| producer score 与 delivery 的 causal binding | `PARTIAL` | synthetic/replay 已验证，真实 runner 尚未调用 |
| scorer UNKNOWN/FAIL 不更新 controller | `OPEN` | controller 尚未识别 ProducerScore，必须先写 update gate |
| recipient judgment 仍为核心而非 oracle 替代 | `PARTIAL` | schema 分开；尚未有 matched `Q_p`/judgment calibration 分析 |
| benchmark 资格、第二 structural root | `OPEN` | TeamBench 任务文本泄露与单 root 未解决 |
| online update/backbone/A800 | `OPEN` | 没有有效科学信号，禁止启动 |

下一步只做两件事：把 producer-score response/UNKNOWN 语义接入 runner 的 delivery 后、
judgment 前边界（不更新 controller），并补一个 replay mutation matrix；之后再决定是否
值得运行新的真实 API episode。Goal 没有变化，不需要用户决定。
