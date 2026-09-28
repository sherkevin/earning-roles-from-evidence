# 2026-09-28 PIPE3 recipient/adoption scorer v2 qualification

- 状态：工程契约矩阵通过；`scorer_is_qualified=false`
- 真实 API：0；GPU：0；native TeamBench grader：未调用；科学 claim：禁止
- Goal：只推进可审计的 scorer 接入，不改变故事线、方法论或验收门槛

## 触发原因

PIPE3 real smoke v2 中，producer Qp 和 recipient Qr 已完成，但 adoption scorer 的
`A1_producer_boundary` 用了公开模型 `VALID_ACTIONS` 之外的 `action="probe"`，导致
coverage/decision 不完整。v2 real smoke 因冻结 stop rule 正确停止为 UNKNOWN；不能把这个
UNKNOWN 解释成模型或任务失败。

首次 v2 qualification 运行在创建 `seed_0/recipient` 子目录前调用 scorer，产生了
`FileNotFoundError`。该日志保留在
`experiments/logs/n03_pipe3_recipient_scorer_v2_qualification_20260928_v1/`，没有覆盖。
随后修正 qualification harness 的父目录创建，并重新运行 v2 矩阵。

## 通过的矩阵

回执：[n03_pipe3_recipient_scorer_v2_qualification_20260928_v2](/Users/jingwu/work/earning-roles/experiments/logs/n03_pipe3_recipient_scorer_v2_qualification_20260928_v2)

在 TeamBench PIPE3 的 seed 0、seed 1（同一 structural root 的变体）上，分别对
recipient 与 adoption 两种视图运行原始 fixture。四个 case 都满足：

- worker 使用公开 `VALID_ACTIONS` 的第一个合法值，不再制造 scorer 自身的非法输入；
- transport complete；
- `decision_complete=true`、`coverage_complete=true`；
- parent schema、task/seed、artifact digest、check inventory 和 label/status 一致性通过；
- 原始 fixture 的真实质量仍由 scorer 决定为 PASS 或 FAIL，未被强行改成 PASS。

这是 scorer contract 的回归验证，不是证明原始 fixture 正确，也不是独立 root 或
benchmark qualification。`scorer_is_qualified=false` 保持不变，因为还缺正确/near-miss
recipient artifacts、责任归因审查、完整 runner 和强同信息 baseline。

## Goal 对照

| Goal 要求 | 状态 |
|---|---|
| 可复现、版本化、UNKNOWN 不冒充标签 | 本矩阵满足 |
| 真实 consumer 的 situated judgment 可形成可信标签 | 未满足，尚需责任归因与完整链 |
| benchmark/baseline 可支持 AAMAS 效果结论 | 未满足 |
| Goal 不因工程失败而降级 | 保持 |

下一步只允许使用新的 scorer 版本卡做一次真实 integration smoke；若链路闭合，仍需
先处理 producer-owned、recipient-owned、sink-owned 缺陷的标签归属，再进入独立 root、
同信息 baseline 和重复实验。
