# Engineering lessons

### 0001-idealab-single-authentication-header | 2026-09-22 | earning-roles

- **Symptom:** the first real inference health request returned HTTP 401.
- **Cause:** it sent both `x-api-key` and `Authorization`; idealab explicitly
  rejects simultaneous authentication headers on its code endpoint.
- **Prevention:** map cc-switch `ANTHROPIC_AUTH_TOKEN` to the Bearer header only,
  validate with a real small call, and archive failed attempts before retrying.
- **Evidence:** `artifacts/experiments/aamas2027/dev_20260922/preflight_raw.jsonl`.
- **Outcome:** the next request returned HTTP 200 with model `qwen3.8-max` and
  real usage. Endpoint/catalog availability alone was not called inference health.

### 0002-httpx-ipv6-cidr-import | 2026-09-22 | earning-roles

- **Symptom:** importing the official ReAct parser failed in litellm/httpx before any task model call.
- **Cause:** NO_PROXY contained `::1/128`; httpx turned it into an invalid URL host. Early bracket/removal attempts targeted `::1` and missed the CIDR.
- **Prevention:** inspect parser source and the relevant sanitized environment value before patching. Normalize only `::1/128` to equivalent `::1` inside the experiment subprocess; do not modify global proxy settings.
- **Evidence:** all fixture failures and the eventual check are in `artifacts/experiments/aamas2027/dev_20260922/runtime_fixture_raw.jsonl`.

### 0003-semantic-arm-label-in-storage-path | 2026-09-22 | earning-roles

- **Symptom:** memory-arm solving completed, but official evaluation had zero assertions and a storage exception.
- **Cause:** pinned AppWorld tests whether the substring `memory` occurs anywhere in a DB changes path, so a normal arm label was mistaken for SQLite in-memory storage.
- **Prevention:** keep scientific labels in metadata, use neutral hashes for native storage paths, and test both treatment and control scorer paths before broad execution.
- **Repair:** preserve original errors; copy already saved state files byte-for-byte to neutral paths and call the unchanged official scorer. Do not rerun a model or treat an unavailable scorer as a task-quality failure.
- **Evidence:** `scorer_storage_repair.json` and per-episode `rescoring_raw.jsonl` under the current experiment directory.

### 0004-requested-output-is-not-total-generation-cap | 2026-09-22 | earning-roles

- **Symptom:** all six induction responses reported output usage above the requested text limit.
- **Cause:** the provider's reported total includes reasoning generation; the nominal parameter is not an independently enforced aggregate spend limit.
- **Prevention:** distinguish requested settings from actual reported usage, include cached input and reasoning output, retain unknown failed-request usage, and use attempted-call ceilings explicitly. Do not publish an exact dollar bill without prices.
- **Evidence:** the first round's six induction raw responses and `analysis.json`.

### 0005-resume-must-respect-persisted-outage-stop | 2026-09-22 | earning-roles

- **Symptom:** pre-inference independent review found that a controller could skip completed tasks after restart and thereby bypass a prior two-task outage stop.
- **Cause:** the circuit breaker was checked only after newly completed work.
- **Prevention:** before any paid subprocess, check durable stop events and the ordered completed prefix, including a crash between result persistence and stop-event persistence.
- **Outcome:** fixed before the full-dev census's first request; the reviewed code and contract were then hashed and frozen.

### 0006-cost-categories-must-partition-the-full-ledger | 2026-09-22 | earning-roles

- **Symptom:** total 329 raw requests reconciled, but acquisition subtotal 86 omitted the 16-call explicitly tagged repair; a residual 48 was incorrectly described as null cost.
- **Cause:** an exact-stage filter did not include the repair stage; the independent reviewer checked arithmetic without reclassifying every episode.
- **Prevention:** include every stage and assert acquisition 102 + validation 195 + unchanged controls 32 = raw 329. Category-level checks are necessary even when the grand total passes.
- **Repair:** preserved the pre-fix report/analyzer/review and added a correction record; official scores and gate decision are unchanged.

### 0007-database-checkpoint-is-not-complete-agent-state | 2026-09-22 | earning-roles

- **Symptom:** a native checkpoint copied into a fresh world lost `playlists` at the first continuation; native teardown also raised freezegun errors.
- **Cause:** AppWorld `save_state` stores database changes, not the REPL namespace or model messages. Its `load_state` closes process-global runtime state, interacting with context-manager cleanup.
- **Prevention:** reconstruct and validate the complete continuation state in isolated processes; charge prefix execution and environment calls. Do not infer faithful replay from matching DB files.
- **Evidence:** `artifacts/experiments/aamas2027/replay_fixture_20260922/` preserves the config, two identical complete code replays, failed database-only continuation and unmodified stderr. Zero new LLM calls; the overall fixture is explicitly partial.

### 0008-single-trajectory-difference-is-not-causal-proof | 2026-09-23 | earning-roles

- **Symptom:** a report described a treatment-versus-control trace difference as experience changing behavior.
- **Cause:** each arm was run once and repeated untreated execution also changed request count and actions; the analysis skipped this variance check when moving from observation to causal wording.
- **Prevention:** state the observed contrast first, inspect unchanged-agent repeat variation, and reserve attribution to acquired content for a prospectively controlled comparison that separates content, generic reminders and prompt length.
- **Evidence:** [reassessment](../docs/scientist/analysis/AAMAS_Q1_FEASIBILITY_REVIEW_20260922.md#报告判断的再次复核) and [task record](../docs/coordination/AAMAS_TASKS.md); frozen raw runs remain unchanged.

### 0009-streamjev-random-baseline-was-too-weak | 2026-09-24 | earning-roles
- **现象:** selected-only RLS showed a small positive simulated gain, but the comparison called a uniform policy “static” and did not test task-dependent candidate ranking.
- **根因:** the first smoke was written to validate event/update plumbing, then its result was read too close to a method comparison; context was added additively, so it could not change within-menu ordering.
- **避免:** label plumbing smokes as such; before any effect run, require a non-zero static scorer, a same-exploration no-update control, task×candidate interaction, and a separate old-task revisit gate.
- **Evidence:** `references/aamas/streamjev_20260924/experiments/logs/selected_only_review_20260924_results.json` and the controlled-iteration ledger.

### 0010-experiment-provenance-must-be-frozen-before-run | 2026-09-24 | earning-roles
- **现象:** the saved experiment config recorded the checkout HEAD before the experiment code was committed, and omitted several runtime head parameters.
- **根因:** execution started from a dirty working tree while the provenance check assumed HEAD identified all executed code.
- **避免:** freeze or hash the source tree and diff before execution, record the complete learner config, and stream raw rows as each event is produced; never repair old provenance by silently rerunning.
- **Evidence:** the original config, its preserved report, and the post-hoc analysis input hashes.

### 0011-gui-failure-is-not-filesystem-denial | 2026-09-26 | earning-roles
- **现象:** 图形终端/编辑器调用受阻或超时后，曾将其解释为无法读写本地项目。
- **根因:** 把某个界面的调用失败等同于操作系统文件权限失败，没有先检查可用 shell 路径。
- **避免:** 先用只读 shell 命令定位 cwd、目标文件和实际权限，再通过可用终端与 apply_patch 完成本地读写；只有具体文件操作被拒绝时才报告该权限问题，不能从 GUI 失败推断全部工具不可用。
- **Evidence:** 2026-09-26 本地文件读写恢复；本轮四份报告/审计通过终端读取和 apply_patch 更新。

### 0012-future-assignment-must-affect-future-execution | 2026-09-26 | earning-roles
- **现象:** 初版先生成所有 peer 的产物再选择，记录后续 assignment 却在下一轮独立选人；消费者标记 repair/redo 后仍评分原交付。
- **根因:** 只检查日志字段齐全，没有检查反馈是否改变下一次执行前决策，以及消费者动作是否改变最终被评分对象。
- **避免:** 强制 selection→task start→selected peer 执行，下一轮消费 assignment 并保留真实 propensity；实际生成 use/repair/redo 产物，由 grader 评分该产物。负面证据允许改派其他 peer。
- **Evidence:** [ADR 0015](../docs/user/decisions/0015-select-before-execution-and-bind-later-assignment.md)；causal_v1 保留第二轮 random propensity 误记 1.0 的失败，causal_v2 为 1/3。16 条夹具仍不能证明学习效果。

### 0013-grader-dependency-failure-is-not-model-failure | 2026-09-26 | earning-roles
- **现象:** DIST1 grader 使用 pytest 的 `--timeout`，缺少 pytest-timeout 时检查失败，污染任务质量分数。
- **根因:** 运行前只检查 pytest 可用，没有检查原生评分命令依赖的插件；环境失败被混入任务失败。
- **避免:** 在真实执行前预检完整 grader 依赖，并用已知正确/错误产物检查评分动态范围；缺失依赖时停止并记录环境错误，不返回有效任务质量分。
- **Evidence:** `experiments/logs/peerrolebench_dist1_fixture_qualification_20260926/` 记录 pytest-timeout 2.4.0；seed 0 初始 6/12、repair 12/12，不能推广为其他 seed 均已合格。

### 0014-source-allowlist-must-follow-task-instance | 2026-09-26 | earning-roles
- **现象:** CR2 seed 1 的修复产物得 3/13，起初被解释为修复对新 seed 泛化失败。
- **根因:** grader 的 source allowlist 写死 seed 0 的 `test_helpers.py`，没有复制 seed 1 的 `api_client.py`；另有真实尾逗号修复遗漏。仅检查测试文件未改不足以确认评分的是候选源文件。
- **避免:** 从可信任务实例元数据确定允许复制的源文件，并比较 candidate 与 evaluator 执行前后的 source digest；先确认评分对象正确，再讨论能力差异。
- **Evidence:** CR2 首次 qualification 保留 12/13、3/13；`peerrolebench_cr2_fixture_qualification_20260926_v2` 两个 seed 均为 13/13，失败日志不覆盖。

### 0015-deduplicate-evidence-and-seal-before-selection | 2026-09-26 | earning-roles
- **现象:** 新 evidence ID 可重复提交同一 judgment/action；下一轮先 selection、尚未 task start 时仍可补写 assignment。
- **根因:** 去重只验证事件 ID，时间边界只验证执行开始，没有验证证据来源和决策已经作出的事实。
- **避免:** 按 judgment/action 来源去重，改版本或到达时间不生成新观测；同任务 episode 已有 selection 即拒绝后补 assignment。保留负反馈可选不同 peer 的正例，并测试同来源重放与后补决策的拒绝路径。
- **Evidence:** [strict 协议回归测试](../references/aamas/test_peer_role_protocol_strict_20260925.py)；修复后两份协议测试共 15 项通过。这是合约保证，不是方法效果。

### 0016-score-the-actual-recipient-behavior | 2026-09-26 | earning-roles
- **现象:** DIST1 原生分无法区分真正正确的 consumer 与不 ack、不 nack 的 consumer。
- **根因:** 原生 grader 只检查 consumer 语法，行为测试自建消费循环；之前把队列分误当协作终局分。
- **避免:** 从被评分对象追到调用链，做针对性正常/缺陷对照；新增指标单独版本化，不改称原生分或完整正确率。
- **Evidence:** `experiments/logs/n01_consumer_behavior_20260926_v2/`；实际 worker 接入见 `n01_runtime_qualification_20260926_v3/`。

### 0017-unknown-must-not-erase-observation-or-become-negative-label | 2026-09-26 | earning-roles
- **现象:** 后续超时一度覆盖此前失败；子进程返回 MemoryError/PermissionError 又会被统一断言为能力 FAIL。
- **根因:** 只在整轮捕获异常，且混同传输/运行限制与任务行为。
- **避免:** 每个检查立即保存；未完成整轮为 UNKNOWN，保留观察失败但不生成总体负标签；父子两端资源错误均显式分类。
- **Evidence:** v1 失败日志保留；`tests/test_peerrolebench_consumer_errors.py` 七项定向回归，最终契约检查66项通过。

### 0018-runtime-compatibility-needs-source-backed-diagnosis | 2026-09-26 | earning-roles
- **现象:** 手写 Seatbelt profile 使 dyld 执行前中止；macOS 又拒绝预设 RLIMIT_DATA，冗余 kill 已退出进程组报错。
- **根因:** 只按 Linux/POSIX 直觉拼权限与资源限制，没有核查该运行时的具体语义。
- **避免:** 复用固定上游 runtime，精确核对根 vnode 许可；区分硬限额与RSS watchdog；只清理仍活跃的进程组，保留失败版本。
- **Evidence:** `references/aamas/sandbox_runtime_20260926/` 与 `experiments/logs/n01_runtime_qualification_20260926{,_v2,_v3}/`。

### 0019-verify-downloaded-package-content-before-building | 2026-09-26 | earning-roles
- **现象:** 直接下载的 hyperxmp.sty 实为 HTML，导致 LaTeX 构建失败；tlmgr 镜像亦遇到校验问题。
- **根因:** 下载命令成功不代表响应是所需包文件。
- **避免:** 核验文件类型与内容，使用官方 dtx/ins 生成依赖并保存哈希；失败构建与成功回执分别保留，不能改官方模板掩盖缺依赖。
- **Evidence:** `artifacts/aamas2027/proposal_20260926/receipt.json`，官方类文件保持不变。

### 0020-separate-assigned-integration-from-upstream-repair | 2026-09-26 | earning-roles
- **现象:** 两次真实consumer声明repair，却都只改变自己负责的consumer.py；第一轮将自己的writable_paths误当producer漏做义务。
- **根因:** 载荷合并源码后未显式保留原职责，把动作选择与修改权误当可归因返工；全部集成调用成本亦可能被误称额外返工。
- **避免:** 公开原始文件归属，扩写权限不转移责任；分别保存声明、真实修改、独立行为检查和阶段成本。只有修了文件也不自动证明生产者缺陷。
- **Evidence:** N02 v3封存判断/源码及`n02_posthoc_responsibility_20260926`；历史输出不回改。

### 0021-consumer-pass-is-not-complete-delivery-correctness | 2026-09-26 | earning-roles
- **现象:** 两轮consumer四项全通过，priority却分别导入失败、原构造接口失败；judge均断言已修好。
- **根因:** 新增consumer评分只覆盖实际消费路径，遗漏producer其他公开交付义务。
- **避免:** 每项公开义务映射独立检查，同时标明是否进入实际consumer依赖；分报交付和集成结果，不因事后发现改旧分或喂回历史agent。
- **Evidence:** `n02_posthoc_priority_sandbox_20260926`使用实际运行边界；两例缺陷与正确control均保留。

### 0022-peer-labels-without-state-do-not-create-learnable-identities | 2026-09-26 | earning-roles
- **现象:** N02的A/B/C使用同模型、fresh prompt，producer不接收身份或个人经验，过去经历不能影响下一次产物。
- **根因:** 将账本的persistent ID误等同于执行者具有persistent experience；接线试验若直接扩样会学习随机调用噪声。
- **避免:** 先定义相同起点、合法个人经验如何进入后续工作，与别人对peer的评价分开；所有对照固定同一记忆规则，不预设专长制造效果。即使有记忆也仍须验证可预测差异。
- **Evidence:** N02 v3源码/producer请求及独立审查；本轮没有角色形成证据。

### 0023-negative-label-fixtures-can-hide-gate-information | 2026-09-29 | earning-roles
- **现象:** 三事件反事实中责任门与去门控更新器产生完全相同的选择，起初容易被误读为责任门没有价值。
- **根因:** recipient-owned 行使用 `raw=0` 且与 producer 候选特征正交；对角更新只改变分母，不产生方向性系数。
- **避免:** 机制资格测试必须覆盖 raw 正值、零值、缺失值和非正交特征；先检查手算可识别性，再解释负结果。缺失信号保持 `UNKNOWN`，不能编码为 0。
- **Evidence:** `experiments/logs/n03_four_event_counterfactual_20260929_v1/` 与 `experiments/logs/n03_gate_identification_matrix_20260929_v1/`。

### 0024-candidate-formula-and-code-must-share-piecewise-contract | 2026-09-29 | earning-roles
- **现象:** 候选卡的 ridge 常数、空窗口 anchor 投影和 pending 容量与 reference implementation 的实际语义不完全一致。
- **根因:** 先写连续公式，后补状态边界；空集合和延迟队列没有作为同一数学合同的分支与容量写出。
- **避免:** 每个公式都写空集/边界 case、参数冻结值和可运行实例；同步检查实现的 `lambda`、empty-window、queue/tombstone 与 snapshot/restore。
- **Evidence:** `docs/research/candidates/method_lock_card_v0.1_20260929.md` 与候选静态审计/修复日志。

### 0025-python-bytecode-cache-can-fail-outside-project-write-root | 2026-09-29 | earning-roles
- **现象:** `py_compile` 首次尝试因系统 Python 将 `.pyc` 写入受限用户缓存目录而失败，源码本身没有语法错误。
- **根因:** 验证命令未把 bytecode cache 定位到项目可写目录。
- **避免:** 在受限环境中使用项目/临时目录的 `PYTHONPYCACHEPREFIX`，并保留原始权限错误；不能把环境写权限失败当作源码失败。
- **Evidence:** 本轮终端回执；修正后 `PYTHONPYCACHEPREFIX=/tmp/earning_roles_pycache python3 -m py_compile ...` 通过。

### 0026-shared-policy-seams-must-preserve-event-time | 2026-09-30 | earning-roles
- **现象:** RARE 能在直接 policy 流中使用 arrival_index，但 sidecar bridge 最初丢弃该字段，replay 又按 arrived_at 排序，导致同一延迟流无法复现 watermark/correction 语义。
- **根因:** 把审计墙钟时间当成在线事件顺序，且把候选 updater 的元数据要求留在下游实现，没有让共享 sidecar/runner 合同承载它。
- **避免:** 在接口层显式版本化 event-time sidecar，要求 v4 的 arrival_index、correction lineage 和 frozen expected schedule；历史版本只能走兼容回放，不能与新流混用。
- **Evidence:** `docs/coordination/task_reports/20260930_rare_policy_adapter.md`；`experiments/logs/n03_rare_policy_adapter_20260930_v3/`。

### 0027-updater-validation-must-be-atomic-and-restorable | 2026-09-30 | earning-roles
- **现象:** malformed RARE feedback 在 updater 校验前就被记为 seen，修复元数据后重放会被错误当作 duplicate；sidecar bridge 的 correction lineage 也无法从 policy snapshot 恢复。
- **根因:** replay bookkeeping 与 concrete updater commit 没有事务边界，bridge 自己维护了一份没有 snapshot 合同的平行历史。
- **避免:** 只有 updater 接受事件后才提交 seen/lineage；correction lineage 以 policy snapshot 为准，bridge 不复制一份不可恢复的状态；对跨 selection/channel 的 supersedes 做硬拒绝。
- **Evidence:** `scripts/peerrolebench_baseline_policies.py`、`scripts/peerrolebench_policy_sidecar.py` 及 78 项定向回归。

### 0028-feedback-must-be-consumed-before-the-next-selection | 2026-09-30 | earning-roles
- **现象:** 离线 policy matrix 先封存当前选择再消费同一 offer 的 feedback；日志看似记录了更新，但早到 judgment 没有参与本次 read-cut 后的选择。
- **根因:** runner 把“反馈已写入状态”和“反馈对哪个 decision 可见”当成同一件事，偏离了 PIPE3 的 consume-before-choose 顺序；同时 matrix 没有 raw acceptance 正向 fixture，无法资格化该 baseline。
- **避免:** 在每次 choose 前只消费 arrival_index 不晚于 read_cut、且已绑定历史 source selection 的事件；为每个 feedback channel 写正向、UNKNOWN、unselected、late 和 self-reference mutation case，并把预期语义纳入通过条件。
- **Evidence:** `docs/coordination/task_reports/20260930_policy_matrix_runner.md`；`experiments/logs/n03_policy_matrix_runner_20260930_v9/`。

### 0029-closest-method-must-share-the-causal-unit-and-information-cut | 2026-09-30 | earning-roles

- **现象:** selector/delegation 论文很容易被写成 ArtifactRole 的 closest baseline，但它们没有 recipient adoption、producer attribution、selected-only 分母或 later assignment；Meta-Team 原生还读取终局与完整轨迹。
- **根因:** 只按“都能选择/反思/更新 profile”命名近邻，没有先固定 causal unit、公开信息 cut、成本和 assignment 时序。
- **避免:** 严格 drop-in 缺失时明确 `NO-GO`；若独立实现语义 adapter，分成 original-info 上限、public 同信息主比较和 profile-only 消融，并预注册 schema/parser、预算、watermark、correction/replay、later assignment 和完整成本。不能用手写 trust score 冒充已发表方法。
- **Evidence:** [closest adapter audit](../docs/coordination/task_reports/20260930_closest_adapter_audit.md)；[candidate closest-method table](../docs/research/candidates/closest_method_table_v0.1_20260929.md)。

### 0030-qualifying-a-profile-schema-is-not-qualifying-the-profile-generator | 2026-09-30 | earning-roles

- **现象:** Meta-Team 风格的定性 profile 字段和 watermark/纠错合同可以在零调用 fixture 中通过，但这并不说明摘要模型看到了正确的信息、profile 能预测 later-use，或 baseline 已实现。
- **根因:** 把 schema/lineage 的可构造性与 profile 生成质量、调用成本和真实 assignment 消费混为一层资格。
- **避免:** 把资格分成 schema boundary、真实 public builder/replay、LLM profile quality、独立 live history 和 later-use effect；任何层失败都保留证据并停止向下一层推断。真实 adapter 必须绑定 source_input_digest，禁止 trajectory/terminal/private scorer 泄漏。
- **Evidence:** [Meta-Team-L2-public qualification](../docs/coordination/task_reports/20260930_metateam_public_profile_qualification.md)；[v6 logs](../experiments/logs/n03_metateam_public_profile_qualification_20260930_v6/)。

### 0031-selection-identity-must-not-be-inferred | 2026-09-30 | earning-roles
- **现象:** 原生 `PeerSelection` 只保存 bare candidate ID，而 profile sidecar 使用 `candidate_id@candidate_version`；它也不携带 versioned candidate view 或 `selected_at`。直接把两者当成同一对象会掩盖版本漂移、菜单重排和时间水位线错误。
- **根因:** ledger identity、policy candidate key 和 assignment read-cut 被不同模块分别表示，却没有显式的 canonical view。
- **避免:** 通过严格 registry adapter 显式映射版本，保留菜单顺序、chosen index、task index、选择时间和 selector；未知版本、菜单变更、错误选择和非单调时间一律拒绝，绑定前不从 bare ID 猜版本。
- **Evidence:** [selection view qualification](../docs/coordination/task_reports/20260930_selection_view_adapter_qualification.md)；`experiments/logs/n03_selection_view_adapter_qualification_20260930_v1/`。

### 0032-unknown-projections-must-retain-event-time-lineage | 2026-09-30 | earning-roles
- **现象:** `project_feedback` 的 UNKNOWN 分支原本只保留 label 为空，丢失了 v4 `arrival_index` 和 `supersedes`；后续 offer 无法检查迟到顺序或 correction lineage。
- **根因:** eligible 与 ineligible 分支分别构造 projection 时，没有把事件时间与修订元数据视为 policy-visible 的审计字段；误把“没有 label”当成“没有事件元数据”。
- **避免:** UNKNOWN 仍必须保留 event-time 和修订引用，但不能携带 label 或 gate/raw 私有原因；offer adapter 对旧 wall-clock-only projection 直接拒绝，并要求公开、固定的 unknown reason。
- **Evidence:** [public feedback-row adapter qualification](../docs/coordination/task_reports/20260930_public_feedback_row_adapter_qualification.md)；`experiments/logs/n03_public_feedback_rows_qualification_20260930_v1/`。

### 0033-source-bound-offers-must-validate-before-serialization | 2026-09-30 | earning-roles
- **现象:** typed projection 可以正确生成 public row，但 `make_offer` 本身不验证 projection 是否来自 canonical ledger、完整责任链或冻结 arrival schedule；直接调用会把结构正确误当成来源正确。
- **根因:** sidecar binding、lineage validation、schedule validation 和 public serialization 分散在不同模块，缺少一个强制顺序的入口。
- **避免:** 先绑定 selection/feedback 到 canonical records，再要求 v4 与责任链、schedule 一一对应，最后才调用 projection→row→offer；raw acceptance 另走 comparator 通道，UNKNOWN 不更新。
- **Evidence:** [source-bound adapter qualification](../docs/coordination/task_reports/20260930_source_bound_feedback_adapter_qualification.md)；`experiments/logs/n03_source_bound_feedback_adapter_qualification_20260930_v1/`。

### 0034-real-ledger-replay-must-preserve-pending-attribution | 2026-09-30 | earning-roles
- **现象:** 冻结的真实 v6 episode 有完整 Qp/Qr/adoption 和 recipient-owned repair，但没有 producer-eligible evidence；如果直接把 terminal success 当 label，会把责任错误传给 producer。
- **根因:** 终局成功、消费者修复和 producer responsibility 是不同因果量，历史 ledger 以 UNKNOWN 表达等待归因。
- **避免:** 对真实历史 ledger 先做 canonical replay，再经 v4 lineage/schedule adapter；pending attribution 只生成带公开原因的 UNKNOWN row，不能写 label 或 policy update，也不能回写历史结果。
- **Evidence:** [frozen v6 source-bound replay](../docs/coordination/task_reports/20260930_v6_source_bound_replay_qualification.md)；`experiments/logs/n03_v6_source_bound_replay_qualification_20260930_v1/`。

### 0035-a-process-flag-is-not-an-isolated-read-trace | 2026-09-30 | earning-roles
- **现象:** runner 原先把 `recorded_public_input_digest` 和 `isolated_policy_trace=false` 作为同一条边界；仅在父进程记录 profile digest 不能证明 policy 真读了公开 profile。
- **根因:** profile consumption、attestation 和 policy read 没有明确的进程边界与响应核对顺序。
- **避免:** opt-in 子进程只接收 sealed public payload，父进程核对 offer/profile/read-cut/policy-input digest 后才提交 state transition；worker hash、schema 和 trace 一起记录。明确这是 non-adversarial boundary，不冒充 hostile sandbox。
- **Evidence:** [isolated policy-read qualification](../docs/coordination/task_reports/20260930_isolated_policy_read_qualification.md)；`experiments/logs/n03_isolated_policy_read_qualification_20260930_v1/`。

### 0036-isolated-read-must-share-the-task-start-decision-index | 2026-09-30 | earning-roles
- **现象:** isolated profile read、selection binding 和 native `task_start` 各自通过并不代表它们属于同一个 later assignment；若 decision index 漂移，profile consumption 可能被错配到另一任务。
- **根因:** 之前三个 boundary qualification 是分开的，缺少一个组合 trace 检查 worker digest、selection seal 和 native task-start 的同一 decision index。
- **避免:** 在同一 runner 中按固定顺序执行并记录四阶段 trace，要求 attestation digest 与 worker digest相同，native task_start 的 task index 等于 offer decision index。
- **Evidence:** [isolated assignment/task-start qualification](../docs/coordination/task_reports/20260930_isolated_assignment_task_start_qualification.md)；`experiments/logs/n03_isolated_assignment_runner_qualification_20260930_v1/`。

### 0037-generator-seam-must-separate-fixture-from-quality | 2026-09-30 | earning-roles
- **现象:** 新增 profile generator 测试时把请求类型名写成了不存在的别名，且很容易把 deterministic profile fixture 误写成真实摘要模型结果。
- **根因:** 接口命名和“资格边界/科学效果”两层语义没有在第一版中同时锁定。
- **避免:** 让唯一的 `PublicProfileGenerationRequest`/`GeneratedPublicProfile` 类型贯穿调用；receipt 强制记录零调用、成本和 `scientific_claim_allowed=false`，任务报告明确 fixture 不能支持 profile quality 或 efficacy claim。
- **Evidence:** [profile generator seam qualification](../docs/coordination/task_reports/20260930_profile_generator_seam_qualification.md)；`experiments/logs/n03_profile_generator_seam_qualification_20260930_v1/`。

### 0038-direct-scorer-fallback-must-clear-import-cache | 2026-09-30 | earning-roles
- **现象:** macOS nested scorer transport 失败后，直接调用同一 worker 的 CPU fallback 会把前一个临时 workspace 的 `models/producer/processor/sink` 模块留在 `sys.modules`，导致后续 case 得到错误的 adoption 结果。
- **根因:** worker 使用短模块名导入，fallback 复用了同一 Python 进程，却没有隔离模块缓存和临时 source path。
- **避免:** 每次 fallback 前清除四个短模块名并插入当前临时 source 根目录，完成后移除 path 和模块；在 JSONL 中保留 transport failure 与 fallback worker，不把 fallback 当生产 sandbox。
- **Evidence:** [PIPE3 profile episode composition](../docs/coordination/task_reports/20260930_pipe3_profile_episode_composition.md)；`experiments/logs/n03_pipe3_profile_episode_qualification_20260930_v1/events.jsonl`。

### 0039-source-bound-next-selection-must-continue-the-canonical-boundary | 2026-09-30 | earning-roles
- **现象:** 第一版 source-bound selection wrapper 能读到公开反馈，但新建了自己的 ledger/auxiliary chain；同时把来源 task index 误当成目标 task index，且 offer mutation 测试在构造器摘要校验处提前失败。
- **根因:** 为了复用接口又复制了 selection boundary，缺少 canonical ledger/manifest continuation；目标任务索引没有成为 source-bound adapter 的显式输入；dataclass 是不可变摘要对象，直接 `replace` 会留下旧 digest。
- **避免:** 复用同一 `Pipe3SelectionBoundary` 完成 task 0→task 1；source-bound offer 显式携带并校验 `target_task_index` 与 previous auxiliary root；篡改测试必须通过 `make_offer` 重新计算 digest 后再进入 runner。
- **Evidence:** [source-bound boundary qualification](../docs/coordination/task_reports/20260930_pipe3_source_bound_boundary_qualification.md); 保留失败日志 `experiments/logs/n03_source_bound_selection_qualification_20260930_v1/`、`v2/`。

### 0040-source-bound-records-must-belong-to-the-supplied-ledger | 2026-09-30 | earning-roles
- **现象:** sidecar 的 hash 绑定本身通过时，来自另一份 ledger 的 selection/feedback record 仍可能被传入 adapter。
- **根因:** adapter 只验证调用者提供的 record 与 sidecar hash 一致，没有把它与传入 ledger 的 canonical `(event_type,event_id)` record 做 membership 比较。
- **避免:** 在 source-bound offer sealing 前，从 supplied ledger 的 event index 取 canonical selection 与 feedback records，并要求它们与参数逐字一致；随后才做 lineage、schedule 和公开投影。
- **Evidence:** [source-bound boundary qualification](../docs/coordination/task_reports/20260930_pipe3_source_bound_boundary_qualification.md)。

### 0041-preflight-before-mutation-is-required-at-selection-boundaries | 2026-09-30 | earning-roles
- **现象:** `choose_and_seal` 原先先追加 offer、消费反馈和更新 policy，再构造 consumption attestation；`read_cut`、offer availability 或后续 RNG/ledger 错误可能留下半条 selection 链。
- **根因:** attestation 的部分合法性检查发生在状态改变之后，且 policy/ledger/manifest 没有统一事务边界。
- **避免:** 在 mutation 前检查角色、菜单、重复 task/selection、版本、时间、水位、可用性和 selected-only feedback 绑定；随后以对象级快照保护仍可能在采样后抛出的错误，并恢复 policy、ledger、selection cache 及双 manifest。
- **Evidence:** [PIPE3 preflight-before-mutation qualification](../docs/coordination/task_reports/20260930_pipe3_preflight_mutation_qualification.md)；`experiments/logs/n03_pipe3_preflight_mutation_qualification_20260930/`。

### 0041-selection-boundaries-must-preflight-before-mutation | 2026-09-30 | earning-roles
- **现象:** `choose_and_seal` 原先先写 auxiliary offer、消费反馈和 policy decision，之后才构造 consumption attestation；read-cut 越界、offer 尚不可用、角色/menu 不匹配或后续 policy/ledger 异常可能留下部分状态。
- **根因:** 输入时序约束和对象构造校验分散在 attestation、policy、native ledger 三层，入口没有在第一次写入前统一检查，也没有失败回滚。
- **避免:** 先 preflight role/selector、episode/event identity、版本与时间、`read_cut <= decision_index`、offer availability、menu/features 和 selected-only feedback binding；再进入 mutation transaction。对 preflight 后仍可能出现的 policy/ledger/RNG/attestation 异常，恢复 policy、ledger、selection cache、两条 manifest 链和可捕获的 numpy/getstate RNG 状态；无状态接口的 RNG 不宣称可恢复。
- **Evidence:** [preflight qualification](../docs/coordination/task_reports/20260930_pipe3_preflight_mutation_qualification.md)；`experiments/logs/n03_pipe3_preflight_mutation_qualification_20260930/`；309 项 PeerRoleBench 回归通过。
