# 三条方法不变量的合同—证据映射

日期：2026-10-04
状态：`PARTIAL`（工程性质已有回执；正式定理和 live scientific evidence 未完成）
对应 Goal：ER-G2、ER-G4、ER-G5/G2
`goal_change_requested=false`

## 目的

六范式审查建议把“理论照亮经验”收紧为三个可检验不变量，而不是在正文中直接声称方法稳定、实时或安全。本报告把它们分别写成定义、前提、可观察失败条件和现有回执来源。它不改变 active method，不把工程资格升级为科学结果。

## 不变量定义

### I1：pre-selection noninterference

给定 target assignment 的 sealed preview、候选菜单、read cut、arrival schedule、propensity 和 policy namespace，在 target selection 完成之后才到达的 target outcome 不得改变该 target selection 的 `decision_digest`、chosen candidate 或 sealed propensity。

**可观察反例**：target outcome 在 selection 前可见；selection digest 与 sealed preview 不一致；重放读取 future outcome；assignment 被重新采样。

**论文可用措辞（当前）**：

> The execution contract makes target selection independent of outcomes that arrive after its sealed read cut; the property is checked by replay and late-outcome mutation tests.

不能写成“the method proves no leakage”，除非补充正式证明或完整 machine-checkable proof artifact。

### I2：recipient-only attribution safety

若 source episode 只有 recipient-owned integration path 发生变化，且没有预注册、可唯一绑定 producer 的 defect，则 source episode 不得发布 producer `RoleEvidence`，不得追加 producer history，不得触发 producer policy update；合法结果是 `UNKNOWN`/`PENDING_ATTRIBUTION`。

**可观察反例**：recipient-only 或 mixed change 产生 producer label；later outcome 单独把 source 转为 eligible；UNKNOWN 被当作负例；producer score 与 recipient integration 没有独立字段。

**论文可用措辞（当前）**：

> The responsibility gate rejects recipient-only and mixed ownership as producer evidence, preserving an explicit UNKNOWN path.

这说明合同和工程资格，不说明真实 API 流中 producer attribution 已经具有预测价值。

### I3：idempotent replay

对同一个 `assignment_id + later_outcome_lineage`，第一次合法 delayed credit 最多追加一次 history entry；相同 lineage 的重放返回 `NOOP`，不增加 entry/seal/update，不改变 state/projection digest。不同 lineage 或 digest/version/read-cut/arrival 绑定不一致时必须拒绝或 `UNKNOWN`。

**可观察反例**：重复 credit 产生第二个 entry；snapshot replay 改变 policy state；未知 version、篡改 digest、截断或 late arrival 被空历史接受。

**论文可用措辞（当前）**：

> The versioned history path is exactly-once under the declared assignment/outcome lineage and fails closed on digest, version, read-cut, or arrival mutations.

这仍是服务/审计性质，不等于 updater 已经快速或有效。

## 现有证据映射

| 不变量 | 现有工程证据 | 状态 | 尚未证明 |
|---|---|---|---|
| I1 noninterference | `tests/test_peerrolebench_selection_preview.py`、`tests/test_peerrolebench_four_event_counterfactual.py`；`20261004_history_provenance_qualification.md` 的 `read-cut-before-source`、`arrival-before-decision`；`20261004_history_process_boundary_qualification.md` 的跨进程 replay | `PASS`（零调用/fixture 工程） | 独立 live target stream、真实质量/成本后果、正式定理 |
| I2 recipient-only safety | `20261003_pipe2_responsibility_gate.md`、`20261003_pipe2_chain_composition.md`；`20261004_history_provenance_qualification.md` 的错绑 mutation 全部 `UNKNOWN`/零 append | `PASS`（保守 gate 工程） | 真实 recipient action→later assignment 的独立 producer label 信息价值；第二 root |
| I3 idempotent replay | `20261004_history_provenance_qualification.md` 的 `duplicate-credit`：第一次 `APPENDED`、第二次 `NOOP`；未知 version/digest/truncation 负例；进程边界回执 | `PASS`（工程） | live arrival rate 下 p50/p95、并发、漂移、遗忘和 complete cost |

## 与六范式和三份验收标准的关系

- I2 是“根因手术刀”的安全边界：它直接针对 responsibility confounding；
- I1 是“反直觉重构”的时序边界：局部判断可以影响未来，但未来结果不能改写已封存选择；
- I3 是“理论照亮经验”的可回放实现：它把 delayed credit 的语义变成可观察状态转换；
- ④“新基准暴露失效”仍须通过独立 root、同信息 baseline、scorer coverage 和 live history 才能升级为 benchmark 结论。

按 claim–evidence 分级，三条不变量目前最多支持协议级/工程级表述，不能支撑 signal-level、closed-loop-level 或 generalization-level claim。`storyline` 中的 role-learning 主张、`method` 中的实时性/时效性/稳定性主张和 `benchmark` 中的主轨 scientific result 均保持 OPEN。

## 下一步

1. 为 I1–I3 各写一个最小形式化 lemma 或 machine-checkable property，注明假设、状态字段和反例；
2. 将三个 property 接入即将执行的 canonical PIPE3 same-information parity qualification，要求所有 arm 共享 read-cut/arrival/cost 但保持独立 policy namespace；
3. 在 live API 之前继续保持零调用、UNKNOWN/no-update 负例；只有 benchmark/baseline 门通过后，才将这些性质与 H1/H2/H3 结果连接；
4. 论文正文暂用“makes testable / checked by replay”措辞，不使用“proves / guarantees / real-time”措辞。
