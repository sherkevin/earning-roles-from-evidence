# 0033：更正 independent consumer scorer 的 tuple/list 实现错误

日期：2026-09-27。  
状态：Accepted；取代 ADR 0032 的错误经验性差异，不改变 Goal v1.0。

## 背景

ADR 0032 记录了同一 sealed source 上旧 parent scorer `4/4 PASS`、独立 scorer `FAIL, 0.75`
的差异，并把它当成评分语义问题。复核 hidden worker 后发现 `queue.get()` 在 worker
同进程内返回 Python tuple，而经过 parent JSON RPC 后才会变成 list；private worker 的
`payload_and_ack` check 写死 `isinstance(value, list)`，因此它把正确 tuple 误判为失败。

## 决定

1. 撤回“旧 scorer 与 independent scorer 的差异证明了任务评分盲点”这一经验性结论；旧
   `n03_independent_scorer_smoke_20260927/` 日志保留为实现失败证据，不修改历史结果。
2. hidden worker 的 pair check 同时接受合法的 tuple 和 JSON list；对同一保存的 N02 v3
   sealed source 重新运行得到 `PASS, 1.0`，因此该回放不提供 producer correctness 或
   scorer blind-spot 证据。
3. ADR 0032 的因果决策仍然有效：producer `Q_p` 与 recipient `Q_r` 必须分开；这来自
   ownership 和 treatment order，而不是那次错误的分数差异。
4. runner 的 producer scorer 只允许评分实际 `delivery_files`，不能误用 operator 原始
   template；完整 PASS/FAIL 还必须回显并匹配 delivery digest。

## 后果

论文矩阵和 task report 不得再引用 `4/4 vs 0.75` 作为科学发现。后续 scorer 资格必须
先通过 type/serialization round-trip 测试，再进行 baseline 或真实 API 链路。Goal 没有
降级，`goal_change_requested=false`。
