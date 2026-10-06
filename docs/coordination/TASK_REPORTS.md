# Task reports

每个小任务完成后必须在 `docs/coordination/task_reports/` 写一份报告，并与
[`GOAL.md`](GOAL.md) 对照。报告不能只写“做了什么”，必须回答：

1. 本任务对应 Goal 的哪条硬标准；
2. 运行前冻结了什么，真实使用了什么 API/fixture，原始证据在哪里；
3. 哪些标准已满足、哪些只部分满足、哪些未开始；
4. 未完成的具体原因是实现缺陷、任务/评分缺陷、证据不足还是外部阻塞；
5. 下一步修复是什么，是否需要用户决定；
6. 是否存在 Goal 变更请求。没有用户明确同意时，必须写 `goal_change_requested=false`。

固定状态含义：`COMPLETE` 只表示对应 Goal 条目有足够证据；`PARTIAL` 表示工程或
协议进展但科学门未过；`OPEN` 表示尚未取得证据；`UNKNOWN` 表示运行无法判定；
`BLOCKED_BY_EVIDENCE` 表示继续运行前必须先修复测量/资格问题。失败不会自动变成
Goal 修改。

## Reports

- [partial] 2026-10-06 structural-owner gate activation：按用户确认将 contract/registry/scorer 推导的 structural owner 升格为 active method v1.2，保留 judged-role disagreement 做校准；A1--A8 zero-call mutation/replay qualification 8/8 通过，43 项定向回归通过，科学效能门仍开放，见 [activation report](task_reports/20261006_structural_owner_gate_activation.md)。

- [partial] 2026-10-06 structural-owner paper PDF：将 v1.2 责任门同步到主稿，重新构建并视觉核验正文 8 页、参考文献第 9 页起、0 overfull；结果表仍为空，科学投稿门保持关闭，见 [PDF report](task_reports/20261006_structural_owner_paper_pdf.md)。

- [partial] 2026-10-06 active-document version reconciliation：将 active storyline、benchmark/baseline 与方法评价标准同步到方法 v1.2 / 评价 v1.3，修复六份研究主文档的版本闭环；未改变 Goal，科学 benchmark、baseline parity 和 efficacy 仍开放，见 [reconciliation report](task_reports/20261006_active_document_version_reconciliation.md)。

- [partial] 2026-10-06 C1 v2 card freeze：为下一条 bounded live stream 显式冻结 structural-owner/judged-role 合同、注册 producer defect 与完整成本字段；一次突变校验失败已修复，16 项定向测试通过，尚未发起 API，见 [card report](task_reports/20261006_c1_v2_card_freeze.md)。

- [blocked_by_evidence] 2026-10-06 C1 v2 live rerun：10 个真实 API 请求验证 structural owner 与 judged-role disagreement；no-update 与 RARE 完成开发链，contextual arm 因真实 recipient-owned `processor.py` 修改正确停为 UNKNOWN。发现共同完成样本与成本聚合仍不足，已修复 runner 记录缺口，不重复运行同一识别不足的卡，见 [live result](task_reports/20261006_c1_v2_live_result.md)。

- [blocked_by_evidence] 2026-10-06 post-rewrite paper gate review：独立 Codex 复核确认纸面结构、8 页排版和引用覆盖已有明显改善，但 ArtifactRole benchmark、same-information baseline parity、确认 manifest、候选方法锁定和真实结果仍未过科学门；同时用 ADR 0046 修复主稿标题漂移，见 [gate review](task_reports/20261006_updated_paper_gate_review.md)。

- [partial] 2026-10-06 credit-assignment and interactive-agent reference pass：补入 AgentBench、$\tau$-bench、COMA 与 QMIX，并将共享回报的 credit-assignment 先行工作与本论文的 artifact ownership 边界写成可检验对照；v2 仍保持正文 8 页，见 [reference pass](task_reports/20261006_credit_assignment_reference_pass.md)。

- [partial] 2026-10-06 candidate realization boundary：在方法公式前明确 profile/delta/residual 只是用于资格验证的候选实现，最终 backbone/updater 仍待 same-information controls 后锁定；v3 仍保持正文 8 页，见 [method boundary report](task_reports/20261006_candidate_realization_label.md)。

- [partial] 2026-10-06 experiment-matrix design boundary：在正文明确 RQ 矩阵是 pre-specified design scaffold，只有 root/stream/seed/budget/scorer/cost/stopping/manifest 全部预冻结的 cell 才能进入 confirmation analysis；v4 仍保持正文 8 页，见 [matrix report](task_reports/20261006_matrix_design_boundary.md)。

- [blocked_by_evidence] 2026-10-06 ownership-gate candidate design：在等待 A/B 选择期间，准备结构化 owner + judged-role calibration 的非生效候选设计和 8 个 zero-call mutation/replay cells；不改 active method、不启动 live/API/GPU，见 [candidate design report](task_reports/20261006_ownership_gate_candidate_design.md)。

- [partial] 2026-10-06 AI figure drafts v17：按用户要求改用 AI 出图并保留全部版本与提示词；Figure 2 v2 修复了 v1 的语义箭头错误，三张图仍等待专业平台重绘后才替换正文资产，见 [figure report](task_reports/20261006_ai_figure_drafts_v17.md)。

- [partial] 2026-10-06 AAMAS reference expansion and citation audit：将当前主稿参考文献扩展到 24 条、正文实际引用 18 条，补齐 benchmark、协调、信任/声誉、上下文选择、延迟反馈与团队研究的原始来源；引用覆盖改善但科学门仍未打开，见 [reference report](task_reports/20261006_reference_expansion_audit.md)。

- [partial] 2026-10-06 AAMAS paper structure and prose rewrite：按六范式审计与 AAMAS best-paper 写作规律重写摘要、引言、相关工作、benchmark 定位与贡献链，隔离构建正文正好 8 页；benchmark 资格、强基线和真实效果仍开放，见 [structure report](task_reports/20261006_paper_structure_rewrite.md)。

- [blocked_by_evidence] 2026-10-06 ownership gate design review：C1 v3 显示同一结构化 source
  在不同 arm 得到不同 `target_role` 文本，导致 contextual arm 被随机 censor。报告区分
  contract-defined structural owner 与模型 judged role，给出保守 gate 与校准字段的两种
  版本；未修改 active method，下一次 live comparison 前必须显式选定，见
  [ownership review](task_reports/20261006_ownership_gate_design_review.md)。

- [complete] 2026-10-06 AAMAS body-page budget recheck：隔离构建正文正好 8 页、参考文献从第
  9 页开始、0 overfull，PDF 与 verification receipt 已保留；科学 submission gate 仍关闭，见
  [page recheck](task_reports/20261006_paper_page_budget_recheck.md)。

- [partial] 2026-10-06 C1 bounded PIPE3 live development card：真实 API v3 完成 10 个请求；
  `no_update` 与 RARE 的严格 ledger replay 通过，RARE 发生 1 次 delayed update，
  `contextual_trust_linear` 因模型责任字段触发严格 gate 而 UNKNOWN；复核还发现 judgment
  label 与 terminal quality、repair-cost 命名和汇总成本字段需要分开。v1 启动错误和 v2
  ledger 缺陷均保留并修复；这仍只是单 root development seam，未打开 scientific gate，见
  [C1 card](task_reports/20261006_c1_bounded_live_card.md)。

- [partial] 2026-10-05 AAMAS paper framework and exact body-page build：按官方 AAMAS 2027
  instructions 将主稿补齐为可执行的 pre-results 论文框架，加入 selector/state contract、
  result-filling contract、RQ1--RQ4 结果占位和 artifact/replay 说明；隔离构建核验正文
  正好 8 页、参考文献从第 9 页开始、0 overfull、引用解析、官方模板文件未改。科学
  readiness 仍为 false，结果、最终 benchmark/backbone/update 和 submission gate 均未被
  伪造完成，见 [paper framework report](task_reports/20261005_paper_framework_eight_pages.md)。

- [blocked_by_evidence] 2026-10-05 fusion method self-audit：对“profile prior + episodic
  evidence + delayed residual”按 ER-G2、方法评价和 AAMAS 反驳门复核；可实现性 7.0/10，
  标签有效性 4.0、任务泛化 4.5、可识别性 3.5、创新性 3.5，当前方法门不通过。主要问题
  是同一 evidence 重复进入 profile/prototype、`y^J`/`y^L` 快照未隔离、选择偏差和融合
  权重未冻结。修订候选 v0.2 分开 profile snapshot、post-cut evidence delta 和 later
  residual head，并新增 provenance、permutation、topic/identity controls；Goal 不变，
  未通过 CPU temporal gate 前不启动 API/A800，见 [self-audit](task_reports/20261005_fusion_method_self_audit.md)。

- [partial] 2026-10-05 embedding profile debate：用户提出将 peer judgment 聚合成 Agent
  画像并用 task/profile embedding 匹配；经 primary-source 复核，FlyRoute 已有 success-store/
  profile distillation/routing，AgentNet 已有 capability-vector similarity，DyTopo 已有
  semantic topology matching，因此该组合不能单独作为创新。保留 A 作为 profile baseline，
  优先验证 B 条件化 edge-evidence retrieval，再视跨 root 瓶颈决定是否训练 C compatibility
  head；随后补充融合候选“profile prior + episodic evidence + delayed residual”，三层分工
  和标签归属已记录，见
  [debate report](../research/debates/20261005_embedding_profile_debate.md)。

- [blocked_by_evidence] 2026-10-05 few-shot task generalization gap：确认当前在线 RLS 只更新固定特征，尚未执行历史任务相似度检索；将任务记忆、相似任务支持度、严格 read-cut、few-shot/任务族切分、泛化与遗忘指标列为方法和 benchmark 的必需科学门。延迟 policy adapter 可作为记忆写入/回放接缝，但尚无 few-shot 泛化证据，见 [gap report](task_reports/20261005_few_shot_task_generalization_gap.md)。

- [partial] 2026-10-05 六份研究主文档质量审计：核对唯一 active registry，逐项评价故事线/方法/benchmark+baseline 与对应三份评价标准的结构、可实现性、证据边界和完备性；确认文档治理约 8/10，但科学 readiness 仍未通过。补齐方法符号到 PIPE3 case 的最小实例表，收敛 `contextual_trust_linear` 与 context-only diagnostic 的 baseline 名称歧义，并记录 novelty table、machine-checkable gate matrix、冻结 benchmark 与 live evidence 的开放项，见 [audit report](task_reports/20261005_six_research_documents_quality_audit.md)。
- [partial] 2026-10-05 PIPE3 feature-aware two-stage composition qualification：将
  `contextual_trust_linear` 接入既有 canonical `preview→assignment→commit`，source/target
  selection 统一传入 `hash64-v1`、`matrix-features-v1`、64 维 bounded feature map；source/
  target sidecar、feature digest、policy factory/config/version 和 assignment chosen-key
  binding 均落盘；3 个 control 的 zero-call composition 通过，feature contract receipt 1/1，
  定向回归 110 项、0 API/0 GPU。它仍不是 chosen-candidate 独立 delivery/action/adoption/
  later outcome 或 scientific baseline，见 [qualification report](task_reports/20261005_pipe3_feature_composition_qualification.md)。
- [partial] 2026-10-05 delayed policy adapter qualification：复用真实
  `FeatureContextualTrustPolicy` 与 `DelayedCreditLedger`，新增 publish/update 分离的
  candidate adapter；公开 `RoleEvidenceOffer` 不改变策略 state，只有目标 selection 的
  selected-only recipient channel 才能延迟更新，并补上 assignment-level alternate-outcome
  拒绝、candidate/channel/namespace 绑定、容量与回滚；随后接入 canonical replay、
  `derive_later_credit_from_ledger` 与 history binding，v9 为 8/8 `QUALIFIED_OFFLINE`，
  26 项定向测试通过，0 API/0 GPU；这不是实时训练收益，也不冻结 baseline，见
  [adapter report](task_reports/20261005_delayed_policy_adapter_qualification.md)。
- [partial] 2026-10-05 C0 candidate parity hardening：独立复核后补上 arm namespace 唯一性、
  factory/config 绑定、1 MiB state cap、chosen-key/outcome/跨 arm feedback 错绑拒绝；v2
  schema mismatch 失败保留，v3 7/7 cases 通过，0 API/0 GPU，仍为 candidate-only，见
  [hardening report](task_reports/20261005_c0_candidate_parity_hardening.md)。
- [partial] 2026-10-05 C0 candidate parity preflight：在不改 active 七臂 manifest 的前提下，
  对 `contextual_trust_linear`/RARE 复用 PIPE3 fixture 做 candidate-only preflight；两臂
  public input digest 完全一致，独立 policy/outcome namespace 与 snapshot/restore 通过，
  1/1 case、0 API/0 GPU，`baseline_frozen=false`。结果不是 live parity 或质量 label，下一步
  必须让 chosen candidate 独立生成 delivery/action/adoption/later outcome，见 [C0 report](task_reports/20261005_c0_candidate_parity_preflight.md)。
- [partial] 2026-10-05 A0/B0 closest adapter 与第二 root go/no-go：严格 ArtifactRole closest published
  判为 `NO-GO`，Meta-Team L2 只保留为需预注册信息边界的候选 adapter；PIPE3 保留 primary
  development candidate，PIPE2 因 seed fixture validity/authority/语义未闭合暂不作
  confirmation root，MULTI3 不进入主矩阵。该决策整合已有零调用回执，0 API/0 GPU，Goal 不
  降级，下一步是 C0 canonical parity preflight，见 [go/no-go report](task_reports/20261005_a0_b0_go_no_go.md)。
- [partial] 2026-10-05 feature-aware contextual baseline qualification：修复 r5.66 暴露的
  strongest same-information 缺口，新增 `contextual_trust_linear` 普通 diagonal RLS
  comparator，并让 RARE 与其共享 64-d `hash64-v1` bounded feature、menu 和 base-score
  输入；6/6 zero-call cases、80 项相关回归通过，0 API/0 GPU，`baseline_frozen=false`。
  原 Beta `contextual_trust` 保留为 context-only diagnostic；canonical live parity、
  closest/second root、independent histories 和 scientific efficacy 仍开放，见
  [qualification report](task_reports/20261005_feature_contextual_baseline_qualification.md)。
- [blocked_by_evidence] 2026-10-05 same-information baseline gap audit：静态复核确认 `RarePolicy` 使用 64-d `captured_features` 而 `ContextualTrustPolicy`/`PooledControllerPolicy` 只使用 context/candidate Beta，且 RARE 丢弃 `base_scores`；这违反 active method 与 benchmark 要求的 same-`φ` strongest control。尚未修改 active method/arm 名单，也未启动 API/GPU；建议先确认并实现版本化 `contextual_trust_linear_v1` 零调用 comparator，再进入 bounded PIPE3 live parity，见 [gap audit](task_reports/20261005_same_information_baseline_gap_audit.md)。
- [partial] 2026-10-05 canonical runtime stream builder qualification：新增 `build_runtime_stream_values`，从实际 `MatrixOffer`/arrival schedule/registry 自动投影十项公开 stream，并在 runner preflight 前完成 digest binding；v8 receipt 17/17 通过，七臂 synthetic preflight 各选择2次、fixture updates=3，runtime mutation 与14个 manifest mutation 全部 fail-closed，32项定向回归通过，0 API/0 GPU。它仍只关闭 manifest-to-runtime 工程门，closest published、第二 root、independent live histories、same-information live parity 和 scientific readiness 仍开放，见 [builder report](task_reports/20261005_canonical_runtime_stream_builder_qualification.md)。
- [partial] 2026-10-04 canonical manifest runtime-digest binding qualification：`validate_runtime_binding` 与 `PolicyMatrixRunner` preflight 绑定 root/registry/schedule/RNG/stream digest；clean v6 receipt 17/17（含 runtime mutation）通过，46 项回归通过，0 API/0 GPU。当前 `stream_values` 仍由 synthetic caller 提供，尚未从真实 offers/三类 adapter 自动构造，科学 baseline 继续未冻结，见 [runtime binding report](task_reports/20261004_canonical_manifest_runtime_binding_qualification.md)。
- [partial] 2026-10-04 canonical manifest preflight qualification：将 nested validator 接入 `PolicyMatrixRunner` 首道 gate；clean commit 上16-case receipt（valid + synthetic runner +14 mutations）通过，42项回归通过，负向均 runner 未启动/零更新，0 API/0 GPU。它仍未完成 manifest-to-runtime stream binding，也未打开 scientific baseline，见 [preflight report](task_reports/20261004_canonical_manifest_preflight_qualification.md)。
- [partial] 2026-10-04 canonical nested manifest validator qualification：复用 `RootRunnerManifest` 实现 nested canonical envelope，强制检查 root/authority/material、七臂 factory/version/digest、三类 source channel、十项 public stream digest、成本/UNKNOWN/assignment、15 个 cell 和 blocked `closest_published`。v2 结构化 receipt 15/15 通过，12 项 focused、32 项 baseline/root/matrix regression 和27项 canonical adapter regression 通过，0 API/0 GPU；validator 尚未接入 live runner，科学 baseline 仍未冻结，见 [qualification report](task_reports/20261004_canonical_manifest_validator_qualification.md)。
- [partial] 2026-10-04 canonical seven-arm manifest execution card：字段审查确认继续复用 `RootRunnerManifest`/`LiveRuntimeBinding`，不另造 root 协议；冻结 nested envelope 的 root、arm、三类 source channel、public `φ`/菜单/read-cut/arrival/propensity、成本、assignment/UNKNOWN、cells 与 analysis-plan digest。七臂只作为工程 stream，`closest_published` 仍是 blocked required 第八臂，未激活 baseline、未调用 API/GPU，见 [execution card](task_reports/20261004_canonical_seven_arm_manifest_card.md)。
- [partial] 2026-10-04 canonical adapters after three-document audit：独立复核确认 PIPE3 public-input parity v21、raw-acceptance v4 与 terminal-only v5 只关闭了 source projection、fail-closed 和 replay 的工程子门；storyline/method/benchmark 三份 active 文档仍为 `NOT_READY`，G0/G1/G2 为 `PARTIAL`、G3–G5 为 `OPEN`。下一道唯一门是冻结同一 canonical 七臂 executable manifest，统一 judgment/raw/terminal projection、菜单、read-cut、arrival、成本、registry/history mutation、UNKNOWN 和 namespace；未通过前不启动正式 API/A800，不修改 Goal，见 [post-adapter audit](task_reports/20261004_three_doc_post_adapter_audit.md)。
- [partial] 2026-10-04 canonical PIPE3 public-input parity qualification：v18 初版因 terminal quality/status 进入 RARE φ 而 contextual trust 不消费，被降格为中间证据；v19 修正公共投影，v20 又升级 φ schema 版本并修正 late-cell 标识。v20 的 public trace/φ/schema/namespace 与 UNKNOWN、反馈 after frozen read-cut、offer digest mutation 四格通过，0 API/0 GPU。科学 same-information baseline、positive source adapters、registry/history adversarial 与 benchmark authority 仍开放，见 [task report](task_reports/20261004_canonical_pipe3_parity_qualification.md) 和 [experiment card](task_reports/20261004_canonical_pipe3_parity_card.md)。
- [partial] 2026-10-04 canonical PIPE3 parity independent review：独立 Codex 先后审查 v18→v20，确认 v20 只能作为 engineering public-input/schema parity，保留 terminal-field fairness bug、positive raw/terminal adapter 与 registry/history mutation 的开放边界，见 [review](task_reports/20261004_canonical_pipe3_parity_review.md)。
- [partial] 2026-10-04 canonical PIPE3 parity reproducibility replay：v21 以当前 runner SHA-256 `b094416c...` 重放并通过同一 public-input/schema、UNKNOWN、late-rejection、offer-digest mutation 与 namespace checks；13 项定向回归通过，0 API/0 GPU。它只固定当前源码对应的工程回执，不打开 scientific baseline parity 或 benchmark gate，见 [replay report](task_reports/20261004_canonical_pipe3_parity_replay_v21.md)。
- [partial] 2026-10-04 source-adapter and history-mutation replay：当前七-arm fixture matrix、typed raw-acceptance sidecar、registry/peer-history mutation controls 均以 `QUALIFIED_OFFLINE` 重放；raw/terminal positive update paths、wrong-decision/producer/duplicate rejection、history permutation/candidate/projection mutation rejection 通过，34 项定向回归、0 API/0 GPU。该回执仍不是 canonical scientific same-information parity；terminal-specific mapping、runner-level registry preflight、second root、live history 与 later-use 仍开放，见 [report](task_reports/20261004_source_adapter_mutation_replay.md)。
- [partial] 2026-10-04 canonical channel-adapter parity design：冻结下一道零调用卡，要求 raw acceptance 与独立 terminal outcome projection 接入 canonical PIPE3 的同一菜单/read-cut/arrival/φ 合同，并将 registry/history mutation 拦在 MatrixOffer 之前；terminal provenance 与 producer responsibility 明确分离，见 [experiment card](task_reports/20261004_canonical_channel_adapter_card.md)。
- [partial] 2026-10-04 canonical raw-acceptance adapter qualification：native `s0/d0/j0` 经 `DecisionSidecar → RawAcceptanceSidecar → project_raw_acceptance` 后才进入七-arm MatrixOffer；raw arm 一次 eligible/一次 update，其余六 arm ignore/0 update，七类错误在 runner 启动前以零选择/零更新拒绝，7 项 focused tests 通过，0 API/0 GPU。terminal-only 仍未接入，见 [report](task_reports/20261004_canonical_raw_adapter_qualification.md)。
- [partial] 2026-10-04 canonical terminal-only adapter qualification：新增独立 `TerminalOutcomeSidecar → project_terminal_outcome`，只由 native `TerminalOutcome.success` 产生 label，不读 producer attribution/scorer-private 字段；terminal arm 一次 eligible/一次 update，其余六 arm ignore/0 update，八类错误在 runner 启动前零选择/零更新拒绝，terminal focused 7 项与回归 45 项通过，0 API/0 GPU，见 [report](task_reports/20261004_canonical_terminal_adapter_qualification.md)。
- [partial] 2026-10-04 六大叙事范式与当前故事线审查：独立 Codex 选择“根因手术刀”为主、“新基准暴露失效”为重要辅助、“反直觉重构/理论照亮经验”为支撑；Introduction 已加入构造性最小反例并修正归因与 sealed-assignment 时序，复核 PASS，故事设计潜力 7.0/10、正式投稿就绪度仍 3.8/10；benchmark/结果门未改变，见 [task report](task_reports/20261004_six_paradigm_story_audit.md) 和 [review](task_reports/20261004_six_paradigm_reviewer_report.md)。
- [partial] 2026-10-04 六范式叙事第二轮复核：隔离目录构建 `narrative_20261004_isolated_v4` 为 7 页、0 overfull boxes、0 未定义引用；只验证排版/叙事版本，`scientific_claim_allowed=false`，不打开三份科学验收门。
- [partial] 2026-10-04 长任务阶段检查：对照三份唯一生效验收标准复核提交后的 history integration。正式 v2 回执绑定 `df8f3f8`，off/append 三 control 的 ledger/selection trace 相等，producer-owned 追加 1 条 PASS history，recipient-owned/mixed 保持 UNKNOWN，26 项 focused tests 通过；故事/方法仍未证明科学效果，benchmark/baseline 仍 `NOT_READY`。下一步先冻结并执行 history/no-history/shuffled/reset 四格零调用 matched replay，见 [checkpoint](task_reports/20261004_long_task_checkpoint.md)。
- [partial] 2026-10-03 PIPE3 canonical peer-history append integration：新增 `peer-history-canonical-adapter-v1`，将已提交 delayed credit 接到 `HistoryBindingReceiptV1` 与 `PeerHistoryV2` seal/append；`history_mode=off|append` matched zero-call qualification 对 producer-owned 追加 1 条 PASS history，recipient-owned/mixed 保持 UNKNOWN，ledger/selection trace 不变；seal 后 append 失败会恢复 history snapshot。26 项 focused tests 通过，0 API/0 GPU；selector consumption、四格反事实、真实 history/baseline parity 和 scientific efficacy 仍未完成，见 [task report](task_reports/20261003_peer_history_integration.md)。
- [partial] 2026-10-03 canonical source-to-target history binding：复用 native ledger、`RoleEvidenceOffer`、`LaterAssignment` 与 target outcome，新增独立 `HistoryBindingReceiptV1`，显式绑定 candidate version/registry/read-cut/source→target IDs、delayed-credit digest 和 native event order；对 read-cut、身份和 late-arrival mutation fail-closed。25 个 focused tests 通过，qualification v1/v2/v3 均 10/10（v3 绑定提交 1742404），0 API/0 GPU，尚未接 live runner 或 selector，见 [task report](task_reports/20261003_peer_history_binding.md)。
- [partial] 2026-10-03 PIPE2 gate reachability audit：初始八格零调用审计发现 canonical strict-defect 分支允许 recipient repair 伪装成 producer evidence；`two-stage-role-evidence-v2` 收紧为独立 FAIL/0 + direct accept/use + no changed paths，v3 重跑后 canonical 与 PIPE2 gate 均只有唯一正例、无分歧。15 项定向测试通过，0 API/0 GPU，未产生科学标签，见 [task report](task_reports/20261003_pipe2_gate_reachability_audit.md)。
- [partial] 2026-10-03 PeerHistoryV1 implementation audit：确认当前模块只是 append/projection seam，不能改变 producer 能力；source/target lineage、recipient judgment 必填和 selector consumption/四格反事实仍缺失。保留模块但阻止进入 scientific cell，0 API/0 GPU，见 [task report](task_reports/20261003_peer_history_implementation_audit.md)。
- [partial] 2026-10-03 PeerHistoryV2 hardening：将 determinate history entry 收紧为必须同时拥有 recipient judgment 与 later outcome label；定向 6 项和 qualification 5/5 通过，0 API/0 GPU。source/target lineage、真实 selector consumption 与四格 scientific comparison 仍未完成，见 [task report](task_reports/20261003_peer_history_implementation_audit.md)。
- [partial] 2026-10-03 PIPE2 派生候选根：CSV-writer overlay 在版本化 hash-only recipe 下修复 seeds 1/4/6/9 的 malformed CSV；全 10 seed 形状审计与同一 sandbox 的 producer×recipient/adoption qualification 通过（0 LLM/0 GPU），但仍不是 active benchmark，situated judgment、later assignment、独立 outcome 和 baseline parity 未开始，见 [task report](task_reports/20261003_pipe2_derived_candidate.md)。
- [partial] 2026-10-03 PIPE2 responsibility gate：方法审查补上 `producer_defect_registered`/独立 FAIL-0 条件；v1 旧 25-control receipt 保留，v2 在五个材料等价类的 30 个 authored controls 全部通过，direct-use 无 defect 返回 PENDING，recipient repair/mixed/UNKNOWN 不发 producer label，真实 judgment、later assignment、independent outcome 和 baseline parity 仍未接入，见 [task report](task_reports/20261003_pipe2_responsibility_gate.md)。
- [partial] 2026-10-03 PIPE2 typed responsibility chain：独立方法审查发现无 defect 的 `accept/use` 不能产生 producer evidence；当前组合收窄为 conservative typed-ledger plumbing，保留 v1/v3/v5 历史回执，v6 将 15/15 authored controls 记为 PENDING/UNKNOWN 并显式 `active_method_compatible=false`，0 API/0 GPU，见 [task report](task_reports/20261003_pipe2_chain_composition.md)。
- [partial] 2026-10-03 PIPE2 runtime receipt replay：只读重放已完成的真实 sandbox receipt，40 个 producer×recipient 组合全部保守为 `UNKNOWN`，0 label/0 policy update；确认旧 runtime scorer 缺 recipient judgment、consumer action/ownership 和独立 terminal outcome，见 [task report](task_reports/20261003_pipe2_runtime_replay.md)。
- [partial] 2026-10-03 N02 v3 strict replay：重放两条真实 API ledger；真实 judgment/action/terminal 存在，但 producer score/defect registration 缺失，当前 gate 将两条历史 role-evidence 都判为 `PENDING_ATTRIBUTION`，0 label/0 update，见 [task report](task_reports/20261003_n02_strict_replay.md)。
- [partial] 2026-10-03 N03 real small-chain card：根据 N02 严格回放与 PIPE3 现有 seam，冻结一个单 seed、最多两 episode、每 episode 三次 API 请求的 design-only card；要求 Qp、judgment、ownership diff、独立 outcome 与 preview→assignment→commit 全部可审计，尚未运行 API/GPU，见 [task report](task_reports/20261003_n03_live_small_chain_card.md)。

- [partial] 2026-10-01 baseline manifest runner integration：离线 matrix runner 现在消费每个 case 的 root manifest，绑定 schedule/registry digest 并把 manifest digest 写入回执；v13 为 `QUALIFIED_OFFLINE`，PeerRoleBench 360 项通过，仍未接入 canonical-ledger live runner，见 [task report](task_reports/20261001_baseline_manifest_runner_integration.md)。
- [partial] 2026-10-01 baseline manifest scope audit：独立审查收紧 v13 的证据边界：历史 receipt 保留但不能宣称完整 root manifest enforcement；修复了身份/组件 hash、arrival order、denominator 绑定、root seed、预算与执行前封存，并要求提交后重跑 v14。无 API/A800，无 Goal 降级，见 [task report](task_reports/20261001_baseline_manifest_scope_audit.md)。
- [partial] 2026-10-01 baseline manifest hardening v2：v16 在新 commit 上重跑七个 hand-authored case，封存逐 offer RNG schedule、反馈行内容不可变性、正常 prefix re-visible 与 selected×classification 分母；只证明 offline implementation parity，见 [task report](task_reports/20261001_baseline_manifest_hardening_v2.md)。
- [partial] 2026-10-01 PIPE3 two-stage composition：18 次实际 pinned CPU sandbox scorer 调用，v2 通过 producer-owned 两阶段 contract/replay/delayed-credit 与 recipient/mixed UNKNOWN 保护控制；没有 LLM/API/GPU 或科学效果，见 [task report](task_reports/20261001_pipe3_two_stage_composition.md)。

- [partial] 2026-10-01 root manifest qualification：封存 root/source/generator/scorer、seed split、schedule/registry digest、arm 顺序、visibility rule 与预算；定向 14 项及 PeerRoleBench 359 项通过，仍未接入 live runner，见 [task report](task_reports/20261001_root_manifest_qualification.md)。

- [partial] 2026-10-01 baseline root-runner contract：将七个 ArtifactRole baseline 的信息通道、UNKNOWN 规则、16 项成本字段、完整 schedule prefix、denominator 与 assignment-before-task-start 写成版本化零调用契约；定向 16 项与 PeerRoleBench 358 项通过，仍未接入正式 root runner、独立 live histories 或科学比较，见 [task report](task_reports/20261001_baseline_root_runner_contract.md)。

- [partial] 2026-10-01 PIPE2 material/ownership qualification：3 个 seed 的 ETL ownership、去 oracle、hidden output 隔离与 typed delivery 通过；v2 将 operator correctness 字段移出 public artifact，定向 3 项、完整 337 项通过，0 API/0 GPU，见 [task report](task_reports/20261001_pipe2_material_qualification.md)。
- [partial] 2026-10-01 second structural root screen：筛选 `PIPE2_data_pipeline` 作为比 MULTI3 更合适的第二 root 候选，明确其三段 ETL 资产与 native scorer 缺陷；尚未冻结或启动 API/GPU，见 [task report](task_reports/20261001_second_root_screen.md)。
- [partial] 2026-10-01 benchmark authority re-audit：以官方论文/仓库复核 TeamBench、CooperBench、MARBLE、Collab-Overcooked、AgentCollabBench 与 graph-ipd，确立 TeamBench 权威底座 + PeerRoleBench-TB 因果扩展的边界，active benchmark 仍未冻结，见 [task report](task_reports/20261001_benchmark_authority_reaudit.md)。
- [partial] 2026-10-01 role-evidence selection plan：公开证据只形成 overlay 输入，preview 固化 choice/propensity，commit 先写 `LaterAssignment` 再 exact replay selection，失败可回滚；定向 16 项与完整 334 项通过，未调用 API/GPU，见 [task report](task_reports/20261001_role_evidence_selection_plan.md)。
- [partial] 2026-10-01 delayed credit 原子性：updater 失败时 snapshot/restore 回滚、credit key 仅成功后登记，定向 15 项与完整 332 项通过，未调用 API/GPU，见 [task report](task_reports/20261001_delayed_credit_atomicity.md)。
- [partial] 2026-10-01 RoleEvidenceOffer 与 selection preview 接缝：分离 native evidence id/source event id，从 canonical ledger 绑定 subject/lineage，资格化 preview→assignment→exact propensity commit；修正旧 B-evidence→C-assignment 歧义，未启动 API/GPU，见 [task report](task_reports/20261001_role_evidence_offer_and_preview.md)。

- [partial] 2026-09-30 两阶段 evidence 发布与 delayed update 资格：用户确认方案 A；active method/evaluation 升级为 v1.1/v1.2，producer-owned/recipient-owned CPU controls 通过发布、assignment、later credit、replay 和幂等检查，仍无 benchmark/baseline/效能证据，见 [task report](task_reports/20260930_two_stage_evidence_update_qualification.md)。

- [done] 2026-09-29 Benchmark、baseline 与实验结果验收审计：新增 active 评价标准 v1.2，补齐 benchmark 选型评分卡、primary/secondary track、baseline parity、完整 cell manifest、数值精度门和结果 truth table；当前科学 benchmark/baseline 仍未通过，未启动新 API/GPU，见 [task report](task_reports/20260929_benchmark_baseline_acceptance_audit.md)。
- [partial] 2026-09-29 Benchmark 轨道选择审计：从 Goal 的因果链区分 PeerSelect/IPD 机制轨道与 ArtifactRole/PeerRoleBench-TB 核心任务轨道，形成未激活候选方案；等待 primary/secondary 确认，未启动新 API/GPU，见 [task report](task_reports/20260929_benchmark_track_decision_audit.md)。
- [partial] 2026-09-29 论文标题候选：围绕动态、自进化、situated judgment 和跨领域适用性形成三档标题候选；未覆盖正式论文源文件，等待作者选择，见 [task report](task_reports/20260929_title_candidates.md)。
- [done] 2026-09-29 标题确认与 LaTeX 同步：用户确认 `Earning Roles: Self-Evolving Responsibility from Situated Peer Judgments`；已同步 proposal/pre-results 源码，保留历史稿并完成 PDF 构建验证，见 [task report](task_reports/20260929_title_confirmation.md)。

- [done] 2026-09-28 故事线与论文写作评价标准 v1.2：基于四篇 AAMAS 正文补充全文主链、章节顺序、段落职责、结果解释和本项目段落映射；未改变 Goal，见 [task report](task_reports/20260928_storyline_writing_logic_v12.md)。

- [done] 2026-09-28 PIPE3 full responsibility-chain qualification：17 个事件的两 episode 零调用链、v3 lineage sidecar、native/auxiliary manifest、arrival schedule 和 UNKNOWN/fault rejection 通过；真实 runner、benchmark 与科学效果仍开放，见 [task report](task_reports/20260928_pipe3_full_chain_qualification.md)。

- [done] 2026-09-28 PIPE3 actor/scorer dispatch boundary qualification：真实 sandbox RPC 下 producer/recipient payload、selected delivery、operator denial、Qp/Qr/adoption view 和写权限 mutation 通过；真实 LLM runner 与科学效果仍开放，见 [task report](task_reports/20260928_pipe3_dispatch_boundary_qualification.md)。

- [unknown] 2026-09-28 PIPE3 real smoke v1：1 次真实 `内部/qwen3.8-max` 请求成功并保存 raw SSE，但 Qp v1 用非法 `action=probe` 造成 coverage UNKNOWN；按卡片停止，无 judgment/action/update，见 [task report](task_reports/20260928_pipe3_real_smoke_v1.md)。

- [done] 2026-09-28 PIPE3 producer scorer v2 qualification：修复 v1 测试事件使用非法 `probe` action 的契约缺陷；seed 0/1 的 authored-correct、original-delivery、syntax-failure 与四类 UNKNOWN mutation 零调用矩阵通过。`scorer_is_qualified=false`，recipient/adoption/runner、独立 root 与 benchmark 仍开放，见 [task report](task_reports/20260928_pipe3_producer_scorer_v2_qualification.md)。

- [done] 2026-09-28 PIPE3 recipient/adoption scorer v2 qualification：修复 adoption fixture 使用非法 `probe` action 的契约缺陷；首次 qualification 的输出目录错误保留，后续 seed 0/1 v2 recipient/adoption 确定性 coverage/decision 矩阵通过。`scorer_is_qualified=false`，责任归因与科学 gate 仍开放，见 [task report](task_reports/20260928_pipe3_recipient_scorer_v2_qualification.md)。

- [done] 2026-09-28 PIPE3 real smoke v3：三个版本化 scorer 均完成 qualification 后，真实 `内部/qwen3.8-max` 完成一个八事件 episode，Qp/Qr/adoption 均 PASS、ledger replay PASS；3 次 API、0 GPU、0 policy update。producer 已通过而 judgment/consumer 修改 recipient-owned processor，责任归因风险仍在，见 [task report](task_reports/20260928_pipe3_real_smoke_v3.md)。

- [done] 2026-09-28 PIPE3 responsibility audit：对冻结 v3 episode 运行 operator-side 归因审计；producer-owned path 未变更而 recipient-owned `processor.py` 被修复，输出 `PENDING_ATTRIBUTION`，阻止 producer policy update，见 [task report](task_reports/20260928_pipe3_responsibility_audit.md)。

- [done] 2026-09-28 PIPE3 responsibility-aware label qualification：同一真实 material root 上的五类 ownership sidecar gate 通过；只有 producer defect eligible，mixed edit 为 UNKNOWN，其余不更新 producer，见 [task report](task_reports/20260928_pipe3_responsibility_label_qualification.md)。

- [done] 2026-09-29 PIPE3 consumer response contract qualification：五格严格 envelope parser 通过；bare dict、extra metadata、missing path、non-text source 均 UNKNOWN，见 [task report](task_reports/20260929_pipe3_consumer_response_qualification.md)。

- [unknown] 2026-09-28 PIPE3 real smoke v4：structured responsibility judgment 成功且明确归因为 recipient-owned `processor.py`，但 consumer response 没有 `source_files` envelope，runner 严格 UNKNOWN 停止；3 次真实 API、无 action/outcome/update，见 [task report](task_reports/20260928_pipe3_real_smoke_v4.md)。

- [unknown] 2026-09-29 PIPE3 real smoke v5：模型已返回严格 `source_files` envelope，但 runner 使用 recipient 初始路径集合而非 selected delivery contract，合法四文件快照被拒；3 次真实 API、无 update，见 [task report](task_reports/20260929_pipe3_real_smoke_v5.md)。

- [done] 2026-09-29 PIPE3 real smoke v6：delivery-aware envelope 通过后，真实 chain 完成 Qp/Qr/adoption PASS 与 terminal outcome；structured judgment 判定 recipient-owned `processor.py`，责任 gate 输出 `COMPLETE_PENDING_ATTRIBUTION`，不写 producer evidence/update，见 [task report](task_reports/20260929_pipe3_real_smoke_v6.md)。

- [done] 2026-09-29 PIPE3 pending-attribution replay audit：v6 七事件 ledger 的唯一缺失是有意等待的 role evidence，无 hash/顺序/协议错误；确认需要拆分 attribution review 与 eligible evidence，见 [task report](task_reports/20260929_pipe3_pending_replay_audit.md)。

- [done] 2026-09-28 验收标准 v1.1 升级：将官方要求、项目化识别门和高质量论文目标分层，补充 estimand、统计、closest baseline、污染审计、clean replay 与 Proceedings/Findings 双档；未改变 Goal，见 [task report](task_reports/20260928_evaluation_standard_v11.md)。

- [done] 2026-09-28 三份验收文档来源审计：核对 AAMAS 官方要求和定向获奖论文样本，明确官方底线、项目操作化与未完成系统综述的边界，见 [task report](task_reports/20260928_acceptance_criteria_provenance.md)。

- [done] 2026-09-28 研究文档重组与唯一 active 版本登记：建立六类唯一生效文档、版本登记、历史归档和职责边界；未改变 Goal、benchmark freeze 或科学结论，见 [task report](task_reports/20260928_research_document_reorganization.md)。

- [2026-09-28 决议文件治理与研究标准归档](task_reports/20260928_decision_0038_governance.md)：记录双重确认及研究质量硬标准，0038 替代重叠的 0037；未改变 Goal，未新增科学效果证据。
- [2026-09-28 second-root re-audit](task_reports/20260928_second_root_reaudit.md)：零 API 直接组合复核保留 PIPE3 为条件性主候选，拒绝把 MULTI3 原生 canonical-input 测试当作 adoption 证据，并新增完整 responsibility-lineage runner gate；未冻结 benchmark 或启动 API/A800。
- [2026-09-28 responsibility lineage qualification](task_reports/20260928_responsibility_lineage_qualification.md)：v3 sidecar 逐跳绑定 delivery/artifact/action 与 canonical ledger；首轮失败暴露 fixture action 不一致，修正后五格零 API 矩阵通过，live runner 和 benchmark 仍开放。
- [2026-09-27 Goal reconciliation](task_reports/20260927_goal_reconciliation.md)：
  当前故事、方法、benchmark、实验和论文状态的第一份逐项对照；未请求 Goal 降级。
- [2026-09-27 recipient runtime probe](task_reports/20260927_recipient_runtime_probe.md)：
  recipient payload、selected delivery 和有限 lineage hash-chain 的运行时边界检查；未请求 Goal 降级。
- [2026-09-27 ledger replay gate](task_reports/20260927_ledger_replay_gate.md)：
  parent-side ledger 的 hash/因果回放和变异矩阵通过；仍是协议资格，不是 benchmark 或在线学习结果。
- [2026-09-27 runner replay integration](task_reports/20260927_runner_replay_integration.md)：
  将 replay gate 接到真实 runner 的恢复、role update 和 episode summary 边界；未重跑历史实验。
- [2026-09-27 runner boundary qualification](task_reports/20260927_runner_boundary_qualification.md)：
  用保存的真实 ledger 验证中断、retry 和 scorer 异常的 UNKNOWN/拒绝语义；hidden scorer IPC 仍开放。
- [2026-09-27 scorer IPC preflight](task_reports/20260927_scorer_ipc_preflight.md)：
  记录 digest 混淆失败并修正；独立 private scorer 与 candidate read denial 通过，真实 runner 接入仍开放。
- [2026-09-27 producer scorer contract qualification](task_reports/20260927_producer_scorer_contract_qualification.md)：
  producer-only 五格零 LLM 矩阵区分 buggy/correct/near-miss；首次 independent consumer scorer 差异由 tuple/list 实现错误造成并已更正，producer event、live runner 和 benchmark 资格仍开放。
- [2026-09-27 producer-score event replay](task_reports/20260927_producer_score_event_replay.md)：
  新增独立 producer-score protocol event、状态/digest 约束和 replay causal order；旧 N02 ledger 回归通过，真实 runner/controller 接入仍开放。
- [2026-09-27 runner producer-score boundary](task_reports/20260927_runner_producer_score_boundary.md)：
  可选 scorer 已接到 delivery→judgment 边界并写入独立 ProducerScore；旧 N02 不重跑，controller/A800 仍未启动。
- [2026-09-27 producer scorer mutation matrix](task_reports/20260927_producer_scorer_mutation_matrix.md)：
  P5/P6/P7 扩展到 dict/list、tie-break、10k/20+20 并发和 response mutation；资源失败保留 UNKNOWN，benchmark/scorer qualification 仍未锁定。
- [2026-09-27 producer scorer seed regression](task_reports/20260927_producer_scorer_seed_regression.md)：
  seed 1/2 类名与 transport/malformed mutation 回归通过；seed 2 压力 worker-exit 保留 UNKNOWN，第二 root/baseline/真实 API 链仍开放。
- [2026-09-27 scorer discrepancy correction](task_reports/20260927_scorer_discrepancy_correction.md)：
  定位并修正 private consumer scorer 的 tuple/list 实现错误；旧错误日志保留，修正回放 PASS 1.0，撤回评分盲点结论。
- [2026-09-27 second-root audit](task_reports/20260927_second_root_audit.md)：
  PIPE3 保留为条件性主候选，MULTI3 为低优先级备选；两者都未冻结，强基线和真实 API 链不启动。
- [2026-09-27 benchmark / baseline freeze gate](task_reports/20260927_benchmark_baseline_gate.md)：
  固定两个 root、同信息 baseline、manifest、主指标和停止规则；当前不冻结 benchmark、不启动新 API/A800。
- [2026-09-27 candidate manifest validation](task_reports/20260927_manifest_validation.md)：
  用机器校验候选 root/split/baseline/信息契约，保持 API/GPU gate 关闭；真实 root 资格仍开放。
- [2026-09-27 material payload runtime preflight](task_reports/20260927_material_payload_runtime_preflight.md)：
  DIST1/PIPE3 双 root payload、delivery digest、operator deny 和 lineage 通过 pinned sandbox；live runner/scorer 仍开放。
- [2026-09-27 neutral producer scorer preflight](task_reports/20260927_neutral_producer_scorer_preflight.md)：
  中性 DIST1 producer payload 的独立 P1–P7 检查完整返回 FAIL；仅作 scorer/适配器诊断，controller update 关闭。
- [2026-09-27 controller update gate](task_reports/20260927_controller_update_gate.md)：
  新 diagnostic card 可显式禁止 legacy controller mutation，历史 card 行为保持兼容。
- [2026-09-27 neutral live episode](task_reports/20260927_neutral_live_episode.md)：
  三次真实 API 请求完成，但任务公开接口与 hidden scorer 不一致，producer/consumer scorer 均 UNKNOWN；不产生学习证据。
- [2026-09-27 DIST1 neutral-v2 contract qualification](task_reports/20260927_dist1_v2_contract_qualification.md)：
  修复并版本化公开队列接口，完成 adapter/provenance/runtime/scorer 的零调用检查；旧 v1 UNKNOWN 保留，v2 仍未冻结 benchmark 或产生科学结果。
- [2026-09-27 neutral DIST1 v2 live episode](task_reports/20260927_neutral_v2_live_episode.md)：
  三次真实 API 请求完整返回；producer priority 生成触发 dataclass 导入错误，scorer coverage 不完整，按规则不产生 label/evidence/update，集成路线关闭。
- [2026-09-27 producer failure label semantics](task_reports/20260927_producer_failure_label_semantics.md)：
  独立审查定义 candidate-origin import failure、scorer/infrastructure UNKNOWN 与 `decision_complete`/`coverage_complete` 分离；历史日志不回写。
- [2026-09-27 manifest v2 validator fix](task_reports/20260927_manifest_v2_validator_fix.md)：
  validator 接受候选 v1/v2 版本并拒绝未知版本；v2 机器校验回归通过，benchmark 仍未冻结。
- [2026-09-27 producer scorer v2 failure matrix](task_reports/20260927_producer_scorer_v2_failure_matrix.md)：
  以新 schema 区分可归因的候选导入/交付 `FAIL/0` 与 scorer/环境 `UNKNOWN`；离线控制矩阵通过，scorer 与 benchmark 资格仍开放。
- [2026-09-27 PIPE3 producer scorer qualification](task_reports/20260927_pipe3_producer_scorer_qualification.md)：
  PIPE3 root-specific producer scorer 首轮暴露 raw-Unicode 责任边界错误，修正为 JSON 语义保真后 seed 0/1 矩阵通过；recipient/adoption/runner 仍未资格化。
- [2026-09-27 PIPE3 lineage preflight](task_reports/20260927_pipe3_lineage_preflight.md)：
  Qp/Qr/adoption 四格控制和 UNKNOWN no-update replay 在 seed 0/1 通过；正式 runner、过程隔离、第二 root 与 baseline 仍开放。
- [2026-09-27 PIPE3 runner adapter boundary](task_reports/20260927_pipe3_runner_adapter_boundary.md)：
  新增不执行候选代码的 root-specific material/action/scorer-view seam，14 项 PIPE3 单测通过；真实 runner 和 API 仍未启动。
- [2026-09-27 decision 0037 mainline invariants](task_reports/20260927_decision_0037_mainline_invariants.md)：
  固化故事线、benchmark/baseline 证据要求与创新点不可静默降级规则；本任务不改变 Goal 标准。
- [2026-09-27 baseline implementation audit](task_reports/20260927_baseline_implementation_audit.md)：
  审计 manifest 中每个 baseline 的真实代码、信息边界和可复现实验入口；确认只有 RLS 与部分 synthetic controls 有实现，多个强 baseline/RARE 仍是 OPEN，未冻结 benchmark 或启动 API/A800。
- [2026-09-28 baseline policy contract](task_reports/20260928_baseline_policy_contract.md)：
  四个实现条件接入统一 selected-only policy 合约，完成版本/频道/UNKNOWN/快照回归；仍是零 API 离线资格，真实 runner、RARE/RLS 和 baseline freeze 继续开放。
- [2026-09-28 baseline bridge audit](task_reports/20260928_baseline_bridge_audit.md)：
  对冻结 N02 ledger 做无默认值映射审计；15 条事件缺候选版本/上下文/模型 schema、反馈延迟/provenance 和 label mapping，返回 NOT_MAPPABLE，policy update 保持关闭。
- [2026-09-28 public policy sidecar schema](task_reports/20260928_policy_sidecar_schema.md)：
  增加版本化 Decision/Feedback sidecar 与 ledger record-hash 绑定；离线资格通过，eligible/UNKNOWN 反馈边界明确，尚未接 PIPE3 runner。
- [2026-09-28 canonical policy sidecar stream replay](task_reports/20260928_policy_sidecar_stream_replay.md)：
  在完整 strict ledger 之后验证 sidecar 一对一覆盖、固定反馈顺序、UNKNOWN no-update 与 selected producer/version lineage；5 格零 API qualification 通过，真实 runner 仍开放。
- [2026-09-28 sidecar manifest attestation](task_reports/20260928_policy_sidecar_stream_replay.md)：
  以独立 append-only manifest 保存 sidecar digest，避免把未知字段塞入原生 protocol event；canonical replay qualification 记录 manifest root，真实 episode sealing 仍开放。
- [2026-09-28 PIPE3 policy-sidecar integration contract](task_reports/20260928_pipe3_policy_sidecar_integration_contract.md)：
  将 sidecar/manifest/replay 闸门映射到未来 root-specific runner 的 selection、delivery、judgment、terminal 与 snapshot seam；无 API/GPU，真实 runner 仍开放。
- [2026-09-28 PIPE3 policy-sidecar integration fixture](task_reports/20260928_pipe3_policy_sidecar_fixture.md)：
  用 pinned seed-0 material adapter 走通 source ownership→artifact→strict ledger→sidecar/manifest replay；只证明接口连通，scorer/LLM/benchmark 仍开放。
- [2026-09-28 J/A/U/F factorial mapping qualification](task_reports/20260928_factorial_mapping_qualification.md)：
  两个完整 PIPE3 episode 的零调用 hash-chain replay 通过；账本能表达四因素，但当前 policy sidecar 只支持不含 A/F 的四个 cell，producer attribution 与 future-assignment consumption 仍需接入。
- [2026-09-28 factorial 设计审计与口径修正](task_reports/20260928_factorial_design_correction.md)：
  独立复审发现“账本记录”不能代替“policy 使用并影响下一次 decision”；将 J/A/U/F 改为正交 projection/state-transition 因素，修正为 0/16 scientific cells ready，并保留旧日志。
- [2026-09-28 候选在线更新方法：有界窗口与稳定锚点](task_reports/20260928_method_candidate_bounded_anchor.md)：
  为 active method 的实时更新合同补充 typed event、O(d) 增量、窗口内 correction、稳定锚点和容量上界；仍是 candidate，未通过不变量、closest baseline 或真实流验证。
- [2026-09-28 故事线评价标准 v1.3 对齐](task_reports/20260928_storyline_eval_v13_alignment.md)：
  修复 active storyline v1.1 与评价对象仍指向 v1.0 的治理错位；v1.3 评价当前主线，v1.2 保留为历史版本，未放宽 Goal。
- [2026-09-28 故事线与方法论严格复评](task_reports/20260928_story_method_acceptance_reaudit.md)：
  将合同覆盖度与科学证据准备度分开评分；故事线和 active method 均仍未过硬门，候选 updater 只完成零调用不变量，未改变 Goal 或停止条件。
- [2026-09-28 typed policy projection seam](task_reports/20260928_policy_projection_seam.md)：
  将 operator/scorer 私有归因信息与 policy 最小反馈对象分离；经复审补齐 UNKNOWN/label/跨事件/selected-only 闸门，最终源码上的 18 格零调用 mutation qualification v6 通过，保留 v1--v5 失败日志；未产生 scorer、runner 或科学效果证据。
- [2026-09-28 pre-decision evidence offer and consumption attestation](task_reports/20260928_assignment_evidence_attestation.md)：
  用不含 chosen agent/propensity 的 pre-decision offer 替代 LaterAssignment 作为 F 输入；双 watermark、公开字段约束、F0/F1 toy sensitivity 和 12 格零调用资格 v5 通过，F scientific cell 仍为 0。
- [done] 2026-09-28 event-time interleaving qualification (task_reports/20260928_event_time_interleaving.md)：
  固定候选菜单、seed、证据和 decision cut，验证早到 feedback 只影响后续 decision、晚到 feedback 不回写已执行 decision；以同一 policy 的 F0/F1、未选 candidate mutation 防护和前置哈希篡改测试收紧证据链；用独立 auxiliary manifest hash-chain 封存 offer/consumption，v5 的 12 格零调用时序资格通过，v1--v4 历史日志保留。仍无 PIPE3 真实 runner、LLM/GPU 或 scientific cell，toy orchestrator 也不能证明隔离进程内的 policy-read trace。
- [done] 2026-09-28 PIPE3 candidate registry boundary (task_reports/20260928_candidate_registry_boundary.md)：
  新增不可变 `candidate_id@candidate_version` registry、源/model config digest、canonical registry digest 及 native ID 到 sidecar `CandidateRef` 的严格映射；13 项定向测试通过。它是身份工程子门，不是能力或 scientific cell 证据；完整 registry card、global arrival schedule、PIPE3 真实 runner 和双 manifest replay 仍开放。
- [done] 2026-09-28 PIPE3 global event-time schedule boundary (task_reports/20260928_event_time_schedule_boundary.md)：
  新增 versioned 全局 `arrival_index` schedule validator，拒绝重复时间、重复 protocol identity、缺失反馈和未知事件类型；candidate registry、schedule、manifest、event-time 定向集合共 16 项通过。它只关闭确定性时间轴工程子门，尚未接入真实 policy loop 或 scientific cell。
- [done] 2026-09-28 PIPE3 real runner contract (task_reports/20260928_pipe3_runner_contract.md)：
  固化真实 runner 的 pre-call freeze、native/auxiliary 双链、responsibility v3 时机、global arrival 顺序、UNKNOWN no-update 和双回放准入规则；没有调用 API/GPU，也没有冻结最终 updater。下一步实现 versioned runner boundary。
- [done] 2026-09-28 PIPE3 selection runner boundary (task_reports/20260928_pipe3_runner_boundary.md)：
 新增 versioned selection boundary，真实绑定 native selection record hash、candidate registry、consumption attestation 和 native/auxiliary 双 manifest；19 项定向测试和提交后 v4 structured qualification 通过。仍缺 actor/scorer/action/outcome、完整 fault-injection、responsibility v3 feedback 和真实 API。
- [done] 2026-09-30 benchmark 轨道确认与 active 计划升级 (task_reports/20260930_benchmark_track_confirmation.md)：
  用户确认 ArtifactRole 为论文主轨、PeerSelect 为机制副轨；新增 ADR 0042，active benchmark 计划升级为 v1.1，两个轨道不合并评分，正式 API/A800 仍受资格门约束。
- [done] 2026-09-30 RARE selection adapter qualification (task_reports/20260930_rare_policy_adapter.md)：
  候选 RARE 接入统一 selected-only policy 与 PIPE3 selection seam，补齐固定特征、encoder、UNKNOWN、correction lineage 和 event-time sidecar；v6 零调用资格与 79 项定向测试通过。只关闭接口工程子门，方法、benchmark 和科学效果仍未冻结。
- [done] 2026-09-30 baseline parity audit (task_reports/20260930_baseline_parity_audit.md)：
  七个 arm 可构造但尚未形成公平 benchmark；统一 root runner、全局 event-time、UNKNOWN 分母、完整成本、later assignment 和 closest published adapter 仍开放，RARE/contextual 不能暂称同信息强基线。
- [done] 2026-09-30 policy matrix runner qualification (task_reports/20260930_policy_matrix_runner.md)：
  七个 arm 在同一离线 runner 的七个 hand-authored feedback case 上通过菜单/seed/registry/protocol lineage/event-time/observe-before-choose/selected-only/UNKNOWN/raw acceptance/snapshot 及语义 contract；v1--v8 失败/修复保留，v9 仅为 parity 子门，不是 benchmark、方法效果或科学结果。
- [done] 2026-09-30 closest published adapter audit (task_reports/20260930_closest_adapter_audit.md)：
  严格 ArtifactRole causal unit 没有可直接复现的 published drop-in；Meta-Team L2-style profile 是唯一进入候选的语义近邻，但只能独立重实现并拆为 original-info/public/ablation，当前 `NOT_IMPLEMENTED / QUALIFICATION_REQUIRED`。DecisionBench 只作 selector/delegation control，CooperBench 只作 collaboration substrate，graph-ipd 只作机制副轨；baseline 仍未冻结。
- [done] 2026-09-30 Meta-Team-L2-public profile boundary qualification (task_reports/20260930_metateam_public_profile_qualification.md)：
  以一手 L2 profile 字段建立零调用 schema/builder/replay contract，验证 selected-only、public eligible、watermark/later assignment、correction/digest、hidden-info 拒绝、typed-sidecar source-input digest 和 source replay；最终 qualification 11 格、定向 12 项、完整 PeerRoleBench 277 项通过。它不是 Meta-Team 效果或已实现 baseline，真实 profile generator、PIPE3 runner、成本和独立 history 仍开放。
- [done] 2026-09-30 Meta-Team-L2-public × PIPE3 source replay qualification (task_reports/20260930_metateam_pipe3_replay_qualification.md)：
  使用真实 PIPE3 seed-0 material、ledger record hash、typed sidecar 和 recipient judgment projection 完成 profile/source digest replay；wrong candidate 与 public payload mutation 拒绝，v1 event-type 失败保留。仍是零调用工程子门，fixture profile 不是摘要模型或科学 baseline，assignment offer/next-episode runner、成本和独立 history 仍开放。
- [done] 2026-09-30 Meta-Team profile assignment offer/consumption qualification (task_reports/20260930_metateam_assignment_offer_qualification.md)：
  profile-specific offer/attestation 绑定候选菜单、watermark、later decision、profile IDs 和 policy input digest；13 格语义检查、定向 14 项、完整 PeerRoleBench 279 项通过。仍不是隔离 policy-read trace、真实 selector/next episode 或 profile effect，runner、成本和独立 history 仍开放。
- [done] 2026-09-30 Meta-Team profile offer → next selection binding (task_reports/20260930_metateam_assignment_runner_binding.md)：
  将 offer/attestation 绑定到后续 selection 的 decision index、candidate menu 和 read-cut；v11 menu fixture mismatch 失败保留，v12 14 格 qualification、定向 15 项、完整 PeerRoleBench 280 项通过。仍不是隔离 policy-read trace、真实 selector/next episode 或 profile effect，runner、成本和独立 history 仍开放。
- [done] 2026-09-30 PIPE3 assignment runner boundary qualification (task_reports/20260930_pipe3_assignment_runner_boundary_qualification.md)：
  将 profile offer/consumption attestation 接入 selection→task-start 状态机，记录四阶段 JSONL trace；缺失 attestation、消费前 selection、错误 menu、重复消费、过早 watermark 和 post-offer profile mutation 均被拒绝。最终 v3 zero-call qualification 通过，定向 1 项、全量 PeerRoleBench 281 项通过；输入仍是 hand-authored offline fixture，`isolated_policy_trace=false`，不能替代真实 PIPE3 episode、profile generator、隔离读取、完整成本或科学结果。
- [done] 2026-09-30 PIPE3 assignment → native task-start ledger qualification (task_reports/20260930_pipe3_assignment_task_start_ledger_qualification.md)：
  在同一边界中把已绑定的 assignment 接到原生 `PeerRoleLedger`，验证 native selection 后追加相同 decision index 的 `task_start` 并记录其 hash；最终 v4 `ledger_task_start` 通过，0 API/0 GPU。仍是 offline fixture，未执行真实 source/scorer/action/outcome/profile generator，`isolated_policy_trace=false`，不能解冻 benchmark/baseline。
- [done] 2026-09-30 versioned/native selection view adapter qualification (task_reports/20260930_selection_view_adapter_qualification.md)：
  严格 registry adapter 显式映射 `candidate_id@version` 与 native selection，保留菜单顺序、chosen index、task index、selected-at 和 selector，并覆盖未知版本、错误选择、负时间、native menu mismatch 与 assignment menu reordering；8 格离线资格、4 项定向测试、完整 PeerRoleBench 285 项通过，0 API/0 GPU。仍不是真实 feedback row、live runner、profile generator、隔离 policy-read 或 benchmark/scientific evidence。
- [done] 2026-09-30 typed public feedback-row adapter qualification (task_reports/20260930_public_feedback_row_adapter_qualification.md)：
  将 `PolicyFeedbackProjection` 严格序列化为 `AssignmentEvidenceOffer` 的 public rows，要求 event-time、candidate version、UNKNOWN reason 和 correction lineage；7 格离线资格、24 项定向测试、完整 PeerRoleBench 290 项通过，0 API/0 GPU。同步修复 UNKNOWN projection 丢失 `arrival_index`/`supersedes`；canonical ledger/schedule binding、真实 runner、profile generator 和科学证据仍开放。
- [done] 2026-09-30 source-bound PIPE3 feedback adapter qualification (task_reports/20260930_source_bound_feedback_adapter_qualification.md)：
  将 canonical ledger binding、v4 responsibility lineage、frozen arrival schedule、typed projection 与 public offer sealing 接成强制顺序；5 格离线资格、5 项定向测试、完整 PeerRoleBench 295 项通过，0 API/0 GPU。仍未执行真实 source/scorer/action/outcome/profile generator 或 isolated policy-read，不能解冻 benchmark/baseline。
- [done] 2026-09-30 frozen real v6 source-bound replay (task_reports/20260930_v6_source_bound_replay_qualification.md)：
  对历史真实 PIPE3 v6 ledger/artifact lineage 做零调用 canonical replay，recipient-owned repair 保持 `UNKNOWN` 和公开原因，未生成 producer label；1 项定向测试、完整 PeerRoleBench 296 项通过，0 API/0 GPU。仍不是新 live episode、online-learning result 或 benchmark evidence。
- [done] 2026-09-30 isolated public-profile read qualification (task_reports/20260930_isolated_policy_read_qualification.md)：
  assignment runner 的 opt-in 子进程只消费 sealed public offer，父进程核对 offer/profile/read-cut/policy-input digest 后记录 worker hash；5 格离线资格、3 项定向测试、完整 PeerRoleBench 298 项通过，0 API/0 GPU。仍是 non-adversarial process boundary，未接真实 next episode 或科学效果。
- [done] 2026-09-30 isolated read → selection → task-start composition (task_reports/20260930_isolated_assignment_task_start_qualification.md)：
  在同一 runner trace 中闭合 isolated profile consumption、selection seal 和 native `PeerRoleLedger.task_start`，核对 worker/attestation digest 与同一 decision index；4 格离线资格、4 项定向测试、完整 PeerRoleBench 299 项通过，0 API/0 GPU。仍不是 live episode 或 online-learning evidence。
- [done] 2026-09-30 public profile generator seam qualification (task_reports/20260930_profile_generator_seam_qualification.md)：
  新增 typed public-only profile generator seam 与 generation receipt；确定性 fixture 只接收 eligible public projection，拒绝 UNKNOWN、private/terminal 字段和未选 candidate，并记录 digest、耗时、token、成本、API/GPU 计数及科学声明开关。5 格零调用 qualification、3 项定向测试通过；真实 summarizer、profile quality、later assignment 和 benchmark freeze 仍开放。
- [done] 2026-09-30 PIPE3 profile episode composition qualification (task_reports/20260930_pipe3_profile_episode_composition.md)：
  用 pinned PIPE3 material 与 v2 CPU scorer 执行 producer-owned / recipient-owned 两个控制；责任 gate 由实际 scorer/action/outcome 输出计算，前者生成 profile 并闭合 isolated read→selection→task_start，后者保持 PENDING_ATTRIBUTION/no-profile。25 条 JSONL 事件、0 API/0 GPU；仍是单 root、deterministic profile 和协议资格，不是科学效果或 baseline 结果。
- [done] 2026-09-30 benchmark gate status audit (`task_reports/20260930_benchmark_gate_status_audit.md`): reconciled the active benchmark/baseline plan against every strict gate; no API/GPU call was made and no Goal requirement was downgraded. Root independence, executable same-information baselines, closest adapter, independent histories, later-use effect, complete cost and precision remain open.
- [done] 2026-09-30 ArtifactRole cell-manifest parity reconciliation (`task_reports/20260930_cell_manifest_parity_reconciliation.md`): v0.2 makes all eight required policy roles explicit in both ArtifactRole cells; zero API/GPU and scientific readiness remains false.
- [done] 2026-09-30 source-bound PIPE3 boundary continuation (`task_reports/20260930_pipe3_source_bound_boundary_qualification.md`): reused one canonical boundary for task 0→task 1, enforced explicit future task index and auxiliary-chain continuation, and verified v4 public feedback updates the later selection; v1 failed expectation and v2 wrapper failures are preserved.
- [done] 2026-09-30 PIPE3 preflight-before-mutation qualification (`task_reports/20260930_pipe3_preflight_mutation_qualification.md`): preflight now rejects invalid read cuts, unavailable offers, identity/menu errors before mutation, and a transaction guard restores policy/ledger/manifests plus common RNG state after post-preflight failures; v2 targeted 9 and full 310 PeerRoleBench tests pass, 0 API/0 GPU. Immutable v1 receipt remains recorded.
- [done] 2026-09-30 versioned source-bound PIPE3 composition (`task_reports/20260930_pipe3_versioned_source_bound_composition.md`): pinned CPU scorer/action/outcome outputs now traverse the same canonical boundary into a later selection for producer-owned and recipient-owned controls. V1 stopped on a record-construction bug; v2 exposed an `ELIGIBLE` versus `policy_update_allowed` semantic leak and is retained but rejected; v3 preserves UNKNOWN/no-update under the current gate and passes both controls, 0 API/0 GPU.
- [done] 2026-09-30 PIPE3 isolated live-trace qualification (`task_reports/20260930_pipe3_isolated_live_trace_qualification.md`): pinned scorer/action/outcome, public-only trace, separate-process profile read and later canonical selection are co-ordered with the responsibility gate closed; v3 passes, 0 API/0 GPU. The profile offer and source-bound feedback offer are still separate objects, so this is an ordering/process qualification rather than a complete evidence-consumption or scientific result.
- [done] 2026-09-30 source-bound offer isolated-read binding (`task_reports/20260930_source_offer_isolated_binding.md`): the child process now reads the exact canonical `AssignmentEvidenceOffer`, with child-side bundle/policy digest checks and parent verification of record/menu/task/role/context/evidence-version/watermark fields; v9 trace from clean commit and 315-test regression pass, 0 API/0 GPU. Failed v5 is retained; scientific readiness remains false.
- [done] 2026-09-30 PIPE3 versioned live-runner promotion gate (`task_reports/20260930_pipe3_live_runner_promotion_gate.md`): two independent controls reach source-offer/isolated-read/next-selection and stop conservatively at the closed responsibility gate; no role evidence, later assignment, task start or outcome is fabricated. V1/V2/V3 receipts, explicit NOT_RUN baseline parity and qualification-only history status are retained; 317-test regression passes and scientific readiness remains false.
- [done] 2026-09-30 responsibility/update gate deadlock analysis (`task_reports/20260930_responsibility_gate_deadlock_options.md`): documents the cyclic contract and three resolutions without selecting one or changing the active method/Goal; no API/GPU and no scientific claim.
- [partial] 2026-10-01 PIPE2 runtime/adoption qualification (`task_reports/20261001_pipe2_runtime_adoption_qualification.md`): actual sandbox execution and parent-side responsibility/adoption checks distinguish original and corrected controls for seed 0/2; full seed set remains invalid because seed 1's CSV has an undeclared extra field. `v5`/`v6` receipts preserve both the valid-subset pass and full-root rejection; 340 tests in `tests/`, 0 API/0 GPU, no benchmark or efficacy claim.
- [partial] 2026-10-01 PIPE2 fixture shape audit (`task_reports/20261001_pipe2_fixture_shape_audit.md`): generator-level audit of seeds 0–9 finds invalid CSV fixtures at 1/4/6/9 due to unescaped comma-containing fields; public 0–2 has 1/3 invalid and hidden 3–9 has 3/7. No candidate/API/GPU/native score; benchmark authority remains blocked.
- [partial] 2026-10-01 PIPE2 v2 runtime handoff qualification (`task_reports/20261001_pipe2_runtime_adoption_v2.md`): v8 executes the explicit v2 material contract through an actual producer×recipient 2×2 matrix, exact key-sequence/row-count lineage, separate canary, and drop-row/ignore-artifact negative controls; valid seeds 0/2 pass the limited offline runtime/scorer gate. v9 replays 0–9 and rejects the full root because 1/4/6/9 are invalid fixtures; old v5/v6 wording is corrected without rewriting receipts. 17 targeted tests, 0 API/0 GPU, no benchmark or efficacy claim.
- [partial] 2026-10-01 MULTI3 fallback audit (`task_reports/20261001_multi3_fallback_audit.md`): pinned TeamBench MULTI3 seeds generate parseable JSON, but native frontend tests use hardcoded correct artifacts and do not exercise producer→recipient adoption; sample generation, schema enforcement, seed split and prompt oracle remain open. Kept as conditional-low fallback only; no API/GPU or benchmark replacement.
- [waiting-author] 2026-10-01 second-root fixture authority options (`task_reports/20261001_benchmark_authority_options.md`): compares PIPE2 generator repair, an explicitly derived valid subset, a new MULTI3 handoff adapter, and deferring the second root. No authority path is selected silently; the active benchmark and Goal remain unchanged.
- [partial] 2026-10-01 PIPE2 derived fixture probe (`task_reports/20261001_pipe2_derived_fixture_probe.md`): an offline standard-CSV-writer overlay preserves valid seeds and repairs shape for `1,4,6,9`, yielding derived root digest `cd4a4b7f...`; it is decision evidence only and is not an active benchmark fixture.
- [partial] 2026-10-01 PIPE3 P0 contract repairs and real-scorer gate (`task_reports/20261001_pipe3_p0_repairs.md`): candidate treatment digest binding, strict producer attribution, terminal feedback channel, and canonical auxiliary-chain continuation pass 368-test regression plus injected qualification; after one transport probe, the v1.2 CPU qualification completes `QUALIFIED_OFFLINE` for the producer-owned delayed-update contract and protective UNKNOWN/no-update recipient/mixed controls. It remains same-root engineering evidence (`0` LLM API, `0` GPU, `scientific_claim_allowed=false`); independent root, live judgment, baseline parity and benchmark freeze remain open.
- [partial] 2026-10-01 three-document gate status audit (`task_reports/20261001_three_doc_gate_status.md`): reconciles the v4 engineering qualification against the active storyline/innovation, method, and benchmark/baseline acceptance standards. All three scientific gates remain `NOT_READY`; the next blockers are second-root authority, live same-information baseline parity, and independent live histories. No Goal downgrade or A800 run.
- [partial] 2026-10-01 ArtifactRole baseline live parity design (`task_reports/20261001_baseline_live_parity_design.md`): specifies matched replay plus independent live arm histories, selected-artifact treatment binding, third-decision continuation, measured costs, and explicit closest-adapter block. Design only; no API/GPU or benchmark activation.
- [partial] 2026-10-01 live runtime/material binding seam: `LiveRuntimeBinding` and `validate_live_root_receipt` now require runtime/material/candidate digests and measured costs for future live parity receipts; 2 focused tests pass. The live runner remains unimplemented and no scientific claim is enabled.
- [partial] 2026-10-02 PIPE3 policy-factory seam: composition v1.3 accepts explicit policy construction while the default remains terminal-only; historical v1.2 receipts are untouched. Focused regression covers all three controls; no API/GPU or scientific cell.
- [partial] 2026-10-02 PIPE3 policy-name semantics: v1.3 exposes the selected arm name and a negative `no_update` qualification; later credit is committed while policy updates remain zero, with no terminal-only assumption. Seven-arm live parity is still open.
- [partial] 2026-10-02 PIPE3 feedback-channel gate (`task_reports/20261002_pipe3_feedback_channel_gate.md`): `credit_committed` no longer suffices for qualification when an arm declares an accepted feedback source; contextual-trust receiving a terminal event is preserved as UNKNOWN. An evidence-content mutation audit also shows the current hand-authored overlay leaves the choice unchanged, so evidence consumption remains unidentifiable. Seven arm public adapters, evidence-consumption decision digest, second root and live parity remain open; 0 API/0 GPU.
- [partial] 2026-10-02 stateless role-evidence assignment scorer (`task_reports/20261002_role_evidence_assignment_scorer.md`): adds a frozen public-judgment Beta overlay comparator and an opt-in preview wrapper that excludes terminal quality/Qp and persistent updates; v2 targeted receipt has 10 passes. It is not integrated into the seven-arm live runner, and complete B/C evidence mutation, second root, live parity and scientific readiness remain open; 0 API/0 GPU.
- [partial] 2026-10-02 benchmark/baseline gate re-audit (`task_reports/20261002_benchmark_baseline_gate_reaudit.md`): re-scores benchmark authority, baseline fairness, experiment-matrix execution, and result interpretation after comparator integration; only the public-judgment assignment seam is qualified, while benchmark freeze, live parity, independent histories, complete cost, and scientific results remain `NOT_READY`.
- [partial] 2026-10-02 public judgment assignment composition (`task_reports/20261002_role_evidence_assignment_composition.md`): versioned PIPE3 composition v1.4 now consumes the opt-in public-judgment comparator in the canonical assignment path; producer-owned control qualifies offline, recipient-owned/mixed remain UNKNOWN, and no API/GPU/scientific claim is made.
- [partial] 2026-10-02 public judgment effect and correction audit (`task_reports/20261002_role_evidence_assignment_composition.md`): v1.5 removes the public-mode hand-authored base preference, adds explicit judgment sensitivity fixtures with score-delta receipts, and fails closed on duplicate delivery evidence without correction lineage; this remains zero-call engineering evidence.
- [partial] 2026-10-02 recipient-judgment baseline channel (`task_reports/20261002_role_evidence_assignment_composition.md`): v1.6 maps contextual-trust/pooled recipient feedback to the target public judgment while terminal-only retains terminal feedback; raw acceptance remains UNKNOWN without an independent raw projection. This closes one channel mismatch but not seven-arm parity.
- [partial] 2026-10-02 AAMAS paper initial draft (`task_reports/20261002_paper_initial_draft.md`): rewrites the current LaTeX mainline as “Know Who You Are: Earning Roles from Situated Peer Judgments,” preserves the historical allocation draft, and adds the complete benchmark/baseline experiment matrix with blank result cells. The paper is an internal pre-results draft; no efficacy or training claim is enabled.
- [partial] 2026-10-02 AAMAS 主稿排版与版式审计 (`task_reports/20261002_paper_layout_audit.md`)：核对官方 AAMAS 2027 八页正文上限、模板/双盲/supplementary 约束；加入闭环架构图、事件时序图、实验矩阵图、headline result 表和 trace 表的可重复版式，占位结果保持为空；主稿完成 7 页编译、引用解析、无 overfull box。科学 submission gate、benchmark/baseline 和效能结果仍未就绪。
- [partial] 2026-10-02 图稿确定与多轮迭代 (`task_reports/20261002_figure_iteration.md`)：结合 Top-Conf Figure Gallery 与两位独立 Codex 审查，确定正文 F1 闭环、F2 Evidence-to-role state 方法图、F3 benchmark/baseline map；保留 v0–v7 及独立候选图稿，修正延迟反馈箭头穿框、selected-only 回写封存 assignment、after-seal 时序和 Type3 字体问题，正文图位完成 7 页版式集成，真实结果图仍待实验资格门通过。
- [partial] 2026-10-02 N03 前置设计 (`task_reports/20261002_n03_prerequisite_design.md`)：把 N02 的责任误归因、无持久 peer 状态、第二 root 权威性和 baseline parity 缺口固化为下一次真实实验的四个放行门；补齐零调用 replay→真实材料→信息价值→同信息 parity→confirmation→A800 的顺序。0 API、0 GPU，Goal 与科学成功标准未降级。
- [partial] 2026-10-02 第二 structural root 审查 (`task_reports/20261002_second_root_audit.md`)：复核 PIPE2、MULTI3、CROSS5、DIST1 后确认目前没有候选满足 ArtifactRole 五段合同；PIPE2 最值得做下一轮零调用资格，但尚未成为 benchmark，后续必须补齐材料权威、真实 judgment、later assignment、独立 outcome 和 baseline parity。
- [partial] 2026-10-02 PIPE2 全量材料形状审计 (`task_reports/20261002_pipe2_shape_audit.md`)：全量 seed 0–9 重跑确认 6 个有效、4 个 malformed（source/expected CSV 出现额外 `null` 列）；v4 runner 启动错误原样保留，v5 config/raw/summary 完整归档。PIPE2 仍不能升格 benchmark，0 API、0 GPU。
- [partial] 2026-10-02 PIPE2 严格 qualification 路径审查 (`task_reports/20261002_pipe2_qualification_review.md`)：确认现有 v2 runner 可复用但只支持 pinned fixture；derived probe 尚未接入 manifest/loader，因此下一步必须先显式封存 authority、fixture bundle 与 digest seam，不能重复 handoff 或把 valid subset 升格为 root。
- [partial] 2026-10-02 PIPE2 authority manifest seam (`task_reports/20261002_pipe2_manifest_seam.md`)：新增 fail-closed fixture manifest/loader，绑定 authority、root digest、每 seed source/expected bytes、split 和 malformed policy；8 项定向测试及真实 pinned bytes round-trip 通过，未选择任何 active authority，0 API、0 GPU。
- [partial] 2026-10-03 N03 PIPE3 real closed-loop card audit (`task_reports/20261003_n03_live_small_chain_card.md`)：独立审查指出 source→target 时序、责任标签注册来源和 peer 可识别性未封闭；卡已补充 episode/ledger 绑定、ownership 分类表、mutation registry、candidate registry/propensity 和完整 API UNKNOWN 契约。仍是 runner 设计与零调用资格阶段，0 API、0 GPU、`scientific_claim_allowed=false`。
- [partial] 2026-10-03 AAMAS 主稿与图稿复核 (`task_reports/20261003_paper_layout_audit.md`)：主稿 7 页、letter 双栏、三张矢量图无裁切/重叠/字体问题；Figure 3/Table 2 小字号和内部 pre-results 状态保留为投稿前门槛。排版通过不打开 scientific submission gate。
- [partial] 2026-10-03 N03 PIPE3 source→target contract qualification (`task_reports/20261003_n03_chain_contract_qualification.md`)：新增 v7 executable card 与零调用 schema/lineage validator，27/27 通过；负例验证缺失 target-credit keys、把 source adoption 当 later-use 时 fail closed。7 项定向测试通过，0 API/0 GPU，仍不产生科学 claim。
- [partial] 2026-10-03 N03 PIPE3 live runner precondition contract (`task_reports/20261003_n03_pipe3_live_contract.md`)：新增独立 schema/qualification，复用 registry、schedule、ledger replay 与 selection semantics；source→target 时序、ledger key binding、ownership table、candidate menu/propensity、UNKNOWN/no-update 五类 case 通过，5 项 focused tests 通过。Receipt 为 0 API/0 GPU、`scientific_claim_allowed=false`；真实 API 绑定、独立 Qp/Qr/later-use、持久 peer history 与 scientific readiness 仍开放。
- [partial] 2026-10-03 最小持久 peer history contract (`task_reports/20261003_peer_history_contract.md`)：明确初始同质状态、role/state scope 聚合、只读 public projection、E0→E1 写入时机和 history/no-history/shuffled/reset 对照。该设计只解决 peer 可识别性的前置规范，未修改 active method/benchmark/Goal，0 API/0 GPU。
- [partial] 2026-10-03 PeerHistoryV1 zero-call implementation (`task_reports/20261003_peer_history_contract.md`)：新增 append-only seal/entry/projection 模块；v1 断言失败与 v2 修复回执均保留，v2 5/5 通过、5 项 focused tests 通过，0 API/0 GPU。真实 E0/E1 和科学效果仍未运行。
- [partial] 2026-10-03 Benchmark/baseline gate 增量审计 (`task_reports/20261003_benchmark_baseline_gate_audit.md`)：确认第二独立 root、same-information contextual baseline、canonical live parity、independent histories、later-use、成本和 precision/UNKNOWN cell manifest 仍未完成；不启动正式效果流或 A800。
- [partial] 2026-10-03 Same-information baseline repair proposal (`task_reports/20261003_same_information_baseline_repair.md`)：明确 RARE 与 contextual trust 当前 feature/correction 输入不等价，提出冻结同一 public feature schema、selected-only rows、propensity、capacity 和 correction contract 后再做 live parity；不改变 active benchmark/method/Goal。
- [partial] 2026-10-04 History 四格 matched replay qualification (`task_reports/20261004_history_four_cell_qualification.md`)：在 canonical PIPE3 fixture 上完成 `history/no-history/shuffled-history/reset-history` 零调用 matched replay；selector 只消费 public projection，合法 history 改变 propensity，空历史与 reset 完全相等，乱序 fail-closed；18 项 focused tests、0 API/0 GPU，真实跨 episode history、baseline parity 与 scientific readiness 仍未关闭。
- [partial] 2026-10-04 History 四格审查修正 (`task_reports/20261004_history_four_cell_qualification.md`)：独立审查发现原 v3 的多 scope 聚合风险，selector 已要求 `target_scope_key` 并以 v4 回执重跑；19 项 focused tests 通过。报告明确保留单条非法 arrival-order 负例不等于合法 permutation，reset 尚未覆盖跨进程 replay；下一步进入持久边界卡，0 API/0 GPU。
- [partial] 2026-10-04 History 跨进程恢复边界 (`task_reports/20261004_history_process_boundary_qualification.md`)：父进程封存 snapshot、子进程 replay/projection/selector 的五 cell qualification 通过；history/empty 恢复选择完全相等，digest、截断和未知 version 均非零退出并写 UNKNOWN；20 项 focused tests、0 API/0 GPU。真实跨 episode、projection provenance、baseline parity 与 scientific readiness 仍开放。
- [partial] 2026-10-04 跨进程资格后的三份标准收敛审计 (`task_reports/20261004_convergence_after_process_boundary.md`)：将新增回执映射回故事线/创新、方法论、benchmark+baseline 三份唯一生效标准；三份仍为 `NOT_READY`，G0/G1/G2 仅部分关闭，G3–G5 未打开。下一步限定为至少两条合法 history 的 permutation/错配/rate-mutation/scope-isolation 零调用反例门，Goal 不变。
- [partial] 2026-10-04 多条 peer history 反例与 scope 隔离 (`task_reports/20261004_history_adversarial_qualification.md`)：两条合法 entry 的 permutation、candidate 错配、projection 聚合篡改均 fail-closed 为 UNKNOWN；不匹配 scope 改变不影响目标 selection；v1 失败、v2 修复和 clean-commit v3 正式回执均保留，21 项 focused tests、0 API/0 GPU。真实 provenance、independent live histories、baseline parity 与科学结果仍开放。
- [partial] 2026-10-04 Peer-history 工程门之后的唯一下一步 (`task_reports/20261004_post_history_gate_next_step.md`)：审查确认当前仍缺 hand-authored fixture 之外的 canonical provenance 放行门；冻结正例/负例、false-accept=0、exactly-once、projection whitelist 和完整成本指标，禁止在该门前启动第二 root、baseline parity、正式 API 或 A800。
- [partial] 2026-10-04 Canonical history provenance qualification (`task_reports/20261004_history_provenance_qualification.md`)：native ledger→offer/read-cut→assignment→target outcome→exact credit→history append 的 valid chain 与 cross-process digest 通过；8 类 source/target/candidate/registry/read-cut/arrival/selection/credit 篡改均 UNKNOWN、零 append/update，重复 credit 为 NOOP；22 项 focused tests、0 API/0 GPU。真实 live histories、baseline parity、第二 root 和科学结果仍开放。
- [partial] 2026-10-04 Provenance 门之后的 benchmark/baseline gate 审计 (`task_reports/20261004_benchmark_baseline_post_provenance.md`)：canonical provenance 与 v16 七 arm 离线实现 parity 仅关闭工程子门；公共 feature parity、same-information live comparison、第二 root、closest adapter、later-use/成本/统计仍 OPEN。下一张卡只冻结 canonical PIPE3 parity，不启动 API/A800。
- [partial] 2026-10-04 Canonical history provenance clean replay：在 clean commit `257791f` 上重跑正式 v2 回执，配置记录空 worktree；v1 未提交工作树回执保留，valid/mutation/exactly-once 结论不变。
- [partial] 2026-10-04 三份审查核验文档距离审计 (`task_reports/20261004_three_doc_distance_audit.md`)：按当前唯一生效的故事线、方法论、benchmark+baseline 及三份评价标准重算距离；三份均仍 `NOT_READY`，G0/G1/G2 为部分关闭，G3–G5 未打开。工程 provenance/history 与七 arm 离线 parity 已有回执，但第二结构 root、公共 feature same-information parity、closest adapter、independent live history、future utility、实时/遗忘/成本和科学统计仍开放；不降级 Goal，不启动 API/A800。
- [partial] 2026-10-04 三条方法不变量的合同—证据映射 (`task_reports/20261004_invariant_mapping.md`)：将 pre-selection noninterference、recipient-only attribution safety、idempotent replay 写成当前可检验性质，映射到既有零调用回执；三者目前最多支持协议/工程级 claim，不能替代 live scientific evidence 或正式定理。
