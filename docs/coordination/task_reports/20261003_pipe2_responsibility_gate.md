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

`accept_with_rework`、`reject_redo`、recipient-owned repair、mixed ownership、缺失/UNKNOWN
coverage 都不发 producer label；mixed edit 为 `UNKNOWN`，recipient-only rework 为
`PENDING_ATTRIBUTION`。即使资格通过，`policy_update_allowed=false`。

## 零调用验证

命令：

```bash
python3 scripts/peerrolebench_pipe2_responsibility_qualification.py \
  --output experiments/logs/n03_pipe2_responsibility_qualification_20261003_v1 \
  --seeds 0 1 2 3 4
```

五个材料等价类各取一个 seed，运行五种 authored control，共 25 个控制。结果：
`QUALIFIED_OFFLINE`，25/25 通过；0 candidate code、0 LLM/API、0 GPU、0 native grader。
原始 `config.json`、append-only `raw.jsonl` 和 `summary.json` 已保存。控制中的
`ELIGIBLE` 是 gate 行为的确定性 fixture，不是模型判断、真实标签或效果结果。

## Goal 对照

| 要求 | 状态 | 说明 |
|---|---|---|
| 责任边界不把 recipient repair 归因给 producer | `PARTIAL → zero-call pass` | 25 个 authored controls 覆盖 direct use、repair、mixed、redo、UNKNOWN |
| 真实 recipient 对交付的 situated judgment | `OPEN` | 尚未调用模型产生结构化 judgment |
| judgment→evidence→future assignment | `OPEN` | 尚未接 canonical ledger/read-cut/later task |
| 独立 terminal outcome 与 producer quality | `OPEN` | 当前 outcome 只是 gate fixture 输入 |
| baseline parity、benchmark freeze、online update | `OPEN` | 不在本任务范围内，仍禁止 API/A800 科学运行 |

## 下一步

把该 gate 接到派生 PIPE2 的零调用 ledger/replay composition：保留实际 producer×recipient
运行 receipt，补 delivery/judgment/action/outcome 的 digest 绑定和 later-assignment/read-cut
控制；只有该 composition 通过后，才讨论真实 API 小链。Goal 未修改，
`goal_change_requested=false`。
