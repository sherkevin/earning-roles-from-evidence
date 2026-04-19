# SCIENTIST_TODO — 科学家工作清单 + 决策池

> 维护者：科学家（论文撰写负责人）。
> 创建日期：2026-04-19。
> 当前位置：`docs/coordination/SCIENTIST_TODO.md`（Phase 1 重构后）。
> 协作规范：[`.cursor/rules/four-role-todo-workflow.md`](../../.cursor/rules/four-role-todo-workflow.md) § 1–12（含审稿人角色 §11 + ID 命名约定 §12）。
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
| `U-006-rerun-decide` | S-009（用真 fullval 数字替换 §4.3 pending 措辞） | ⏳ 待用户 + provider 恢复 + `U-EXEC-001` 充值 |
| `U-007-cleanup-autogen` | none（仅清洁，依赖 U-010 先 init） | ⏳ 待用户 |
| `U-008-decide` | none（暂缓 Phase 2） | ⏳ 待用户 |
| `U-009-decide` | S-013（.md → .tex 迁移）、build 脚本封装 | ✅ 隐式解决（article/ 已采用） |
| `U-010-git-decide` | S-103（commit 工作流） | ⏳ 待用户 |
| `U-011-decide` | **所有 §B 写作（决定 framing 方向后才能继续）** | ⏳ **最高优先级**（reviewer fatal flaw） |

---

## B. 我自己的写作 TODO（不依赖你 / 不依赖工程师，可以做）

按 `four-role-todo-workflow.md §2` 硬规则：**所有 ❌ 且不被 blocked 的项必须连续做完再回报。**

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
| S-009 | 用 fullval 真数字替换 §4.3 "pending rerun" 措辞 | 等 fullval rerun（U-006 拍板后） | tracking-S-009 |
| S-010 | 拿到 Figure 1 PNG 后嵌入论文 + 写最终 caption（依赖用户出图） | 等用户出 Figure 1 PNG | tracking-S-010 |

### B.5 来自 reviewer_20260419_163139 (P5 oral gatekeeper) 的新 fix-TODO（S-104 ③ "诚实接受" 阶段产物）

| ID | 任务 | 估计时间 | 阻塞 | 状态 |
|---|---|---|---|---|
| **U-011-decide** | 决定本论文 framing 走向：(a) Stage-1 negative result 重 framing（保留现状）vs. (b) 实现 Stage-2（split / audit / persona vector）后再投；reviewer 指出当前 narrative 被作者自己 Finding 4 证伪 | — | 用户拍板 | ⏳ **最高优先级决策** |
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

### S-104 dissent log（科学家保留权利不接受 reviewer 意见）

> 留给科学家本人填写。reviewer agent 提出的每条 NEW 意见旁边的"⚠ 未处理"如果转成"❌ 拒绝接受"，必须在这里写 1 行理由（criteria：能否用现有证据反驳？是否与既往 fix_themes 冲突？是否超出 scope？）。

| reviewer_id | 拒绝的具体意见 | 拒绝理由 |
|---|---|---|
| _(空)_ | _(待填)_ | _(待填)_ |

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

---

## E. 我的"不停问下一步"承诺

按 workflow §2，**Tier 1 拍板**（U-003/U-009/U-006）之后，我会按 B.1 的剩余无阻塞项**一次性全部做完**再回报，不再每完成一项就来问。

**当前 turn 即将连续完成**：S-011 → S-003 → S-006a → S-006b → 更新 PROJECT_STRUCTURE → ReadLints。
