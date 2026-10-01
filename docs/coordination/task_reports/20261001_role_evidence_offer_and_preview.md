# Task report — role evidence offer and selection preview seam (2026-10-01)

## Goal alignment

- **对应标准**：ER-G2；方法评价 A/B，尤其是 native evidence lineage、future responsibility 和 assignment-before-selection。
- **状态**：`PARTIAL`。补上了两阶段方案的两个关键语义接缝；尚未接入真实 source-bound live runner，也没有 benchmark/baseline 效果证据。
- **goal_change_requested**：`false`。

## 发现的具体问题

独立审查和最小复现发现两个真实漏洞：

1. 旧 `AssignmentEvidenceOffer.evidence_ids` 实际填的是 policy `source_event_id`（selection id），而原生 `LaterAssignment` 要求 `RoleEvidenceUpdate.evidence_id`；两者不能混用。
2. 原生 ledger 本身不会检查 evidence 的 producer subject，因此 B 的 evidence 可以被错误地用于 C 的 assignment。此前零调用资格脚本确实存在这个 B→C 错配，历史回执保留但不再作为正确语义。

## 实现

- 新增 [`peerrolebench_role_evidence_offer.py`](../../../scripts/peerrolebench_role_evidence_offer.py)：独立 `RoleEvidenceOffer` schema，以 native evidence id 为主键。
- `build_role_evidence_from_ledger()` 从 canonical evidence→judgment/action/outcome→delivery 派生 producer、artifact digest、task index 和公开判断；错误 candidate、错误 role、未来 source 和断裂 lineage 拒绝。
- isolated reader/worker 新增 `peerrole-role-evidence-read-v1`，只接受公开字段，不接收 scorer/gate 私有信息。
- 新增 [`peerrolebench_selection_preview.py`](../../../scripts/peerrolebench_selection_preview.py)：preview 在事务快照中生成完整 probabilities/propensity，恢复 policy/RNG；写入 assignment 后用 `FixedChoiceRNG` 原样提交，禁止重采样。
- 两阶段资格脚本已改为 producer source evidence → 独立 role offer/read → assignment 选择相同 producer subject → later outcome → delayed credit；不再构造 evidence B、assignment C 的错配。

## 验证

- 新增 offer、canonical subject、isolated read、future/private rejection、preview state byte equality、menu mutation 和 exact propensity 测试。
- 定向两阶段/offer/preview/canonical-credit 测试：**15 passed**（另含 delayed-credit rollback）。
- 当前 `python3 -m pytest -q tests` 全部 **332 passed**，`py_compile` 和 `git diff --check` 通过。
- 当前零调用回执：`experiments/logs/n03_two_stage_role_evidence_qualification_20261001_v3/`；producer-owned 分支 role read、assignment、canonical later credit 和 replay 通过，recipient-owned 分支不发布 evidence。
- API calls=0，GPU jobs=0，`scientific_claim_allowed=false`。

## 验收结论

已满足：native evidence id 与 policy source id 分离；subject/lineage 可从 canonical ledger 派生；assignment 先于 selection；chosen peer 和 propensity exact replay；publication 不隐式触发 persistent update。

仍未满足：现有 versioned source-bound PIPE3 live runner 尚未消费新的 RoleEvidenceOffer；合法 UNKNOWN 与 crash-incomplete 还需分开计数；benchmark、same-information baselines、独立 histories、真实 API 和 A800 仍关闭。

## 下一步

把 `RoleEvidenceOffer`、isolated read 和 preview seam 接入 versioned source-bound runner，增加 canonical later-credit validator（assignment→selection→delivery→action→outcome 全链路），然后重跑 benchmark/baseline gate audit。没有这些门，不启动真实 API/A800。
