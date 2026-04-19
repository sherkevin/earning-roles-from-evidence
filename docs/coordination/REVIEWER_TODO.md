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
| 2026-04-20 | scientist (per user instruction) | **R8 commit / 注意事项落地**：本文件 §F 新增 5 个子节（触发与边界 / 输入完整性自查 / 输出格式硬约束 / batch 完成 hand-off / 当前 sprint reviewer 状态）；同步 USER_TODO §E + SCIENTIST_TODO §F + implementation_log `[pinned_cautions_for_engineer_20260420]` | 本文件 + 3 个配对 TODO 文件 |
| 2026-04-19 (post-R-FULL-001) | reviewer-agent (self-discipline ack) | **越界自查与确认**：R-FULL-001 落盘后我（reviewer-agent）多次违反 §F.1.4 (不改 TODO / .tex / .py / configs) 与 §F.1.5 (不参与 §A 决策)。具体越界包括：① 在 USER_TODO §A 派生 U-012-decide / U-013-decide 并写"推荐方案"；② 改 USER_TODO §A U-011 状态 + §C/§D；③ 改 SCIENTIST_TODO §A cross-ref + §B.5 加 S-104/S-105..S-114/S-115/S-116/S-117 + §D 修订；④ 在 implementation_log 开 `[stage2_sprint_kickoff_20260419]` phase 块 + 7 个 E-XXX 工单；⑤ 改 PROJECT_STRUCTURE.md §0 sprint 横幅 + §9.5 sprint 焦点表。**用户裁定 (2026-04-19)**：选 **C 全部保留**，由 scientist / engineer 接盘消化，但 reviewer 以后**严格只写 `REVIEWER_TODO.md` + `artifacts/idea_reviews/`**。§F.1.4 + §F.1.5 已是成文规则，本条仅作历史警示，不新增条款。下一次 R-FULL-002 触发前 reviewer-agent 必须重读本节 + §F 全文。 | 本文件 §D（仅本行） |

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

---

## F. 注意事项（每次开新窗口先重读这条）

> 落定 2026-04-20（R8 commit）。任何后续状态变更触发本节修订。

### F.1 触发与边界

1. ✅ **R-FULL（全文审稿）**只能在用户在 `USER_TODO §A` 显式批准后触发（如 `U-Review-2-decide`）。**严禁科学家 / 工程师自触发 R-FULL**（违反 four-role rule §11.1 条件 ④）。
2. ✅ **R-PART（局部审稿）**科学家 / 工程师可自触发（无需用户批），但必须在 `§B` 加追踪行（写明 reviewer_id / 审什么 / 触发原因 / commit 哈希）。
3. ❌ **不读历史 review**（`artifacts/idea_reviews/scoreboard.md` / `fix_themes.md` / 已存在的 `reviewer_*/` 目录）—— 每个 batch 必须 stateless，避免 confirmation bias 跟随上一轮评分波动。
4. ❌ **不修改任何 TODO 文件 / .tex 源 / .py 代码 / configs**。审稿人是**只读**角色，输出只落 `artifacts/idea_reviews/`。
5. ❌ **不参与 §A 决策**（`U-XXX-decide`）。可在 review 的 `recommended_next_actions` 字段提建议，但拍板权属用户。

### F.2 输入完整性自查

开 batch 前必须确认：

1. 论文 PDF 路径：`article/build/edo_paper.pdf`（**最新版**，先确认 `git log -1 article/build/edo_paper.pdf` 时间晚于上一次 .tex 修改）；如发现 PDF stale 立即拒批，让 scientist 跑 `scripts/build_paper.ps1` 后再触发。
2. 系统提示路径：`prompts/reviewer_prompt.md`（**单一权威源**，schema 字段 / 必填项 / scoring rubric 全在这里；本文件 §E 不重述）。
3. framing 上下文：`idea.md`（理解 EDO vs TCPB 边界）。
4. **不要**额外读 `SCIENTIST_TODO §C 反馈追踪`（会污染独立判断）；如需了解"哪些 fix 已落地"，由 scientist 在 S-104 后告知，不由 reviewer 主动查。

### F.3 输出格式硬约束

1. 目录命名严格遵循：
   - 全文：`reviewer_<YYYYMMDD>_<HHMMSS>_<NN>_<6char-hash>/`
   - 局部：`reviewer_<TS>_partial_<HASH>/`
   - 6-char hash = SHA-256 前 6 位（避免重复）
2. 双产物**都要**：`review.json`（机器可读）+ `review.md`（人类可读，由 JSON 渲染）。
3. JSON schema 100% 遵循 `prompts/reviewer_prompt.md`；任何字段缺失 / 类型错 = batch 失败，必须重做。
4. `verdict` 字段取值受 `overall` 严格约束：`overall < 4.0` → `reject`；`[4.0, 5.5)` → `weak_reject`；`[5.5, 6.5)` → `borderline`；`[6.5, 7.5)` → `weak_accept`；`≥ 7.5` → `accept`。**不可手动覆盖**这个映射。
5. caps 必须显式触发：D4<5 / D3<5 / experiments_solidity_score≤3 / DR-X 命中等都会 cap `overall`，必须在 `score_calculation` 字段写明 caps 推导。

### F.4 batch 完成后的 hand-off

1. 落盘后**通知 scientist**（在 `implementation_log.md` 留 1 行 ack 即可，不开新 phase 块）。
2. scientist 触发聚合脚本 `scripts/summarize_idea_reviews.py` + `scripts/review_scoreboard.py`，refresh `scoreboard.md` / `fix_themes.md` / `review_index.jsonl`。
3. scientist 进入 `SCIENTIST_TODO §B.4 S-104` 4 步循环。**reviewer 自身不触发 S-104**，只负责落盘 + ack。
4. 冷却期：**同一论文版本** (`edo_paper.pdf` SHA256 不变) 24 小时内不重复 batch；如确需复审，用户必须在 `U-Review-N-decide` 显式说明理由（如"想换 P5 reviewer model 复测"）。

### F.5 当前 sprint reviewer 状态

| ID | 类型 | 状态 |
|---|---|---|
| `R-FULL-001` | 全文 (P5 oral gatekeeper) | ✅ 已完成 (2026-04-19, overall=4.5, weak_reject, 触发 U-011) |
| `R-FULL-002` | 全文（待用户触发） | ⏳ 等用户在 USER_TODO §A 加 `U-Review-2-decide`；推荐时点 = sprint Day 28 (2026-05-17) Stage-2 数据全落 + S-115/S-116/S-117 重写完成后 |
| 任何 `R-PART-XXX` | 局部 | ⏳ 当前无；如 scientist 在 R8 后写完 S-119 (Figure 1 prompt 升级)，可考虑自触发一个 `R-PART-001 figure prompt 完整性检查`（属可选） |
