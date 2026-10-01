# Task report — two-stage evidence publication and delayed update (2026-09-30)

## Goal alignment

- **对应标准**：ER-G2（可归因的 situated judgment → role evidence → future responsibility）、方法评价 A/B/E/H。
- **状态**：`PARTIAL`。完成了方案 A 的方法合同和 CPU 协议资格；没有取得 benchmark、baseline 或科学效能证据。
- **goal_change_requested**：`false`。

## 为什么要改

独立代码审查收窄了上一份 deadlock 报告：原生 ledger 并不要求 `task_start` 必须先有
`LaterAssignment`，runner 是因为把 diagnostic `ELIGIBLE`、public evidence 和持久 update
绑在一起而主动停止。若直接放开旧门，会把 recipient-owned repair 或 later outcome 错当作
producer label。用户确认采用方案 A，因而新建 ADR 0043 和 active method v1.1，不修改旧
receipt 或 Goal。

## 方法变更

`method_v1.1_20260930.md` 将状态拆成：

```text
attribution_eligible
  -> evidence_publish_allowed
  -> pre-execution assignment/read cut
  -> later task outcome
  -> policy_update_allowed (selected-only, at most once)
```

`producer_feedback_eligibility` 中 `later_valid` 不再被允许单独制造源归因；公开 evidence
发布不调用 updater，later credit 只评价未来 assignment/use，不能重写源 episode。

## 实际验证与证据

运行前写入 `experiments/logs/n03_two_stage_role_evidence_qualification_20261001_v3/config.json`（早期 v1/v2 回执保留），
使用 pinned `PeerRoleLedger(require_selection=True, require_terminal_outcome=True)`、原生
`RoleEvidenceUpdate`/`LaterAssignment`、parent replay 和新的
`scripts/peerrolebench_two_stage_gate.py`。没有 LLM API、GPU 或 hidden scorer。

- `producer_owned`：源 episode 通过 attribution，发布 evidence 后 persistent digest 不变；assignment 在 selection/task start 前写入；后续 outcome 完成后产生一次 delayed credit；重复 credit 为 no-op；17 条 ledger 事件 replay `PASS`。
- public assignment view 已改用独立 `RoleEvidenceOffer`，以 native `evidence_id` 为主键，并从 canonical ledger 绑定 producer candidate、delivery、judgment/action/outcome 和 artifact digest；旧 feedback offer 不再冒充 role evidence。
- `recipient_owned`：processor-only change 为 `PENDING_ATTRIBUTION`，不发布 evidence、不建 assignment、不更新；不完整链保留 `UNKNOWN`。
- `preview→assignment→selection` 的 exact chosen/propensity 资格测试通过；定向 gate/qualification 测试 **15 passed**，当前 `python3 -m pytest -q tests` 全部 **332 passed**；这只证明合同和顺序可执行，不证明 selector 质量、future assignment gain 或训练收益。

## 对验收标准的结论

已满足：责任门不把 later outcome 当源标签；publication/update 可独立消融；assignment、propensity、replay 和幂等语义已有最小实现。

仍未满足：公认 benchmark 冻结、同信息 executable baseline、closest published adapter、独立 live histories、真实 API later-use 效果、完整 cost/precision、A800 updater 选择。当前仍不得把 `QUALIFIED_OFFLINE` 写成科学结果或解冻 API/A800。

## 下一步

下一步把独立 `RoleEvidenceOffer` 和 preview→assignment→commit 接入现有 source-bound PIPE3 runner；发布阶段保持 `consume_evidence=False`，source terminal 后登记原生 evidence，assignment 先于目标 selection，later outcome 后再通过 replay gate 调 updater。完成 paired recipient/mixed/late-correction tests 后，重新做 benchmark/baseline gate audit；只有该 gate 通过才考虑真实 API。
