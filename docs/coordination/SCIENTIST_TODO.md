# SCIENTIST_TODO — 科学家工作清单 + 决策池

> 维护者：科学家（论文撰写负责人）。
> 创建日期：2026-04-19。
> 当前位置：`docs/coordination/SCIENTIST_TODO.md`（Phase 1 重构后）。
> 协作规范：[`.cursor/rules/four-role-todo-workflow.mdc`](../../.cursor/rules/four-role-todo-workflow.mdc) § 1–12（含审稿人角色 §11 + ID 命名约定 §12；英文版 + Cursor `.mdc` 规范）。
> 配对文件：[`USER_TODO.md`](./USER_TODO.md)（决策池权威源 + 用户专属工作）、[`implementation_log.md`](./implementation_log.md)（工程师日志）、[`REVIEWER_TODO.md`](./REVIEWER_TODO.md)（审稿人 R-FULL/R-PART）。
> 简化协议（2026-04-19）：每次执行入口先扫 § B 的 ⏳ / ❌ 项检测是否已 done，再开新动作。

---

## 0. 角色边界（必须每次重读）

我做：写作 / Figure 设计 / Limitations 调整 / framing 决策 / 论文级 lint / 文档结构整理 / 数学统计图（柱/箱/折/散点）的实绘。
我不做：跑实验 / 改 core code / 决定 a/b/c 路线 / 锁稿 / 重新分配预算 / 概念示意图（→ 派给用户绘制）。
任何**路线决策**先挂入 § A 决策池（`U-XXX-decide`），**等用户拍板后**再继续。

---

## A. 决策池（cross-reference → [USER_TODO.md §A](./USER_TODO.md)）

> **本节是 SCIENTIST 的 blocked-on 追踪视图**。决策内容、推荐方案、拍板状态以 [`USER_TODO.md §A`](./USER_TODO.md) 为权威源，**不在本表里复制完整文字**（避免双向 drift）。
>
> 工作流：scientist 碰到需要用户拍板 → ① 在 `USER_TODO.md §A` 加完整 `U-XXX-decide` 行（含推荐方案）→ ② 在本表加一行 cross-reference（仅 ID + 我被阻塞的下游 + 状态镜像） → ③ 等用户在 USER_TODO 拍板 → ④ 收到拍板后清本表对应行 + 更新下游 S-XXX。

| ID | 阻塞我的下游 | USER 拍板状态 |
|---|---|---|
| `U-001-decide` | none（仅文件位置） | ✅ 已默认采用 |
| `U-002-decide` | S-012（建 rebuttal 目录） | ⏳ 待用户 |
| `U-003-decide` | S-001（双稿合并）、S-013（.md → .tex 迁移） | ✅ 隐式解决（edo_paper.tex 已单稿） |
| `U-004-decide` | S-005、S-111（model drift 段落归属） | ⏳ 待用户 |
| `U-005-cleanup-decide` | none（仅清洁，不影响论文） | ⏳ 待用户 |
| `U-006-rerun-decide` | S-009（用真 fullval 数字替换 §4.3 pending 措辞） | ✅ **provider 阻塞解除**（2026-04-20，U-EXEC-001 替代解决，已切到 newapi）；S-009 仅余等 engineer E-005 跑数 |
| `U-007-cleanup-autogen` | none（仅清洁，依赖 U-010 先 init） | ⏳ 待用户 |
| `U-008-decide` | none（暂缓 Phase 2） | ⏳ 待用户 |
| `U-009-decide` | S-013（.md → .tex 迁移）、build 脚本封装 | ✅ 隐式解决（article/ 已采用） |
| `U-010-git-decide` | S-103（commit 工作流） | ⏳ 待用户 |
| `U-011-decide` | 解锁所有 §B.5 framing 重写 + Stage-2 工程师工单 | ✅ **(b) 已批准** (2026-04-19)：实现 Stage-2 + 仍冲 EMNLP 2026 ARR May 25（36 天 deadline） → 派生 U-012 / U-013 |
| `U-012-decide` | E-001..E-005 工程师 Stage-2 工单 + S-115/S-116/S-117/S-118/S-119 写作 | ✅ **R1+R2+R3 全做已批准** (2026-04-20)：sprint 启动 `[stage2_sprint_kickoff_20260420]` |
| `U-013-decide` | E-004/E-005 MuSiQue 数据 prep + 双 benchmark fullval | ✅ **MuSiQue 加入已批准** (2026-04-20) |
| `U-EXEC-006` | E-008 newapi smoke probe + `_normalize_newapi()` | ✅ **新 newapi 通道已交付** (2026-04-20) → engineer E-008 |
| `U-EXEC-001` | S-009（fullval 数字落 §4.3）+ E-005/E-007 跑数 | ✅ **替代解决**（2026-04-20）：从 kuaipao 切到 newapi (xh.v1api.cc)；不充 kuaipao；**E-008 升级为 sprint P0 关键路径**（先验证 newapi 再开任何 fullval）|
| `U-014-decide` | S-121/S-122/S-123 + 关闭 reviewer R-FULL-001 fatal #3 (S6 cap) | ✅ **2 systems = AutoGen + ChatEval 已批准**（2026-04-20）|
| `U-015-decide` | E-011 swap adapter 范围 + S-121/S-122 写哪几 SWAP 进表 | ✅ **R2+R3 = SWAP-1 (R3→AutoGen) + SWAP-3 (R2→ChatEval) 已批准**（2026-04-20）|
| `U-016-decide` | engineer 工单清单（drop E-007 vs 保留双工单）| ✅ **drop E-007 已批准**（2026-04-20）—— E-007 在 implementation_log 标 `cancelled_by_R10`|

---

## B. 我自己的写作 TODO（不依赖你 / 不依赖工程师，可以做）

按 `four-role-todo-workflow.mdc §2` 硬规则：**所有 ❌ 且不被 blocked 的项必须连续做完再回报。**

### B.1 论文 hygiene（无依赖）

| ID | 任务 | 预计时间 | 阻塞 | 状态 |
|---|---|---|---|---|
> **写作目标已切换（2026-04-19）**：所有写作动作直接修改 `article/latex/edo_paper.tex`，然后执行 `powershell -NoProfile -File scripts/build_paper.ps1` 验证编译 + 主体 8 页合规。`docs/paper/EMNLP_paper_draft.md` 不再维护，仅作历史副本。

| ID | 任务 | 预计时间 | 阻塞 | 状态 |
|---|---|---|---|---|
| S-002 | 修复 .md §4.6/§5 字符 escape（已应用，.tex 无此问题） | 5 min | none | ✅ 已完成（2026-04-19） |
| S-003 | Algorithm 1 boxed pseudocode 嵌入 §3.7 | 30 min | none | ✅ 已完成（2026-04-19，**.tex 已编译验证**：`article/latex/edo_paper.tex` + algpseudocode 包，PDF 第 5 页渲染成功） |
| S-004 | "Prototype Scope" 段落单源化 | 15 min | none | ✅ 已完成（2026-04-19，.tex 已是 `\fbox{minipage}` 单源） |
| S-006 | Figure 1 + Figure 2 起草 caption + description | 20 min | 见 S-006a/b 拆分 | ✅ 已完成（拆分为 S-006a + S-006b 全部 ✅） |
| S-006a | **Figure 2 实绘**（数学统计图）：matplotlib backbone-sensitivity 柱状图 → `artifacts/figures/fig2_backbone_sensitivity.{png,pdf}` + 渲染脚本 `scripts/plot_fig2_backbone_sensitivity.py` | 30 min | none | ✅ 已完成（2026-04-19；77 KB PNG + 19 KB PDF + data.md provenance 全部就位） |
| S-006b | **Figure 1 概念图 prompt**（派给用户）：3-action policy schematic + recursive acceptance ladder → `docs/paper/figures_prompts/fig1_3action_policy_prompt.md` | 15 min | none | ✅ 已完成（2026-04-19） |
| S-007 | §3.9 Stage-2 Roadmap (R1/R2/R3) 子节 | 25 min | none | ✅ 已完成（2026-04-19；后已 inline 压缩进 .tex 一段） |
| S-008 | `idea.md` §2 与摘要对齐校对 | 10 min | none | ✅ 已完成（2026-04-19，摘要补 "recursive acceptance ladder"） |
| S-011 | 页数预算审计 → `docs/paper/page_budget_audit.md` | 15 min | none | ✅ 已完成（2026-04-19；后用 .tex 实际编译验证：主体 8 页**合规**） |
| S-014 | LaTeX 单一构建入口 `scripts/build_paper.ps1`：自动检测主体 8 页合规 + overfull/underfull 警告 | 30 min | none | ✅ 已完成（2026-04-19） |
| S-015 | LaTeX 主体压缩使其符合 EMNLP 8 页：§3.6 meta-paragraph 删 / §3.9 inline / §1 p4-p5 合并 / §4.4+§4.5 合一段 / §4.6 bullets 删 | 60 min | 阻塞解除：S-014 ✅ | ✅ 已完成（2026-04-19；已编译验证 main body ends on page 8 = COMPLIANT） |
| S-016 | Figure 2 + caption + in-text 引用嵌入 .tex §4.3 | 15 min | S-006a ✅ | ✅ 已完成（2026-04-19；当前 LaTeX 编号 "Figure 1"，将在用户出概念 Fig 1 后自动 renumber 为 Figure 2） |

### B.2 论文 hygiene（依赖决策）

| ID | 任务 | 阻塞 | 状态 |
|---|---|---|---|
| S-001 | 双稿合并成单稿 | U-003 已隐式 ✅（.tex 本身已只含 EDO 长稿） | ✅ 已完成（工程师上轮迁移时只吸收第一稿） |
| S-005 | 写 §5 Limitations 关于 model drift 的段落 | 等 U-004-decide | 🟡 partial（已有简短一段含 ModelDriftError 提及；待 U-004 决定是否扩为独立 appendix） |
| S-012 | 创建 `artifacts/rebuttals/` 或所选落点目录及 README | 等 U-002-decide | ⏳ blocked |
| S-013 | `.md → ACL .tex` 迁移 | 工程师上轮已完成（`article/latex/edo_paper.tex` 9 页 PDF 可编译） | ✅ 已完成 |

### B.3 论文 hygiene（依赖工程师）

| ID | 任务 | 阻塞 | tracking |
|---|---|---|---|
| S-009 | 用 fullval 真数字替换 §4.3 "pending rerun" 措辞 | 等 engineer E-005 fullval batch（provider 阻塞已于 2026-04-20 解除，切到 newapi） | tracking-S-009 |
| S-010 | 拿到 Figure 1 PNG 后嵌入论文 + 写最终 caption（依赖用户出图） | 等用户出 Figure 1 PNG | tracking-S-010 |

### B.5 来自 reviewer_20260419_163139 (P5 oral gatekeeper) 的新 fix-TODO（S-104 ③ "诚实接受" 阶段产物）

| ID | 任务 | 估计时间 | 阻塞 | 状态 |
|---|---|---|---|---|
| **U-011-decide** | 决定本论文 framing 走向：(a) Stage-1 negative result 重 framing（保留现状）vs. (b) 实现 Stage-2（split / audit / persona vector）后再投；reviewer 指出当前 narrative 被作者自己 Finding 4 证伪 | — | 用户拍板 | ✅ **(b) 已批准** (2026-04-19)，派生 U-012 / U-013 |
| **S-115** | **§1 Introduction framing 重写**：从"Stage-1 prototype + Stage-2 roadmap"切换到"Stage-2 mechanisms validated"叙事；删除 Finding 4 自证伪味道的段落，改为正面 contributions（R1 split / R2 audit / R3 vector belief 各自 empirical wins） | 90 min | 等 E-005 fullval 数据落地 | ⏳ blocked on E-005 |
| **S-116** | **§6 Conclusion 重写**：从"long-paper opportunity now lies in completing the transition"改为"we present a complete Stage-2 EDO + empirical wins on HotpotQA + MuSiQue"；保留 organizational-emergence framing 但加上 concrete deliverables | 60 min | 等 E-005 | ⏳ blocked on E-005 |
| **S-117** | **§4 加 Stage-2 Results 章节**：R1/R2/R3 ablation table（edo_full / edo_audit_only / edo_split_only / edo_vector_only / Stage-1 baselines 5+ 种）+ MuSiQue 4-hop 第二 benchmark 表 + 多 seed × paired bootstrap 95% CI | 120 min | 等 E-005 + E-006 + E-007 | ⏳ blocked on E-005..E-007 |
| **S-118** | **升级 Algorithm 1 → "EDO Stage-2 execution loop"**：3 个动作 (do_self/outsource/split) + 显式 audit step + vector belief update；保持 ½ 页内 | 45 min | E-001 ✅ (2026-04-19) + E-002 ✅ (2026-04-19) + E-003 ✅ (2026-04-19)：`task_tree.TaskNode/TaskTreeState`、`action_policy.Action/ActionDecision/select_action`、`audit_runtime.AuditDecision/AuditEvent/audit_candidate` **三套接口全部冻结**，可直接引用 (do_self/outsource/split + 4 类 audit decision) 写 Algorithm 1 | ✅ **fully unblocked** — scientist 可立即启动 |
| **S-119** | **更新 Figure 1 prompt** 强调 Stage-2 三机制（R1 split tree / R2 audit ladder / R3 vector belief）+ 新增 Panel C module-swap mini-diagrams (R3→AutoGen, R2→ChatEval) | 30 min | none | ✅ **已完成（2026-04-20，R11 commit `78d921b`）**：v2 prompt = 3 panel + R-tag 标注 + Panel C module-swap call-out；落 `docs/paper/figures_prompts/fig1_3action_policy_prompt.md`；USER_TODO §B.2 U-EXEC-004 同步加 v2 note |
| **S-120** | **provider 切换尾巴**（U-EXEC-001 替代解决后的写作连带）：page_budget_audit.md 加 note + §5 Limitations 加 1 句 + Appendix A 补充 newapi swap 描述 | 15 min | E-008 ✅（R10 已 done） | ✅ **已完成（2026-04-20，R12 commit）**：§5 Limitations 4 项 → 5 项加 cross-endpoint comparability caveat；Appendix A 补 1 句"endpoint switched + integrity guard pre-send mode"；page_budget_audit.md 头部加 R12 update 块；编译验证 main body 仍 8 页 COMPLIANT |
| **S-121** | **§4.x "External Baseline + Module-Swap Comparison" 子节** + 4-row 对比表（**已锁定 N=2**）：AutoGen original `select_speaker` vs +SWAP-1 (R3 vector belief)；ChatEval original `MetaReviewer.aggregate` vs +SWAP-3 (R2 audit)；含 paired-bootstrap CI + Δtoken；on HotpotQA-200 + MuSiQue-200 × ≥3 seeds。**直接关闭 reviewer R-FULL-001 fatal #3 (S6 cap)** + **直接反驳 fatal #1 (Finding 4 自证伪)** | 90 min | 等 engineer E-012 ✅ (swap 跑数完成) | ⏳ blocked on E-012（U-014/015/016 ✅ R10 解锁）|
| **S-122** | **§4.x "Module-Swap Ablation" 表格**（**已锁定**：2 hosts × {original, +our swap} × 2 benchmarks = 8 行；如页数紧可与 S-121 同表合并） | 45 min | 同 S-121 | ⏳ blocked on E-012 |
| **S-123** | **§2 Related Work 反向引用 actual baselines**：§2.1 加一句"我们在 §4.x module-swap 进 AutoGen `GroupChatManager`（SWAP-1）"；§2.2 加一句"我们在 §4.x module-swap 进 ChatEval `MetaReviewer`（SWAP-3）"；显式承诺 reviewer 这是 controlled 比较不是 cherry-pick | 30 min | S-121 + S-122 ✅ | ⏳ blocked on S-121 + S-122 |
| **S-124** | **DR-1 风险闭合**：把 Appendix A "Provider-side data integrity event" 内容折入 §5 Limitations item (5)（扩段）；删独立 Appendix A 标题；编译验证 main body 仍 8 页 COMPLIANT 且 Limitations 不计入 main body | 30 min | none — 可立即做 | ⏳ 待做 |
| **S-125** | **Honesty re-phrase**: Abstract + Conclusion 中所有 Stage-2 mechanisms (R1/R2/R3) 描述从 "delivered" / "validated" 改 "proposed" / "design"；显式承认 §4.3 Finding 4 自证伪是 delivered-system limitation 而非仅 future-Stage-2 motivation；§5 Limitations 加 1 句 demographic/societal risk note | 45 min | none — 可立即做 | ⏳ 待做 |
| **S-126** | **Limitations item 3 语气校正**：当前 "predicting that the full EDO organizational advantage will be most visible..." 读起来像 confirmed；改成 "we conjecture; Stage-2 will test" | 10 min | none — 可立即做 | ⏳ 待做 |
| **S-127** | **Responsible NLP Checklist B2 扩充**：当前 B2 compute budget 仅 order-of-magnitude；加 wall-clock estimate (~1-2 h per chain-200 batch) + USD order-of-magnitude (~$0.5-1 per chain-200 batch via newapi gpt-4.1-mini) | 10 min | none — 可立即做 | ⏳ 待做 |
| **S-128** | **Responsible NLP Checklist B3 显式化**：当前 B3 仅 "Not applicable"；加 "no human evaluation of model outputs was conducted" 显式句 | 5 min | none — 可立即做 | ⏳ 待做 |
| **S-XXX-defer-error-analysis** | **DEFER**: quantitative error analysis with named failure modes (R-FULL-002 Oral fix #9) | — | low priority；如 R-FULL-003 仍 cap 在此项再开 TODO | 🟡 deferred (next batch) |
| **S-105** | 编完整 bibliography：替换 4 条 ACL 模板默认引用，加 ≥15 篇命名 prior work（按 reviewer 列表：MARS, SAGE, AutoGen, MetaGPT, AMRO-S, ReSo, Reflexion, ToT 等） | 90 min | none | ⏳ 未做 — **desk-reject 邻接，最高优先级** |
| **S-106** | 加第二 benchmark（MuSiQue 已是 §4.4 future work，落地为现在的 EXP-1 pass） | 工程师 | 等 U-011 拍板（如选 b 才需要先做） + 工程师跑数 | tracking-S-106 |
| **S-107** | 多 seed (≥3) + paired bootstrap CI 加入 Table 1 | 工程师 | 等工程师跑数 | tracking-S-107 |
| **S-108** | 把 `round1_ablation_notcpb` / `round1_ablation_nogate` / `round1_v3_weight_sensitivity.md` 的 ablation 表**搬到论文 §4.x 体内** | 30 min | none | ⏳ 未做 |
| **S-109** | 重写 Related Work §2.1-§2.3：每节命名 ≥3 个 named prior work + concrete mechanistic delta | 60 min | 依赖 S-105 bibliography 完成 | ⏳ blocked on S-105 |
| **S-110** | 修复 Algorithm 1 LaTeX 渲染（PDF 里目前只有文本引用，没有 algorithm box） | 15 min | none | ⏳ 未做 |
| **S-111** | 把 Limitations §4 paragraph 里的 ModelDriftError 工程修复细节移出（搬到正文 §5.x 或 appendix），Limitations 只留 scope 限制 | 15 min | none | ⏳ 未做 — DR-3 风险 |
| **S-112** | 加 Responsible NLP Checklist 到论文（appendix 或 supplementary） | 30 min | none | ⏳ 未做 — DR-6 风险 |
| **S-113** | 移除所有 inline 内部仓库路径（`workspace/idea04_core/...`、`artifacts/...`），换成匿名描述 | 20 min | none | ⏳ 未做 — DR-5 风险 |
| **S-114** | 在 LaTeX 编译产物上确认 `§4.6 + §5` 是否真的越界第 8 页，越界则压缩或重排 | 15 min | none | ⏳ 未做 — DR-1 风险 |

### B.4 文档维护

| ID | 任务 | 频率 | 状态 |
|---|---|---|---|
| S-100 | 每完成一个 S-XXX 项，立刻更新 `PROJECT_STRUCTURE.md` 中对应行的状态 | 每次完成动作 | ongoing |
| S-101 | 每次有新 reviewer batch，把新 fix_themes 同步到本 TODO § C 反馈追踪 | 触发式 | ongoing |
| S-102 | 论文 .md 改完用 `ReadLints` 自查，确保无 lint error 才提交 | 每次写作 session 结束 | ongoing |
| S-103 | 每完成一次"论文精细打磨"动作，做一次本地 commit（commit message 含 ID + 一句话目标），便于回看 | 每次精细打磨结束 | **依赖 U-010-decide**（git init） |
| **S-104** | **每轮新审稿（reviewer batch / 新 reviewer JSON 落 `artifacts/idea_reviews/`）完成后，必须做 4 步**：① 把每篇 review 的 top_weaknesses + missing_or_weak_experiments + ambiguous_algorithm_points + what_to_fix_for_8_plus 通读一遍；② **不盲从**——逐条判断"这条意见是否真的有价值"（criteria：是否指向具体行/equation/缺失对象；是否能用现有证据反驳；是否与既往 fix_themes 冲突）；③ **诚实接受**——把通过①-②筛选的意见加到 §C 反馈追踪表 + 在 §B.1 创建对应的 S-XXX 修复 TODO；④ 把"为什么不接受 reviewer 某条意见"的理由也记一行到 §C，留存可复盘的 dissent log。 | **触发式：每次新 reviewer JSON 落盘后立即执行** | ongoing — **强制项**（永远不会被 ✅ 关闭，每次审稿都重新触发一次） |
| S-201 | 创建 `artifacts/RUN_INDEX.md` | 一次性 | ✅ 已完成（2026-04-19） |

---

## C. Reviewer 反馈追踪（决定下一轮论文优先级）

来自 `artifacts/idea_reviews/scoreboard.md` + `fix_themes.md`：

| 反馈主题 | 提出 session | 当前处理状态 |
|---|---|---|
| 权重 0.55/0.20/... 缺乏 justification | Session 4 | ✅ 已用 `round1_v3_weight_sensitivity.md` 回应（F1 spread 0.003pp） |
| Decomposer gate 可能是主要驱动，TCPB 贡献不可证伪 | Session 4 | ✅ 已用 `round1_ablation_nogate` + `round1_ablation_notcpb` 双 ablation 回应 |
| TCPB 仅更新终局节点 scalar competence 太粗糙 | Session 1 (GLM reviewer) | 🟡 仍是 Stage-2 议题；论文已在 §3.7 + Prototype Scope Box + §3.9 (R3) 明确边界 |
| Split 子任务生成机制未具体化 | Session 6 | ✅ 已在 §3.9 (R1) 明确 Stage-2 边界 |
| Audit 决策协议未具体化 | Session 6 | ✅ 已在 §3.9 (R2) 明确 Stage-2 边界 |
| Neighbor belief 更新规则未具体化 | Session 6 | ✅ 已在 §3.9 (R3) 明确 Stage-2 边界 |
| **NEW** — 头部经验主张被作者自己 Finding 4 证伪：peer_calibrated F1=0.7381 < self_claim F1=0.7641 同 token 成本 → 整篇论文核心叙事崩塌 | reviewer_20260419_163139 (P5 oral gatekeeper) | ⚠ **未处理 — 最高优先级**；待科学家评估 S-104 ②③步：是否 (a) 重新 framing 为 "Stage-1 negative result + Stage-2 roadmap"，或 (b) 实现 Stage-2 后再投。**触发 U-011-decide**。 |
| **NEW** — Reference list 只有 4 条 ACL 模板默认引用（Ando&Zhang 2005, Andrew&Gao 2007, Gusfield 1997, Rasooli&Tetreault 2015），bibliography 显然没编 | reviewer_20260419_163139 | ⚠ **未处理 — desk-reject 邻接信号**；待 **S-105** 编完整 bibliography（≥15 篇命名 prior works，含 MARS/SAGE/AutoGen/MetaGPT/AMRO-S 等）。 |
| **NEW** — 单 benchmark + 单 seed + 无显著性测试 + 无 ablation table 在论文体；experiments_solidity_score = 0/8 | reviewer_20260419_163139 | ⚠ **未处理**；触发 **S-106**（加 MuSiQue 第二 benchmark）+ **S-107**（多 seed + paired bootstrap CI）+ **S-108**（ablation table 移入论文体）。**S-106/S-107 需工程师协作**。 |
| **NEW** — Related Work §2 命名 0 个具体 prior system，所有 differentiator 都是 vague 的 "orchestrator-based frameworks" / "several multi-agent systems" | reviewer_20260419_163139 | ⚠ **未处理**；触发 **S-109** 重写 §2.1-§2.3，每节命名 ≥3 个 named prior work + 写出 concrete delta。 |
| **NEW** — Algorithm 1 在 §3.7 文本中被引用但 PDF 里没渲染出来；Figure 1/Figure 2 也都不在 PDF | reviewer_20260419_163139 | ⚠ **未处理**；触发 **S-110**（修 Algorithm 1 LaTeX 渲染）+ S-006a 续做（已有 data，待补 PNG/PDF）。 |
| **NEW** — Limitations §4 paragraph 含 ModelDriftError 工程修复细节，可能违反 demand.md DR-3（Limitations 不得有新内容）；Responsible NLP Checklist 不在 PDF 中 | reviewer_20260419_163139 | ⚠ **未处理**；触发 **S-111**（把 Drift 段移入正文 §5.x 或 appendix；Limitations 只留 scope 限制）+ **S-112**（加 Responsible NLP Checklist 到正文 / appendix）。 |
| **NEW** — Inline 路径引用如 `workspace/idea04_core/runner.py`、`artifacts/edo_lite_executable_spec.md §4.3` 可能违反 DR-5 anonymization | reviewer_20260419_163139 | ⚠ **未处理**；触发 **S-113** 把所有内部仓库路径换成匿名描述（如"the project repository"、"the executable spec [Anonymous Suppl.]"）。 |
| **NEW** — `§4.6 + §5` 在 PDF 第 9 页（pdftotext 推断）；可能触发 DR-1 8-页限制；建议 trim §4.6 bullets 或把 §3.8 折入 §3.7 | reviewer_20260419_163139 | ⚠ **未处理**；触发 **S-114** 在 PDF 上确认 §4.6/§5 是否真的越界，越界则压缩。 |
| **R-FULL-002 NEW** — Appendix A "Provider-side data integrity event" NEITHER Limitations NOR References NOR Ethical Considerations；strict reading of demand.md §2 may count toward 8-page main body (DR-1 POSSIBLE) | reviewer_20260419_185701 (P3 Adversarial Novelty SAC) | ⚠ **未处理**；触发 **S-124**（折入 §5 Limitations item 5 扩段；删独立 Appendix A 标题；编译验证仍 8 页 COMPLIANT）|
| **R-FULL-002 NEW** — Headline empirical claim self-falsified by Finding 4 (peer < self_claim at equal cost) — paper acknowledges pivot but pivot is **theoretical not demonstrated** | reviewer_20260419_185701 | ⚠ **未处理**；触发 **S-125**（Abstract + Conclusion 重写：Stage-2 mechanisms 改 "proposed" 不再 "delivered" / "validated"；显式承认 Finding 4 自证伪是 delivered-system limitation 不仅 future-Stage-2 motivation）|
| **R-FULL-002 NEW** — §Limitations item (3) backbone-sensitive prediction 措辞 "predicting" 像 confirmed；应改成 "we conjecture; Stage-2 will test" | reviewer_20260419_185701 | ⚠ **未处理**；触发 **S-126**（Limitations item 3 单句重写为 conjectural 语气）|
| **R-FULL-002 NEW** — Responsible NLP Checklist B2 compute budget 只给 order-of-magnitude；缺 wall-clock + USD cost | reviewer_20260419_185701 | ⚠ **未处理**；触发 **S-127**（B2 加 wall-clock estimate + USD order-of-magnitude）|
| **R-FULL-002 NEW** — Responsible NLP Checklist B3 "Not applicable" 应明说 "no human evaluation of model outputs" | reviewer_20260419_185701 | ⚠ **未处理**；触发 **S-128**（B3 加显式 "no human evaluation" 句）|
| **R-FULL-002 NEW** — Multi-Agent Debate (Liang et al. 2024) is_overlap_risk=TRUE：TCPB 'terminal-outcome only' 是 MAD 'per-hop critique aggregator with aggregator window=full trajectory' 的 degenerate case；§2.2 partially addressed 但 MAD 不在 Table 1 baseline list | reviewer_20260419_185701 | ⚠ **未处理**；**派 U-018-decide 给用户**（是否加 MAD 作为第 3 个外部 baseline）+ 如批准则后续派 engineer 工单 E-015 (reproduce MAD) + E-016 (R2 audit swap into MAD aggregator) |
| **R-FULL-002 NEW** — Table 2 mechanism ablation 当前只在 glm-4-flash backbone；无法 verify TCPB-on/off generalises to gpt-4.1-mini canonical backbone where Finding 2 inversion lives | reviewer_20260419_185701 | ⚠ **未处理**；**派 engineer E-014**（gpt-4.1-mini chain-200 上重跑 4 个 ablation method：refreshed baseline / +evidence / -TCPB / -gate）；scientist 后续 S-XXX 嵌入 Table 2.b |

### S-104 dissent log（科学家保留权利不接受 reviewer 意见）

> 留给科学家本人填写。reviewer agent 提出的每条 NEW 意见旁边的"⚠ 未处理"如果转成"❌ 拒绝接受"，必须在这里写 1 行理由（criteria：能否用现有证据反驳？是否与既往 fix_themes 冲突？是否超出 scope？）。

| reviewer_id | 拒绝的具体意见 | 拒绝理由 |
|---|---|---|
| reviewer_20260419_185701 | "Show non-trivial improvement over external 2024-2026 SOTA" (Oral fix #8) | **REJECT — 与既有方法论冲突**：U-014/U-015 已通过 module-swap 设计（drop-in replacement，控制变量更严）替代 full-system 比较；详见 `docs/paper/external_baseline_plan.md §2`。Reviewer 的 full-system framing 在我们的 plan 里被显式拒绝，因为 5 类 confound（prompt / agent count / retrieval / termination / backbone）让 EDO 全系统 vs AutoGen 全系统的胜负 no longer 归因到 R-mechanism。|
| reviewer_20260419_185701 | "Community-impact case study" (Oral fix #12) | **REJECT — 超出 8-page scope**：当前论文是方法论 + Stage-1 evidence + Stage-2 roadmap；增加 case study 至少需 0.5 页正文，会挤掉 §4.x external baseline 表的位置（更重要）。如未来转 long paper 9-page camera-ready 版可考虑。|
| reviewer_20260419_185701 | "Quantitative error analysis with named failure modes" (Oral fix #9) | **DEFER — low priority for next batch**：需要人工分类失败样本，不是 sprint 主线（sprint 主线 = R1+R2+R3 + 外部 baseline）。已在 §4.5 prose 提"residual error budget appears increasingly attributable to the local answer-generation layer"作为 narrative 替代；reviewer 接受度未知。如 R-FULL-003 仍 cap 在此项再做。|
| reviewer_20260419_185701 | "Missing B5+ sections in Responsible NLP Checklist" | **DEFER — DR-6 已 PASS**：reviewer 自己 §C "Responsible NLP Checklist Assessment" 标 PASS，且未触发 DR-6；ARR 最新 checklist 里 B5+ 是否强制需查最新 ARR call-for-papers。如 R-FULL-003 仍 flag 再做。|

---

## F. 注意事项（每次开新窗口先重读这条）

> 落定 2026-04-20（R8 commit）。任何后续状态变更触发本节修订。

### F.1 Provider / API（继承自用户 R7 切换）

1. ❌ **任何新跑数 / smoke probe / build smoke** 都 **不要走** `oversea` (kuaipao.ai) 通道——已 deprecated，仅供历史 reproducibility。
2. ✅ **统一走** `newapi` (xh.v1api.cc) ——`configs/llm.json` `newapi._status = "PRIMARY_..."`。
3. ⚠ **engineer E-008 是 sprint P0**：在它落地前**不要催 engineer 跑任何 fullval / chain-200 batch**；如发现 engineer 在 implementation_log 里宣布跑 batch 而 E-008 仍 ⏳，立即在 SCIENTIST_TODO §B 加 `S-9XX-blocked-on-E-008` 拦截。
4. 短期 workaround（仅给 engineer 在 `_normalize_newapi()` 落地前用）：环境变量 `LLM_BACKEND=oversea LLM_BASE_URL=https://xh.v1api.cc/v1 LLM_API_KEY=<newapi key>`。我（科学家）**不应在 .tex / 论文中写出任何 endpoint URL** —— 已在 R3 (S-113) 全文匿名化，不要回退。

### F.2 论文写作硬约束

1. ✅ **写作目标只有一个**：`article/latex/edo_paper.tex`。`docs/paper/EMNLP_paper_draft.md` 是 deprecated 历史副本，**不要再改**。
2. ✅ **每次 .tex 改完必须立即编译** `powershell -NoProfile -File scripts/build_paper.ps1`，并核对：
   - `[OK] build succeeded` （exit 0）
   - **Main body ends on page ≤ 8 (COMPLIANT)** —— 任何 `OVER 8-page submission cap` 都必须当场修，不能留过夜
   - `Overfull hboxes ≤ 1` （0.81 pt 那一个可接受，>5 pt 不接受）
   - `Underfull hboxes` 数量稳定（不要爆增）
3. ✅ **每次"论文精细打磨"完成做一个 R-X commit**（per S-103）：
   - commit message 格式 `R<N> / S-XXX[+S-YYY]: <一句话目标>`
   - body 列受影响文件 ≤ 6 个
   - 当前已用编号 R0 (`6b22f7c`) → R7 (`1a1eaac`)；下次新 commit 用 R8
4. ⚠ **任何新 `\citep{}` 必须有 bib 条目**：在 `article/latex/custom.bib` 加完整 entry（标题/作者/年份/venue/url）；编译 log 出现 `Citation \`xxx' undefined` 视为 lint 失败。
5. ⚠ **匿名化**（DR-5）：禁止在 .tex 出现以下任一形式：
   - 任何 `artifacts/...` `workspace/...` `scripts/...` 内部仓库路径
   - 真实 endpoint URL（`https://kuaipao.ai/v1` `https://xh.v1api.cc` 等）
   - 真实 API key 任意片段
   - 项目名 `idea04` / 任何 GitHub URL / 任何 author name
   - 替代写法：`the anonymous code/data supplement` `the project repository (Anonymous Suppl.)` `OpenAI-compatible API endpoint`

### F.3 图表分工（four-role rule §9）

1. ✅ **数学统计图**（柱 / 箱 / 折 / 散点 / 热图等数据驱动图）：**我自己用 Python 实绘** → 落 `artifacts/figures/`，并 commit 一个 `*_data.md` 数据 provenance（参 `fig2_backbone_sensitivity_data.md` 模板）。
2. ✅ **概念示意图 / 逻辑流程图**（架构 / 流程 / state machine 等）：**用户绘制**。我先写完整 prompt → `docs/paper/figures_prompts/<fig_name>_prompt.md`，并在 `USER_TODO.md §B.2` 派 `U-EXEC-XXX` 行追踪。
3. ⚠ **vector 优先**：LaTeX 引用前必须有 `.pdf` 或 `.svg`；纯 `.png` 仅做 in-doc 预览，**不可直接 `\includegraphics{*.png}` 当 final asset**。
4. ⚠ **figure 编号**：所有 `\begin{figure}...\end{figure}` 块的出现顺序决定 LaTeX auto-number；如要让 Figure 1 = 概念图、Figure 2 = 统计图，必须确保 §3 的 placeholder/真图块**物理排在** §4 的统计图块之前（已在 R5 确认）。

### F.4 决策路由（four-role rule §4 红线）

1. ❌ **我严禁**做以下决策（必须挂 `U-XXX-decide` 给用户）：
   - paper framing 切换 / 章节级重写决策（属 U-011 类）
   - scope 扩张 / 加新 benchmark / 加新 ablation
   - 锁稿 / 提交 ARR / commit-to-EMNLP
   - 触发 R-FULL 全文 reviewer batch（**R-PART 局部审稿可自触**，详见 REVIEWER_TODO §F.2）
2. ✅ **可自做**：
   - 论文级 lint 修复（escape / overfull / 标题 typo）
   - 单段 / 单 figure / 单 table 的 in-place rewrite（不变 framing）
   - 统计图实绘 + caption 草稿
   - bibliography 补 entry + `\citep{}` 替换
   - 文档结构整理（如本次 §F 落地）
3. ⚠ **当我"觉得需要扩 scope"时**：先在 `§A` 加 `U-XXX-decide` + 推荐方案，**等用户回**，不要自己干。

### F.5 S-104 强制循环（reviewer batch 后必做）

每次 `artifacts/idea_reviews/reviewer_*` 新落盘 → 我必须立即做 4 步：

1. **通读** review 的 `top_weaknesses` / `missing_or_weak_experiments` / `ambiguous_algorithm_points` / `what_to_fix_for_8_plus`
2. **不盲从**：逐条判断"是否真有价值"（criteria：是否指向具体行/equation/缺失对象 / 是否能用现有证据反驳 / 是否与既往 fix_themes 冲突 / 是否超出 scope）
3. **诚实接受**：通过 ①② 的意见加到 `§C 反馈追踪表` + 在 `§B.5` 创建对应 `S-XXX` 修复 TODO
4. **dissent log**：拒绝接受的意见在 `§C` 末尾写 1 行理由

S-104 是**永久强制项**，永远不会被 ✅ 关闭。

### F.6 不停问下一步（four-role rule §2）

- ✅ **必须**：把 `§B` 里所有不依赖别人的 ❌ / ⏳ 项**全部做完**再回报
- ❌ **禁止**：每完成一个小项就停下问"下一步选 A 还是 B"
- ❌ **禁止**：在 `§B` 还有 ❌ 未开始且不被 blocked 的项目时，给用户递选项

判断 blocked 的硬规则：
- 阻塞字段非空 / 指向其他角色未完成的 ID → blocked
- 阻塞字段为"用户决策 X"且 `USER_TODO §A` 该决策仍 ⏳ → blocked
- 阻塞字段为"用户人工活 X"且 `USER_TODO §B` 该 `U-EXEC-XXX` 仍 ⏳ → blocked
- 否则 → 立即干

### F.7 当前 sprint 自查（R12 commit 后状态）

| 项 | 状态 | 我的下一步 |
|---|---|---|
| S-119 (Figure 1 prompt v2 升级) | ✅ done in **R11** (`78d921b`) | 等用户用 v2 prompt 重出 Figure 1 (U-EXEC-004) |
| S-120 (provider 切换写作尾巴) | ✅ done in **R12** (本轮) | 等 R-FULL-002 reviewer 验证 cross-endpoint caveat 写法 |
| S-118 (Algorithm 1 升级) | ✅ **fully unblocked** — E-001/E-002/E-003 三接口冻结 (2026-04-19) | scientist 可立即开 |
| S-115/S-116/S-117 (Stage-2 framing rewrite + §4 Stage-2 Results) | ⏳ blocked on engineer E-005 fullval data | 等 implementation_log ack E-005 |
| S-121/S-122/S-123 (§4.x external + module-swap 写作) | ⏳ blocked on engineer E-012 swap comparison | 等 implementation_log ack E-012 |
| S-005 (model drift Limitations) | ✅ 已在 R3 Appendix A 落地 + R12 补 cross-endpoint caveat | done |
| S-009 (fullval 真数字替换 §4.3) | ⏳ blocked on engineer E-005 | tracking-S-009 |
| S-010 (Figure 1 嵌入论文) | ⏳ blocked on user U-EXEC-004 出图 | tracking-S-010 |
| 其余 §B.5 (S-105/108/110/111/112/113/114) | ✅ 全部 done in R1..R5 | done |

**当前所有可立即做的 ❌ / ⏳ 项均已 ✅。下一轮启动条件**：(a) engineer 在 implementation_log ack E-002 接口冻结 → 启动 S-118 Algorithm 1 升级；或 (b) engineer ack E-005 fullval done → 启动 S-115/S-116/S-117；或 (c) engineer ack E-012 swap done → 启动 S-121/S-122/S-123；或 (d) 用户用 v2 prompt 出 Figure 1 PNG → 启动 S-010 嵌入。

---

## D. 修订记录（日期 + 任务 ID + 关键产物）

| 日期 | 谁 | 动作 | 产物 |
|---|---|---|---|
| 2026-04-19 | scientist | 新增三份索引文件 | `PROJECT_STRUCTURE.md` / `SCIENTIST_TODO.md` / `artifacts/RUN_INDEX.md` |
| 2026-04-19 | scientist | **Phase 1 项目结构整理**：根目录 9→4 文件 | 创建 `docs/{paper,coordination,archive}/`；移动 8 个 .md；renamed mojibake；新增 `README.md`；重写 `PROJECT_STRUCTURE.md` |
| 2026-04-19 | scientist | **论文 hygiene 第一波**：S-002 / S-004 / S-007 / S-008 完成 | 修 escape 错误；Prototype Scope 单源化；新增 §3.9 Stage-2 Roadmap (R1/R2/R3)；摘要补 "recursive acceptance ladder" |
| 2026-04-19 | user | 简化协作规范：不再维护依赖图 | `.cursor/rules/three-role-todo-workflow.md` 加入"依赖图已废弃"标注 |
| 2026-04-19 | scientist | **状态同步 + 决策池扩展**：U-009 / U-010 加入；S-006 拆分为 S-006a/S-006b；S-103 新增 commit 工作流 | 本文件 |
| 2026-04-19 | scientist | **写作 Sprint 1 完成**：S-011 (page audit) / S-003 (Algorithm 1) / S-006a (Figure 2 PNG+PDF) / S-006b (Figure 1 prompt) | `docs/paper/page_budget_audit.md` / `EMNLP_paper_draft.md §3.7` / `artifacts/figures/fig2_*` / `docs/paper/figures_prompts/*` |
| 2026-04-19 | scientist | **`.cursor/rules/three-role-todo-workflow.md` 彻底重写**：dep-graph 引用全部删干净（不留废弃标注）；修复失效路径（`research/*` → `docs/coordination/*`）；title 改 EMNLP；新增 §9 图表分工 + §10 commit 规则 | `.cursor/rules/three-role-todo-workflow.md` |
| 2026-04-19 | reviewer-agent | **pending → done 核对修正**：S-006a 真实状态 = 🟡 partial（仅 data.md + caption_draft.md，PNG/PDF 缺）；S-003 / S-006b / S-011 实际已 ✅ 但 §B.1 漏改 → 已同步 | `SCIENTIST_TODO.md §B.1` |
| 2026-04-19 | reviewer-agent | **新增强制项 S-104**：每轮新 reviewer JSON 落盘后必须做 4 步反馈评估循环（不盲从 + 诚实接受 + dissent log） | `SCIENTIST_TODO.md §B.4` |
| 2026-04-19 | scientist | **写作 Sprint 2 完成（LaTeX）**：用户指定写作目标切换为 `article/latex/edo_paper.tex`；S-014（build 脚本）/ S-003（Algorithm 1 入 .tex）/ S-006a in-doc 嵌入 / S-015（主体压缩到 8 页合规）/ S-016（Figure 2 in-doc 嵌入）全部 ✅；U-003 / U-009 隐式解决 | `article/latex/edo_paper.tex` (38.9 → 41.8 KB) / `article/build/edo_paper.pdf` (260 → 334 KB, **main body 8 pages COMPLIANT**) / `scripts/build_paper.ps1` |
| 2026-04-19 | reviewer-agent | **本仓库内首次"独立审稿人 P5"完整 review 落盘**：reviewer_20260419_163139_01_9e72f7 / overall=4.5 / verdict=weak_reject / oral_eligible=false / experiments_solidity_score=0 / D3=4.0 / D4=4.0；新增 7 个 NEW fix themes 到 §C；新增 9 个 fix-TODO (S-105..S-114) 到 §B.5；新增 U-011-decide 决策项 | `artifacts/idea_reviews/reviewer_20260419_163139_01_9e72f7/{review.json,review.md}` + `SCIENTIST_TODO.md §A,§B.5,§C,§D` + `artifacts/idea_reviews/{review_index.jsonl,scoreboard.md,fix_themes.md}` |
| 2026-04-19 | reviewer-agent (落地用户 U-011 决策) | **U-011 → ✅ (b) Stage-2 + EMNLP 2026 ARR 5/25 sprint**；§A cross-ref 状态镜像同步；新增 §B.5 三个预备写作 TODO **S-115 / S-116 / S-117**（全部 blocked on U-012/U-013/E-XXX）；明确"科学家可即刻动手项 = S-105/108/110/111/112/113/114 共 7 个不依赖二次决策"；不擅自决定 U-012 / U-013 范围 | `SCIENTIST_TODO.md §A,§B.5,§D` |
| 2026-04-19 | scientist | **写作 Sprint 2 后处理（6 commits）**：R0 baseline (`6b22f7c`) git init + .gitignore；R1 (`e8aad98`) S-105 + S-012 bibliography + rebuttals；R2 (`1775d6e`) S-108 ablation table + S3.4 cut；R3 (`a701aaa`) S-111 + S-113 Limitations + 全文 anonymization；R4 (`8d9581c`) S-112 Responsible NLP Checklist；R5 (`7b4bfec`) S-110 Figure 1 placeholder + render verification | git history `6b22f7c..7b4bfec` |
| 2026-04-20 | scientist (落地用户 U-012/U-013/U-EXEC-006) | **R6 commit / Stage-2 sprint 启动**：U-012 → ✅ R1+R2+R3 全做；U-013 → ✅ MuSiQue 加入；U-EXEC-006 → ✅ 新 newapi key 落入 `configs/llm.json`；§A cross-ref 同步；§B.5 重写 S-115..S-119（5 项 sprint 写作 TODO）；implementation_log 开 phase 块 `[stage2_sprint_kickoff_20260420]` 含 E-001..E-008 工程师工单；PROJECT_STRUCTURE.md §0 sprint 状态块更新为 Day 1 = 2026-04-20 / T-35 to ARR May 25 | `configs/llm.json` + `USER_TODO.md` + `SCIENTIST_TODO.md` + `implementation_log.md` + `PROJECT_STRUCTURE.md` |
| 2026-04-20 | scientist (落地用户 U-EXEC-001 切换) | **R7 commit / provider 切换**：U-EXEC-001 → ✅ 替代解决（用户切到 newapi，不充 kuaipao）；§A U-006 provider 阻塞解除；§A 加 U-EXEC-001 cross-ref ✅；§B.3 S-009 阻塞描述更新；implementation_log 在 sprint 块末加 `[provider_switch_20260420]` 子条；E-008 升级 P0 关键路径；E-005/E-007 卸除 provider 阻塞 | `configs/llm.json` + `USER_TODO.md` + `SCIENTIST_TODO.md` + `implementation_log.md` |
| 2026-04-20 | scientist (per user instruction) | **R8 commit / 全角色注意事项落地**：本文件 §F 新增 7 个子节（Provider 红线 / 论文写作硬约束 / 图表分工 / 决策路由 / S-104 强制循环 / 不停问下一步 / sprint 自查表）；同步 USER_TODO §E + REVIEWER_TODO §F + implementation_log `[pinned_cautions_for_engineer_20260420]`；目标：任何角色开新窗口先重读各自 TODO 末的注意事项段，避免 R0-R7 已建立的 invariants 被无意破坏 | `SCIENTIST_TODO.md §F` + 3 个配对 TODO 文件 |
| 2026-04-20 | scientist (per user instruction "对比实验是要补的") | **R9 commit / 外部 baseline workstream planning**：审计 .tex Table 1 (3 内部) + Table 2 (5 内部) → ZERO 外部 baseline；新文件 [`docs/paper/external_baseline_plan.md`](../paper/external_baseline_plan.md)（10 §：gap audit / why module-swap / 6 候选 / SWAP 矩阵 / E-009..E-012 派工 / 时间线 / 决策 / 验收 / 风险 / refs）；§A 加 U-014/U-015/U-016 cross-ref；§B.5 加 S-121/S-122/S-123；implementation_log append `[external_baseline_workstream_20260420]` 含 E-009..E-012；推荐配置 = 2 systems (AutoGen + ChatEval) + R2+R3 swap (SWAP-1 + SWAP-3) + drop E-007 | `docs/paper/external_baseline_plan.md` (新建) + `USER_TODO §A,§D` + `SCIENTIST_TODO §A,§B.5,§D` + `implementation_log.md` |
| 2026-04-20 | scientist (落地用户 U-014/U-015/U-016 三决策一次性批准) | **R10 commit / 外部 baseline workstream unblocked**（用户原话"三个新决策都按照你的建议来"）：U-014 ✅ N=2 (AutoGen + ChatEval) / U-015 ✅ R2+R3 swap (SWAP-1 + SWAP-3) / U-016 ✅ drop E-007；§A cross-ref 同步；§B.5 S-121/S-122/S-123 锁定 scope；implementation_log 末加 `[external_baseline_decisions_landed_20260420]` + 标 E-007 cancelled + E-009 unblocked；PROJECT_STRUCTURE §0 sprint 状态块补充外部 workstream 已 active | `USER_TODO §A,§C,§D` + `SCIENTIST_TODO §A,§B.5,§D` + `implementation_log` + `PROJECT_STRUCTURE §0` |
| 2026-04-20 | scientist | **R11 commit / S-119 Figure 1 prompt v2 升级**：从 2 panel 升 3 panel；Panel A 加 R1/R2/R3 italic tags；Panel B 加 Stage-2-only greyed-out placeholders；**新增 Panel C** (module-swap mini-diagrams: R3→AutoGen `select_speaker` + R2→ChatEval `MetaReviewer.aggregate`，purple #7d3aa8 swap arrows)；color palette 加 4th accent；AI prompt 重写；acceptance criteria + failure modes 各加新条；USER_TODO §B.2 U-EXEC-004 加 v2 note | `docs/paper/figures_prompts/fig1_3action_policy_prompt.md` (v1→v2) + `USER_TODO §B.2` |
| 2026-04-20 | scientist | **R12 commit / S-120 provider 切换尾巴**（E-008 R10 已 ✅ → 此项 unblock 后立即做）：§5 Limitations 4→5 项加 cross-endpoint comparability caveat；Appendix A 补 1 句 endpoint switched + integrity guard pre-send mode；page_budget_audit.md 头部加 R12 update 块标注 fullval 数据来源切换；编译验证 main body 仍 8 页 COMPLIANT (PDF 总页 10→11，新增 1 页 Limitations + Appendix 文字) | `article/latex/edo_paper.tex §5 + Appendix A` + `docs/paper/page_budget_audit.md` + `SCIENTIST_TODO §B.5,§D` |
| 2026-04-20 | scientist (S-104 强制循环 R-FULL-002) | **R13 commit / S-104 处理 R-FULL-002 + bundle engineer Day 1.5 closure**：18 reviewer items 全过 4-step；5 NEW S-124..S-128 + U-018-decide + E-014 + 4 dissent log；同 commit 也带过 engineer 已完成的 E-002 ✅ / E-003 ✅ / E-009 ✅（task_tree + action_policy + audit_runtime 三接口冻结）→ S-118 fully unblocked | `SCIENTIST_TODO §B.5,§C,§D` + `USER_TODO §A,§D` + `REVIEWER_TODO §A,§C,§D` + `implementation_log [reviewer_r_full_002_ack_20260420]` + (engineer side) `action_policy.py / audit_runtime.py / test_*.py / external_baselines/survey_report.md / etc.` |

---

## E. 我的"不停问下一步"承诺

按 workflow §2，**Tier 1 拍板**（U-003/U-009/U-006）之后，我会按 B.1 的剩余无阻塞项**一次性全部做完**再回报，不再每完成一项就来问。

**当前 turn 即将连续完成**：S-011 → S-003 → S-006a → S-006b → 更新 PROJECT_STRUCTURE → ReadLints。
