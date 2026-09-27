# Task report：neutral DIST1 producer scorer preflight / 2026-09-27

状态：`PARTIAL`；`goal_change_requested=false`。

## Goal 对照

- **ER-G3**：版本化 `dist1-neutral-v1` 交付可被独立 producer scorer 读取，digest、接口名、7 项检查和完整 `PASS/FAIL` 响应均可回放；scorer 仍标记为未资格化，不能成为 benchmark label。
- **ER-G4**：真实 pinned sandbox worker 执行了检查，raw/response/transport/summary 均落盘；0 LLM、0 GPU、未运行 native grader。
- **ER-G1/ER-G2**：没有新的 recipient judgment、future assignment、baseline 或在线更新结果。

## 实际运行与结果

脚本 [`peerrolebench_neutral_producer_scorer_preflight.py`](../../scripts/peerrolebench_neutral_producer_scorer_preflight.py)
加载中性材料的 DIST1 seed 0 producer payload，在固定 `dist1-producer-objective-v1`
worker 中运行 P1–P7。原始证据在
[`n03_neutral_producer_scorer_preflight_20260927`](../../experiments/logs/n03_neutral_producer_scorer_preflight_20260927/)。

响应是完整 `FAIL`，`quality_score=0.2857142857142857`，`label=0`，transport `complete`：
P1 source parse 与 P7 zero-loss 通过；P2 capacity、P3 ack receipt、P4 nack recovery、
P5 type safety、P6 deterministic ordering 失败。这个结果与原始 DIST1 buggy source
一致，说明中性适配器没有替换被测行为。

## 解释与边界

这是 scorer transport/adapter 的诊断回执，不是 producer 能力真值或学习信号。当前
scorer 的 P2 forced-race 与 P7 压力边界、跨 seed 覆盖和预注册 qualification 仍未完成；
因此该结果在 ledger 中不能更新 controller，也不能支持“判断有信息”或“RARE 有效”。

下一步仍是 live runner 的 hidden scorer/ledger/UNKNOWN seam 和正式小批量卡审查；在此
之前不调用新的真实 API、不进入 PIPE3 confirmation、不启动 A800。
