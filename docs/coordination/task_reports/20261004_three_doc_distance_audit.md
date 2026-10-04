# 三份审查核验文档距离审计

日期：2026-10-04
状态：`PARTIAL / NOT_READY`
审计对象：当前唯一生效的 storyline v1.1、method v1.1、benchmark/baseline v1.1 及其三份评价标准
基线提交：`36312b0`
`goal_change_requested=false`

## 目的和判定口径

本次任务只回答一个问题：我们距离三份审查核验文档要求的“可作为优秀 AAMAS 方法论文提交的证据状态”还有多远。审计不把主观录用概率当指标，也不把零调用 fixture、协议通过或版式完成写成科学结果。

判定分为三档：

- `已满足（工程）`：已有可重放回执，但只表示协议/实现边界通过；
- `部分满足`：定义、设计或局部资格已完成，仍缺能识别主张的独立证据；
- `未满足（科学硬门）`：当前不能支撑对应论文主张，必须保留为 `OPEN`/`NOT_READY`。

## 总结结论

三份标准目前均为 `NOT_READY`。已经推进的是“能否安全地记录、传播和拒绝错误 evidence”的工程底座；还没有完成“这种 evidence 是否在同信息、同成本条件下带来可归因的 future assignment 和未见任务收益”的科学证明。

因此当前论文阶段仍是 **内部 pre-results research design**：可以继续写问题定义、机制合同、实验矩阵和限制；不能填写方法收益数字，不能把“自进化、实时训练、形成专业化”写成已证实结论，也不能启动正式效果流或 A800。

## 一、故事线与创新点

对应标准：`storyline_v1.1_20260928.md`、`storyline_v1.3_20260928_eval.md`。

| 验收门 | 状态 | 已有证据 | 尚缺的证据 |
|---|---|---|---|
| 问题切口 sharp，且是多 agent 必要问题 | 部分满足 | situated recipient judgment → producer evidence → future assignment → unseen quality/cost 已固定为一句问题和一条链 | 尚缺首屏可复现的最小失败反例，以及用结果证明该切口比 acceptance/terminal score 更能识别问题 |
| 唯一主机制与创新边界 | 部分满足 | 已把 situated judgment、责任过滤、延迟更新、future assignment 作为一个有机闭环，并明确反驳条件 | novelty table、closest-method audit、同信息 contextual trust/bandit 等替代解释尚未被真实比较排除 |
| 因果链的责任与时序 | 已满足（工程） | canonical provenance、ownership gate、read-cut、candidate/scope binding、UNKNOWN/no-op、snapshot/replay、跨进程恢复和多条 history 篡改拒绝均有回执 | 回执来自 pinned CPU/hand-authored 流；没有真实 recipient action → later assignment → unseen utility 的独立 live 链 |
| Claim–evidence 对齐 | 部分满足 | active 文档明确区分 protocol、signal、closed-loop、generalization 四级证据，论文保留空结果表 | 目前只能支撑协议级/设计级表述；signal、closed-loop、泛化级证据仍为空 |
| Proceedings-ready 闭环 | 未满足 | — | 至少两个结构独立 root、独立 live histories、future owner 实际消费 evidence、未见任务质量/返工/采用率/完整成本和 confirmation split |

**故事线距离判断：**故事本身已经收敛，距离“可被结果支撑的创新论文”仍缺整条后半段。最关键的缺口不是再润色标题，而是证明 judgment 真的提供增量信息，并改变了别人的后续 assignment。

## 二、方法论

对应标准：`method_v1.1_20260930.md`、`method_v1.2_20260930_eval.md`。

| 验收门 | 状态 | 已有证据 | 尚缺的证据 |
|---|---|---|---|
| 三层状态分离 | 已满足（工程） | `attribution_eligible`、`evidence_publish_allowed`、`policy_update_allowed` 已分开；recipient-owned repair 不产生 producer label | 还需在真实 live stream 中验证，而不是只在 fixture 中验证 |
| 可重放事件合同 | 已满足（工程） | source→offer/read-cut→assignment→target outcome→delayed credit→history append；duplicate NOOP、late/unknown/truncation/version/digest mutation fail-closed | 尚缺真实跨 episode history 被独立 policy 持久消费的回执 |
| 机制是否真正新 | 未满足（科学） | 四格和 policy factory 有离线骨架；RARE、raw、terminal、contextual 等 arm 已有实现接缝 | 最终 backbone/updater 未锁定；四格科学消融、closest published adapter、同信息强 baseline 尚未完成，不能把 RLS/SGD/refit/JEV wrapper 组合称为已证明创新 |
| 实时性 | 未满足 | — | selected-only 每条反馈的 update/read/publish p50/p95、lag、吞吐/backlog、state bytes、CPU/GPU/token/tool/人工成本 |
| 时效性 | 未满足 | drift、late correction、read-cut 已进入合同 | drift 后响应窗口、future quality/regret 的变化尚未测量 |
| 稳定性与抗遗忘 | 未满足 | replay 和拒绝边界已测 | 旧 root/task holdout 的峰值/平均 forgetting、恢复时间、UNKNOWN 率尚未测量 |
| 方法论文交付门 | 未满足 | 工程合同可写入方法章节 | 没有真实 selected-only incremental update 与独立 live efficacy；`QUALIFIED_OFFLINE` 不能升格为方法结果 |

**方法论距离判断：**我们已经把“错误更新会发生什么”规定清楚，但还没有证明“正确更新能以实时、稳定、低成本方式改善未来选择”。这正是 ER-G2 的核心，当前仍是 `OPEN`。

## 三、Benchmark 与 baseline

对应标准：`benchmark_baseline_v1.1_20260930.md`、`benchmark_baseline_v1.2_20260929_eval.md`。

| 验收门 | 状态 | 已有证据 | 尚缺的证据 |
|---|---|---|---|
| 轨道边界 | 已满足（设计） | `ArtifactRole` 主轨与 `PeerSelect` 副轨分开，claim/label/scorer/统计分母不混用 | 尚未由冻结 benchmark 和结果证明主轨确实承载完整因果链 |
| 候选任务与权限合同 | 部分满足 | TeamBench-derived `PeerRoleBench-TB`、PIPE3 接缝、sandbox、ledger、UNKNOWN 和 provenance 有工程回执 | 主 benchmark 仍是 candidate；PIPE3 完整 scorer/adoption/later-assignment qualification 未完成，DIST1 有 repair-direction leakage |
| 结构独立 root 与 authority | 未满足 | PIPE2 只形成候选和 derived probe；无 active authority 选择 | 至少第二个结构不同 root；PIPE2 seeds 1/4/6/9 的 malformed fixture 处理；development/confirmation split 和 clean replay manifest |
| baseline 名单与离线执行器 | 部分满足 | v16 七 arm 在同一 hand-authored stream 上通过 menu/schedule/registry/RNG/snapshot parity | 这不是 live scientific parity；各 arm 尚未读取同一 canonical `φ`/receipt/read-cut，也没有独立 state namespace 的 paired history |
| closest published 对照 | 未满足 | Meta-Team L2-style 已做语义审计，当前为 `OPEN/NO-GO` | faithful public adapter、成本/assignment 资格与可执行回执 |
| 实验矩阵 | 部分满足 | H1/H2/H3、root/split、baseline、成本、UNKNOWN 和停止规则已列入计划 | 尚缺冻结后的可执行 cell manifest、精度/功效理由和全部 arm 的 same-information qualification |
| 结果合理性 | 未满足 | 有明确主 estimand、失败分类和统计要求 | 没有 assignment-level future quality/regret、完整成本、UNKNOWN 分母、95% 区间、未见 root 和 confirmation 结果 |

**Benchmark/baseline 距离判断：**实验“名单和骨架”已经有了，实验“能公平识别主张的冻结系统”还没有。只要第二 root、公共 feature parity、closest adapter 和独立 live history 中任一项未关闭，baseline 就不能标记为 `FROZEN`。

## 四、Goal 阶段门对照

| Goal 门 | 当前状态 | 含义 |
|---|---|---|
| G0 目标/故事 | `PARTIAL` | 问题、责任语义和反驳边界清楚；真实闭环证据未有 |
| G1 Benchmark 资格 | `PARTIAL` | 单 root 工程接缝较完整；第二 root、authority 和污染/精度门未闭合 |
| G2 方法 | `PARTIAL` | 状态机、provenance、replay 边界通过；最终 updater、实时性、漂移和遗忘未证 |
| G3 开发实验 | `OPEN` | 尚无冻结后的真实 API、独立 live histories 和 same-information 科学比较 |
| G4 确认实验 | `OPEN` | 尚无独立 confirmation root/stream |
| G5 论文提交 | `OPEN` | 版式、图位和实验矩阵草稿存在；结果与 claim–evidence 仍不足 |

## 距离目标的最短可验证路径

下一步只做一张卡，不扩大范围：**canonical PIPE3 same-information parity qualification（零调用）**。

1. 把同一 canonical `RoleEvidenceOffer`/history projection、candidate registry/version、菜单、read-cut、arrival schedule、propensity、state cap 和 cost schema 接入七个 arm。
2. 每个 arm 使用独立 policy namespace；统一处理 selected-only、UNKNOWN、duplicate、late correction 和 no-update。
3. 记录每格的 candidate/menu/`φ`/feedback/propensity/selection/assignment/state/cost digest。
4. 加入 evidence-content 双向 mutation、错绑、未来泄漏和 scope mutation；通过条件是 mismatch 全部 `UNKNOWN/no-op`，false-accept=0，公共输入 digest 和成本 schema 完全一致。
5. 这张卡通过后，再处理第二 root authority 和一条有完整成本、后续 assignment 的 bounded real API episode；A800 继续后置。

这条路径不会自动打开科学门，但能把当前最大的不确定性从“baseline 是否公平”推进到可被真实小流检验的状态。Goal 没有修改，也没有因失败降低验收标准。

## 证据索引

- [GOAL.md](../GOAL.md)
- [三份唯一生效文档登记](../../research/canonical/README.md)
- [故事范式审查](20261004_six_paradigm_story_audit.md)
- [history provenance qualification](20261004_history_provenance_qualification.md)
- [benchmark/baseline post-provenance audit](20261004_benchmark_baseline_post_provenance.md)
- [三份标准上一轮收敛审计](20261004_convergence_after_process_boundary.md)
