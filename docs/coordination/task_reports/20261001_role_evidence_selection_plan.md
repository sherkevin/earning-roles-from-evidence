# Task report — role-evidence selection plan (2026-10-01)

## Goal alignment

- **对应标准**：ER-G2；方法评价 A/B/E/H 的 public evidence information boundary、future responsibility 和 selected-only update。
- **状态**：`PARTIAL`。将公开 RoleEvidenceOffer 接入一个可回滚的 preview→assignment→commit seam；尚未形成真实 runner、benchmark 或效能证据。
- **goal_change_requested**：`false`。

## 实现

新增 `scripts/peerrolebench_role_evidence_selection.py`：

- `SelectionPlan` 固化 candidate menu、chosen peer、完整 probability/propensity、native evidence ids、offer digest、persistent policy digest、overlay input digest、read cut 和版本字段。
- `preview_role_evidence_selection()` 只以 overlay score vector 读取公开角色证据并在现有事务 preview 上采样；主 policy、ledger、manifest 和外部 RNG 不变。
- `commit_role_evidence_selection()` 先写原生 `LaterAssignment`，再使用 `FixedChoiceRNG` 提交同一选择；assignment subject/evidence lineage、propensity、候选菜单和持久 policy digest 都重新校验，异常时恢复 policy/ledger/manifest。
- 旧 `AssignmentEvidenceOffer`、`choose_and_seal()` 与历史 receipts 未修改；公开 role evidence 不走 `_consume_rows()`，因此不会隐式调用 updater。

## 验证

- 新增 preview 前后持久状态不变、assignment 先于 selection、chosen/propensity exact replay、stale plan 拒绝测试。
- 定向 role-evidence/preview/gate 测试：**16 passed**。
- `python3 -m pytest -q tests`：**334 passed**；`py_compile` 与 `git diff --check` 通过。
- 本任务没有调用 LLM API、Nebula、GPU 或外部数据，回执为测试文件；`scientific_claim_allowed=false`。

## 验收结论

已满足：公开证据与持久更新分离；assignment-before-selection 可以在旧 runner 语义不变的条件下执行；commit 不重新抽样且可回滚。

仍未满足：overlay score 的真实学习器、source-bound live runner 接入、合法 UNKNOWN/crash-incomplete 分母、独立 histories、same-information baselines、benchmark freeze、真实 API/A800 和 future assignment utility 仍开放。

## 下一步

把 `SelectionPlan` 接入 versioned source-bound runner 的真实 producer/scorer/action/outcome trace，新增 role-overlay receipt（分别记录 persistent/overlay digest），再做 benchmark/baseline gate audit；在这些门通过前不启动正式效果实验。
