# Task report — delayed-credit atomicity (2026-10-01)

## Goal alignment

- **对应标准**：ER-G2；方法评价 B/E/H 的 selected-only、可重放、稳定更新要求。
- **状态**：`PARTIAL`。补齐了 delayed credit 的失败回滚语义；没有改变 benchmark、baseline 或科学就绪状态。
- **goal_change_requested**：`false`。

## 问题与修复

`DelayedCreditLedger.apply_once()` 原先只在 updater 返回后登记幂等键。如果 updater
修改多个持久对象后抛错，调用方可能得到半更新状态，重试又无法由 ledger 自身判断哪些
字段已改变。现在接口仍要求 updater 对单对象更新保持原子；对于多对象更新，可传入
`snapshot`/`restore`，异常时恢复快照，且只有 updater 成功后才写入 credit key。

## 验证

- 新增失败更新、状态恢复、可重试成功和重复 no-op 测试。
- 定向两阶段/offer/preview 测试：**15 passed**。
- `python3 -m pytest -q tests`：**332 passed**。
- `py_compile` 与 `git diff --check` 通过。
- 该任务没有调用 LLM API、Nebula、GPU 或外部数据；代码/测试回执是
  `tests/test_peerrolebench_two_stage_gate.py`，因此 `scientific_claim_allowed=false`。

## 验收结论

已满足：selected-only delayed credit 在 updater 失败时不会登记成功 credit，提供回滚
钩子并可安全重试；历史 receipt 未修改。

仍未满足：真实 source-bound runner 接入、合法 UNKNOWN 与 crash-incomplete 分离、独立
histories、same-information baselines、benchmark freeze、真实 API/A800 与 future
assignment utility 证据仍开放。

## 下一步

把该事务接口接入 source-bound live runner 的 delayed-update seam，并在 runner trace 中
记录 snapshot/restore 与 retry 结果；在此之前不启动正式效果实验。
