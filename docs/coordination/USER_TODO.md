# USER_TODO — 用户工作清单 + 决策池

> 维护者：用户（总协调 / 大方向把握 / 重要卡点决策）。
> 创建日期：2026-04-19。
> 当前位置：`docs/coordination/USER_TODO.md`。
> 协作规范：[`.cursor/rules/four-role-todo-workflow.mdc`](../../.cursor/rules/four-role-todo-workflow.mdc) §0/§4/§11/§12（英文版 + Cursor `.mdc` 规范）。
> 配对文件：[`SCIENTIST_TODO.md`](./SCIENTIST_TODO.md)（科学家工作清单，§A 是 cross-ref 镜像）、[`implementation_log.md`](./implementation_log.md)（工程实现日志，append-only）、[`REVIEWER_TODO.md`](./REVIEWER_TODO.md)（审稿人工作清单，R-FULL 仅我触发 / R-PART 科学家工程师可自触）。

---

## 0. 角色边界（每次重读）

我（用户）做：
- **重要卡点决策**：所有 a/b/c 路线、锁稿、预算、是否做 rebuttal-only 实验、是否启动新 reviewer batch 等的最终拍板（§A）。
- **大方向把握**：研究方向、framing 取舍、reviewer 反馈是否值得改进、long-paper 优先级（§B 末"持续判断"）。
- **API 充值 / provider 切换 / endpoint 维护**（§B U-EXEC-001 等）。
- **概念示意图 / 逻辑流程图绘制**（§B U-EXEC-002 等，配科学家给我的 prompt 一起用 AI 工具出图）。
- **部分参考文献调研**（§B U-EXEC-003，主要是我"知道哪些 paper 应该引"的领域记忆部分；具体 bib 条目录入由科学家完成）。
- **接收科学家 / 工程师 / 审稿人派给我的物理操作任务**（在 §B 加 U-EXEC-XXX）。

我**不做**：
- 论文 .tex 内容编写（→ 科学家）。
- 跑实验 / 写 core code / 改 runner（→ 工程师）。
- 论文 .md 文档维护（→ 科学家）。
- 跑审稿（→ 审稿人 AI；但是否启动 batch 由我在 §A `U-Review-XXX-decide` 拍板，见 four-role rules §11.1 条件 ④）。

任何**协作者觉得需要我介入的任务**，他们直接在 §B 加一行 `U-EXEC-XXX`；我处理完后把它标 ✅ + 填完成日期。

---

## A. 决策池（重要卡点）

> 所有 `U-XXX-decide` 集中在这里。**本节是权威源**。`SCIENTIST_TODO.md §A` 仅做 cross-reference 镜像。
> 科学家 / 工程师 / 审稿人**严禁擅自决策**，必须先在这里挂行 + 推荐方案，等我拍板。

| ID | 决策 | 推荐 | 影响 / 阻塞下游 | 状态 |
|---|---|---|---|---|
| **U-001-decide** | 科学家 TODO 文件位置 | 单一 `SCIENTIST_TODO.md` | — | ✅ 默认采用单一文件（2026-04-19） |
| **U-002-decide** | rebuttal 记录的落点 | `artifacts/rebuttals/`（与 `idea_reviews/` 同层） | S-012 创建目录 | ✅ **已批准 `artifacts/rebuttals/`**（2026-04-19） |
| **U-003-decide** | `EMNLP_paper_draft.md` 双稿处理 | 合并成单稿 | S-001 / S-013（已自动消解） | ✅ 隐式解决（.tex 已是单稿） |
| **U-004-decide** | `ModelDriftError` 故事写主文 §5 还是 appendix | 不写主文，只写 appendix | S-005 / S-111 | ✅ **已批准 appendix-only**（2026-04-19） |
| **U-005-cleanup-decide** | 清理 `🟡 dead` 类 run dir（共 5 个目录 < 1.5 MB） | camera-ready 后再清 | 极小 | ⏳ 待拍板（不紧急） |
| **U-006-rerun-decide** | provider 恢复后是否立即重跑 fullval `static_roles + self_claim` | 是 | S-009 替换 §4.3 数字 | ✅ **已批准**（2026-04-19）；当前**等 provider 恢复 + U-EXEC-001 充值** |
| **U-007-cleanup-autogen** | `workspace/autogen/` 56 MB clone 是否保留 | 保留 + `.gitignore` | 已通过 .gitignore 路径解决 | 🟡 自动消解（无需独立拍板） |
| **U-008-decide** | Phase 2：`idea.md` + `experiment.md` 是否移入 `docs/` | 暂缓，等论文 freeze | 跨文件改 + 全仓 grep | ⏳ 待拍板（不阻塞主线） |
| **U-009-decide** | LaTeX 模板落点 | 留 `article/` | — | ✅ 隐式解决（2026-04-19） |
| **U-010-decide** | 是否 `git init` 用于本地版本管理 | 建议 init | S-103 commit 工作流 | ✅ **已批准 init**（2026-04-19） |
| **U-011-decide** | **论文 framing 走向（reviewer 20260419 P5 oral gatekeeper 触发）**：当前论文 §4.3 Finding 4 自承认 `peer_calibrated F1=0.7381 < self_claim F1=0.7641` 同 token 成本 → 头部经验主张被作者自己证伪。两条路：**(a)** 主动重 framing 为 "Stage-1 backbone-sensitivity negative result + Stage-2 roadmap"，接受 `oral_quality_score ≤ 5`，靠 honesty + insight 拿 weak_accept（最快路径，可在 1-2 周内完工）；**(b)** 暂停投稿，先实现 Stage-2 (R1 split / R2 audit / R3 persona vector) 中至少 1 项，让 EDO 真有 empirical 优势再投（最远路径，可能 2-3 月） | **取决于你的时间预算**：若 EMNLP 2026 年底/2027 年初 deadline 紧 → 选 (a)；若可推到 ARR 后续 cycle 或换 venue → 选 (b) | **所有 §B.5 fix-TODO 的优先级 + S-001 主体 framing 重写都依赖这条**；S-105/108/109 等可独立先做（见 §B.5 标注） | ⏳ **最高优先级，等用户拍板** |

---

## B. 我自己的工作（不依赖任何人，可以做 / 接收派工）

> 所有 ID 用 `U-EXEC-XXX` 全局递增编号。当前最大已用：U-EXEC-005。

### B.1 API / Provider / 资源运维

| ID | 任务 | 派任者 / 派任日期 | 紧急度 | 状态 |
|---|---|---|---|---|
| **U-EXEC-001** | **充值 kuaipao.ai endpoint**（gpt-4.1-mini API 余额，估算需支持完整 fullval n=7405 × 2 方法重跑 + 后续 reviewer batch） | scientist (2026-04-19) | high — U-006 batch rerun 的硬前置 | ⏳ 待执行 |
| **U-EXEC-002** | **monitor kuaipao.ai 是否仍把 gpt-4.1-mini 静默路由到 gpt-5.1**（即 model drift 是否还在）；可让工程师写一次 smoke probe 然后告知 provider 状态 | scientist (2026-04-19) | medium — 每次开 batch 前必查 | ⏳ ongoing |
| **U-EXEC-003** | 备用 provider 评估：NVIDIA 端 llama-3.3-70b 是否值得作为 fallback baseline 并入论文 | scientist (2026-04-19) | low — 主线 fullval 优先 | 🟡 可暂缓 |

### B.2 概念示意图绘制（用我的 AI 工具出图）

| ID | 任务 | prompt 文件 | 落点 | 派任者 / 紧急度 | 状态 |
|---|---|---|---|---|---|
| **U-EXEC-004** | **Figure 1（3-action policy 概念图）** —— 双 panel：上 panel EDO 全图（5 节点稀疏图 + 三动作 + 递归 audit）；下 panel TCPB chain 退化版 | [`docs/paper/figures_prompts/fig1_3action_policy_prompt.md`](../../docs/paper/figures_prompts/fig1_3action_policy_prompt.md) | `artifacts/figures/fig1_3action_policy.{pdf,svg,png}`（vector 优先） | scientist (2026-04-19) / medium —— .tex 已加 placeholder，不阻塞编译；但 reviewer batch 前必须有真图 | ⏳ 待出图 |

### B.3 参考文献调研（领域知识）

| ID | 任务 | 派任者 / 紧急度 | 状态 |
|---|---|---|---|
| **U-EXEC-005** | **EDO / multi-agent / delegation / sparse graph organization 主要参考文献清单**（你脑子里"应该被引"的领域 paper），特别是：(a) AutoGen / MetaGPT / HuggingGPT 类 orchestrator 系统；(b) Reflexion / Tree-of-Thoughts / SelfRefine 类 self-reflection；(c) MARS / SAGE / AMRO-S / Brain-Inspired Graph MAS 类 peer critique；(d) 社会学/组织学 division of labor 经典；(e) 任何与"persona-tag 形成"或"recursive audit"接近的 prior work。给科学家一份 markdown 清单（标题 + 作者 + 年份 + venue + 一行 why-relevant），科学家负责录入 bib 条目 + LaTeX 引用。**reviewer fatal #4 触发**：当前 PDF 只有 4 条 ACL 模板默认 placeholder，是 desk-reject 邻接信号。 | scientist (2026-04-19) / **high** — desk-reject 邻接 | ⏳ 待执行（科学家本轮已用占位 EDO/MAS 公开文献占位补到 ≥10 条，可继续等你的领域清单 PR-style 补充） |

### B.4 大方向 / framing 持续判断（无 ID，触发式）

- **每次 reviewer batch 后**：判断是否要调整 paper framing（不是字句级，而是"研究问题"级）。当前**最高优先级是 U-011-decide**。
- **决定 paper target**：是否把 EMNLP 2026/27 long paper 切到其他 venue（NAACL / ACL / NeurIPS workshop），何时切换。
- **决定 Stage-2 实施起步时间**：什么时候让工程师真的开始写 split / audit / vector belief 代码（强相关 U-011 的 (b) 选项）。
- **ARR / EMNLP 2026 commitment 时间线**：你掌握时间表。

---

## C. 已完成（用户自己处理过的，含日期与备注）

| ID | 任务 | 完成日期 | 备注 |
|---|---|---|---|
| _(空)_ | _(空)_ | _(空)_ | _(空)_ |

---

## D. 修订记录

| 日期 | 谁 | 动作 | 产物 |
|---|---|---|---|
| 2026-04-19 | scientist | **新建本文件**：从 `SCIENTIST_TODO.md §A` 迁出决策池为权威源；新增 §B 用户专属工作（U-EXEC-001..005 按 §12 命名重整） | 本文件 + `SCIENTIST_TODO.md §A` 改为 cross-ref + 已与 `four-role-todo-workflow.md §0/§4/§12` 对齐 |
| 2026-04-19 | scientist | 应用用户 04-19 批准（"按你的建议来"）：**U-002 ✅** / **U-004 ✅** / **U-006 ✅** / **U-010 ✅** | §A 4 行状态更新 |
| 2026-04-19 | scientist | **挂入 U-011-decide**：reviewer_20260419_163139 (P5 oral gatekeeper) 触发的 framing 走向决策（最高优先级） | §A 新增 1 行 |
