# Task report：producer scorer mutation / resource matrix / 2026-09-27

状态：`PARTIAL`；`goal_change_requested=false`。本轮扩展了 producer-only scorer 的
near-miss、全量压力和 response mutation 检查，并保留了资源预算不足导致的 UNKNOWN。

## 冻结与实际证据

保持同一 TeamBench pin、DIST1 seed 0、producer-owned `queue.py`/`priority.py` 和
`dist1-producer-objective-v1`。P5 增加 dict 与 list equal-priority payload，P6 增加
equal-priority tie-break，P7 使用 10,000 条消息、20 producer + 20 consumer 线程。
producer scorer 的 RPC timeout 显式提高为 20 秒并写入 config；默认候选 worker CPU cap
没有放宽。

回执在 [`experiments/logs/n03_producer_scorer_qualification_20260927_v6/`](../../experiments/logs/n03_producer_scorer_qualification_20260927_v6/)。
矩阵结果为：原始 buggy source `FAIL`（有一次同配置压力执行因 CPU cap 得到 UNKNOWN，
两者都不转成正/负学习标签）、手写 correct `PASS`、priority-only `FAIL`、ack-only
`FAIL`、malformed `UNKNOWN`；worker timeout、artifact digest、coverage 和 unknown-check
四种 response mutation 全部 `UNKNOWN`。历史 v2/v4/v5 的 timeout/worker-exit 也保留，
没有覆盖或删除。

## Goal 对照与限制

- **ER-G3**：部分满足。压力和 mutation 语义没有把资源失败伪装成 FAIL；artifact/response
  digest、UNKNOWN gate 和 producer-score replay 已在前序任务完成。
- **ER-G4**：部分满足。每版 config/raw/response/summary 均有记录；全程零 LLM、零 GPU、
  未调用 native grader。
- **ER-G1/ER-G2**：未开始。没有 situated judgment、future assignment 或在线更新效果。

该 scorer 仍不是 benchmark qualification：P2 的 forced-race harness 依赖 TeamBench
当前 source 对 `deque` 的绑定方式，P7 资源预算会让严重 buggy source 只能 UNKNOWN，
还没有其他 structural root，也没有与 strong same-information baseline 的比较。private
worker 是当前 non-adversarial Python instrumentation 边界，不能宣称防御恶意 candidate。

## 下一步

先把这份 matrix 的结论写入新实验卡：对 UNKNOWN 只保留诊断，不更新 controller；补 seed
1/2 的 source-shape regression 和一个合法 timeout/permission worker mutation。只有
benchmark root、scorer semantics 和 baseline matrix 都通过后，才启动一条新的真实 API
链路；不因这轮压力结果自动选择 backbone、训练方法或启动 A800。
