# idea04 — Emergent Delegation Organization (EDO)

EMNLP long paper 仓库。研究**近似同质 LLM agent 在稀疏图上通过递归委派与递归验收形成分工组织**。
当前可执行原型 `Terminal-Consensus Peer Backpropagation (TCPB)` 是 Stage-1 受限实例。

---

## 1 分钟入口

| 你想做的事 | 应该读 |
|---|---|
| **理解项目全貌** | [`PROJECT_STRUCTURE.md`](./PROJECT_STRUCTURE.md) |
| **理解方法论** | [`idea.md`](./idea.md) |
| **跑实验前必读规范** | [`experiment.md`](./experiment.md) |
| **看当前论文稿** | [`docs/paper/EMNLP_paper_draft.md`](./docs/paper/EMNLP_paper_draft.md) |
| **看 EMNLP 2027 投稿要求** | [`docs/demand.md`](./docs/demand.md) |
| **看用户的 TODO + 决策池**（**权威源**） | [`docs/coordination/USER_TODO.md`](./docs/coordination/USER_TODO.md) |
| **看科学家的写作 TODO** | [`docs/coordination/SCIENTIST_TODO.md`](./docs/coordination/SCIENTIST_TODO.md) |
| **看工程实现日志（append-only）** | [`docs/coordination/implementation_log.md`](./docs/coordination/implementation_log.md) |
| **看每个 run 的状态标签** | [`artifacts/RUN_INDEX.md`](./artifacts/RUN_INDEX.md) |
| **看可执行 spec** | [`artifacts/edo_lite_executable_spec.md`](./artifacts/edo_lite_executable_spec.md) |
| **看 8-page 预算审计** | [`docs/paper/page_budget_audit.md`](./docs/paper/page_budget_audit.md) |
| **看论文图（Figure 2）** | [`artifacts/figures/fig2_backbone_sensitivity.pdf`](./artifacts/figures/fig2_backbone_sensitivity.pdf) |
| **看 Figure 1 概念图绘制 prompt** | [`docs/paper/figures_prompts/fig1_3action_policy_prompt.md`](./docs/paper/figures_prompts/fig1_3action_policy_prompt.md) |

---

## 顶层目录

```
idea04/
├── README.md              ← 你正在看这个
├── PROJECT_STRUCTURE.md   详细目录说明
├── idea.md                方法论（理论主对象）
├── experiment.md          实验执行规范（单一事实源）
│
├── docs/                  所有文档
│   ├── demand.md            EMNLP 投稿要求
│   ├── paper/               论文稿
│   ├── coordination/        协作 / TODO / 日志
│   └── archive/             历史文档（不再活跃）
│
├── configs/               所有实验 yaml + llm.json
├── prompts/               runtime prompt（被 methods.py 调用）
├── scripts/               跑数 / 校验 / 后处理 / reviewer loop
├── workspace/
│   ├── idea04_core/         真正的方法实现
│   └── autogen/             AutoGen 完整 clone（历史依赖）
│
├── artifacts/             所有跑数 + 论文资产 + reviewer 归档（2.5 GB）
├── data/                  MuSiQue Stage-2 备料
└── .cursor/               协作硬约束（必读）
    └── rules/
```

详细每个子目录的内容、状态标签、归档约定见 [`PROJECT_STRUCTURE.md`](./PROJECT_STRUCTURE.md)。

---

## 角色与协作

| 角色 | 入口文件 |
|---|---|
| 用户（总协调） | [`docs/coordination/USER_TODO.md`](./docs/coordination/USER_TODO.md) — §A 决策池（权威源）+ §B 人工执行 |
| 科学家（writing lead） | [`docs/coordination/SCIENTIST_TODO.md`](./docs/coordination/SCIENTIST_TODO.md) — §B–E 写作 TODO（§A 仅 cross-reference 到 USER_TODO） |
| 工程师 | [`docs/coordination/implementation_log.md`](./docs/coordination/implementation_log.md) — append-only 工程日志 |
| 审稿人（异步触发） | [`artifacts/idea_reviews/`](./artifacts/idea_reviews/) — 每 batch 独立 `reviewer_<...>/` 目录 + 聚合 `scoreboard.md` / `fix_themes.md`；用 [`prompts/reviewer_prompt.md`](./prompts/reviewer_prompt.md) 触发 |

协作规范硬约束：[`.cursor/rules/four-role-todo-workflow.md`](./.cursor/rules/four-role-todo-workflow.md)（4 个协作角色：用户 / 科学家 / 工程师 / 审稿人）。

---

## 论文资产约定

- **figure 最终交付** (`.pdf` / `.tex`)：`workspace/autogen/dotnet/website/articles/paper/`（用户指定，加 `paper/` 子目录避免污染 autogen 上游）
- **figure 工作区**（科学家实绘 + 数据 provenance）：`artifacts/figures/`
- **figure prompt**（用户出概念图前科学家先写 prompt）：`docs/paper/figures_prompts/`
- **rebuttal 记录**：⏳ 待 U-002 拍板（候选位置见 `SCIENTIST_TODO.md § A`）

### 谁画哪种图

- **数学统计图**（柱 / 箱 / 折 / 散点 / 热图）：科学家用 Python 实绘 → `artifacts/figures/`
- **概念示意图 / 逻辑流程图**：用户绘制；科学家先写完整 prompt → `docs/paper/figures_prompts/`
