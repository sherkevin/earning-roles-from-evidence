# PIPE1 offline adapter binding repair — 2026-10-07

状态：`QUALIFIED_OFFLINE_ADAPTER_BINDING_REPAIR`。独立审查发现上一版 adapter 的
`selection receipt` 只校验调用者提供的 menu/chosen/propensity，没有和 ledger 中的
target `PeerSelection` 交叉绑定；把 receipt 改成另一个 peer 仍可能得到
`READY_FOR_ROUTE`。审查还复现了 evidence id 与 source task index 脱钩。这是会把经验
归给错误 peer 的真实归因漏洞，因此在接入 route 前先修复。没有调用 API、生成器、候选
程序或 GPU，也没有修改历史 v1 回执。

## 修复

`scripts/peerrolebench_pipe1_offline_adapter.py` 现在额外要求：

1. `target_selection_id` 唯一对应 native `peer_selection`，且 task id/index 一致；
2. native `candidate_ids` 与外部 receipt 的 menu 顺序一致，chosen peer 和 propensity
   一致；candidate version 仍由既有 registry validator 检查；
3. `assignment_id` 唯一对应 target `later_assignment`，其 task/index、agent 和
   cited evidence 与 target selection 一致；
4. cited `role_evidence_update` 的 judgment/action/outcome 都指向同一
   `producer_delivery`，该 delivery 属于 source task index；
5. source/target index 必须是非负整数且 source 先于 target；malformed event row 统一
   转为 fail-closed `UNKNOWN`。

`route_ready` 仍只表示结构可以进入下一道 route preflight；它不表示
`attribution_ready`、收益可用、真实 route 已执行或策略可以更新。

## 验收

v2 配置在最终检查前冻结于
[`config.json`](../../../experiments/logs/n03_pipe1_offline_adapter_qualification_20261007_v2/config.json)。
调试期先出现 2 failed/11 passed（tuple/list 兼容问题），失败记录保存在
[`debug_failure.txt`](../../../experiments/logs/n03_pipe1_offline_adapter_qualification_20261007_v2/debug_failure.txt)，
没有被覆盖。修复后：

- adapter 与既有 PIPE3 contract：`13 passed`；
- `py_compile` 与 scoped `git diff --check`：通过；
- chosen peer、menu 顺序、错误 evidence、负 source index、malformed row 的篡改均
  `UNKNOWN`，不创建 assignment、不产生 label、不更新 policy；
- 完整回执见
  [`summary.json`](../../../experiments/logs/n03_pipe1_offline_adapter_qualification_20261007_v2/summary.json)。

计数为 0 API、0 generator、0 candidate、0 GPU、0 policy update，且
`scientific_claim_allowed=false`。

## Goal 对照

本轮关闭了一个会直接破坏责任归因的工程漏洞，提升了未来 benchmark 的可解释性；
它仍未证明真实 actor 交付、Verifier 终局质量、后续收益、任务泛化、baseline parity
或实时训练效果。三份验收标准、投稿 gate 和 Goal 均保持原状。下一步才是把此 binding
结果与 route receipt/material preflight 做一个显式 join；selected-only 目前仍只是
receipt 声明，不能写成已经实测的信息隔离。
