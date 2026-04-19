---
description: EMNLP long paper — four-role TODO workflow (user / scientist / engineer / reviewer); covers role mapping, decision routing, blocked semantics, ID naming, handoff, and reviewer batch lifecycle
globs:
  - docs/coordination/USER_TODO.md
  - docs/coordination/SCIENTIST_TODO.md
  - docs/coordination/REVIEWER_TODO.md
  - docs/coordination/implementation_log.md
  - artifacts/idea_reviews/**
  - PROJECT_STRUCTURE.md
alwaysApply: true
---

# EMNLP long paper — 四角色 TODO 协作规则

> **历史**：2026-04-19 之前文件名为 `three-role-todo-workflow.md`，仅含用户 / 科学家 / 工程师三角色；用户 04-19 明确澄清协作实际是**四角色**（加入"审稿人"），文件 rename 为 `four-role-todo-workflow.md`。`implementation_log.md` 中保留对旧文件名的历史引用，**不回写**。

## 0. 角色与状态文件映射

仓库里有 **四份持久 TODO 文件 + 一类审稿归档目录 + 一份索引**，由四个角色分别维护：

| 角色 | 状态/输出文件 | 主要内容 |
|------|---------------|----------|
| **用户**（总协调） | [`docs/coordination/USER_TODO.md`](../../docs/coordination/USER_TODO.md) | §A 决策池（U-XXX，**single source of truth**）+ §B 用户专属工作（API 充值 / 概念图 / 参考文献 / 大方向）+ §C 派给用户的具体 todo |
| **科学家**（writing lead） | [`docs/coordination/SCIENTIST_TODO.md`](../../docs/coordination/SCIENTIST_TODO.md) §B–E（§A 仅 cross-reference 到 USER_TODO） | 写作 / Figure 设计 / Limitations 调整 / framing 决策 / 论文级 lint / **审稿反馈处理（§B.4 S-104 4 步循环）** |
| **工程师** | [`docs/coordination/implementation_log.md`](../../docs/coordination/implementation_log.md) | append-only 工程实现日志（跑实验 / 改 core code / 校验 log / 后处理 / 加 runtime guard） |
| **审稿人** | [`docs/coordination/REVIEWER_TODO.md`](../../docs/coordination/REVIEWER_TODO.md) + [`artifacts/idea_reviews/`](../../artifacts/idea_reviews/) 下的 `reviewer_<YYYYMMDD>_<HHMMSS>_<NN>_<6char-hash>/` 子目录 + 聚合 `scoreboard.md` / `fix_themes.md` | §A 全文审稿（仅用户触发）+ §B 局部审稿（科学家/工程师可自触发，用于审自己新写的内容）+ stateless within batch（写新 review 时不读历史 review，避免 confirmation bias） |

项目级单一索引（任何角色接手新窗口必读）：[`PROJECT_STRUCTURE.md`](../../PROJECT_STRUCTURE.md)。

## 1. 单角色操作准则（CRITICAL）

每个角色（用户 / 科学家 / 工程师 / 审稿人）**每次开始执行新动作时**必须做以下 2 步，**缺一不可**：

1. **检测 pending → done**：扫**当前角色对应的 TODO 文件**里所有 ⏳ 或"等别人完成 `<ID>`"的项，逐一判断上游 / 外部条件是否已满足。已满足的项立刻标 ✅，并填"结果链接"列指向产物。这一步是 cycle 的入口。
2. **更新当前动作的 TODO 状态**：开始动作时在自己 TODO 加一行 ⏳；完成后立刻把它标 ✅ + 填产物链接。如果新派发了任务给别人，在自己 TODO 加一条 `tracking-XXX` 行，标"等 `<角色>` 完成 `<ID>`"。

**违反任意一步 = 工作未完成**。下一个角色接手时找不到状态。

## 2. "不停问下一步"协议（HARD RULE）

执行任务时：

- ✅ **必须**：把自己 TODO 里所有 **不依赖别人** 的任务**全部做完**，再询问用户下一步。
- ❌ **禁止**：每完成一个小任务就停下问 "下一步选 A 还是 B"。
- ❌ **禁止**：在 todos 里还有 ❌ 未开始且不被 blocked 的项目时，给用户递选项。

判断"是否 blocked"的硬规则：

- 任务的 `阻塞` 字段不为空 / 指向其他角色未完成的 ID → blocked。
- 任务的 `阻塞` 字段为"用户决策 X"且 `USER_TODO.md § A` 该决策仍 ⏳ → blocked。
- 任务的 `阻塞` 字段为"用户人工活 X"且 `USER_TODO.md § B/§C` 该项仍 ⏳ → blocked。
- 否则不 blocked → 必须立刻干。

## 3. 跨角色协作通过"阻塞列"传递

每个 TODO 文件的 `阻塞` 列必须明确写：

- 自由格式 `等 <角色> 完成 <ID>` 或 `用户决策 <decision-ID>` 或 `用户人工活 <U-XXX>`；
- 完成自己任务时，回头检查其他 TODO 文件，把 "等我" 的下游任务的 `阻塞` 字段清空。

跨四角色的典型阻塞链示例：

```
用户 (U-RES-001 充值 API)
   → 工程师 (跑 fullval rerun)
   → 科学家 (S-009 用真数字替换 §4.3 pending 措辞)
   → 审稿人 (R-FULL-N 下一轮全文 batch 才能测真实 fullval framing)
   → 用户 (依据 reviewer overall 决定 U-011 framing 拍板)
```

## 4. 决策走 USER_TODO.md § A，不能擅自决定

科学家 / 工程师 / 审稿人**严禁**做以下决策（典型路线决策类型清单，**非穷尽**）：

- **结构性**：选 a/b/c 路线（如 LaTeX 模板落点、rebuttal 落点、双稿合并方式、目录重构）；
- **冻结类**：是否锁稿 / 是否提交 ARR / 是否 commit-to-EMNLP；
- **预算类**：是否花 GPU 重跑 / 是否充值 API quota / 是否换 backbone provider；
- **scope 扩张**：是否加新 benchmark（MuSiQue 等）/ 是否加新 ablation / 是否做 rebuttal-only 实验；
- **审稿触发（仅全文）**：是否启动新一轮**全文审稿** batch（`R-FULL-XXX`）—— 局部审稿 `R-PART-XXX` **不**需用户批准（科学家 / 工程师可自触发，用于审自己新写的部分内容）；
- **版本控制**：是否 git init / 是否 force push / 是否 squash 历史 commit。

**所有决策**先在 [`docs/coordination/USER_TODO.md`](../../docs/coordination/USER_TODO.md) `§ A`（**权威源**）加一行 `U-XXX` + "推荐 / 待用户拍板"；**同时**在 `SCIENTIST_TODO.md § A` 加一行 cross-reference（仅 ID + 阻塞下游 + 状态镜像）方便 scientist 追踪自己被阻塞的链。**等用户在 USER_TODO 回复后**再继续。

任何**只有 USER 能做的物理操作**（API 充值、用 prompt 画概念图、上传 paper、注册账号、OpenReview 操作）走 `USER_TODO.md § B/§C`。

## 5. 切换窗口 / 开新对话的 handoff 协议

新窗口起手，按角色读以下文件（≤ 100 lines/file）：

| 角色 | 必读文件 |
|------|----------|
| 用户 | `USER_TODO.md § A` 决策池最近 ⏳ 项 + `§ B/§ C` 最近 ⏳ 项 |
| 科学家 | `SCIENTIST_TODO.md § B` 最近 ⏳ / ❌ 项 + `USER_TODO.md § A`（看自己被阻塞的决策状态）+ `artifacts/idea_reviews/scoreboard.md` + `fix_themes.md`（最新审稿状态）+ `PROJECT_STRUCTURE.md` |
| 工程师 | `docs/coordination/implementation_log.md` 最近 ⏳ / ❌ 项 + `USER_TODO.md § A`（看自己被阻塞的决策状态）+ `PROJECT_STRUCTURE.md` |
| 审稿人 | `REVIEWER_TODO.md § A/§B` 最近 ⏳ 项 + 当前论文 PDF / 待审片段 + `idea.md`（理解 framing）+ `prompts/reviewer_prompt.md`（系统提示）；**不读历史 review**（保持每 batch 独立判断） |

新窗口 handoff（一行 ≤ 80 char）：

```
Goal: <one sentence>
Success criteria: <verifiable artifact>
Relevant files: <≤ 5 paths>
Confirmed findings: <facts already established>
Open risks: <known blockers>
Next step: <one sentence>
Role: user / scientist / engineer / reviewer
Last TODO check: <YYYY-MM-DD HH:MM>
```

## 6. 最低质量门槛

- 每次写新 .md / .tex / .py：完成后**用 ReadLints 检查**自己刚改的文件，无 lint error 才提交。
- 每次跑实验：**必须 cross-check** 数字与已存在的 ground truth（如果有），diff > 1e-4 必须解释。
- 每次改代码：**必须保留 reproducibility**（脚本 + seed + n_boot 都在文件名 / log 里）。
- 每次审稿：**必须按 [`prompts/reviewer_prompt.md`](../../prompts/reviewer_prompt.md) 中规定的结构化格式输出**，不接受纯散文形式。

## 7. 失败回滚协议

仅 commit-bearing 角色（用户 / 科学家 / 工程师）发现自己 commit 引入回归（如 PDF Overfull 新增 / 数字漂移 / 脚本崩溃 / 论文页数突破 8 页 / 编译失败）：

1. 立即在 `USER_TODO.md § A` 加一行 `U-Rollback-XXX`（并在 `SCIENTIST_TODO.md § A` 加 cross-reference）；
2. 在自己 TODO 把对应已完成项从 ✅ 退回 ⏳ 并加备注 `⚠ regressed: <原因>`；
3. 等用户拍板是否 git revert / amend / forward-fix。

> **审稿评分波动 ≠ 回滚触发**。reviewer batch 之间 overall 分数小幅波动（±0.5 / ±1.0）属于审稿人采样噪声，**不触发回滚**。科学家在 S-104 第 ② 步"不盲从"时**必须兼顾历史评分趋势**（参考 `artifacts/idea_reviews/scoreboard.md` 累积分布），单次小波动不能阻碍前进。仅当**多次连续 batch** 在同一 fix-theme 上指向真实退化时，才考虑用 7 的回滚机制。

## 8. 完成回报与等待

完成自己 TODO 所有可做项目后：

1. 给用户一份简明状态报告；
2. 等用户下指令；
3. 在等待期间不擅自跑额外实验、不擅自启动新全文 reviewer batch（局部 batch 见 §11.1）。

## 9. 论文图表分工

- **数学统计图**（柱形 / 箱形 / 折线 / 散点 / 热图等数据驱动图）：**科学家**用 Python 实绘 → `artifacts/figures/`，并落数据 provenance md。
- **概念示意图 / 逻辑流程图**（架构 / 流程 / state machine 等）：**用户**绘制；科学家**先写完整 prompt** 落 `docs/paper/figures_prompts/`，作为派给用户的 todo（在 `USER_TODO.md § B/§C` 加条目，并在 `SCIENTIST_TODO.md § B.3` 用 `tracking-XXX` 行追踪）。
- 任何 LaTeX 引用之前的 figure 必须有 `.pdf` 或 `.svg` vector 版本；纯 `.png` 仅做 in-doc 预览。

## 10. 论文精细打磨与本地 commit

每完成一次"论文精细打磨"动作（包括但不限于：合稿、章节级 rewrite、figure 嵌入、数字 finalize、校对扫错），**必须做一次本地 commit**：

- commit message 格式：`<task-ID>: <一句话目标>`，body 列受影响文件（≤ 6 个）；
- 便于后续 revert / blame / 投稿前回看修订史。

依赖：仓库需先 `git init`。如未 init，相关 commit 任务挂 `等用户决策 U-010` 状态，不强行 init。

## 11. 审稿人角色规范

> 审稿人是 idea04 协作的**第四个角色**。它有自己的 TODO 文件 [`REVIEWER_TODO.md`](../../docs/coordination/REVIEWER_TODO.md)，分两类任务：**全文审稿**（`R-FULL-XXX`，仅用户触发）+ **局部审稿**（`R-PART-XXX`，科学家/工程师可自触发）。

### 11.1 触发权限矩阵

| 任务类型 | 谁可以触发 | 用途 | 落点 |
|---------|-----------|------|------|
| **全文审稿** `R-FULL-XXX` | **仅用户** | 模拟独立 P5 oral gatekeeper 审整篇 PDF；投 ARR / EMNLP 前的合规复查 | `artifacts/idea_reviews/reviewer_<TS>_<NN>_<HASH>/` 完整 batch |
| **局部审稿** `R-PART-XXX` | **科学家 / 工程师**（自触发） | 审自己新写 / 新改的部分内容（如新 §3.7 rewrite、新嵌入 figure、新 ablation 段落） | `artifacts/idea_reviews/reviewer_<TS>_partial_<HASH>/`（轻量版） |

**红线**：科学家 / 工程师**不得**擅自启动**全文** batch（属 §4 红线）。**局部** batch 可自启，但必须在 `REVIEWER_TODO.md § B` 留行追踪（含审什么 / 触发原因 / 产物路径）。

### 11.2 输入 / 输出契约

完整 schema、字段定义、必填项**全部以 [`prompts/reviewer_prompt.md`](../../prompts/reviewer_prompt.md) 为准**（避免双源 drift）。本规则不重述字段细节。

详细 I/O 约定见 `REVIEWER_TODO.md § E`。

### 11.3 聚合状态（自动生成）

- `artifacts/idea_reviews/scoreboard.md` —— 历史所有 batch 的总平均分 / latest_overall / 评分分布
- `artifacts/idea_reviews/fix_themes.md` —— 跨 batch 聚合的 fix-themes 列表（去重后的开放反馈）
- `artifacts/idea_reviews/review_index.jsonl` —— 所有 batch 的 metadata 索引

聚合脚本：`scripts/summarize_idea_reviews.py` + `scripts/review_scoreboard.py`，在每次新 batch 落盘后由 scientist 触发。

### 11.4 hand-off：scientist S-104 强制循环

batch 完成 → **scientist 必须立即**按 `SCIENTIST_TODO.md § B.4 S-104` 的 4 步评估循环处理：

1. **通读**每篇 review 的关键字段（具体字段以 `prompts/reviewer_prompt.md` 为准）；
2. **不盲从** —— 逐条判断"这条意见是否真的有价值"；**必须兼顾历史评分趋势**（参考 `scoreboard.md` 的累积分布），单次评分小波动不能阻碍前进；
3. **诚实接受** —— 通过 ①② 筛选的意见加到 `SCIENTIST_TODO.md § C` 反馈追踪表 + 在 `§B.5` 创建对应的 `S-XXX` 修复 TODO；
4. **dissent log** —— 写下"为什么不接受 reviewer 某条意见"的理由到 `§C` 末，留存可复盘的 dissent log。

S-104 是**永久强制项**，永远不会被 ✅ 关闭，每次 batch 都重新触发一次。

### 11.5 审稿人不做的事

- ❌ batch 内不读历史 review（保持每 batch 独立、避免 confirmation bias；REVIEWER_TODO.md 本身只跟踪 batch 元数据，不缓存 review 内容）
- ❌ 不修改 `USER_TODO.md` / `SCIENTIST_TODO.md` / `implementation_log.md`（输出只落 `REVIEWER_TODO.md` + `artifacts/idea_reviews/`）
- ❌ 不擅自启动**全文** batch（必须用户批准，见 §11.1）
- ❌ 不参与 `§ A` 决策（只能在 review 中提建议，决策权仍在用户）

## 12. ID 命名约定（速查表）

**前缀按角色分配**（用户指令 2026-04-19）：`U-x` 用户 / `S-x` 科学家 / `E-x` 工程师 / `R-x` 审稿人。完整清单：

| ID 前缀 | 归属 TODO 文件 | 含义 | 例子 |
|---------|---------------|------|------|
| `U-XXX` | `USER_TODO.md § A`（权威源）+ `SCIENTIST_TODO.md § A`（cross-ref） | 用户路线决策 / 结构性 / 预算类 / scope 扩张 / 冻结 / 版本控制 | `U-003` 双稿合并 / `U-011` framing 走向 |
| `U-RES-XXX` | `USER_TODO.md § B.1` | 用户专属：API / Provider / 资源运维 | `U-RES-001` 充值 kuaipao.ai |
| `U-FIG-XXX` | `USER_TODO.md § B.2` | 用户专属：概念示意图绘制 | `U-FIG-001` Figure 1 |
| `U-REF-XXX` | `USER_TODO.md § B.3` | 用户专属：参考文献调研（领域记忆） | `U-REF-001` |
| `U-DIR-XXX` | `USER_TODO.md § B.4` | 用户专属：大方向 / framing 持续把握 | `U-DIR-001` |
| `U-Rollback-XXX` | `USER_TODO.md § A` + `SCIENTIST_TODO.md § A`（cross-ref） | 任意 commit-bearing 角色发现回归后挂的回滚决策（见 §7） | `U-Rollback-001` |
| `C-XXX` | `USER_TODO.md § C` | 科学家 / 工程师**派给用户**的具体 todo（dispatch inbox） | `C-001` 派给 USER 出 Figure 1 |
| `S-XXX` | `SCIENTIST_TODO.md § B`（B.1/B.2/B.3/B.4/B.5 子分组） | 科学家自己的写作 / hygiene / fix-TODO | `S-001` 双稿合并 / `S-104` 审稿反馈循环 |
| `E-XXX` | `docs/coordination/implementation_log.md` | 工程师工作项（未来新 phase block 用此前缀；历史 phase block 用 `[<descriptive-name>]` 不回写） | `E-001` (示例) |
| `R-FULL-XXX` | `REVIEWER_TODO.md § A` | 审稿人**全文**审稿任务（仅用户触发） | `R-FULL-001` |
| `R-PART-XXX` | `REVIEWER_TODO.md § B` | 审稿人**局部**审稿任务（科学家 / 工程师可自触发） | `R-PART-001` |
| `tracking-XXX` | 任意角色 TODO 表的"派工出去后追踪"行 | 派任务给别人后，在自己 TODO 留一行追踪"等 X 完成 Y" | `tracking-S-009`（科学家追踪工程师跑数）/ `tracking-C-001` |

**ID 编号约定**：

- 数字部分**全局递增**（`U-001` / `U-002` / ... 跨节通用），不重置。
- 一旦分配，**永不重用**（即使任务取消，ID 也保留为 `❌ cancelled` 状态行，便于历史追溯）。
- 新增 ID 时先 `Grep "<前缀>-"` 查最大编号，再 +1。
