# REVIEWER_TODO — 审稿人工作清单

> 维护者：审稿人。
> 创建日期：2026-04-19。
> 当前位置：`docs/coordination/REVIEWER_TODO.md`。
> 协作规范：[`.cursor/rules/four-role-todo-workflow.mdc`](../../.cursor/rules/four-role-todo-workflow.mdc) §11（英文版 + Cursor `.mdc` 规范）。
> 配对文件：[`USER_TODO.md`](./USER_TODO.md)、[`SCIENTIST_TODO.md`](./SCIENTIST_TODO.md)、[`implementation_log.md`](./implementation_log.md)；批量审稿归档：[`artifacts/idea_reviews/`](../../artifacts/idea_reviews/)。

---

## 0. 角色边界（每次重读）

我（审稿人）做：

- **全文审稿（`R-FULL-XXX`）**：对当前论文 PDF 完整审稿，模拟独立 P5 oral gatekeeper 视角；产物含完整 schema 字段（见 `prompts/reviewer_prompt.md`）。**仅用户在 `USER_TODO.md § A` 显式批准后触发**。
- **局部审稿（`R-PART-XXX`）**：对部分内容审稿（如新写的 §3.7 / 新嵌入的 figure / 新增 ablation 段落 / 一段重写的 framing）；产物可只覆盖 schema 子集。**科学家 / 工程师可自触发**（无需用户批准），但必须在本文件 §B 留行追踪。
- 输出落 `artifacts/idea_reviews/reviewer_<YYYYMMDD>_<HHMMSS>_<NN>_<6char-hash>/` 目录（全文）或 `reviewer_<TS>_partial_<HASH>/` 目录（局部）。
- batch 内 stateless：写新审稿时**不读历史 review**，避免 confirmation bias。

我**不做**：

- 修改论文 .tex / .md
- 修改 `USER_TODO.md` / `SCIENTIST_TODO.md` / `implementation_log.md`
- 参与 `§ A` 决策（只能在 review 中提建议）
- 跑实验 / 改 core code
- 擅自启动**全文** batch（必须用户批准）

---

## A. 全文审稿任务（`R-FULL-XXX`，仅用户触发）

> 工作流：用户在 `USER_TODO.md § A` 加一行 `U-Review-XXX`（或类似）批准 → 触发本节加一行 `R-FULL-XXX` → 审稿 → 产物落 `artifacts/idea_reviews/reviewer_<TS>_<NN>_<HASH>/` → scientist 触发 `S-104` 4 步循环。

| ID | 触发日期 | 论文版本 | 用户批准 ID | 产物路径 | 状态 |
|---|---|---|---|---|---|
| **R-FULL-001** | 2026-04-19 | `edo_paper.pdf` (commit 待 git init 后补 SHA) | (历史 batch，先于本规范创建) | `artifacts/idea_reviews/reviewer_20260419_163139_01_9e72f7/` | ✅ 完成（overall=4.5, weak_reject, 触发 U-011） |

---

## B. 局部审稿任务（`R-PART-XXX`，科学家/工程师可自触发）

> 工作流：科学家 / 工程师写完 / 改完局部内容 → 在本节加一行 `R-PART-XXX`（注明：审什么 / 触发原因 / 哪个 commit 或文件 hash）→ 审稿 → 产物落 `artifacts/idea_reviews/reviewer_<TS>_partial_<HASH>/`。无需用户批准。

| ID | 触发日期 | 谁请求 | 审什么（具体 §/figure/段落） | 触发原因 | 产物路径 | 状态 |
|---|---|---|---|---|---|---|
| _(空)_ | _(待用)_ | _(scientist/engineer)_ | _(例如：§3.9 R1-R3 是否清晰)_ | _(例如：刚 inline 压缩完，担心信息丢失)_ | `artifacts/idea_reviews/reviewer_<TS>_partial_<HASH>/` | _(待用)_ |

---

## C. 已完成（按日期倒序）

| 日期 | ID | 任务 | 产物 / 关键发现 |
|---|---|---|---|
| 2026-04-19 | R-FULL-001 | 首次本仓库内独立 P5 oral gatekeeper 全文审稿 | overall=4.5 / weak_reject / oral_eligible=false / experiments_solidity_score=0；指出 Finding 4 自证伪 → 触发 U-011-decide framing 走向决策 |

---

## D. 修订记录

| 日期 | 谁 | 动作 | 产物 |
|---|---|---|---|
| 2026-04-19 | engineer (per user instruction) | 创建本文件；明确 R-FULL（仅用户触）vs. R-PART（科学家/工程师可自触）的双轨；接管 `artifacts/idea_reviews/` 历史 batch 元数据 | 本文件 + `four-role-todo-workflow.md §11` 规范引用本文件 |

---

## E. 输入 / 输出契约

### E.1 输入

- **论文**：当前 PDF（`article/build/edo_paper.pdf`，由 `scripts/build_paper.ps1` 生成）；局部审稿可只输入待审片段（如某 §的 markdown 源、某 figure 的 PDF）。
- **framing 上下文**：`idea.md`（理解 EDO vs TCPB 边界与方法论 framing）。
- **系统提示与 schema**：[`prompts/reviewer_prompt.md`](../../prompts/reviewer_prompt.md) 是**单一权威源**，定义所有结构化字段、必填项、取值约束、scoring rubric。本文件**不重述** schema 内容（避免双源 drift）。

### E.2 输出

- **全文审稿（`R-FULL-XXX`）**：
  - 落点：`artifacts/idea_reviews/reviewer_<YYYYMMDD>_<HHMMSS>_<NN>_<6char-hash>/`
  - 必有产物：完整结构化 review（机器可读）+ 人类可读版本
  - Schema：以 `prompts/reviewer_prompt.md` 为准（含 `overall` / `verdict` / `top_weaknesses` / `oral_eligible` / 等所有强制字段）
- **局部审稿（`R-PART-XXX`）**：
  - 落点：`artifacts/idea_reviews/reviewer_<TS>_partial_<HASH>/`
  - 必有产物：覆盖 schema 子集的结构化 review + 人类可读版本
  - 子集最少必含：审什么 / 通过/不通过 / 主要 weakness（如有）/ 修复建议
  - 不强制 `overall` 评分（局部审稿无法对论文整体评分）

### E.3 聚合

batch 完成后由 scientist 触发 `scripts/summarize_idea_reviews.py` + `scripts/review_scoreboard.py`，自动 refresh：

- `artifacts/idea_reviews/scoreboard.md`（历史评分趋势）
- `artifacts/idea_reviews/fix_themes.md`（去重后的开放反馈）
- `artifacts/idea_reviews/review_index.jsonl`（所有 batch 元数据）

### E.4 hand-off：scientist S-104 强制循环

batch 落盘后必须 → scientist 进入 `SCIENTIST_TODO.md § B.4 S-104` 4 步循环：通读 → 不盲从（**兼顾 `scoreboard.md` 历史趋势**，单次评分小波动不阻碍前进）→ 诚实接受 → dissent log。详见 `four-role-todo-workflow.mdc §11.4`。
