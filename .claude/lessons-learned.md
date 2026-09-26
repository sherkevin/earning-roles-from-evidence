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
