# docs/user/decisions

User decision records and external-operation summaries.

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
