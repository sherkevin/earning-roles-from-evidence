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
