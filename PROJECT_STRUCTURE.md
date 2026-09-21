# PROJECT_STRUCTURE - 论文协作项目结构索引

> AAMAS 2027 active entry points, updated 2026-09-16: read [REQUIREMENTS.md](docs/paper/aamas2027/REQUIREMENTS.md), then [AAMAS_TASKS.md](docs/coordination/AAMAS_TASKS.md). This pair supersedes historical scientific/venue plans and duplicated AAMAS queues below. Requirements live in the first file; gaps, task states, owner/dependency/acceptance criteria and execution links live in the second. Role TODO files remain historical indices and pointers. The current internal manuscript is `article/aamas2027/`; `article/latex/` is preserved EMNLP material.

> 维护者建议：科学家（writing lead）主维护本索引；工程师、审稿人和用户在路径变化时补充。
>
> 目标：让任意新协作者只读这一份文件，就能知道项目怎么推进、任务状态写到哪里、角色间交付文档放到哪里、论文编译边界在哪里。

---

## 0. 本文件只负责三件事

1. 定义稳定目录结构和命名约定。
2. 定义四类协作者的职责边界与入口文件。
3. 定义“状态、交付物、论文源文件、实验产物”分别应该落在哪里。

本文件不记录临时战况、某次实验进度、某个 reviewer 的完整意见、某天 blocked/unblocked 状态。这些内容必须进入对应 TODO、角色文档、实验产物或审稿归档。

---

## 1. 四角色协作边界

| 角色 | 负责什么 | 不能做什么 | 入口 |
|---|---|---|---|
| 用户 | 最终拍板、资源协调、范围/预算/提交决策 | 不需要维护所有技术细节 | `docs/coordination/USER_TODO.md` |
| 科学家 | 方法论、论文叙事、图表设计、证据入文、review 闭环 | 不静默替工程师改核心实现，不替用户拍板 | `docs/coordination/SCIENTIST_TODO.md` |
| 工程师 | 代码、实验、日志、结果校验、可复现执行链 | 不代写论文 framing，不替用户做路线决策 | `docs/coordination/ENGINEER_TODO.md` 或当前 legacy `docs/coordination/implementation_log.md` |
| 审稿人 | 独立评审、证据缺口、可执行反馈 | 不直接改论文正文/代码，不参与用户决策 | `docs/coordination/REVIEWER_TODO.md` |

核心原则：

- 决策有单一权威源：用户决策只进 `USER_TODO.md`。
- 任务有单一状态面：每个角色只维护自己的 TODO/log。
- 交流不靠聊天记忆：跨角色交付必须写成文件。
- 论文声称必须能追溯到实验、分析或审稿闭环。

---

## 2. 推荐目录结构

```text
idea04/
├── PROJECT_STRUCTURE.md              项目结构总索引
├── README.md                         1 分钟上手说明
├── idea.md                           研究问题、核心假设、方法草图
├── experiment.md                     实验原则、设置约束、评估规范
├── prompts/                          角色 prompt 与审稿模板
│   ├── ROLE_PROMPTS.md
│   ├── reviewer_template.md
│   └── reviewer_templates/            single-lens reviewer entrypoints and snippets
├── docs/
│   ├── coordination/                 任务状态与决策状态，只放“队列/状态”
│   │   ├── USER_TODO.md
│   │   ├── SCIENTIST_TODO.md
│   │   ├── ENGINEER_TODO.md
│   │   ├── REVIEWER_TODO.md
│   │   └── implementation_log.md      legacy 工程日志，待逐步迁移
│   ├── chats/                        轻量跨角色交流文档
│   │   ├── scientist/
│   │   ├── engineer/
│   │   ├── reviewer/
│   │   └── user/
│   ├── scientist/                    科学家生成的分析、写作交付、派工说明
│   │   ├── analysis/
│   │   ├── handoffs/
│   │   └── decisions/
│   ├── engineer/                     工程师生成的详细工程产物
│   │   ├── logs/
│   │   ├── results/
│   │   ├── runbooks/
│   │   └── handoffs/
│   ├── reviewer/                     审稿人生成的轻量索引/局部审稿说明
│   │   └── handoffs/
│   ├── user/                         用户输入、外部提交记录、资源说明
│   │   └── decisions/
│   ├── paper/                        论文相关说明、图表说明、补充分析
│   └── archive/                      历史文档与废弃方案
├── article/                          只放可编译论文需要的东西
│   ├── latex/                        LaTeX 源文件、bib、style
│   └── build/                        编译产物 PDF/log/aux
├── scripts/                          构建、实验、校验、后处理脚本
├── configs/                          实验配置、模型配置、环境配置
├── workspace/                        核心实现代码
├── data/                             数据集或数据索引
├── artifacts/                        实验输出、图表、统计结果、审稿归档
├── references/                       参考论文、笔记、调研资料
└── .cursor/rules/                    IDE/Agent 协作规则
```

说明：目录不必一次性建全，但一旦某类信息开始出现，就按上述位置落盘。

---

## 3. 状态面、交付面、证据面

### 3.1 `docs/coordination/` 是状态面

这里只放任务、阻塞、优先级、验收标准、结果链接。不要把长分析、长实验日志、长审稿全文塞进 TODO。

| 文件 | 用途 |
|---|---|
| `USER_TODO.md` | 用户决策池、用户专属任务、外部资源/提交事项 |
| `SCIENTIST_TODO.md` | 科学家写作、分析、审稿闭环、论文级修复队列 |
| `ENGINEER_TODO.md` | 工程师当前任务队列与关键状态索引 |
| `REVIEWER_TODO.md` | 审稿批次、局部审稿请求、review 产物索引 |
| `implementation_log.md` | 当前历史遗留工程日志；新详细日志应逐步落到 `docs/engineer/logs/` |

### 3.2 `docs/<role>/` 是角色交付面

凡是“某角色生成，供别人消费”的中间文档，都按作者归档：

- 科学家给工程师的任务背景：`docs/scientist/handoffs/S-XXX_to_engineer_<topic>.md`
- 工程师给科学家的结果总结：`docs/engineer/results/E-XXX_<topic>_summary.md`
- 工程师运行日志或事故复盘：`docs/engineer/logs/E-XXX_<topic>_log.md`
- 审稿人给科学家的局部审稿说明：`docs/reviewer/handoffs/R-PART-XXX_<topic>.md`
- 用户资源/提交说明：`docs/user/decisions/U-XXX_<topic>.md`

命名规则：

```text
docs/<author-role>/<type>/<ID>_<target-role>_<topic>_<YYYYMMDD>.md
```

其中 `<author-role>` 表示文档作者，不表示接收者。接收者写在文件名和正文 front matter 里。

### 3.3 `docs/chats/` 是轻量交流面

如果某段交流不是正式分析、结果或 runbook，但又会影响后续协作，就放到：

```text
docs/chats/<author-role>/<YYYYMMDD>_<from>_to_<to>_<topic>.md
```

`docs/chats/` 适合短 memo、裁决前摘要、交接说明；一旦内容成为正式证据或长期说明，应升级到 `docs/<role>/...` 或 `artifacts/...`。

### 3.4 `artifacts/` 是证据面

`artifacts/` 放机器生成或实验/审稿产物，包括实验输出、图表、统计结果、forensic 备份、review batch。每个 artifact 最好能回溯到脚本、配置、seed、数据切片或 reviewer prompt。

---

## 4. `article/` 的边界

`article/` 只放编译论文需要的东西：

- `article/latex/`：论文 `.tex`、`.bib`、`.sty`、局部 LaTeX include。
- `article/build/`：由构建脚本生成的 PDF、log、aux、bbl 等。

不要把实验日志、审稿记录、角色间 memo、临时草稿混入 `article/`。论文正文引用的图表可以来自 `artifacts/figures/`，但最终编译路径必须清晰可复现。

---

## 5. 推荐协作流

1. 科学家在 `idea.md` 和 `experiment.md` 明确 claim、证据需求和实验约束。
2. 用户在 `USER_TODO.md` 拍板范围、资源、预算、提交路线。
3. 科学家把工程任务写入 `ENGINEER_TODO.md`，并把完整背景写到 `docs/scientist/handoffs/`。
4. 工程师执行代码/实验，把详细日志写到 `docs/engineer/logs/`，结果总结写到 `docs/engineer/results/`，在 TODO 中只留状态和链接。
5. 科学家把工程结果转写进论文，并在 `SCIENTIST_TODO.md` 闭环。
6. 审稿人按 `prompts/reviewer_template.md` 独立评审，review batch 落到 `artifacts/idea_reviews/`。
7. 科学家执行 S-104：不盲从、不防御，诚实筛选真正有价值的 reviewer 反馈并派生修复任务。

---

## 6. ID 与优先级

所有跨角色任务都必须带 ID 和优先级。

| 前缀 | 所属角色 | 含义 |
|---|---|---|
| `U-XXX` | 用户 | 路线、预算、范围、提交等决策 |
| `C-XXX` | 用户 | 其他角色派给用户的执行项 |
| `S-XXX` | 科学家 | 写作、分析、图表、审稿闭环 |
| `E-XXX` | 工程师 | 实现、实验、验证、运行时修复 |
| `R-FULL-XXX` | 审稿人 | 用户触发的全文审稿 |
| `R-PART-XXX` | 审稿人 | 科学家/工程师触发的局部审稿 |

优先级统一使用 `P0` 到 `P3`：

- `P0`：停止当前线，先修 correctness / reproducibility / submission blocker。
- `P1`：当前关键路径。
- `P2`：重要但不阻塞当前主线。
- `P3`：可选 polish / 归档 / 清理。

---

## 7. 维护检查清单

每次修改模板时检查：

1. 路径是否与真实仓库一致，尤其是 `prompts/`、`article/latex/`、`article/build/`。
2. TODO 是否只保存状态，不承载长文档。
3. 角色生成的中间文档是否按作者进入 `docs/<role>/...` 或 `docs/chats/<role>/...`。
4. 工程日志和结果是否优先落到 `docs/engineer/logs/` / `docs/engineer/results/`。
5. 论文源文件和编译产物是否仍只在 `article/` 内。
6. 审稿 schema 是否只以 `prompts/reviewer_template.md` 为准。

---

## 8. 一句话原则

聊天负责推进，文件负责记忆；TODO 负责状态，`docs/<role>/` 负责交付，`artifacts/` 负责证据，`article/` 负责可编译论文。
