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
