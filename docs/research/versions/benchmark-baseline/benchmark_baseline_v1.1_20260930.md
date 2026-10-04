# Benchmark、baseline 与实验计划 v1.1

- **状态**：`ACTIVE`
- **生效日期**：2026-09-30
- **类别**：benchmark-baseline
- **前一版本**：[`benchmark_baseline_v1.0_20260928.md`](benchmark_baseline_v1.0_20260928.md)
- **目标约束**：[`docs/coordination/GOAL.md`](../../../coordination/GOAL.md) ER-G3/ER-G4

`ACTIVE` 只表示这是当前唯一的实验计划，不表示 benchmark 已冻结或 baseline 已实现。

## 1. 轨道关系与 Benchmark 状态

本版本已确认两个互补轨道的职责：

- **论文主轨：`ArtifactRole`**。TeamBench-derived `PeerRoleBench-TB` 承载真实交付、recipient 使用/返工/拒绝、责任归因、future assignment 和质量—完整成本闭环。
- **机制副轨：`PeerSelect`**。Pinned `graph-ipd`/PeerSelect-IPD 只承载局部候选、selected-only payoff、在线更新、漂移恢复和服务成本；它不能单独证明 situated judgment 或 producer attribution。

两个轨道共享 selector/update/event API，但 benchmark、label、scorer、统计分母和 scientific claim 分开。副轨结果不能替代主轨结果，主轨的 artifact 结果也不能被合并成 payoff 分数。

主轨候选为 TeamBench-derived `PeerRoleBench-TB`。它目前是候选协议，不是已冻结 benchmark。候选 root 为 `DIST1_queue_race`（development/诊断）和 `PIPE3_stream_processing`（confirmation 候选）；改 seed、改名或字段替换不增加独立 root。DIST1 的历史任务文本泄露修复方向，因此不能直接充当 discovery 科学样本；PIPE3 也必须先通过完整 runner、scorer、ledger、adoption 和 later-assignment 资格。

### 2026-10-01 候选状态 amendment

`PIPE2_data_pipeline` 已完成条件性第二 root screen，并进入“下一候选”队列；它尚未进入本版本的 active root split，也没有改变当前 `DIST1_queue_race`/`PIPE3_stream_processing` 的开发—确认安排。PIPE2 v2 只在 valid seed 0/2 上通过有限 runtime handoff/scorer qualification，完整 seed 0–9 被 generator fixture validity gate 阻塞（`1,4,6,9`），因此不能升格为 benchmark、baseline cell 或 confirmation root。只有在共同确认 fixture/generator authority 处理、独立 history、baseline parity、later-use 和完整成本门之后，才可另行更新本文件版本与 manifest。

一个不改变 pinned checkout 的 CSV-writer probe 已证明 option A 可以在保留逻辑 ETL 合同的前提下修复四个 malformed seed；它生成了新的 derived-root digest，但未写入 active manifest。详见 [derived fixture probe](../../../coordination/task_reports/20261001_pipe2_derived_fixture_probe.md)。

2026-10-01 manifest amendment：v13/v14/v15 的历史离线 receipts 保留但不再被解释为完整
root enforcement；提交 `073708e` 后的 v16 才通过逐 offer RNG schedule、prefix content
immutability、re-visible accounting 和交叉分母的离线 implementation-parity 检查。它仍
不是 TeamBench/canonical-ledger root manifest，也没有解冻 benchmark、baseline 或 API/A800。
PIPE3 v2 的 two-stage CPU composition 只关闭有限 evidence→assignment→later-credit
工程接缝，candidate treatment、责任归因、terminal channel、independent history 与
real situated judgment 仍开放。详见 [manifest hardening v2](../../../coordination/task_reports/20261001_baseline_manifest_hardening_v2.md)
和 [PIPE3 two-stage composition](../../../coordination/task_reports/20261001_pipe3_two_stage_composition.md)。

2026-10-01 P0 amendment：v1.2 qualification 已把 candidate source digest、producer-read-only
 attribution、`terminal_outcome` delayed channel 和 role-offer/read auxiliary-chain continuation
 接入候选 runner；368 项回归与 injected contract qualification 通过。首次完整重跑遇到一次
 macOS `sysctl()` transport 权限错误；预注册的单 scorer probe 成功后，第二次完整 v1.2 CPU
 qualification 以 `QUALIFIED_OFFLINE` 完成：producer-owned control 走通 delayed update，
 recipient-owned/mixed controls 被责任门保护性地停止为 UNKNOWN/no-update。该结果仍是同一
 structural root 的工程资格（0 LLM API、0 GPU、`scientific_claim_allowed=false`），不能升级为
 benchmark、baseline 或方法效果；independent root、真实 situated judgment 与 baseline parity
 仍开放。详见 [P0 repair report](../../../coordination/task_reports/20261001_pipe3_p0_repairs.md)。

对照审查还保留 `MULTI3_polyglot` 作为 `CONDITIONAL-LOW` fallback，而不是 active root：其 JSON fixtures 可解析，但 native tests 使用 hardcoded `correct_wire/correct_envelope`，没有真实 producer→recipient artifact binding；sample generator、seed split、schema contract 和 prompt oracle 也未冻结。详见 [MULTI3 fallback audit](../../../coordination/task_reports/20261001_multi3_fallback_audit.md)。

2026-10-02 baseline-parity amendment：v1.3 composition 已增加显式 policy factory/name seam，
并修复“只提交 delayed credit 就算 arm 通过”的假通过条件；声明了 accepted feedback source
的 arm 若没有对应 policy update 必须为 `UNKNOWN`。新增的
`role-evidence-judgment-beta-v1` 只作为 assignment-side comparator，按 read-cut 前公开
recipient judgment 生成 overlay，排除 terminal quality/Qp 和持久 state。它尚未接入七 arm
live runner，且 evidence-content mutation 仍不能改变当前 hand-authored overlay 的选择；因此
baseline matrix、independent live history、第二 root 与 scientific readiness 仍未冻结。
详见 [feedback-channel gate](../../../coordination/task_reports/20261002_pipe3_feedback_channel_gate.md)
和 [assignment scorer report](../../../coordination/task_reports/20261002_role_evidence_assignment_scorer.md)。

副轨候选为 `graph-ipd@00ef417f60053569175b2b50d0f0e25ff8eb7007`（MIT，arXiv:2608.28977），用于机制 sanity check，不改变主轨的 artifact claim。

冻结前必须有不可变 manifest：TeamBench commit、root/source/generator hash、seed 与 root split、角色可见文件、写权限、scorer/ledger schema、模型/API 配置、预算、主指标和停止规则。任何 root 的信息泄漏、责任归因、评分覆盖或 replay 失败都只能是 `UNKNOWN`/停止，不能靠改 label、减少检查或扩大 timeout 变成通过。

## 2. 任务契约

每个 episode 必须独立记录 producer contract、recipient action/use/rework、sink adoption、final outcome、完整成本和 UNKNOWN 原因。决策在执行前封存；未来 owner 的 assignment 不能读到执行后结果。producer correctness 不等于 recipient integration；recipient 正常完成自己的工作不自动惩罚 producer。

主任务必须有真实依赖：recipient 能够接受、使用、修改、拒绝或返工具体交付。private gold、hidden scorer、operator ledger 和其他 policy 的状态必须隔离。development 与 confirmation 按 root 划分；确认 root 的材料不能在看完结果后重切。

## 3. Baseline 矩阵（按轨道分层）

所有 policy 共享候选集合、初始状态、探索机会、模型/API/工具预算、可见事件和完整成本；只能读取自己的合法历史。

| 条件 | 读取/更新 | 目的 |
|---|---|---|
| `uniform` | 候选集合；固定均匀选择 | 下界与探索上界 |
| `no_update` | 初始先验与当前上下文；不因反馈更新 | 判断单纯执行是否已足够 |
| `raw_acceptance` | 合法 accept/reject | 检验责任过滤的增量 |
| `terminal_only` | 独立 final outcome | 检验 situated judgment 的额外信息 |
| `contextual_trust` | 与主方法相同的 context/judgment/propensity/延迟 | 最强同信息信任/ bandit 对照 |
| `pooled_controller` | 允许的公共历史；不读 private scorer | 集中控制上界 |
| `RARE` | responsibility-aware judgment/action/contract | 主轨候选机制 |

PeerSelect 副轨另保留 graph-ipd reference selector、random/local-uniform、no-history
selector 和 history-only selector；这些只回答局部选择与在线更新问题。ArtifactRole
主轨必须包含上表的 raw/terminal/contextual/RARE 责任对照和 closest published
adapter。当前唯一进入候选审查的 closest semantic adapter 是
**Meta-Team L2-style downstream reflection/profile**（论文 `arXiv:2605.29790v1`，
代码锚点 `36dc85d9dc2219d292fa180f347479738a84acb2`）。它没有被当作可直接复现的
drop-in：本地源码未发现明确 LICENSE/COPYING，只能按论文语义独立重实现。严格标准下，
若不新增责任协议，ArtifactRole 的 published closest 为 `NO-GO`；允许 adapter 时，
状态为 `NOT_IMPLEMENTED / QUALIFICATION_REQUIRED`。DecisionBench 只作 selector/delegation
control，CooperBench 只作 collaboration substrate，graph-ipd/PeerSelect 只作机制副轨。

Meta-Team 候选必须拆为三个报告 cell：`L2-original-info`（保留原生终局/轨迹信息的
宽信息上限诊断，不进入主同信息比较）、`L2-public`（只读 ArtifactRole 公开
delivery→recipient judgment/use/repair→arrival/correction 事件，profile schema、摘要
规则与调用上限预注册）以及 `L2-ablation`（profile-only/no-L3）。任何 arm 都必须共享
公开 ownership、候选菜单、propensity、arrival schedule、成本口径和 UNKNOWN no-update
规则。若 profile parser、摘要预算、later assignment、独立 history 或完整成本不能冻结，
该 adapter 保持 `NO-GO`，不能用手写 trust score 冒充。

RLS、online logistic/SGD、periodic refit 和候选增量 updater 是训练更新比较，不能被重复计入选择 policy，也不能称成 RARE 创新。所有选择 policy 的反馈输入合同必须在实验卡中逐项写明：`raw_acceptance` 只能读合法 recipient accept/reject；`terminal_only` 只能读独立 final outcome；`contextual_trust` 与 RARE 读取相同的 eligible/UNKNOWN、selected-only、propensity、arrival order 和延迟字段，但使用自己的更新规则。任何 policy 都不能把 UNKNOWN 当负例或读取另一个 policy 的 state。

## 4. 实验问题与指标

- **RQ1（主轨信息价值）**：situated judgment 能否预测独立 producer contract/later-use 结果，超出 raw acceptance 与 terminal-only？
- **RQ2（主轨闭环）**：责任证据是否在下一次执行前改变未直接评价候选者 owner 的 assignment，并在未见 root 上改变质量、返工和完整成本？
- **RQ3（副轨机制）**：局部候选、selected-only 更新和漂移后恢复是否在相同预算下改善 payoff/regret，同时满足在线服务预算？
- **RQ4（共同边界）**：责任不清、consumer 自有错误、版本替换、漂移、延迟/乱序反馈时，UNKNOWN 与保护写入是否比错误惩罚更稳健？

主结果按独立 stream 汇总，不把同一 stream 的多个 episode 当独立样本。稳定性报告旧 root holdout 的峰值/平均下降和恢复窗口；时效性报告 drift 后响应窗口；成本包括 producer、recipient、judge、通信、重试、返工、scorer 和 replay。

## 5. 实验顺序与停止规则

1. 零 LLM：分别验证两个轨道的材料、可见性、权限、scorer、ledger replay、sidecar、重复/乱序/UNKNOWN 和 snapshot/restore。
2. PeerSelect 副轨 CPU 机制资格：先验证局部图、selected-only payoff、延迟/漂移和成本指标；结果不得写成主轨 role-learning 证据。
3. ArtifactRole 主轨单 root 最小真实流：只回答接口、责任归因和信息价值；不宣称闭环效果。
4. ArtifactRole 两个 root、独立 live history 的开发卡：冻结主轨 manifest、policy、预算、主指标和失败规则后执行。
5. ArtifactRole 独立 confirmation root：不得在看完开发结果后改 split、label 或指标。
6. 只有任一轨道暴露真实训练瓶颈且方法/benchmark 门已通过，才提交一个 A800 bounded challenger。

停止条件：scorer/ledger/责任边界失败；没有真实 recipient action；policy 无法区分 eligible 与 UNKNOWN；或 RARE 与 contextual trust 在同信息、同成本下没有预注册增量。停止保留失败证据，不修改 Goal。

## 6. 当前证据与开放项

已有工程资产包括 task contract、sandbox、lineage/replay、部分 policy sidecar qualification、graph-ipd CPU smoke 和 RARE candidate diagnostics；RARE 的统一 selected-only 选择适配器与 event-time/correction seam 已通过零调用资格。七个 arm 现在也有一个七 case 的离线 root-level parity runner，能统一检查候选菜单、seed、registry、protocol/source lineage、预注册 schedule digest、event-time、selected-only、UNKNOWN reason、raw acceptance 正向更新、决策序列、observe-before-choose 和 snapshot replay；其 v1--v8 失败/修复与 v9 通过回执均保留。Meta-Team-L2-public 已通过零调用 profile schema、typed-sidecar fixture builder 和 source replay boundary（包括真实 PIPE3 seed-0 material、ledger record hash、selected-only、public eligible、完整 source-input digest、watermark、later assignment、correction、digest 和 hidden-info rejection），assignment offer/consumption attestation 及其到后续 selection 的 decision/menu/read-cut binding 也已通过零调用 contract；hand-authored fixture runner 进一步将该绑定接到 `selection→task_start` 并能写入 native `PeerRoleLedger`，记录四阶段 trace、task-start record hash，并经严格 versioned/native selection-view adapter 保留 `candidate_id@version`、菜单顺序、chosen index 与 selected-at 时间；它拒绝缺失 attestation、错误 menu、过早 watermark、profile mutation、未知版本和菜单重排。typed projection 到 public feedback row 再到 `AssignmentEvidenceOffer` 的严格序列化子门也已通过；source-bound adapter 进一步要求 canonical ledger binding、v4 responsibility lineage 和 frozen arrival schedule 后才允许封存 offer。它要求 v4 event-time、保留 UNKNOWN 的公开 reason/修订血缘，并拒绝任意 scorer 字典。真实 v6 ledger 也已通过该 source-bound path 的离线回放，recipient-owned repair 被保留为 UNKNOWN；这只验证历史 artifact 的责任归因不会泄漏成 producer label。assignment runner 还有一个已验证的 opt-in separate-process public-profile read path，并已与 selection→native task_start 在同一离线 trace 中闭合；typed generator seam 只提供 deterministic public-only fixture 与成本/声明 receipt，随后已有一个 root-specific、两控制的 CPU composition 把实际 v2 scorer/action/outcome 输出接入 eligibility→source-bound offer→profile/UNKNOWN→isolated read→selection→native task_start。该 composition 仍不是真实 next-episode 或科学效果。新增的 PIPE2 v2 runtime qualification 在 seed 0/2 实际执行 producer extractor 与 recipient transform/load，并由 producer×recipient 2×2 矩阵、完整 key sequence/row count lineage、独立 canary 和 drop-row/ignore-artifact negative controls 分别测量 producer contract、recipient self 与 artifact adoption；随后对 seed 0–9 做 shape audit，发现 1/4/6/9 的 generator CSV 因未转义逗号产生额外 `None` 字段，因此 invalid fixture 不发标签，PIPE2 仍不是冻结 benchmark。旧 v5/v6 关于 synthetic canary 的过宽表述已撤回，历史 receipt 保留但不与 v2 合并。真实 profile 生成质量、独立 live history、完整成本和 later-use effect 仍未实现。上述 runner 仍是工程资格，不能替代每个 arm 的独立 live history，也没有完成完整 benchmark cell、Meta-Team-style closest adapter 或 A800 训练结果。N02 两条有限真实链没有产生概率变化。两个轨道的 benchmark 都尚未冻结，强 baseline parity、独立 confirmation stream 和 A800 训练结果均未完成。

2026-10-04 public-input parity amendment：canonical PIPE3 v20 将原生 ledger → `RoleEvidenceOffer` → delayed credit → `PeerHistoryV1` 的公共 projection 接到七 arm 离线回放；菜单、read-cut、arrival、read-cut-specific 64-d `phi`、cost schema 与 per-arm namespace 的 public trace digest 一致，UNKNOWN/no-evidence、反馈 after frozen read-cut、offer bundle-digest mutation 的 false accept 均为 0（`experiments/logs/n03_canonical_pipe3_parity_20261004_v20/`）。v18 中发现 terminal `quality_score/outcome_status` 被误纳入 RARE φ、而 contextual trust 未消费，已保留为中间失败证据；v19 排除这些字段，v20 进一步升级 φ schema 版本并修正 late-cell 标识。该 amendment 只关闭 public-input/schema 工程门，不构成 scientific same-information baseline parity；valid cell 只提供 recipient-judgment row，raw-acceptance/terminal-only 的正向 source adapters、registry/history adversarial、benchmark authority、second root、独立 live history 和 later-use outcome 仍开放。

## 7. 对照标准

本文件按 [`benchmark_baseline_v1.2_20260929_eval.md`](../evaluation/benchmark-baseline/benchmark_baseline_v1.2_20260929_eval.md) 审查。故事与创新见 [`storyline_v1.1_20260928.md`](../storyline/storyline_v1.1_20260928.md)，方法合同见当前生效的 [`method_v1.1_20260930.md`](../method/method_v1.1_20260930.md)。轨道确认记录见 [`ADR 0042`](../../../user/decisions/0042-confirm-artifactrole-primary-peerselect-secondary.md)。
