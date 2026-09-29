# 决议文件夹

存放位置：`docs/user/decisions/`。一份决议对应一个文件，索引保留全部历史编号。

当前管理规则与研究质量标准见 [ADR 0038](0038-decision-record-governance-and-research-invariants.md)。新增或实质修改正式决议须经用户与助手双方明确确认；未确认建议、实验结果和任务进展分别保存在研究文档或任务报告中。

- [0001 — Resume bounded real-data / real-API iteration](0001-resume-real-api-iteration.md): explicit user authorization supersedes the previous pause.

- [0002](0002-close-acquisition-v1-promotion.md): the first real acquisition package fails its unchanged promotion gate; preserve results and costs.
- [0003](0003-complete-independent-dev-census.md): one independent complete empty-agent dev census, with fixed headroom and stopping rules.
- [0004](0004-continue-unstarted-census-after-outage.md): after a verified outage recovery, continue only original unstarted tasks; preserve interrupted outcomes as UNKNOWN.
- [0005](0005-retain-peer-judged-role-learning.md): retain learning roles from actual collaborators' judgments of delivered work as the research core; novelty and algorithm remain to be proven.
- [0006](0006-study-peer-judged-role-formation.md): choose peer-judged role formation as the active direction; retire package replacement/conditional adoption as the main-paper question because agents and workflows co-evolve in this project.
- [0007](0007-reuse-open-source-benchmark-runtime-first.md): reuse pinned benchmark/runtime components and write only thin peer-judgment adapters, with license/scorer gates before scientific lock.
- [0008 — Freeze benchmark layers and baseline matrix](0008-freeze-benchmarks-and-baselines.md): use DecisionBench for selector evaluation, CooperBench for role-formation evaluation, AgentWorld for later external validity, and freeze the matched baseline matrix and scale defaults.
- [0009 — Adopt AnyJev as the shared dynamic-selector stack](0009-adopt-anyjev-shared-selector-stack.md): use pinned AnyJev with Qwen3-4B for both peer and tool selection, while implementing event-level residual updates outside AnyJev's scheduled refit loop.
- [0010 — Reframe the contribution as streaming JEV training](0010-reframe-streaming-jev-training.md): demote AnyJev/Qwen to baselines and make trainable real-time adaptation of a small JEV-style model the research direction.
- [0011 — 按决策价值控制实验节奏](0011-bound-experiments-by-decision-value.md): 先分析现有结果，以单一问题、明确对照、资源上限和停止条件安排下一轮，逐项记录与关闭问题。
- [0012 — 不锁定 Laya，也不把 RLS 当成论文创新](0012-do-not-lock-laya-or-rls.md): Laya 保留为候选 encoder/静态基线，RLS 保留为强基线，最终创新机制和 backbone 待真实闭环与判别实验。
- [0013 — Freeze the minimal symbol boundary for online selection](0013-minimal-symbol-boundary.md): use a seven-item selector/tool kernel and an eight-item peer-judged role extension with explicit judge identity; add hidden state only when data requires it.
- [0014 — Treat the linear associative recurrence as a validated kernel, not the final method](0014-linear-associative-smoke-gate.md): the recurrence is executable and cheaper than dense RLS in a local probe, but its selection gain is negligible, so keep it as a baseline pending a stronger feature/state design.
- [0015 — Select before execution and bind later assignment](0015-select-before-execution-and-bind-later-assignment.md): make peer choice before work begins, grade the actual consumer output, and require later assignment plus propensity to be consumed by the next selection.
- [0016 — 持续目标与小任务复核](0016-persistent-aamas-goal-and-small-task-review.md): 持续推进 N00–N05，每个小任务核对故事、方法与证据，GPU 实验使用星云 A800，题目摘要作为内部研究草稿同步形成。
- [0017 — N02 开发接入评分范围](0017-n02-development-scoring-scope.md): 原严格资格门仍开放；两个真实接入实例只用隔离 consumer 行为分，保留非对抗假设与独立交付质量未测边界。
- [0018 — 一次最终生成配置验证](0018-one-final-bounded-generation-configuration-test.md): 显式修订已触发的v2止损，关闭thinking验证剩余接入机会；跨版最多4次，失败不再生成v4。
- [0019 — 判断与责任结果分开](0019-separate-judgment-from-responsibility-outcomes.md): 正常集成不当上游缺陷；判断、实际修改、原交付检查、最终质量及成本分别记录，旧repair映射不再默认作正确性标签。
- [0020 — PIPE3 作为第二任务 root 的条件性主候选](0020-pipe3-primary-conditional-candidate.md): 父进程四格控制矩阵可分离 producer 质量、recipient 自有工作和 sink adoption；进入下一资格门，不等于 benchmark 冻结。
- [0021 — 独立仓库与 OSS 边界](0021-dedicated-repository-and-oss-boundary.md): earning-roles 使用独立 GitLab 仓库和 `jingwu/earning-roles/` OSS 前缀；benchmark 资产与前缀保持不变。
- [0022 — 论文主线、候选机制与证据门](0022-paper-mainline-method-and-evaluation-contract.md): 将论文收敛到 situated judgment→role evidence→future responsibility，RARE 仅作为待验证候选机制，明确强基线与证据门。
- [0023 — PIPE3 前置资格通过但不冻结 benchmark](0023-pipe3-preflight-qualification.md): seed 0/1/2 的任务契约、隐藏评分边界、写权限和账本顺序通过；真实执行、生产安全与最终 benchmark 资格仍开放。
- [0024 — 收窄 PIPE3 前置检查结论](0024-narrow-pipe3-preflight-conclusion.md): 0023 被独立复核收窄为静态契约夹具和 listed canary；任务文本泄露答案，真实 payload/scorer/ledger 仍未验证。
- [0025 — 单 producer payload 的 IPC 可见性探针通过](0025-single-payload-ipc-probe.md): 一个去 oracle producer payload 通过 sandbox RPC，operator-only ledger 读取被拒；recipient、真实 runner、scorer 和账本回放仍未验证。
- [0026 — Goal 标准不可因实验失败自动降级](0026-goal-change-control.md): Goal v1.0 是唯一目标标准；每个 task report 必须逐条对照，目标修改必须由用户明确同意并新建 ADR。
- [0027 — recipient payload 与 selected delivery 的 IPC 探针通过](0027-recipient-delivery-ipc-probe.md): recipient payload、delivery digest/allowlist 和 operator-read denial 通过有界 sandbox RPC；真实 agent/scorer/ledger 仍未验证。
- [0028 — parent-side ledger replay gate](0028-parent-side-ledger-replay-gate.md): 在训练/评分消费前验证 hash chain、因果顺序、唯一性和完整性；不完整链只能显式标为 UNKNOWN。
- [0029 — runner replay before update](0029-runner-replay-before-update.md): 真实 runner 在 role update 与 episode summary 前调用 parent replay gate；中间态保持 UNKNOWN，非法链停止。
- [0030 — unknown scorer boundary](0030-unknown-scorer-boundary.md): scorer 超时、权限、传输、非法 JSON 或覆盖不完整时只能是 UNKNOWN，不产生 label/evidence/update。
- [0031 — independent scorer IPC preflight](0031-independent-scorer-ipc-preflight.md): scorer 的 private truth 留在独立 worker，candidate 只能拿公开请求；delivery、ledger 与 response digest 分开记录。
- [0032 — producer score separate from recipient outcome](0032-producer-score-separate-from-recipient-outcome.md): producer delivery quality 与 recipient integration outcome 分开计量。
- [0033 — correct independent scorer discrepancy](0033-correct-independent-scorer-discrepancy.md): tuple/list 实现错误导致的旧 scorer 差异被撤回；保留因果归因分离决定。
- [0034 — benchmark/baseline freeze gate](0034-benchmark-baseline-freeze-gate.md): 在两个合格 root、同信息 baseline、manifest 和停止规则通过前，不冻结 benchmark、不启动新 API/A800。
- [0035 — candidate-origin failure labels](0035-candidate-origin-failure-label.md): 将可归因的候选导入/交付失败标为 `FAIL/0`，与 scorer/环境不可观测的 `UNKNOWN` 分离；历史结果不回写。
- [0036 — PIPE3 producer/processor boundary](0036-pipe3-producer-processor-boundary.md): producer 只负责语义 JSON 交付与严格时间戳；processor 的 envelope/编码属于独立 recipient/adoption 目标。
- [0037 — 论文主线、证据选择与创新点的不可降级约束](0037-research-quality-and-mainline-invariants.md): 历史版本，已由 0038 替代。
- [0038 — 决议文件治理与研究主线硬约束](0038-decision-record-governance-and-research-invariants.md): 统一规定决议归档、双重确认、故事线、benchmark/baseline 和创新点的不可静默降级标准。
- [0039 — 研究主文档与决议文件的职责边界](0039-canonical-research-documents-and-decision-boundary.md): 六类研究文档各自只保留一个 active 版本；决议只记录小的已对齐选择，不复制研究主文档。
- [0040 — 组合机制的对外创新定位与内部验证](0040-integrated-mechanism-public-positioning.md)：正文呈现有机整体机制，内部用匹配组合、消融和交互效应验证其是否产生新系统性质。
- [0041 — 选择 Earning Roles 工作标题](0041-select-earning-roles-title.md)：确认当前 pre-results/proposal 使用 `Earning Roles: Self-Evolving Responsibility from Situated Peer Judgments`，不改变 Goal 或科学证据边界。
