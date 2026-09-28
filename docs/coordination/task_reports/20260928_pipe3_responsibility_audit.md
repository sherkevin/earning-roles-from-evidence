# 2026-09-28 PIPE3 responsibility audit

- 状态：通过屏蔽伪标签；没有 API/GPU；没有修改历史 v3 episode
- 证据：[n03_pipe3_responsibility_audit_20260928_v1](/Users/jingwu/work/earning-roles/experiments/logs/n03_pipe3_responsibility_audit_20260928_v1)
- 工具：[peerrolebench_pipe3_responsibility_audit.py](/Users/jingwu/work/earning-roles/scripts/peerrolebench_pipe3_responsibility_audit.py)

## 审计规则

对冻结的 v3 episode，审计同时读取 operator-held public materials、validated consumer
action、Qp、judgment 和 adoption score。只有在 Qp 与 downstream outcome 都完整、且
观察到 producer-owned path 的实际变更时，producer feedback 才有资格进入 role update。
recipient-owned-only 的 integration repair 标为 `PENDING_ATTRIBUTION`，不产生 producer
标签。这个工具只做资格判断，不重算任何历史 scorer 分数。

## v3 结果

现有 v3 的 Qp/Qr/adoption 均为 PASS，ledger 为 PASS；但 consumer 只修改了
recipient-owned 的 `processor.py`，producer-owned path 变更为空。审计输出：

```json
{"producer_feedback_status":"PENDING_ATTRIBUTION",
 "producer_feedback_eligible":false,
 "policy_update_allowed":false,
 "scientific_claim_allowed":false}
```

这与 judgment 的 repair plan 一致：它描述的是 processor 的编码和 envelope，而 Qp 已经
判定 producer artifact 完整。该结果把“链路闭合”与“可学习的 producer 责任标签”分开，
阻止当前 runner 将 recipient 自己的修复错误地归因给 producer。

## 对 Goal 的影响

Goal 没有降级。真实 situated judgment→action→outcome 链已能运行，但 attribution-safe
role evidence 仍未完成。下一步需要在任务材料中提供 producer-owned defect、recipient-owned
integration 和 sink adoption 的正负对照，并让 structured judgment 显式声明归因范围；在此
之前不启动 policy learning 或 A800 效果实验。
