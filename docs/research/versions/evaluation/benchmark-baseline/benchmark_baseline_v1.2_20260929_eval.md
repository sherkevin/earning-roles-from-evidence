# Benchmark 与 baseline 评价标准 v1.2

- **状态**：`ACTIVE`
- **类别**：evaluation/benchmark-baseline
- **评价对象**：[`benchmark_baseline_v1.1_20260930.md`](../../benchmark-baseline/benchmark_baseline_v1.1_20260930.md)
- **生效日期**：2026-09-29
- **前一版本**：`benchmark_baseline_v1.1_20260928_eval.md`
- **用途**：在任何新 API、GPU 或正式论文结果前，审查 benchmark/baseline 是否真的能够识别主张、公平比较并解释结果。它是严格门槛，不是录用承诺。

## 0. 先判定研究轨道，不能把两个问题混成一个分数

当前项目有两个互补但不能互相替代的科学层次，必须在实验卡中明确 primary track：

| 轨道 | 要识别的主张 | 合格证据 | 不能单独声称的内容 |
|---|---|---|---|
| `PeerSelect` 机制轨道 | 局部候选集合、selected-only feedback 和在线更新是否改善选择/收益、延迟和漂移恢复 | 真实持久节点、无向局部图、可审计 payoff/label、独立 live streams | 不能单独声称 recipient 对 artifact 的 situated judgment 或责任归因成立 |
| `ArtifactRole` 任务轨道 | recipient 的实际使用/返工/拒绝能否形成可归因 producer evidence，并改变后续 assignment 和质量/成本 | 独立 producer contract、recipient action、sink adoption、later assignment、责任 gate | 不能把外加 selector 的一次工程接入当作 selector 机制已被证明 |

两个轨道可以共享 candidate-set、selected-only event、延迟 ledger 和 updater API，但任务、label、scorer、统计分母和结论必须分开。实验卡必须写出：`primary_track`、`secondary_track`、两者之间的 transfer claim；未填写时不得进入科学实验。

## A. Benchmark 选型硬门：适配性、权威性、覆盖度

### A1. 选型评分卡

候选 benchmark 只有在以下六个维度全部 `PASS` 后，才能写成主 benchmark；任一项 `OPEN` 只能写 `candidate`，任一项 `FAIL` 不能作为主结果来源。每项须给出文件、命令、hash 和审查人，而不是一句主观判断。

| 维度 | 必须回答的问题 | PASS 证据 |
|---|---|---|
| 主张适配 | 任务是否真的包含本轨道要识别的选择、使用、反馈、归因和未来行为链？ | 一张从原始任务字段到每个科学变量的映射表；不能靠 wrapper 名称补齐缺失变量 |
| 上游权威 | 是否有可追溯的论文/官方仓库/维护者、固定 commit/tag、许可证和官方 scorer？ | URL、commit、license、版本与上游运行回执；自定义层必须披露差异 |
| 任务多样性 | 是否有结构不同的 root、不同能力/依赖和真实难度，而不是 seed 改名？ | root taxonomy、共享与独有输入审计、结构相似度/依赖图和 split manifest |
| 信号可识别 | label 是否来自执行前不可见的独立 contract、recipient action、adoption 或 payoff？ | label provenance、responsibility ownership、selected-only/延迟语义和 mutation matrix |
| 污染与复现 | 候选是否读不到答案、hidden tests、后验结果或别的 policy state？第三方能否 clean replay？ | contamination audit、权限/可见性回执、clean-environment reconstruction 命令 |
| 规模与精度 | root、stream、episode 数是否足以支持预注册的效应/精度，而不是事后聚合？ | power/precision note、每格最小独立 stream 数、失败和 UNKNOWN 预算 |

### A2. 根任务和证据边界

- 至少两个结构不同 root；`Proceedings-ready` 的强标准是三个或以上 root，或事先注册且有定量精度理由的双 root 设计。
- seed、改名、字段顺序和同一 generator 的参数轻微变化不自动增加独立 root。必须给出 root-level 依赖矩阵。
- 每个 `ArtifactRole` root 都要独立测量 producer contract、recipient use/modify/rework/reject、sink adoption、final outcome 和 later assignment。recipient 自有错误不能直接记为 producer 失败。
- task/source/tests/expected/scorer/operator ledger/candidate workspace 的可见性、写权限、网络、时间和资源边界在运行前冻结。
- 任务文本不能泄露修复方向、hidden test 名称、答案或后验 label；候选 agent 不能读 private gold、其他 policy state 或 operator ledger。
- scorer、ledger、lineage、UNKNOWN 和资源失败必须有零调用 mutation matrix；覆盖不足只能 `UNKNOWN`，不能改成 `FAIL` 或 `PASS`。

### A3. 当前项目的选择判定

`PeerRoleBench-TB` 仍是 TeamBench-derived 候选协议，不是已经冻结的公认 benchmark；`DIST1` 的历史任务文本泄露修复方向，`PIPE3` 尚未完成科学文本、later assignment 和独立 stream 资格。因此当前最多是工程候选，不能写成 benchmark 已通过。若采用 `PeerSelect-IPD/graph-ipd` 作为机制轨道，必须同时保留上述 ArtifactRole 轨道的独立结论，不能用 payoff 结果替代 situated judgment 结果。

## B. Baseline 选型硬门：能排除哪些替代解释

### B1. 基线角色必须覆盖四类问题

主比较至少包括下表。每个 arm 必须有真实可执行入口、版本、配置、代码 hash、同一事件 schema 和独立 qualification；只在表格里列名字不算 baseline。

| 基线角色 | 必要条件 | 识别目的 |
|---|---|---|
| 下界/不学习 | `uniform`、`no_update`，初始先验和 base score 冻结 | 排除随机选择和静态执行已足够 |
| 反馈机制消融 | `raw_acceptance`、`terminal_only` | 区分 situated judgment、终局结果和粗糙 accept 信号 |
| 最强同信息 | `contextual_trust`/bandit，读到与 RARE 相同的合法字段、延迟、propensity 和候选菜单 | 排除“只是用了 context/更多历史”的替代解释 |
| 共享历史上界 | same-menu `pooled_controller`；unrestricted centralized oracle 只能作诊断上界 | 区分局部 peer 约束和集中式信息收益 |
| 最近邻方法 | 一个可复现、与主张最接近的已发表方法 faithful adapter | 满足 state-of-the-art comparison，不以自造弱基线代替 |
| 主候选与必要消融 | `RARE` 及 responsibility gate、selected-only、延迟、局部性、更新模块消融 | 识别每个机制组件的独立贡献 |

RLS、online logistic/SGD、periodic refit 和其他 updater 是训练更新 comparator，不能被重复计入 policy 创新。oracle 不能成为唯一强 baseline。

### B2. 信息和成本 parity

每个 arm 必须逐项填写 parity table：候选集合、初始状态、可见字段、责任资格、UNKNOWN/selected-only、arrival order、延迟、exploration/propensity、LLM/model/API/tool/token/scorer/retry/communication 预算、state capacity、backbone、并发、wall-clock、训练/判断/评估/返工成本。没有 judgment 的 arm 如何计费也要预注册：要么所有 arm 调用同一判断再屏蔽输入，要么明确报告额外服务成本与 quality-cost Pareto。

任何 baseline 读到更多信息、拥有更多预算、继承 proposed policy 的 live memory 或使用不同候选菜单，整组比较无效。`pooled_controller` 默认仍受同一 menu 约束；不受约束的集中式策略只能作为 upper bound。

### B3. Baseline 冻结判定

在 `raw_acceptance`、strong same-information contextual trust、closest published adapter、RARE 和统一 live runner 全部通过 executable qualification 前，baseline 状态为 `NOT_FROZEN`，不得启动正式效果流或 A800。到 2026-09-30，统一 factory、RawAcceptanceSidecar projection/replay、RARE selection adapter 以及七 arm 的 v9 离线 matrix runner 已通过零调用子门；v9 还覆盖 observe-before-choose、raw acceptance 正向更新、UNKNOWN、unselected、protocol/source lineage 和早/迟反馈。它们仍是协议与实现资格，不能替代真实 PIPE3 versioned runner、完整成本/later assignment、closest published adapter、独立 live histories 或 same-information scientific comparison；此项仍不通过。closest published 审计还确认：严格 ArtifactRole causal unit 没有可直接复现的 drop-in；Meta-Team L2-style 只能作为待实现的 original-info/public/ablation 语义候选，不能把 selector/delegation 控制冒充 closest。见 [`20260930_policy_matrix_runner.md`](../../../../coordination/task_reports/20260930_policy_matrix_runner.md)、[`20260930_closest_adapter_audit.md`](../../../../coordination/task_reports/20260930_closest_adapter_audit.md)、[`20260930_rare_policy_adapter.md`](../../../../coordination/task_reports/20260930_rare_policy_adapter.md)、[`20260929_raw_acceptance_projection_contract.md`](../../../../coordination/task_reports/20260929_raw_acceptance_projection_contract.md) 与 [`20260929_raw_acceptance_replay_contract.md`](../../../../coordination/task_reports/20260929_raw_acceptance_replay_contract.md)。

## C. 实验矩阵硬门：从名单变成可执行设计

实验矩阵不能只列 RQ 或 policy 名称，必须在执行前生成一张完整 cell manifest。每个科学 cell 至少固定以下正交因素：

1. `track/root/split`：primary track、development/confirmation、结构 root 和未见 root；
2. `policy/information`：uniform、no-update、raw、terminal、same-info contextual、closest published、RARE 与必要消融；
3. `responsibility`：producer-defect、recipient-only、sink-only、mixed/unknown，且明确哪些反馈可更新；
4. `locality/pool`：local candidate graph、same-menu pooled history、centralized oracle（诊断）；
5. `time`：early/late/乱序 arrival、版本替换、drift 前后和服务预算；
6. `stream/seed`：独立 live history、RNG、propensity、并发、停止规则和失败重跑规则。

每个 cell 还必须写：冻结输入与 prompt、candidate menu、model/API route、token/tool/scorer/retry 预算、state cap、eligible sample unit、primary endpoint、比较 arm、预期方向、最小 effect/上限、95% interval、UNKNOWN/未启动处理和复现命令。匹配 baseline 使用同一材料、RNG、arrival schedule 和候选菜单；matched replay 只能做机制诊断，不能替代独立 live history。

## D. 结果合理性与解释硬门

### D1. 结果完整性

主分析至少覆盖：

- **信息价值**：judgment 对独立 contract/later-use/payoff 的 out-of-sample log-loss、Brier/AUC 或校准增量；
- **闭环后果**：未来执行开始前的 assignment change、未见 root 质量、返工、采用率和完整成本；
- **在线性质**：update/selection p50/p95、端到端 lag、state size、drift recovery、旧 root 遗忘；
- **边界行为**：版本替换、延迟/乱序、recipient 自有错误、责任不清、scorer/资源失败和 UNKNOWN 率。

逐 root/stream 报告原始结果、ITT 与 per-protocol 分母、均值/中位数、95% interval、effect size、失败/UNKNOWN/未启动数、异质性、quality-cost Pareto、selection propensity、judge reliability/calibration、OOD/cross-root transfer。stream/episode/root 的聚类单位、层级 bootstrap 或配对随机化、缺失上界和多重比较校正必须预注册。

### D2. 数值门和结果 truth table

执行前必须冻结 `delta_information`、`delta_quality`、`delta_cost`、`tau_update_p95`、`rho_unknown`、允许的 forgetting/recovery window 以及 power/precision 计算。没有数值门时只能报告 exploratory，不能用聚合或换指标提高结论等级。

| 观测组合 | 允许的结论 |
|---|---|
| 信息增量和闭环质量/成本均达到门槛，且无安全/延迟回归 | 支持主机制，在测量范围内成立 |
| 有信息增量但 assignment/质量没有改善 | 只支持预测性信息，不能声称 role learning 改善团队 |
| 闭环改善但信息增量不足 | 结果被其他差异混淆，不能归因于 situated judgment |
| RARE 与 strong contextual trust 相当或更差 | 主机制未被识别；停止扩展模型/A800，报告负结果 |
| 质量改善但完整成本、UNKNOWN 或延迟超过门槛 | 不支持 quality-cost 主张，只能报告 trade-off/工程结果 |
| 精度不足、独立 root/stream 不足或大量未启动 | `exploratory`/协议结果，不写主科学结论 |

结果边界检查必须验证分数范围、成本守恒、合法反馈才更新、UNKNOWN 不更新、arrival 顺序、replay 一致性和没有后验泄漏。不得看过结果后改变 benchmark、baseline、primary metric、label 或 claim 范围。

## E. 可复现性、污染和 artifact 硬门

权威基座必须固定 source URL、commit/tag、license、数据版本、scorer 版本和 generator hash；自定义 `PeerRoleBench-TB` 扩展必须公开复现入口，并说明为什么仍保持上游任务语义。运行前做 task/source/test/expected/LLM contamination audit。每个 arm 保留 config、prompt/template、model/API route/version、temperature、tool、token、并发、timeout、retry、storage、GPU 和调参记录。clean environment 必须能从 manifest 重建数据、runner、scorer、主分析脚本和结果摘要，不能只提供截图或手工 notebook。

## F. 结果等级、停止和当前判定

- **Findings-ready**：一个可复现、范围有限的 benchmark/方法/负结果，至少一个独立确认或严格受控诊断，明确不推广到未测范围。
- **Proceedings-ready**：至少三个结构独立 root，或双 root 的预注册精度理由；每个主条件多条独立 live streams；完成同信息强 baseline、未见 root、完整成本、统计和 clean replay。
- 任务泄漏、root 非独立、隔离失败、baseline 不公平、UNKNOWN 被当负例、没有独立 confirmation、没有失败分母、没有完整成本或结果看后改变标准时，不得写主结果。
- `RARE` 未超过 strong contextual trust，或未达到质量—成本/实时性/稳定性门槛时，停止 A800 和更大规模 API，保留失败证据。

**本次审计结论（2026-09-30）**：benchmark 选型、baseline root-runner parity、实验 cell freeze、closest published adapter、数值精度门和科学结果仍为 `NOT_READY`/`OPEN`。七个 arm 已通过 v9 零调用 matrix qualification，RARE、raw channel 和 Meta-Team-L2-public profile schema/fixture-builder/source-replay boundary 也已通过零调用子门；offer/attestation 及 next-selection binding 已接入一个 hand-authored `selection→task_start` fixture runner，并验证 native `PeerRoleLedger.task_start` 写入；新增的严格 versioned/native selection-view adapter 还验证了 candidate version、菜单顺序、chosen index、task index 和 selected-at 时间的显式保留及未知版本/菜单重排拒绝。typed projection→public feedback row→`AssignmentEvidenceOffer` 的严格序列化与 UNKNOWN event-time 保留也已通过零调用子门；source-bound adapter 还把 canonical ledger binding、v4 responsibility lineage 和 frozen arrival schedule 放在 offer sealing 之前，但这些仍只验证状态机、ledger 接缝、身份映射、公开信息投影与拒绝边界。新增的 generator seam 只资格化 deterministic public-only fixture、digest/成本 receipt 和 UNKNOWN/private 输入拒绝，不是真实 profile generator。随后一个 root-specific 的两控制 CPU composition 已把实际 v2 scorer/action/outcome 输出接到 eligibility、source-bound offer、profile/UNKNOWN、isolated read、selection 和 native task_start；它仍是单 structural root、deterministic profile 和零调用工程资格。它没有关闭统一 live history、真实 profile 生成质量、assignment/next-episode 的科学效果、可公平执行的 closest adapter、独立 root/stream、完整成本或 policy effect；离线 offer/attestation 与该 composition 不能替代这些门。冻结 v6 真实 ledger 的 source-bound 回放还证明 recipient-owned repair 会保持 UNKNOWN，不会被转成 producer label；已有的真实链只证明责任 gate 能阻止不合格更新。Goal 不降级，下一步先资格化真实 public-only profile generator，再决定是否进入一条新的有界真实 episode，随后才考虑完整 cell manifest 和 A800。

2026-10-02 update：parity gate 进一步要求每个 arm 的 accepted feedback source 与实际 update
一致；`credit_committed` 不再单独构成通过。`role-evidence-judgment-beta-v1` 作为无状态
assignment comparator 已完成零调用定向测试，但尚未接入 live runner。evidence-content mutation
在当前 hand-authored overlay 下不会改变 chosen index/probabilities，因此 evidence-to-decision
可识别性仍未通过；这两个结果保持 benchmark/baseline `NOT_READY`，不允许启动正式效果流或
A800。

2026-10-05 current-state amendment：canonical runtime stream builder 已通过工程资格，
但静态 parity audit 发现 RARE 使用 64-d `captured_features`，而现有 contextual/pooled
controls 只消费 context/candidate Beta state，且 RARE 忽略 `base_scores`。这直接触犯
本标准 B1/B2 的 strongest same-information 要求；因此不能把当前七臂 offline matrix
称为 scientific baseline parity，也不能启动 bounded live efficacy。待确认的最小修复是
实现同一 `φ` 的 feature-aware contextual control，并完成 mutation/replay、cost、arrival
和 snapshot qualification；closest published 的 A0、第二 root authority 的 B0 仍应先做
低成本 go/no-go 审查。三份 active 文档和 Goal 均不降级。

## 来源边界

AAMAS 官方要求 relevance、validation、evidence、state-of-the-art comparison 和 reproducibility；root 数量、责任分离、parity table、统计精度、成本口径和 UNKNOWN 分母是本项目为了识别自身主张而制定的严格实验标准，不是 AAMAS 官方指定 benchmark 清单。来源见 [`docs/research/20260928_evaluation_criteria_provenance.md`](../../../20260928_evaluation_criteria_provenance.md)。
