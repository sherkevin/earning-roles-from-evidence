# Task report：更正 independent consumer scorer 差异 / 2026-09-27

状态：`COMPLETE`（实现错误更正）；`goal_change_requested=false`。这是一项研究诚信修复，
撤回一个错误的评分差异结论，不增加科学样本，也不降低 Goal。

## 发现与修复

首次 private consumer scorer 在保存的 N02 v3 episode-0 上返回 `payload_and_ack FAIL`、
`0.75`，而历史 parent-side JSON RPC scorer 是 `4/4 PASS`。逐行审查发现两条执行路径的
数据类型不同：parent RPC 先 JSON 序列化 tuple，worker 内部检查直接得到 Python tuple；
hidden check 写死 `isinstance(first, list)`，把正确的 tuple 当成错误。

修复为同时接受合法 tuple 和其 JSON list 表示，并用同一 sealed source、同一四项检查重新
运行。旧错误回执保留在
[`n03_independent_scorer_smoke_20260927`](../../experiments/logs/n03_independent_scorer_smoke_20260927/)，
修正回执在
[`n03_independent_scorer_smoke_20260927_v2`](../../experiments/logs/n03_independent_scorer_smoke_20260927_v2/)。
修正结果为 `PASS, 1.0, coverage_complete=true`，没有 LLM/GPU/native grader。

同时修复 runner 的真实输入边界：producer scorer 现在接收 `delivery_files` 加 operator
support，而不是原始 producer template；完整 PASS/FAIL 必须回显并匹配 delivery digest。

## Goal 对照

- **ER-G3/ER-G4**：实现错误已定位、历史与修正证据分开保存；scorer 仍只是 non-adversarial
  fixture/contract qualification。
- **ER-G1/ER-G2**：未触碰；没有新的真实协作、baseline、online update 或 A800 结果。

后续论文和 task docs 不再把 `4/4 vs 0.75` 写成科学发现；producer/recipient 分离仍因
ownership 与 treatment order 保留。下一步继续按 N03-next-r 做第二 root、强基线和真实小链
资格，不能跳过这次更正。

## 后续边界修补

独立审查又发现空队列的直接 worker 调用可能返回 Python tuple，而 JSON RPC 回放会得到
list。隐藏 worker 的 `empty()` 现在同时接受 `None`、`(None, None)` 和 `[None, None]`，并
增加了回归测试；此前的非空 tuple/list 修复继续保留。另补了完整 `PASS/FAIL` 结果的
delivery digest 不匹配测试，确保错误结果在写入 ledger 前被拒绝。该修改只收紧工程边界，
不增加任何 benchmark、LLM 或学习证据。
