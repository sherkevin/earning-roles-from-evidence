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
| `contextual_trust_linear` | 与 RARE 相同的 `hash64-v1`/`matrix-features-v1`、menu、base score、judgment、propensity 和延迟；普通 diagonal RLS | 当前 strongest same-information comparator 候选；必须通过 live parity 后才可冻结 |
| `contextual_trust` | 只读取 context×candidate 的 Beta/judgment 状态 | context-only diagnostic，不能替代 strongest same-information 对照 |
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

### 2026-10-05 strongest-control qualification amendment

代码审计发现原 `contextual_trust` 并未读取 RARE 使用的 64 维公共 `phi`，且 RARE 的
utility 丢弃了 `base_scores`；所以它不能单独充当 B1 的 strongest same-information
control。新增候选 `contextual_trust_linear` 以同一 `hash64-v1`、64 维 bounded feature、
menu、read cut、arrival、selected-only judgment、base-score、propensity、state cap 和
成本合同运行，使用普通 feature-aware diagonal RLS；原 Beta arm 仍保留为 context-only
diagnostic。零调用 6-case qualification 通过，但 `baseline_frozen=false`，尚未进入七臂
active manifest，也没有 live result。详见
[`feature contextual qualification`](../../../coordination/task_reports/20261005_feature_contextual_baseline_qualification.md)
及其 raw/summary receipt。下一门仍是 canonical manifest parity、独立 namespace/outcome
生成和 A0/B0 go/no-go；不得把离线 qualification 解读为 RARE 优势。

随后 `pipe3-two-stage-composition-v1.8` 将这个公共 feature contract 接入 source/target
selection 与 canonical preview→assignment→commit；`contextual_trust_linear` 的 3-control
zero-call composition 与 feature receipt 通过（[report](../../../coordination/task_reports/20261005_pipe3_feature_composition_qualification.md)）。
它仍使用 hand-authored controls 和 unit scorer，不能当作独立 chosen-candidate outcome、
live parity、质量或成本结果；active 七臂与 `baseline_frozen=false` 不变。

### 2026-10-05 A0/B0 decision amendment

低成本决策门已完成：严格 ArtifactRole closest published baseline 判为 `NO-GO`；
Meta-Team L2-style 只保留为需独立预注册信息边界的 `public adapter candidate`，不能写成
upstream reproduction。PIPE3 保留 primary development candidate；PIPE2 由于 seeds
`1,4,6,9` 的 fixture validity、derived overlay authority 和任务语义尚未闭合，仍不能作为
confirmation root；MULTI3 保留为低条件 fallback。该决定不冻结 benchmark，也不启动正式
API/A800；完整理由与证据见
[`20261005_a0_b0_go_no_go.md`](../../../coordination/task_reports/20261005_a0_b0_go_no_go.md)。

## 4. 实验问题与指标

- **RQ1（主轨信息价值）**：situated judgment 能否预测独立 producer contract/later-use 结果，超出 raw acceptance 与 terminal-only？
- **RQ2（主轨闭环）**：责任证据是否在下一次执行前改变未直接评价候选者 owner 的 assignment，并在未见 root 上改变质量、返工和完整成本？
- **RQ3（副轨机制）**：局部候选、selected-only 更新和漂移后恢复是否在相同预算下改善 payoff/regret，同时满足在线服务预算？
- **RQ4（共同边界）**：责任不清、consumer 自有错误、版本替换、漂移、延迟/乱序反馈时，UNKNOWN 与保护写入是否比错误惩罚更稳健？

### 4.1 2026-10-05 few-shot 泛化实验门

主轨的历史经验不是只按 candidate 累计的计数。每个确认 stream 必须把任务 root、角色
条件、候选版本、edge-local judgment、later outcome、时间和成本作为可检索的历史记录，
并在每个 query 的 sealed read cut 中明确可见集合。实验至少包含：

- `0-shot/1-shot/K-shot` support 曲线，support 只来自 query 之前的任务；
- leave-one-structural-root-out 与 temporal split，禁止随机行切分和近重复泄漏；
- 新候选版本、角色漂移和任务组合漂移；
- no-memory、uniform、普通 `contextual_trust_linear`、最近邻/加权检索、pooled history
  与 RARE candidate 的同信息比较；
- assignment-level future utility/regret、later adoption/terminal quality、选择延迟、
  memory bytes、完整成本、UNKNOWN 分母、旧任务遗忘和 95% interval。

检索器/相似度/`K`/时间衰减必须在实验卡中预注册；later outcome 不得出现在 query 的
表示或检索候选中。该实验门尚未通过，不能用当前固定特征 RLS 的零调用资格替代。

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

2026-10-04 public-input parity amendment：canonical PIPE3 v20 将原生 ledger → `RoleEvidenceOffer` → delayed credit → `PeerHistoryV1` 的公共 projection 接到七 arm 离线回放；菜单、read-cut、arrival、read-cut-specific 64-d `phi`、cost schema 与 per-arm namespace 的 public trace digest 一致，UNKNOWN/no-evidence、反馈 after frozen read-cut、offer bundle-digest mutation 的 false accept 均为 0（`experiments/logs/n03_canonical_pipe3_parity_20261004_v20/`）。v18 中发现 terminal `quality_score/outcome_status` 被误纳入 RARE φ、而 contextual trust 未消费，已保留为中间失败证据；v19 排除这些字段，v20 进一步升级 φ schema 版本并修正 late-cell 标识。v21 在当前 runner SHA-256 `b094416c...` 上完成可复现重放（`experiments/logs/n03_canonical_pipe3_parity_20261004_v21/`）。该 amendment 只关闭 public-input/schema 工程门，不构成 scientific same-information baseline parity；valid cell 只提供 recipient-judgment row，raw-acceptance/terminal-only 的正向 source adapters、registry/history adversarial、benchmark authority、second root、独立 live history 和 later-use outcome 仍开放。

2026-10-04 source-adapter amendment：七-arm fixture matrix 的 raw-acceptance 与 terminal-only 正向更新路径、typed raw sidecar 的 wrong-decision/wrong-producer/duplicate 拒绝，以及 two-entry peer-history 的 permutation/candidate/projection mutation 拒绝均在当前回执中通过（`experiments/logs/n03_policy_matrix_20261004_v1/`, `experiments/logs/n03_raw_acceptance_replay_20261004_v1/`, `experiments/logs/n03_history_adversarial_20261004_v1/`）。该 amendment 只证明可复用工程 adapter 的 reachability 与 fail-closed 行为；它不等于 canonical PIPE3 的 scientific same-information parity。terminal-specific public mapping、runner-level registry preflight、benchmark authority、second root、独立 live history、later-use outcome 和 measured cost 仍开放。

2026-10-04 canonical raw-adapter amendment：native PIPE3 `s0/d0/j0` 经过 `DecisionSidecar → RawAcceptanceSidecar → project_raw_acceptance` 后接入七-arm canonical stream；raw arm 的一次 eligible/update、六 arm ignore/zero-update，以及错误决策、候选、ledger/registry digest、重复、UNKNOWN、迟到七格的 runner-before-start fail-closed 均通过（`experiments/logs/n03_canonical_raw_adapter_20261004_v4/`）。这只关闭 raw channel 的工程接缝，不打开 terminal-only、scientific same-information baseline、second root、独立 live history、later-use 或成本门。

2026-10-04 canonical terminal-adapter amendment：新增独立 `TerminalOutcomeSidecar` 与 `terminal-success-v1` 映射，从 native outcome/delivery/selection/candidate/delivery-record hash 生成只含 public outcome provenance 的 terminal row；terminal-only positive update、六 arm ignore、错误 hash/delivery/selection/candidate/mapping/UNKNOWN/late/duplicate 八格的 preflight fail-closed 均通过（`experiments/logs/n03_canonical_terminal_adapter_20261004_v5/`）。这只关闭 terminal channel 的工程接缝，不能替代 scientific same-information baseline、benchmark authority、second root、独立 live history、later-use 或 measured cost。

2026-10-04 canonical manifest preflight amendment：nested canonical manifest validator 已接入 `PolicyMatrixRunner` 首道 gate；clean commit 上的 synthetic `recipient_only` stream 与14个 manifest mutation/rejection case 通过（`experiments/logs/n03_canonical_manifest_validation_20261004_v4/`）。该回执只证明 manifest 在 policy construction 前可 fail-closed；当前仍未完成 manifest-to-runtime 的 menu/registry/read-cut/arrival/φ digest binding，三类 source projection 也未在同一真实 stream 中执行，因此 baseline、scientific parity、第二 root、live history 和 API/A800 仍未冻结。

2026-10-04 canonical runtime-binding amendment：`validate_runtime_binding` 已接入 runner，
在 synthetic `recipient_only` stream 上同时校验 root/registry/schedule/RNG 与十项 stream
digest；v6 receipt 的 valid、runtime stream mutation 和14个 manifest mutation 均通过
fail-closed（`experiments/logs/n03_canonical_manifest_validation_20261004_v6/`）。这仍
是 engineering-only：stream values 由 qualification caller 显式提供，尚未从真实
offers/三类 source adapter 自动构造，不能写成 scientific same-information parity、
baseline freeze 或 later-use 结果。

2026-10-05 canonical runtime-stream-builder amendment：新增
`build_runtime_stream_values(offers, schedule, registry)`，从实际 `MatrixOffer`、arrival
schedule、candidate registry 与 captured features 生成十项 public stream，再由同一
`canonical_digest` 封存并交给 runner preflight。clean commit `72fb6d2` 的 v8 receipt
完成 valid、synthetic seven-arm preflight、runtime mutation 与14个 manifest mutation，
共17/17 case 通过；负例均在 policy construction 前变为 `UNKNOWN`，0 API/0 GPU
（`experiments/logs/n03_canonical_manifest_validation_20261004_v8/`）。这关闭了
manifest-to-runtime 的公开输入投影工程子门，但仍只使用 hand-authored PIPE3 fixture；
它不构成 benchmark authority、closest-published parity、第二 structural root、
independent live history、later-use utility、measured cost 或 scientific result。下一步
不再继续堆叠 manifest plumbing，而是审查 closest published adapter、第二 root 与
same-information live parity 是否足够进入一条有界 live history。

2026-10-05 same-information parity amendment：静态代码审计发现当前 `RARE` 使用
64-dimensional `captured_features`，而 `contextual_trust`/`pooled_controller` 只使用
context/candidate Beta state；`RARE` 还显式丢弃 `base_scores`。因此现有七臂 matrix 只能
作为 engineering matrix，不能作为 strongest same-information scientific baseline。active
method 的 same-`φ` 要求和 B2 parity gate 保持不变；在确认前不修改历史 receipt、不启动
live efficacy。候选修复是版本化 `contextual_trust_linear_v1`（同一 φ/menu/arrival/
propensity/cost，普通 feature-aware linear/RLS updater），同时保留 Beta contextual 为
辅助 diagnostic；该选择尚未写入 active method，需先完成零调用 mutation/replay
qualification。

2026-10-05 delayed-update seam amendment：候选 `DelayedPolicyAdapter` 在
`FeatureContextualTrustPolicy` 上通过 8 格零调用资格，并在严格路径复用 canonical
replay/history binding，补齐 public evidence 不更新、later target channel 更新和
assignment-level alternate-outcome 拒绝。该 adapter 仍未
进入 active 七臂 manifest；canonical ledger replay、独立 target histories、四格信息价值
和完整成本未完成，因此 `baseline_frozen=false` 保持不变。

## 7. 对照标准

本文件按 [`benchmark_baseline_v1.2_20260929_eval.md`](../evaluation/benchmark-baseline/benchmark_baseline_v1.2_20260929_eval.md) 审查。故事与创新见 [`storyline_v1.1_20260928.md`](../storyline/storyline_v1.1_20260928.md)，方法合同见当前生效的 [`method_v1.1_20260930.md`](../method/method_v1.1_20260930.md)。轨道确认记录见 [`ADR 0042`](../../../user/decisions/0042-confirm-artifactrole-primary-peerselect-secondary.md)。
