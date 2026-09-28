# 2026-09-28 PIPE3 responsibility-aware label qualification

- 状态：五类 ownership gate 通过；仍为 `CANDIDATE_NOT_ACTIVE`
- 真实 API：0；GPU：0；native grader：0；科学 claim：禁止
- 证据：[n03_pipe3_responsibility_label_qualification_20260928_v1](/Users/jingwu/work/earning-roles/experiments/logs/n03_pipe3_responsibility_label_qualification_20260928_v1)

## 验证内容

在同一个 PIPE3 seed 0 material root 上，用 operator-held ownership contract 构造五类
sidecar：producer defect、recipient-only、sink-only、mixed edit、no attribution。门控
读取 Qp/Y 完整性、judgment target role、artifact binding、changed paths 和 later-use
证据；它只决定 producer feedback 是否 eligible，不生成质量分数。

结果严格符合预注册预期：

| case | producer feedback |
|---|---|
| producer defect | `ELIGIBLE` |
| recipient-only | `PENDING_ATTRIBUTION` |
| sink-only | `PENDING_ATTRIBUTION` |
| mixed edit | `UNKNOWN` |
| no attribution | `PENDING_ATTRIBUTION` |

五格均通过。`policy_update_allowed=false` 且 `scorer_is_qualified=false` 保持不变。

## 边界

这次是零调用的结构门测试，sidecar 是合成但绑定同一真实 task material；它没有证明
LLM 会正确输出 `target_role/target_paths/defect_type`，也没有证明 producer defect 的
Qp、later-use 和 final outcome 在真实 runner 中能被独立测量。下一步必须把这些字段加入
真实 judgment schema，并用真实正负 artifact 通过 scorer/runner 后再考虑 policy learning。
