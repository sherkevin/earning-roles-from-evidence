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
| **U-006-rerun-decide** | provider 恢复后是否立即重跑 fullval `static_roles + self_claim` | 是 | S-009 替换 §4.3 数字 | ✅ **已批准**（2026-04-19）；**provider 阻塞已解除**（2026-04-20，U-EXEC-001 替代解决，已切到 newapi）；现在仅等工程师 E-005 跑数自然带过 |
| **U-007-cleanup-autogen** | `workspace/autogen/` 56 MB clone 是否保留 | 保留 + `.gitignore` | 已通过 .gitignore 路径解决 | 🟡 自动消解（无需独立拍板） |
| **U-008-decide** | Phase 2：`idea.md` + `experiment.md` 是否移入 `docs/` | 暂缓，等论文 freeze | 跨文件改 + 全仓 grep | ⏳ 待拍板（不阻塞主线） |
| **U-009-decide** | LaTeX 模板落点 | 留 `article/` | — | ✅ 隐式解决（2026-04-19） |
| **U-010-decide** | 是否 `git init` 用于本地版本管理 | 建议 init | S-103 commit 工作流 | ✅ **已批准 init**（2026-04-19） |
| **U-011-decide** | **论文 framing 走向（reviewer 20260419 P5 oral gatekeeper 触发）**：当前论文 §4.3 Finding 4 自承认 `peer_calibrated F1=0.7381 < self_claim F1=0.7641` 同 token 成本 → 头部经验主张被作者自己证伪。两条路：**(a)** 主动重 framing 为 "Stage-1 backbone-sensitivity negative result + Stage-2 roadmap"，接受 `oral_quality_score ≤ 5`，靠 honesty + insight 拿 weak_accept（最快路径，可在 1-2 周内完工）；**(b)** 暂停投稿，先实现 Stage-2 (R1 split / R2 audit / R3 persona vector) 中至少 1 项，让 EDO 真有 empirical 优势再投（最远路径，可能 2-3 月） | **取决于你的时间预算**：若 EMNLP 2026 年底/2027 年初 deadline 紧 → 选 (a)；若可推到 ARR 后续 cycle 或换 venue → 选 (b) | **所有 §B.5 fix-TODO 的优先级 + S-001 主体 framing 重写都依赖这条**；S-105/108/109 等可独立先做（见 §B.5 标注） | ✅ **(b) 已批准** (2026-04-19)：实现 Stage-2 至少 1 项 + 仍冲刺 **EMNLP 2026 ARR May 25 deadline**（距今 36 天）→ 派生 **U-012-decide**（Stage-2 范围）+ **U-013-decide**（MuSiQue 是否同步上）+ 解锁工程师 Stage-2 sprint |
| **U-012-decide** | **Stage-2 实施范围 — 36 天 deadline 下三选一/几**：**R1 split**（最复杂：新 primitive action + LLM decomposition call + 三动作 utility 选择 + task-tree state；HotpotQA 2-hop 收益小，需 MuSiQue 才显价值）；**R2 audit**（中等：每跳 audit decision + 4 类 audit 输出 + 上游 reject_reroute/resplit；**直接反驳 reviewer fatal #1**——peer 输 self_claim 是因为没 hop-level 拦截重跑）；**R3 persona vector**（最简：scalar competence → vector belief，纯表征改动；论证价值最弱） | **强烈推荐 R2 单做**：① 工程估时 ~12 天 ≤ deadline；② 直接反驳 reviewer fatal flaw（self_claim 没有重跑机制，audit 一加上就有 mechanism gap）；③ 不要求第二 benchmark；④ 改 runner.py + 加 audit_runtime.py 即可 — **可选 + R3** 把 belief vector 顺便升上去（再 +3 天） | 解锁工程师 E-001..E-005 工单 + 科学家 S-115/116/117 写作 + R-FULL-002 复审 | ✅ **R1+R2+R3 全做已批准**（2026-04-20，用户原话"我全部同意"）—— sprint 工程总估时 25-30 天，36-天 deadline 仍 doable；解锁 `implementation_log.md [stage2_sprint_kickoff_20260420]` E-001..E-008 + `SCIENTIST_TODO §B.5` S-115..S-119 |
| **U-013-decide** | **是否同步上 MuSiQue 第二 benchmark — reviewer EXP-1 fail 的最直接补救**：MuSiQue 已是 paper §4.4 future work；data 已下到 `data/musique/` 56 MB；`scripts/download_musique.py` 就位 | **推荐：是**（必须做 — 单 benchmark 是 reviewer experiments_solidity_score=0/8 中 5 项失败的根因之一，且对 R2 audit 有放大效应：MuSiQue 4-hop 上 hop-level audit 价值远超 HotpotQA 2-hop）。**额外工程估时 ~3 天**（数据 export 1 天 + 三方法 fullval 跑数 2 天）。如选**否**，论文必须在 Limitations 显式承认单 benchmark 局限并接受 D4 ≤ 6 上限 | E-006/E-007 MuSiQue 工单 | ✅ **MuSiQue 加入已批准**（2026-04-20，"全部同意"）—— 解锁 E-004 (data prep) + E-005 (HotpotQA + MuSiQue 双 benchmark fullval batch) |
| **U-014-decide** | **外部 baseline 选几个 system 做对比** | (b) 2 systems = AutoGen + ChatEval | 解锁 engineer E-009..E-012 + scientist S-121/S-122/S-123 + 闭合 reviewer R-FULL-001 fatal #3 / S6 cap | ✅ **2 systems = AutoGen + ChatEval 已批准**（2026-04-20，"三个新决策都按照你的建议来"）|
| **U-015-decide** | **module-swap 范围** — drop-in replacement 设计（详见 [`external_baseline_plan.md`](../paper/external_baseline_plan.md) §2-§4） | (b) R2+R3 = SWAP-1 + SWAP-3 | 决定 SWAP-1 / SWAP-3 进 paper §4.x 表；R1 swap (SWAP-5 / MetaGPT) 留 future work | ✅ **R2+R3 已批准** = SWAP-1 (R3 vector belief → AutoGen `select_speaker`) + SWAP-3 (R2 audit → ChatEval `MetaReviewer`)（2026-04-20）|
| **U-016-decide** | **是否 drop 原 sprint 工单 E-007** | 是 (drop)，被 E-009..E-012 subsume | engineer 工单数减 1 | ✅ **drop E-007 已批准**（2026-04-20）—— E-007 在 implementation_log 标 `cancelled_by_R10`；新工单 E-009..E-012 取代 |
| **U-018-decide** | **是否加 Multi-Agent Debate (MAD) 作为第 3 个外部 baseline** | (a) 加 MAD 作为第 3 host (SWAP-4: R2 audit → MAD `final_aggregator`) | 解锁 engineer E-015 (reproduce MAD) + E-016 (R2 audit swap into MAD aggregator) + scientist S-131 (§4.x 表加第 3 host 列 + RW §2.2 重点增 MAD)；sprint 时间线 +5 d engineer，buffer 5-6 d 还能吃 | ✅ **(a) 加 MAD 已批准**（2026-04-20，用户原话 "U-018-decide：a"）—— D3 novelty `is_overlap_risk` cap 关闭；外部 baseline N=2→N=3 |
| **U-017** (informational) | **SSH server 激活记录** — 用户 2026-04-20 instruction "优先用服务器上的 gpu 跑实验 + 对于模型，能部署到服务器上的尽量部署" 默认批准激活 [`ssh-server-rules.mdc`](../../.cursor/rules/ssh-server-rules.mdc)；engineer E-013 SSH probe 已 ✅ 验证：viplabserver12 (10.103.16.12), 8 GPUs (4×RTX 3090 24GB + 4×RTX 2080 Ti 11GB) 全空闲，`/media/data3` 693 GB 可用，Python 3.10.12 系统级 | — | 解锁后续任何 GPU-bound 工单；**仍禁止本地 deploy model 替换 canonical gpt-4.1-mini 主线**（per `experiment.md §1.3`，仅 supplementary appendix） | ✅ **fact record（不是 decide）** (2026-04-20)：详见 `artifacts/server_probe/E-013_ssh_probe_20260419_183124.json` + `implementation_log.md [E-013_ssh_server_probe_20260420]` |
| **U-019-server-ssh-state-decide** | **Server SSH/clone 状态恢复路径** — engineer Day 6 尝试在 server 上 clone ChatEval (E-010 prep) 时发现：单次 session 内多次卡死 ssh 后产生 7 个 orphaned 进程 + 新连接 `Permission denied (publickey,password)` ❌（与 E-013 ✅ probe 矛盾）。Day 7 等 30+ min cooldown 后再 BatchMode 重试仍 fail (Permission denied)。三诊断假设：(1) ssh-agent 状态被 orphaned 进程污染；(2) server fail2ban 临时 ban 本机 IP；(3) server → github 出口慢/被防火墙拦。详见 `implementation_log.md [E-010_chateval_server_clone_attempt_20260420]` | (b) **用户 ssh 到 server 协助诊断** | 阻塞 E-010 server 路径 → 阻塞 E-011/E-012 swap workstream → 阻塞 S-121/S-122/S-123 写作 | ✅ **scientist 直连验证 SSH 已恢复**（2026-04-20，R21；用户原话 "你去登录到远程看一下吧，应该是可以连上的"）：用 `ssh -i ~/.ssh/school -o BatchMode=yes` 4 秒成功连上 viplabserver12；GitHub HTTP 200 (2.2 s) + api.github.com HTTP 200 (0.6 s) → ChatEval/AutoGen/MAD clone path 全可走 server；GPU 7/8 idle (4×3090 + 4×2080Ti)；workdir `/media/data3/dengkw/` 可写；engineer 早先 fail 是 transient（ssh-agent 状态污染或 orphaned process 已自然清理）。**E-010 server 路径 unblocked**；详见 `implementation_log [u_019_server_ssh_recovered_20260420]` 6 项诊断表 |
| **U-020-stage2-fullval-launch-decide** | **Stage-2 fullval batch 启动决策** — engineer Day 7 完成 E-005 全栈整合 + 200-sample sanity probe **大喜**：Stage-2 vs Stage-1 paired 同 200 samples = **F1 +3.38 pp (0.7292 vs 0.6954)** + **token -37% (4113 vs 6520/sample)** + **cost-normalised F1 +66%** + 0 dead_end + 0 premature_accept；validate_logs ✅；R0 baseline byte-id 零回归；97 unit tests pass；详见 `implementation_log.md [E-005_paired_stage1_vs_stage2_200_comparison_20260420]`。**直接闭合 reviewer R-FULL-001 fatal #1**（peer_calibrated F1=0.7381 < self_claim F1=0.7641 自证伪问题）。下一步是跑 7405-sample fullval × 1-3 seeds 拿统计显著性 + paired bootstrap CI | (b) **跑 3 seeds × 7405 fullval**（更稳健 paired bootstrap CI，~$270 总，~9 h wall，但更适合 reviewer 反驳）| 解锁 S-115/S-116/S-117 (Stage-2 fullval data 写作 §3 framing 调整 + §4 results)；解锁 reviewer R-FULL-002 复审之 EXP-1/EXP-2 闭环；闭合 reviewer R-FULL-001/002/003 共同的 EXP-2 multi-seed cap | ✅ **(b) 已批准**（2026-04-20，用户原话 "继续跑"，按推荐方案）：Engineer dispatched in `implementation_log [u_020_stage2_fullval_3seed_launch_20260420]`，3-seed × 7405 paired Stage-2 vs Stage-1 fullval；预算 ~$270 / wall ~9 h on newapi；**直接闭合 reviewer R-FULL-001 fatal #1 (Finding 4 自证伪) + R-FULL-001/002/003 共同 EXP-2 multi-seed cap** |

---

## B. 我自己的工作（不依赖任何人，可以做 / 接收派工）

> 所有 ID 用 `U-EXEC-XXX` 全局递增编号。当前最大已用：U-EXEC-006。

### B.1 API / Provider / 资源运维

| ID | 任务 | 派任者 / 派任日期 | 紧急度 | 状态 |
|---|---|---|---|---|
| **U-EXEC-001** | **充值 kuaipao.ai endpoint**（gpt-4.1-mini API 余额，估算需支持完整 fullval n=7405 × 2 方法重跑 + 后续 reviewer batch） | scientist (2026-04-19) | high — U-006 batch rerun 的硬前置 | ✅ **替代解决** (2026-04-20)：用户切换到 newapi 通道 (xh.v1api.cc, U-EXEC-006)；不再充值 kuaipao；后续所有 sprint 跑数走 newapi |
| **U-EXEC-002** | **monitor kuaipao.ai 是否仍把 gpt-4.1-mini 静默路由到 gpt-5.1**（即 model drift 是否还在）；可让工程师写一次 smoke probe 然后告知 provider 状态 | scientist (2026-04-19) | low — kuaipao 已切换走，不再依赖；保留 monitor 作为历史 forensic | 🟡 降级（kuaipao 已 deprecated） |
| **U-EXEC-003** | 备用 provider 评估：NVIDIA 端 llama-3.3-70b 是否值得作为 fallback baseline 并入论文 | scientist (2026-04-19) | low — 主线 fullval 优先 | 🟡 可暂缓 |
| **U-EXEC-006** | ✅ **新 newapi 通道已交付**（`xh.v1api.cc` + `sk-bSS5...jk`，`_type=newapi_channel_conn`）已加入 `configs/llm.json` 的 `newapi` block（2026-04-20）。下一步派给 engineer 做 **E-008 endpoint smoke probe**（`GET /v1/models` + `POST /chat/completions` smoke + 加 `_normalize_newapi()` 到 `llm_providers.py`）。短期 workaround：用 `LLM_BACKEND=oversea LLM_BASE_URL=https://xh.v1api.cc/v1 LLM_API_KEY=sk-bSS5...` 走环境变量 override | user (2026-04-20) | done (key 落地)；**待 engineer E-008** | ✅ key 已落地；E-008 在 `implementation_log.md [stage2_sprint_kickoff_20260420]` 待 engineer 执行 |

### B.2 概念示意图绘制（用我的 AI 工具出图）

| ID | 任务 | prompt 文件 | 落点 | 派任者 / 紧急度 | 状态 |
|---|---|---|---|---|---|
| **U-EXEC-004** | **Figure 1（3-action policy 概念图）— v2 prompt 已升级（2026-04-20，R11）**：从 2 panel 升级到 **3 panel** = Panel A (full EDO + R1/R2/R3 标注) + Panel B (TCPB chain prototype + 灰色 strikethrough Stage-2-only 占位) + **新增 Panel C** (module-swap mini-diagrams：R3 → AutoGen `select_speaker`，R2 → ChatEval `MetaReviewer.aggregate`)。Panel C 的目的是闭合 reviewer R-FULL-001 fatal #3，让 §4.x external-baseline 表格在视觉上 self-explanatory | [`docs/paper/figures_prompts/fig1_3action_policy_prompt.md`](../../docs/paper/figures_prompts/fig1_3action_policy_prompt.md) v2 | `artifacts/figures/fig1_3action_policy.{pdf,svg,png}`（vector 优先；已通过 `\graphicspath{{../../artifacts/figures/}}` 自动连进 .tex） | scientist (2026-04-19, prompt v2 升级 2026-04-20) / medium —— .tex placeholder 仍占位，不阻塞 sprint 主线；但 R-FULL-002 reviewer batch 前**必须**有真图（推荐 Day 22-26 完成） | ⏳ 待出图（v2 prompt） |

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
| **U-011-decide** | **论文 framing 走向 → 选 (b) Stage-2 实施 + 仍冲刺 EMNLP 2026 ARR May 25** | 2026-04-19 | 用户原话："我选择b，但是是投递2026年的，所以要加快进度干，全力以赴"。距 ARR May 25 截止 36 天。派生 U-012 (Stage-2 范围) + U-013 (MuSiQue) 两个二次决策；同步触发 SCIENTIST_TODO §B.5 + implementation_log Stage-2 sprint phase 块 |
| **U-012-decide** | **Stage-2 实施范围 → R1+R2+R3 全做** | 2026-04-20 | 用户原话："我全部同意"。Engineer sprint 估时 25-30 天 ≤ 36-天 deadline；解锁 implementation_log `[stage2_sprint_kickoff_20260420]` E-001..E-008 + SCIENTIST_TODO §B.5 S-115..S-119 |
| **U-013-decide** | **MuSiQue 第二 benchmark → 加入** | 2026-04-20 | 用户原话："我全部同意"。直接关闭 reviewer EXP-1 fail 根因；4-hop 任务上 R2 audit 价值远超 HotpotQA 2-hop |
| **U-EXEC-006** | **新 newapi 通道（xh.v1api.cc）交付** | 2026-04-20 | key 已加入 `configs/llm.json` 的 `newapi` block；engineer 后续 E-008 做 smoke probe + 扩展 `llm_providers.py` |
| **U-EXEC-001** | **kuaipao.ai 充值 → 替代解决（切换到 newapi）** | 2026-04-20 | 用户原话："现在换到新的 llm 连接上了"。kuaipao 不再依赖；newapi (xh.v1api.cc) 升级为 PRIMARY endpoint。**E-008 (newapi smoke probe) 立即升级为 sprint 关键路径 P0**，所有后续 E-005/E-007 跑数都走 newapi。U-006 rerun 自然解锁（provider 阻塞消除） |
| **U-018-decide** | **加 Multi-Agent Debate (MAD) 作为第 3 个外部 baseline** | 2026-04-20 | 用户原话："U-018-decide：a"。SWAP-4 (R2 audit → MAD `final_aggregator`) 升为主体；闭合 R-FULL-002 D3 novelty `is_overlap_risk=TRUE` cap；派生 engineer 工单 E-015 (reproduce MAD baseline) + E-016 (R2 audit swap into MAD aggregator) + scientist 工单 S-131 (§4.x 表加第 3 个 host 列 + RW §2.2 重点强化 MAD-vs-TCPB delta)；sprint 时间线 +5 d engineer，吸收进现有 5-6 d buffer |
| **U-014-decide** | **外部 baseline = 2 systems = AutoGen + ChatEval** | 2026-04-20 | 用户原话："三个新决策都按照你的建议来"。E-009..E-012 全部 unblocked；scope 锁定 N=2；engineer 工程估时 +5-6 d，由 sprint buffer 吸收 |
| **U-015-decide** | **module-swap 范围 = R2+R3 = SWAP-1 (R3→AutoGen) + SWAP-3 (R2→ChatEval)** | 2026-04-20 | 同上。SWAP-5 (R1→MetaGPT) 留 future work；R2 swap 进 ChatEval 是直接反驳 reviewer fatal #1 (Finding 4 自证伪) 的关键实验 |
| **U-016-decide** | **drop 原 sprint 工单 E-007** | 2026-04-20 | 同上。E-007 (4 d full-system 对比) 被 E-009..E-012 (survey+reproduce+swap+compare) 完全 subsume；implementation_log 标 `E-007 cancelled_by_R10`，避免双倍工作量 |
| **U-019-server-ssh-state-decide** | **Server SSH 恢复路径 → scientist 直连验证 ✅** | 2026-04-20 | 用户原话："你去登录到远程看一下吧，应该是可以连上的"。Scientist 用 `ssh -i ~/.ssh/school -o BatchMode=yes` 4 秒成功连接 viplabserver12（10.103.16.12 = `dengkw`）；网络到 github.com / api.github.com 均 HTTP 200；GPU 7/8 idle；engineer 早先卡死是 transient，已自然恢复。E-010 server 路径 unblocked，engineer 可恢复 ChatEval/AutoGen/MAD 在 server 上的 clone + reproduce |
| **U-020-stage2-fullval-launch-decide** | **Stage-2 fullval batch 启动 → (b) 3 seeds × 7405 ✅** | 2026-04-20 | 用户原话："继续跑"，按 scientist 推荐方案 (b)。Engineer 派工 `[u_020_stage2_fullval_3seed_launch_20260420]`：3-seed × 7405 paired Stage-2 vs Stage-1 fullval；budget ~$270；wall ~9 h on newapi；**临门一脚**：闭合 R-FULL-001 fatal #1 (Finding 4 自证伪) + R-FULL-001/002/003 共同 EXP-2 multi-seed cap |

---

## E. 注意事项（每次开新窗口先重读这条）

> 落定 2026-04-20（R8 commit）。任何后续状态变更触发本节修订。

### E.1 Provider / API（**最高优先级**）

1. ❌ **不要再用 `oversea` (kuaipao.ai) 通道**：2026-04-20 已 deprecated（`configs/llm.json` `oversea._status = "deprecated_..."`）；只保留它供历史 `round1/` `round2_gpt41mini/` 跑数复现，不开任何新 batch。
2. ✅ **所有新跑数走 `newapi` (xh.v1api.cc)**：`configs/llm.json` `newapi._status = "PRIMARY_..."`。
3. ⚠ **engineer E-008 是 sprint P0 关键路径**：必须在任何 chain-200 / fullval 之前完成 newapi smoke probe + 加 `_normalize_newapi()` 到 `llm_providers.py`。如 engineer 自作主张跳过 E-008 直接开 fullval，请立即拍停。
4. 🟡 **kuaipao 的额度状态不再监控**（`U-EXEC-002` 已降级为 low）；如未来又想回 kuaipao（不推荐），先恢复 `_status` 字段并跑一次 model-drift smoke probe。
5. 💸 **newapi 通道额度**：你掌握；如发现额度即将耗尽，立即通知 engineer 暂停下一批 fullval 不要烧光。

### E.2 决策路由（four-role rule §4 红线）

1. ❌ **科学家 / 工程师 / 审稿人严禁擅自做以下决策**（如发现请立即拍停）：
   - 路线决策（a/b/c 选择）
   - 是否锁稿 / 是否提交 ARR / 是否 commit-to-EMNLP
   - 预算决策（GPU / API quota / provider 切换）
   - scope 扩张（加新 benchmark / 加新 ablation）
   - 启动新一轮 reviewer batch（**全文** R-FULL；R-PART 不需要你批）
   - git force push / squash 历史 commit
2. ✅ **所有以上决策**先在 `§A` 加 `U-XXX-decide` 行 + 推荐方案，等你回复后再继续。
3. ⏳ **当前等你拍板的决策**（不阻塞主线，可慢慢回）：U-005 / U-008。

### E.3 你专属可做的工作

1. **概念示意图 / 逻辑流程图**（`U-EXEC-004` 等）：科学家给你 prompt，你用 AI 工具出图，落 `artifacts/figures/`。**不出统计图**（柱/箱/折/散点等数学图归科学家用 Python 实绘）。
2. **API 充值 / provider 切换**（`U-EXEC-001/006` 等）：物理操作只你能做。
3. **领域参考文献清单**（`U-EXEC-005`）：你脑子里"应该被引"的领域 paper 列出来（标题+作者+年份+venue+一行 why-relevant），科学家负责录入 bib。
4. **大方向 / framing 持续判断**（§B.4）：每次 reviewer batch 完成后，判断是否要切 venue / 推迟投稿 / 改 narrative。

### E.4 git / 仓库安全

1. ❌ **不要 `git push` 到任何 remote**：`configs/llm.json` 含 6 个真实 API key（zhipu / oversea / nvidia / gptplus5 / asxs / newapi）；R0 baseline 已把它们提交到本地 git 历史，仅本地不 push 是安全的。如果哪天确实需要 push，先 `git filter-repo` 擦除 6 个 key。
2. ❌ **不要在 OpenReview 投稿时上传 `configs/llm.json`**：直接违反 ARR 匿名化规则（DR-5 风险）。
3. ✅ **每次给科学家 / 工程师新指令后**：他们会做一次 R-X commit（commit message 里写明 task-ID + 受影响文件），你可以 `git log --oneline` 随时看进度。

### E.5 ARR May 25 deadline

- **Day 1** = 2026-04-20（已启动），**T-35** to ARR submission window close（2026-05-25）。
- **关键里程碑**（详见 `implementation_log.md [stage2_sprint_kickoff_20260420]` 时间线）：
  - Day 1.5（04-20 半天后）：engineer E-008 done → 启动 E-001/E-002
  - Day 18（05-07）：Stage-2 fullval batch 完成
  - Day 28（05-17）：所有写作 + R-FULL-002 复审完成
  - Day 35（05-25）：ARR submission deadline
- 如任何关键里程碑滑掉 ≥ 2 天，scientist 会挂 `U-Rollback-XXX-decide` 让你拍板"是否切 venue / 推迟 / 砍 scope"。

---

## D. 修订记录

| 日期 | 谁 | 动作 | 产物 |
|---|---|---|---|
| 2026-04-19 | scientist | **新建本文件**：从 `SCIENTIST_TODO.md §A` 迁出决策池为权威源；新增 §B 用户专属工作（U-EXEC-001..005 按 §12 命名重整） | 本文件 + `SCIENTIST_TODO.md §A` 改为 cross-ref + 已与 `four-role-todo-workflow.md §0/§4/§12` 对齐 |
| 2026-04-19 | scientist | 应用用户 04-19 批准（"按你的建议来"）：**U-002 ✅** / **U-004 ✅** / **U-006 ✅** / **U-010 ✅** | §A 4 行状态更新 |
| 2026-04-19 | scientist | **挂入 U-011-decide**：reviewer_20260419_163139 (P5 oral gatekeeper) 触发的 framing 走向决策（最高优先级） | §A 新增 1 行 |
| 2026-04-19 | reviewer-agent (落地用户决策) | **U-011 → ✅ (b) 已批准**（用户原话"我选择b，但是是投递2026年的，所以要加快进度干，全力以赴"）；派生 **U-012-decide** (Stage-2 范围, 推荐 R2 单做或 R2+R3) + **U-013-decide** (MuSiQue, 推荐 是)；同步 SCIENTIST_TODO §A cross-ref + §B.5 加 S-115/S-116/S-117 + implementation_log 开 Stage-2 sprint phase 块 (`stage2_sprint_kickoff_20260419`) + PROJECT_STRUCTURE.md §0 加 sprint 状态块 + ARR 5/25 倒计时 | `USER_TODO.md §A,§C,§D` + `SCIENTIST_TODO.md §A,§B.5,§D` + `implementation_log.md` + `PROJECT_STRUCTURE.md §0` |
| 2026-04-20 | scientist (落地用户决策) | **U-012 → ✅ R1+R2+R3 全做** + **U-013 → ✅ MuSiQue 加入**（用户原话"我全部同意"）；新 newapi 通道 (xh.v1api.cc) 落入 `configs/llm.json` 作为 `U-EXEC-006`；同步 SCIENTIST_TODO §A + §B.5 加 S-115..S-119；implementation_log 开新 phase 块 `[stage2_sprint_kickoff_20260420]` 含 E-001..E-008 工单；PROJECT_STRUCTURE.md §0 sprint 状态块更新为 Day 1 = 2026-04-20 / T-35 to ARR May 25 | `configs/llm.json` + `USER_TODO.md §A,§B.1,§C,§D` + `SCIENTIST_TODO.md §A,§B.5,§D` + `implementation_log.md` + `PROJECT_STRUCTURE.md §0` |
| 2026-04-20 | scientist (落地用户决策) | **U-EXEC-001 → ✅ 替代解决**（用户原话"现在换到新的 llm 连接上了"）：kuaipao 充值取消，全切到 newapi (xh.v1api.cc)；U-EXEC-002 降级 (kuaipao deprecated)；U-006 provider 阻塞解除；E-008 升级为 sprint P0 关键路径（所有 sprint 跑数依赖）；E-005/E-007 卸除 provider 阻塞；llm.json 更新 newapi note 为 PRIMARY + oversea note 为 deprecated | `configs/llm.json` + `USER_TODO.md §A,§B.1,§C,§D` + `SCIENTIST_TODO.md §A,§B.3,§D` + `implementation_log.md` |
| 2026-04-20 | scientist (per user instruction) | **R8 commit / 全角色注意事项落地**：USER_TODO §E（Provider 红线 / 决策路由 / 用户专属工作 / git 安全 / ARR 时间线）；SCIENTIST_TODO §F（匿名化 / 页数预算 / 编译必验 / 图表分工 / commit-per-polish / 不擅自决策 / S-104 强制循环）；REVIEWER_TODO §F（stateless / R-FULL 仅用户触 / 6-char hash / schema 单源 / 不动别人 TODO）；implementation_log append `[pinned_cautions_for_engineer_20260420]`（E-008 P0 / ModelDriftError 必启 / 不走 kuaipao / Stage-1 byte-id 回归 / token 预算 / log 双轨） | 4 个 TODO 文件 |
| 2026-04-20 | scientist (per user instruction "对比实验是要补的") | **R9 commit / 外部 baseline workstream planning**：审计 .tex 0 个外部 baseline + 8 个内部变体；新文件 `docs/paper/external_baseline_plan.md` (10 §：gap audit / why module-swap / 6 候选 system / module-swap 矩阵 / E-009..E-012 派工 / 时间线 / 决策 / 验收标准 / 风险 / refs)；§A 加 U-014/U-015/U-016；implementation_log append `[external_baseline_workstream_20260420]`；SCIENTIST_TODO §B.5 加 S-121/S-122/S-123 | `docs/paper/external_baseline_plan.md` (新建) + `USER_TODO §A,§D` + `SCIENTIST_TODO §A,§B.5,§D` + `implementation_log.md` |
| 2026-04-20 | scientist (落地用户三决策一次性批准) | **R10 commit / U-014/U-015/U-016 三决策落地**（用户原话"三个新决策都按照你的建议来"）：U-014 → ✅ 2 systems = AutoGen + ChatEval；U-015 → ✅ R2+R3 swap = SWAP-1 + SWAP-3；U-016 → ✅ drop E-007；§C 加 done log；SCIENTIST_TODO §A cross-ref + §B.5 锁定 S-121/S-122/S-123 scope；implementation_log 末加 `[external_baseline_decisions_landed_20260420]` 子条 + 标 E-007 `cancelled_by_R10` + E-009..E-012 unblocked；PROJECT_STRUCTURE §0 sprint 状态块补充外部 baseline workstream 已 unblocked | `USER_TODO §A,§C,§D` + `SCIENTIST_TODO §A,§B.5,§D` + `implementation_log` + `PROJECT_STRUCTURE §0` |
| 2026-04-20 | scientist (S-104 强制循环 R-FULL-002) | **R13 commit / U-018-decide 派工 + S-104 全流程**：R-FULL-002 (`reviewer_20260419_185701`, P3 Adversarial Novelty SAC, weighted_sum=5.925 capped to 4.5) reviewer 明点 MAD `is_overlap_risk=TRUE`；§A 加 U-018-decide (是否加 MAD 作为第 3 个外部 baseline)，推荐 (a) 加 | `USER_TODO §A,§D` + (其他文件由 SCIENTIST_TODO §D R13 行覆盖) |
| 2026-04-20 | scientist (落地用户 U-018 批准) | **R17 commit / U-018 → ✅ (a) 加 MAD**（用户原话 "U-018-decide：a"）：§A 状态翻 ✅；§C 加 done log；外部 baseline N=2→N=3 (AutoGen + ChatEval + MAD)；SWAP-4 (R2→MAD `final_aggregator`) 从 future work 升为主体；engineer 派工 E-015 (reproduce MAD) + E-016 (R2 audit swap into MAD aggregator) 加 implementation_log；scientist 派工 S-131（§4.x 表加第 3 host 列 + RW §2.2 重点强化 MAD delta）加 SCIENTIST_TODO §B.5；external_baseline_plan.md §3.2/§4/§6 同步；PROJECT_STRUCTURE §0 sprint 状态块 N=3 hosts | `USER_TODO §A,§C,§D` + `SCIENTIST_TODO §A,§B.5,§D` + `external_baseline_plan.md §3.2,§4,§6` + `implementation_log [u_018_mad_landed_20260420]` + `PROJECT_STRUCTURE §0` |
| 2026-04-20 | scientist (S-104 强制循环 R-FULL-003) | **R18 commit / S-104 处理 R-FULL-003** (P2 Empirical-NLP SAC, weighted_sum=5.905, exp_solidity=1/8)：12 reviewer items 全过 4-step → 4 NEW (S-132/133/134/135 全 scientist hygiene) + 12 redundant + 2 reject/defer + **0 user 决策**（R17 已盖 MAD；DR-1/DR-3 verification + B5 + Algorithm 1 page-pressure 全是 scientist 内部 hygiene） + 0 engineer 工单（E-014 已存）；本 commit 用户**无需任何动作**，仅一行 §D 修订记录给用户知晓 | `SCIENTIST_TODO §C,§B.5,§D` + `USER_TODO §D（仅本行）` + `implementation_log [reviewer_r_full_003_ack_20260420]` |
| 2026-04-20 | scientist (落地用户 U-019 + U-020 双批准) | **R21 commit / U-019 ✅ + U-020 → ✅ (b) + 工作流元规则**：(1) U-019 → ✅ scientist 直连 SSH 验证服务器可达（`ssh -i ~/.ssh/school` 4 s 连成 + GitHub HTTP 200 + GPU 7/8 idle），engineer E-010 server 路径 unblocked；(2) U-020 → ✅ (b) 3 seeds × 7405 paired Stage-2 vs Stage-1 fullval（用户原话 "继续跑" 按推荐），engineer dispatched in `[u_020_stage2_fullval_3seed_launch_20260420]`；(3) 用户工作流元规则 "需要我拍板的时候，你直接切到的 plan 模式，让我们选择就行" 已落 [`four-role-todo-workflow.mdc §4.1`](../../.cursor/rules/four-role-todo-workflow.mdc) 作为 scientist/engineer 派 `U-XXX-decide` 给用户时的标准 dispatch protocol | `USER_TODO §A,§C,§D` + `SCIENTIST_TODO §B.5（状态块）` + `implementation_log [u_019_server_ssh_recovered_20260420] + [u_020_stage2_fullval_3seed_launch_20260420]` + `.cursor/rules/four-role-todo-workflow.mdc §4.1（新增）` |
| 2026-04-20 | scientist (落地用户工作流元规则 #2) | **R22 commit / 向 engineer dispatch 时顺手答复已知疑问**（用户原话 "在你给工程师派任务的时候，把他的疑惑顺便给他解答了，放在这条todo的注意事项里面，让他知道刚才为什么失败"）：(1) 新建 [`pinned_cautions_for_engineer_ssh_failure_mode_20260420`](./implementation_log.md) 作为 SSH 失败模式 + 5-step Recovery playbook 的**唯一权威说明源**；(2) 回头给 [E-010_chateval_server_clone_attempt] 末加 `#### 后补 ack (R22)` 子条 — 用第二人称写给 engineer："你之前看到的 `Permission denied` 不是 server / fail2ban 问题，是本机 OpenSSH 状态污染..."；(3) 给 E-015/E-016/E-017 三个 server-using 工单加 C-6/C-6/C-7 SSH 注意事项 + cross-ref 唯一说明源；(4) [`four-role-todo-workflow.mdc §4.2`](../../.cursor/rules/four-role-todo-workflow.mdc) 新增 "Engineer-facing dispatch quality bar" 5 子条把这个 pattern 自动化为**所有未来 engineer dispatch 的硬规则** | `implementation_log` 新 phase 块 + 4 处 ticket cautions 改 + `.cursor/rules/four-role-todo-workflow.mdc §4.2（新增）` + 本行 |
| 2026-04-20 | scientist (S-104 强制循环 R-FULL-004) | **R23 commit / S-104 处理 R-FULL-004** (P1 Strict ARR SAC, weighted_sum=4.985 capped to 4.5, exp_solidity=1/8 第 4 次同一 §6 hard-cap)：5 NEW (S-136 TCPB scoring formula / S-137 FIT vector case / S-138 LLM_* prompt templates Appendix C / S-139 Limitations item (6) Pareto-domination / S-140 honesty re-phrase batch — 全 scientist hygiene) + 13 redundant + 1 reject ("withdraw and revise" 与 U-011 (b) ✅ 冲突, scientist 不擅自 override) + 2 defer + 1 reviewer 自我 walk-back protocol observation (留 reviewer-agent / 用户裁定)；本 commit 用户**无需任何动作**；后续 R24..R28 batch 我会立即 self-exec 5 个 NEW S-136..S-140 | `SCIENTIST_TODO §C,§B.5,§D` + `USER_TODO §D（仅本行）` + `implementation_log [reviewer_r_full_004_ack_20260420]` |
| 2026-04-19 | reviewer-agent (per user 授权 "给科学家下任务") | **R-FULL-004 strict re-review + reviewer-agent 主动派工给 scientist**（用户原话 "你不要忘了给科学家下任务，让他来看一下你的审稿意见"）：reviewer 在 §11.5 默认禁令外按用户授权破例改 SCIENTIST_TODO §C/§B.5/§F.5（不动 §A/§D 决策池 + 修订记录）。R-FULL-004 (P1 Strict ARR SAC, weighted_sum=4.985, overall=4.5, weak_reject) 落盘 `artifacts/idea_reviews/reviewer_20260419_202222_04_232b11/review.md`；scientist 在 R-FULL-003 后的 5 项修复 (DR-1/DR-3/Alg-1/B5/Limitations conjectural) 全部 verified 生效。**R-FULL-004 真 NEW 3 条**已派 SCIENTIST_TODO §B.5 **S-136 / S-137 / S-138**（全 scientist self-exec, 估时合计 ~85 min, 无 user 决策, 无 engineer 工单）：S-136 TCPB scoring 显式公式 / S-137 FIT(P, ϕ) vector-case 定义 / S-138 Appendix C Prompt Templates。reviewer 同时承认前一轮 R-FULL-003 评分讨好（6 处维度偏宽），R-FULL-003 review.md 顶部已加 STRICT REVISION errata。**用户无需任何动作**，仅一行知晓；连续 4 轮 weak_reject 都被 §6 cap 锁，**R-FULL-005 触发等 E-017 fullval ack + ≥ 1 外部 baseline + Table 2 gpt-4.1-mini ablation 之后**。 | `artifacts/idea_reviews/reviewer_20260419_202222_04_232b11/review.md` (新建) + `artifacts/idea_reviews/reviewer_20260419_193730_03_288f84/review.md` (errata) + `SCIENTIST_TODO §C,§B.5,§F.5` (reviewer 破例改) + `REVIEWER_TODO §A,§C,§D,§F.5` + `implementation_log §F.4 ack 1 行` + `USER_TODO §D（仅本行）` |
