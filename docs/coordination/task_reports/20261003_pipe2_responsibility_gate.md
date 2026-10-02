# PIPE2 responsibility-safe feedback gate qualification

日期：2026-10-03
状态：`PARTIAL`；责任边界的零调用控制通过，真实 recipient judgment 与后续任务仍未接入。

## 任务目的

修复当前第二 root 最关键的测量风险：recipient 为了完成自己的 transform/load 集成而
修改 recipient-owned 文件时，不能把“repair”动作直接当成 producer 缺陷或 producer
角色标签。新增 `scripts/peerrolebench_pipe2_responsibility_label.py`，只做 parent-side
资格判定，不更新任何 learner。

严格 `ELIGIBLE` 条件同时要求：

1. 独立 producer score 完整且绑定同一 delivery digest；
2. recipient 的结构化 judgment 指向 producer，并绑定同一 artifact；
3. recipient 实际 `accept` 后 `use`，没有 producer/recipient 文件修改；
4. terminal outcome 完整且绑定同一 artifact。

方法审查后补充一条硬条件：成功 `accept/use` 本身不能形成 producer role evidence；还
必须有 producer-owned contract change，或 judgment sidecar 中显式注册的
`producer_defect_registered=true`，并由独立 producer score 的 `FAIL/0` 观察支持。无
defect registration 的 direct-use 现在返回 `PENDING_ATTRIBUTION`。

`accept_with_rework`、`reject_redo`、recipient-owned repair、mixed ownership、缺失/UNKNOWN
coverage 都不发 producer label；mixed edit 为 `UNKNOWN`，recipient-only rework 为
`PENDING_ATTRIBUTION`。即使资格通过，`policy_update_allowed=false`。

## 零调用验证

命令：

```bash
python3 scripts/peerrolebench_pipe2_responsibility_qualification.py \
  --output experiments/logs/n03_pipe2_responsibility_qualification_20261003_v2 \
  --seeds 0 1 2 3 4
```

五个材料等价类各取一个 seed，运行六种 authored control，共 30 个控制。结果：
`QUALIFIED_OFFLINE`，30/30 通过；0 candidate code、0 LLM/API、0 GPU、0 native grader。
新增的 `registered_defect_direct_use` 仅验证显式 defect registration 才能通过 source
gate；`accepted_direct_use_without_defect` 保守返回 `PENDING_ATTRIBUTION`。v1 的 25
控制回执保留为历史版本，不覆盖。所有 `ELIGIBLE` 都是 gate 行为的确定性 fixture，
不是模型判断、真实标签或效果结果。

## Goal 对照

| 要求 | 状态 | 说明 |
|---|---|---|
| 责任边界不把 recipient repair 归因给 producer | `PARTIAL → zero-call pass` | v2 的 30 个 authored controls 覆盖无 defect direct-use、registered-defect、repair、mixed、redo、UNKNOWN |
| 真实 recipient 对交付的 situated judgment | `OPEN` | 尚未调用模型产生结构化 judgment |
| judgment→evidence→future assignment | `OPEN` | 尚未接 canonical ledger/read-cut/later task |
| 独立 terminal outcome 与 producer quality | `OPEN` | 当前 outcome 只是 gate fixture 输入 |
| baseline parity、benchmark freeze、online update | `OPEN` | 不在本任务范围内，仍禁止 API/A800 科学运行 |

## 下一步

把现有 PIPE2 真实 sandbox 回执做只读 replay：不补写缺失 judgment/action/outcome，明确
输出 `UNKNOWN/PENDING_ATTRIBUTION`；随后复用 PIPE3 的 source-gate、role-evidence offer
和 preview→commit seam 接入真实 API 小链。Goal 未修改，
`goal_change_requested=false`。
