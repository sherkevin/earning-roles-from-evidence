# N03-next-r5.72：PIPE3 feature-aware two-stage composition qualification

日期：2026-10-05
状态：`PARTIAL`（canonical composition 的 feature 输入接缝通过；baseline、live parity 与科学效果仍未通过）
`goal_change_requested=false`

## 目的与硬标准

r5.67/r5.69 已经分别确认 `contextual_trust_linear` 与 RARE 应共享
`hash64-v1`、64 维 bounded feature、candidate menu 和 base score；但现有 PIPE3
two-stage composition 的 source/target selection 仍写入 `pipe3-v1/pipe3`，并且没有给
policy 传入 `captured_features`。因此 strongest same-information comparator 还不能
真正走 canonical `preview → assignment → commit` 路径。

本任务的可量化门是：

1. source 和 target selection 都接收同一个版本化、完整、有限且 64 维的公共 feature map；
2. `contextual_trust_linear` 通过现有 `preview_role_evidence_selection` /
   `commit_role_evidence_selection`，不另造一条选择路径；
3. published evidence 仍只作为 assignment 输入，source publication 不改变 policy state，
   target 的 eligible recipient judgment 才产生一次 selected-only update；
4. 配置、逐事件 raw JSONL、summary 在执行前/中/后落盘，明确 0 API、0 GPU、不能产生
   scientific claim 的边界。

## 实现

更新 [`peerrolebench_pipe3_two_stage_composition.py`](../../../scripts/peerrolebench_pipe3_two_stage_composition.py)：

- 版本从历史 `v1.7` 增为 `pipe3-two-stage-composition-v1.8`，不改写旧回执；
- 增加公共 qualification feature contract：`hash64-v1`、`matrix-features-v1`、64 维
  bounded one-hot `phi`；它是同信息工程表示，不是 feature quality 或 learned representation
  结论；
- source `choose_and_seal` 与 target preview/commit 都显式传入同一 `captured_features`，
  且 `policy_version` 按 policy name 绑定；
- raw JSONL 保存 feature contract receipt，便于复核 native ledger 之外的 policy input。

新增 [`peerrolebench_pipe3_feature_composition_qualification.py`](../../../scripts/peerrolebench_pipe3_feature_composition_qualification.py)，
它只调用已有 CPU composition 和明确标注的 deterministic unit scorer；不执行 sandbox
scorer、LLM API 或 GPU。

## 执行前冻结与证据

配置、原始组合日志和汇总位于（v1/v2/v3 历史回执保留，v4 为当前修订回执）：

- [`experiments/logs/n03_pipe3_feature_composition_qualification_20261005_v4/`](../../../experiments/logs/n03_pipe3_feature_composition_qualification_20261005_v4/)

冻结内容包括 source commit、组件 SHA-256、policy、feature encoder/schema/dimension、
`preview->assignment->commit` 合同、`real_api_calls=0`、`gpu_jobs=0`、
`scientific_claim_allowed=false` 和 `baseline_frozen=false`。运行没有使用真实模型结果，
也没有把 unit scorer 输出混入真实 benchmark。

## 结果

- composition：3 个 control（`producer_owned`、`recipient_owned`、`mixed`）完成，整体
  `QUALIFIED_OFFLINE`；producer-owned 的 source publication 不更新，目标 recipient
  judgment 产生 1 次 declared-channel update；不适格 controls 继续按既有规则保留
  `UNKNOWN`；
- feature contract receipt：1/1，source/target 共用 `hash64-v1` + `matrix-features-v1`
  和两个 64 维 bounded candidate vectors；
- source/target 两个真实 `DecisionSidecar` payload、feature digest 和 sidecar digest 均落入
  raw JSONL；`contextual_trust_linear` 的 factory、参数、版本和 config digest 在 policy
  contract receipt 中 fail-closed 绑定；assignment ledger 的 chosen candidate 与 target
  sidecar 保持一致；
- 定向回归：`110 passed`；`py_compile` 通过；
- API/GPU：`0/0`。

这个结果只证明 comparator 能进入现有 canonical two-stage 工程接缝。它没有证明 chosen
candidate 的独立 delivery/action/adoption/later outcome，也没有证明 RARE 或
`contextual_trust_linear` 的质量、实时性、成本或角色学习收益。

## 三份审核标准对照

| 标准 | 本任务关闭的部分 | 仍未满足 |
|---|---|---|
| 故事线与创新点 | “公共 situated evidence 在下一次执行前改变 assignment 输入”的实现链条更具体，且不把 publication 偷换成 update | 自进化/专业化/闭环质量增益仍没有真实证据；故事线验收仍 `NOT_READY` |
| 方法论 | feature-aware strongest comparator 真实通过 preview→assignment→commit；版本、输入、selected-only update 可审计 | independent live histories、跨进程恢复、真实延迟/漂移窗口、成本与 updater 对照仍开放 |
| benchmark+baseline | 关闭了 canonical composition 缺少公共 feature 输入的工程缺口 | active 七臂未改变且 baseline 未冻结；chosen-candidate 独立 outcome、第二 root、closest published、真实 API parity 仍未开始 |

剩余问题的性质是**证据不足与 live benchmark qualification 未完成**，不是借口降低 Goal。
没有请求任何 Goal 或验收标准降级。

## 下一步

只推进下一道有回报的门：在不改变 active manifest 的前提下，将相同 feature contract
接到 chosen-candidate 独立 delivery → recipient action → adoption → later outcome
生成器，并为 `contextual_trust_linear` 与 RARE 保留独立 namespace、history 和成本字段。
在该 live parity 设计冻结并通过 negative controls 之前，不启动真实 API/A800，也不把本
回执写成 benchmark 结果。
