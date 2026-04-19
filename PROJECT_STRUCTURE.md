# PROJECT_STRUCTURE — 项目目录鸟瞰图

> 维护者：科学家（writing lead）。这是项目的**单一索引文件**，新人 / 新窗口接手时**只读这一份**就能定位所有内容。
> 创建日期：2026-04-19  最后更新：2026-04-20（R36 commit：user 双拍板 — **U-022-decide:a** 锁定 Axis A Tier-1 = MA-RAG + ReAgent；**U-021-decide:user-override** 维持 Appendix 放最后 (Path B Stand pat) 不 chase reviewer 严读 demand.md §2 的意见；scientist S-144 1h checkpoint 发现 engineer 已主动 launch E-018 step 1 clone + E-010/E-015 install ✅ done; E-017 seed=42 stage2 = ✅ DONE / stage1 = 76.9% running；scientist 把 MA-RAG vllm 重 install + dpr100 corpus pitfall (C-8 hit) + ReAgent 无 requirements.txt 等 intel 落 implementation_log 让 engineer next session 有 head start）。
> 任何目录新增 / 重命名 / 归档必须同步更新本文件。

---

## 0. 本仓库是什么

EMNLP long paper —— **`Emergent Delegation Organization (EDO)`**：研究近似同质 LLM agent 在稀疏图上通过递归委派与递归验收形成分工组织。
当前可执行原型 **`Terminal-Consensus Peer Backpropagation (TCPB)`** 是 Stage-1 受限实例。

> **🚀 Sprint Day 1.5 已闭合 + Day 2- active（2026-04-20，R17）**：用户已批
> - U-011 (b) + U-012 **R1+R2+R3** + U-013 **MuSiQue** + U-EXEC-006 **newapi key**
> - U-014 **2 hosts (AutoGen+ChatEval)** + U-015 **R2+R3 swap (SWAP-1+SWAP-3)** + U-016 **drop E-007**
> - **U-018 ⚡ R17：3rd host = MAD** → 外部 baseline N=2 → **N=3 (AutoGen + ChatEval + MAD)**；SWAP-4 (R2 audit → MAD `final_aggregator`) 升为主体；新派 **E-015** (reproduce MAD) + **E-016** (R2 audit swap into MAD aggregator)
>
> **Day 1 ✅** = E-001 task_tree + E-008 newapi probe + E-013 SSH server probe。
> **Day 1.5 ✅** = E-002 action_policy + E-003 audit_runtime + E-004 persona_model + E-009 external baseline survey（详见 `[engineer_day1_5_completion_20260420]` + `[E-002/E-003/E-004/E-009_done_*]` 子条；3-4 d ahead of schedule，省下的 buffer 直接吸收 R17 +5 d MAD 工作量）。
>
> **Day 2- active P0** = 多线并行：
> - (a) E-005 (Stage-2 fullval HotpotQA + MuSiQue) — `[E-005_stage2_integration_20260420]` 进行中
> - (b) E-010 (reproduce AutoGen + ChatEval × 2) → 解锁 E-011 / E-012
> - (c) **E-015 (reproduce MAD)** ⚡ NEW — 解锁 E-016
> - (d) E-014 (gpt-4.1-mini Table 2 ablation rerun，R-FULL-002 fix)
>
> **外部 baseline workstream** = `[external_baseline_workstream_20260420]` + `[external_baseline_decisions_landed_20260420]` + `[u_018_mad_landed_20260420]`（R17 子条）共同覆盖 E-009 ✅ + E-010 + E-011 + E-012 + E-015 + E-016 = 6 工单（survey ✅ + reproduce × 3 + swap adapter × 3 + comparison run × 3）。Planning 主文档：[`docs/paper/external_baseline_plan.md`](docs/paper/external_baseline_plan.md)（R17 update 含 §3.2 N=3 + §4 SWAP-4 active + §6 timeline +5 d）。
>
> **目标**：EMNLP 2026 ARR May 25 deadline = T-35（unchanged）。Day 1.5 提前关闭省的 3-4 d 与 R17 +5 d 净对冲后，buffer 仍 ~4-5 天。
>
> 详见 [`docs/coordination/USER_TODO.md`](docs/coordination/USER_TODO.md) `§A,§C` + [`docs/coordination/SCIENTIST_TODO.md`](docs/coordination/SCIENTIST_TODO.md) `§B.5` + [`docs/coordination/implementation_log.md`](docs/coordination/implementation_log.md) `[u_018_mad_landed_20260420]` 末块。

| 角色 | 文件入口 |
|---|---|
| **方法论 / framing** | `idea.md` |
| **论文 LaTeX 源（写作目标）** | `article/latex/edo_paper.tex` |
| **论文 PDF 产物** | `article/build/edo_paper.pdf`（main body 8 pages COMPLIANT） |
| **论文构建脚本** | `scripts/build_paper.ps1`（一键 latexmk + 自动检测 8 页合规） |
| **EMNLP 投稿要求** | `docs/demand.md` |
| **实验执行规范** | `experiment.md` |
| **可执行 spec（Stage-1）** | `artifacts/edo_lite_executable_spec.md` |
| **用户 TODO + 决策池**（**权威源**） | `docs/coordination/USER_TODO.md` |
| **科学家 TODO**（§A 仅 cross-reference 到 USER_TODO） | `docs/coordination/SCIENTIST_TODO.md` |
| **工程实现日志** | `docs/coordination/implementation_log.md` |
| **审稿人 TODO**（R-FULL 全文仅用户触 / R-PART 局部科学家工程师可自触） | `docs/coordination/REVIEWER_TODO.md` |
| **审稿人 batch 归档**（每 batch 独立目录） | `artifacts/idea_reviews/reviewer_<YYYYMMDD>_<HHMMSS>_<NN>_<hash>/` + 聚合 `scoreboard.md` / `fix_themes.md` |
| **审稿人系统提示 + schema 单一源** | `prompts/reviewer_prompt.md` |
| **历史 Markdown 论文稿（不再维护）** | `docs/paper/EMNLP_paper_draft.md` |

---

## 1. 根目录文件清单（极简，仅 4 个）

| 文件 | KB | 类别 | 谁维护 | 状态 |
|---|---:|---|---|---|
| `README.md` | 2.7 | 1 分钟入口 | 科学家 | active |
| `PROJECT_STRUCTURE.md` | (this) | 详细目录索引 | 科学家 | active |
| `idea.md` | 42.6 | 方法论 | 科学家 | active — Session 6 已 tighten phi(z)/utility/persona |
| `experiment.md` | 11.2 | 实验规范 | 用户 + 科学家 | active — backbone 已锁定 `gpt-4.1-mini` |

**为什么 `idea.md` / `experiment.md` 留在根**：被 `implementation_log.md`、各历史 task 文件、论文稿等 15+ 处通过纯文件名引用；移入子目录会破坏所有反向引用。Phase 2 再处理（U-008-decide）。

---

## 2. 顶层目录职责

| 目录 | 用途 | 大小 | 进入入口 |
|---|---|---:|---|
| `.cursor/rules/` | 工作流硬约束（persistent-chat / three-role-workflow / ssh-server） | <1 MB | 进新窗口必读 |
| `.specstory/` | Cursor 内部对话历史（自动生成） | — | 不要手动改 |
| `docs/` | **所有文档**（论文 / 协作 / 归档 / EMNLP 要求） | <1 MB | §3 |
| `configs/` | 所有实验 yaml + `llm.json` 模型清单 | <1 MB | §4 |
| `data/` | MuSiQue validation jsonl（Stage-2 备料） | 56 MB | 当前未使用 |
| `prompts/` | 主 agent runtime prompt + 单文件 reviewer prompt（人工审稿用） | <1 MB | `main_agent_prompt.txt`（runtime）+ `reviewer_prompt.md`（人工审稿） |
| `references/emnlp/` | **EMNLP 2024/2025 高质量 long paper 参考库**（42 PDF：6 Best + 27 Outstanding + 9 其他奖项） | 140 MB | [`references/emnlp/INDEX.md`](./references/emnlp/INDEX.md) |
| `scripts/` | 跑实验 / 校验日志 / 后处理 / reviewer loop | <1 MB | §5 |
| `workspace/idea04_core/` | **真正的方法实现**（contracts / methods / runner / llm_client） | <1 MB | §6 |
| `workspace/autogen/` | AutoGen 完整 git clone | 56 MB | runner 不直接 import；`dotnet/website/articles/` 由用户指定为论文资产存放点 |
| `artifacts/` | 所有跑数 run dir + 论文资产 + reviewer 归档 | **2.5 GB** | §7 |

---

## 3. `docs/` —— 所有文档

```
docs/
├── demand.md                  EMNLP 2027 long paper 投稿要求（用户提供）
├── paper/
│   ├── EMNLP_paper_draft.md   ⚠ 历史 markdown 副本（U-003 已隐式 ✅；写作目标已切到 `article/latex/edo_paper.tex`）
│   ├── benchmark_inventory.md   **benchmark 唯一权威说明文档**（datasets + baselines + topologies + backbones + sample sizes + module-swap + status table；R34 commit；R35 §3.3 加 Axis A SOTA finalists）
│   ├── sota_baseline_survey_2026.md   ⚡ R35 NEW — full-system SOTA 调研（11 candidates → Tier-1 MA-RAG + ReAgent finalists）+ 2-axis design rationale
│   ├── external_baseline_plan.md   外部 baseline 选型 + module-swap 设计 + 时间线（含 SWAP-1/3/4 + N=3 hosts；R35 §10 cross-link 加 sota_baseline_survey_2026.md）
│   ├── page_budget_audit.md   S-011 产出：vs demand.md §5 的差距清单 + 压缩计划
│   └── figures_prompts/       论文图表的 prompt + caption 草稿
│       ├── fig1_3action_policy_prompt.md   Figure 1 概念图 prompt（user 出图）
│       └── fig2_caption_draft.md           Figure 2 caption（asset 已就绪）
├── coordination/              协作 / TODO / 日志（用户 + 科学家 + 工程师 + 审稿人 四角色）
│   ├── USER_TODO.md              **用户决策池 + 用户专属工作（权威源）**
│   │                              §A：U-XXX 路线决策（用户拍板）
│   │                              §B：U-RES/U-FIG/U-REF/U-DIR 用户专属工作
│   │                              §C：C-XXX 派给用户的具体 todo（dispatch inbox）
│   ├── SCIENTIST_TODO.md         科学家写作 TODO（§B–E；§A 仅 cross-reference 到 USER_TODO）
│   ├── REVIEWER_TODO.md          **审稿人工作清单**：R-FULL（仅用户触）+ R-PART（科学家/工程师可自触审局部内容）
│   ├── implementation_log.md     工程实现日志（append-only，工程师维护，新 phase 用 E-XXX 前缀）
│   └── COORDINATION_AGENT1_AGENT2.md  早期工程师 1 ↔ 2 分工约定（archive 候选）
└── archive/                   历史文档（不再活跃，保留 git history）
    ├── engineer_prompt.md                       原 short paper 工程师启动提示词
    ├── research-report.md                       一次外部对话整理
    └── 04_thought_communication_design.md       项目背景文档（原文件名 GBK 乱码，已 rename）
```

注：早期 `agent-1/2/3-task.md` + `agent-1/2/3-summary.md` 6 份 coordination 文件已被用户在 2026-04-19 之前清理。

---

## 4. `configs/` —— 17 个 yaml + 1 个 json

按 backbone × 实验包分组：

| 组 | 文件 | 用途 |
|---|---|---|
| **模型清单** | `llm.json` | 所有 backbone + key + endpoint 的单一事实源 |
| **GLM Stage-1 主线** | `round1_hotpotqa.yaml` | chain-200 / fullval 通用入口（`main_model` 已被改为 `gpt-4.1-mini`） |
| | `round1_hotpotqa_star.yaml` | star 拓扑 |
| **GLM 机制 ablation** | `round1_hotpotqa_ablation_evidence.yaml` | 放大 evidence window |
| | `round1_hotpotqa_ablation_no_tcpb.yaml` | 关闭 TCPB 终局更新 |
| | `round1_hotpotqa_ablation_no_gate.yaml` | 关闭 decomposer 多跳门控 |
| **GLM 敏感性** | `round1_hotpotqa_sensitivity_margin_low.yaml` | accept_margin=0.01 |
| | `round1_hotpotqa_sensitivity_margin_high.yaml` | accept_margin=0.04 |
| | `round1_hotpotqa_sensitivity_gate_low.yaml` | gate_threshold=0.80 |
| | `round1_hotpotqa_sensitivity_gate_high.yaml` | gate_threshold=0.95 |
| **gpt-4.1-mini 主线** | `round2_gpt41mini_chain200.yaml` | **chain-200 canonical 入口** |
| | `round2_hotpotqa_gpt41mini.yaml` | 备用，未广泛使用 |
| **MuSiQue 预备** | `round2_musique.yaml` | Stage-2 预留，未启用 |
| **smoke / backbone 验证** | `smoke_gpt41mini.yaml` | 10 样本 backbone smoke |
| | `smoke_integrity_glm.yaml` | runtime guard 验证用 GLM smoke |
| | `smoke_nvidia_llama33_70b.yaml` | NVIDIA backup supplier check |
| **遗留** | `round0_hotpotqa.yaml` | 🟡 Round0 冒烟阶段，已被 round1 取代 |
| | `huggingface.yaml` | 🟡 早期 HF token 占位，未使用 |

---

## 5. `scripts/` —— 21 个脚本

按调用链分组：

| 组 | 脚本 | 备注 |
|---|---|---|
| **主跑数** | `run_round1_v3.py` | **当前权威入口**，支持 `--methods`、`--resume-run-dir`、`--merge-summary-only` |
| | `run_round0_smoke.py` | 旧冒烟入口，仍被 ROUND0_METHODS 5 方法回归引用 |
| **数据准备** | `export_hotpot_seed.py` | 从 HotpotQA 导出 N 条 validation 样本 |
| | `download_musique.py` | Stage-2 预备，下载 MuSiQue |
| **校验** | `validate_logs.py` | **每个 run dir 强制走一遍**，硬性保证 12 类核心 jsonl 完整 |
| | `_audit_fullval.py` | fullval 损坏 forensic（脏数据 forensic only） |
| | `_negative_smoke_guard.py` | runtime integrity guard 反向测试 |
| | `f1_significance_audit_round1.py` | F1 显著性自审（4 项查检） |
| **后处理** | `compute_paired_bootstrap.py` | 配对 bootstrap CI + 符号检验 |
| | `collect_run_metrics.py` | 把 run dir 里的 metrics.json 合并为 csv + md |
| | `post_fullval_chain.ps1` | validate + bootstrap + merge 一键串联 |
| | `check_fullval_checkpoint.ps1` | 进度监控 |
| | `watch_fullval_and_postprocess.ps1` | 自动后处理触发 |
| **绘图** | `plot_dynamics.py` | competence 时序 / multi-run snapshot |
| | `plot_round1_f1_vs_tokens.py` | F1 vs token 散点 |
| | `plot_fig2_backbone_sensitivity.py` | **Figure 2 论文图**：chain-200 backbone-sensitivity 柱状图（GLM vs gpt-4.1-mini × 3 方法 + peer fullval star） |
| **reviewer 归档处理** | `summarize_idea_reviews.py` | 归并 review.json → fix_themes.md（只读历史 archive） |
| | `review_scoreboard.py` | 算总平均分 → scoreboard.md（只读历史 archive） |
| **辅助** | `idea04_paths.py` | 公共路径常量 |
| | `analyze_round0.py` | 历史，已不调用 |
| | `bootstrap_round0.py` | 历史，已不调用 |
| | `autogen_topology_smoke.py` | 历史 AutoGen 拓扑冒烟 |

注：`scripts/review_idea_with_remote_llm.py`（远端 LLM 审稿调用脚本）已于 2026-04-19 删除；当前审稿改为**人工**用 `prompts/reviewer_prompt.md` 复制粘贴到 LLM。归档处理脚本 (`summarize_idea_reviews.py` + `review_scoreboard.py`) 仍可读 `artifacts/idea_reviews/` 内的 21 篇历史 review。

---

## 6. `workspace/idea04_core/` —— 方法实现

| 模块 | KB | 职责 |
|---|---:|---|
| `contracts.py` | 1.9 | `HandoffPacket` / `AgentOutput` 等数据对象 schema |
| `methods.py` | 32.4 | **方法注册表**：6+ baseline + TCPB peer 路由策略 + competence 更新规则 |
| `runner.py` | 28.9 | runtime：parallel worker + checkpoint/resume + jsonl 日志 + post_sample 更新 |
| `llm_client.py` | 13.9 | 多 provider 客户端 + `ModelDriftError` runtime guard |
| `llm_providers.py` | 9.4 | provider 路由表（GLM / oversea / NVIDIA） |
| `evaluation.py` | 0.9 | HotpotQA EM / F1 计算 |

---

## 7. `artifacts/` —— 跑数 + 论文资产

总大小 **2.5 GB**。详细每个 run dir 的状态标签见 [`artifacts/RUN_INDEX.md`](./artifacts/RUN_INDEX.md)。本节只给一级分组：

| 子目录 | 用途 | 状态 |
|---|---|---|
| `seed/` | 4 个 HotpotQA samples 文件（200 / 7405 / train） | active，论文必引 |
| **mainline 跑数（当前论文证据来源）** | | |
| `round2_gpt41mini/` | **chain-200 canonical** (gpt-4.1-mini) | ⭐ canonical |
| `round2_gpt41mini_fullval/` | fullval (gpt-4.1-mini)，**peer valid + static/self corrupted** | ⚠ partial valid |
| **archived Stage-1 GLM 跑数** | | |
| `round1/` | GLM chain × 17 run dirs（含 fullval n=7405） | archived |
| `round1_star/` | GLM star × 2 run dirs | archived |
| `round1_gpt41mini_baseline/` | 早期 gpt-4.1-mini smoke | archived |
| **机制 / 敏感性 ablation** | | |
| `round1_ablation_baseline/` | refreshed v3 baseline | archived guidance-only |
| `round1_ablation_evidence/` `_nogate/` `_notcpb/` | 三组 mechanism ablation | archived guidance-only |
| `round1_sensitivity_margin_*` `_gate_*` (×5) | 权重敏感性 | archived guidance-only |
| **runtime 验证 / 供应商 fallback** | | |
| `model_backbone_check/` | gpt-4.1-mini 接通 smoke | reference |
| `provider_fallback_check/` | NVIDIA backup supplier 评估 | reference |
| `runtime_integrity_guard/` `runtime_guard_smoke/` | ModelDriftError 正负 smoke | reference |
| **smoke 残留** | | |
| `round1_smoke_live/` `round1_smoke_new/` `round1_smoke_parallel/` | 三个 smoke 残留（共 0.1 MB） | 🟡 dead，camera-ready 后清 |
| `round0/` `round2/` | 旧冒烟 + 占位 | 🟡 round2 是 0 MB ghost |
| **顶层 md / 论文资产** | | |
| `edo_lite_executable_spec.md` | Stage-1 可执行 spec | active，论文 §3.7 + Algorithm 1 引用 |
| `figures/` | **论文最终图（vector+raster）** | active |
| └─ `fig2_backbone_sensitivity.{png,pdf}` | Figure 2 论文图（科学家出） | active |
| └─ `fig2_backbone_sensitivity_data.md` | Figure 2 单一事实源数据 provenance | active |
| `round1_v3_main_table*.csv` `round1_v3_paired_stats*.csv` | 主表 + 配对统计 | active |
| `round1_v3_statistics*.md` `round1_v3_*_metrics.md` | 各方法统计说明 | active |
| `round1_v3_mechanism_ablations.md` `round1_v3_weight_sensitivity.md` | mechanism / sensitivity 报告 | active |
| `round1_v3_central_orchestrator_metrics.md` | CO 基线分析 | active |
| `round1_v3_self_reflect_analysis.md` `round1_v3_usage_appendix.md` | self-reflect / usage 附录 | active |
| `runtime_integrity_guard_note.md` | 供应商 drift 协调 note | active |
| `round1_*.png` `round1_v3_*.png` | 4 张早期论文图候选（dynamics / F1-vs-tokens） | active |
| `idea_reviews/` | 21 份 reviewer 归档 + scoreboard + fix_themes | active |

注：原根目录 `artifacts/COORDINATION_AGENT1_AGENT2.md` 已迁移到 `docs/coordination/`。

---

## 8. `article/` —— 论文 LaTeX 工程目录（**写作主入口**）

**2026-04-19 用户指令**："你要负责论文的编写，每次都写到 latex 模版里然后编译"。论文写作目标已切换为 `article/latex/edo_paper.tex`。

```
article/
├── latex/
│   ├── edo_paper.tex            ⭐ 主写作文件（41 KB；EDO long paper 单稿）
│   ├── acl.sty                  官方 ACL 样式表（不可改）
│   ├── acl_natbib.bst           bibtex 样式
│   ├── acl_latex.tex            ACL 模板原版（参考用，不动）
│   ├── acl_lualatex.tex         lualatex 模板（参考用）
│   └── custom.bib               用户自定义 bibtex 条目
├── build/                       latexmk 中间产物（.aux/.bbl/.fls/.log/.out/.fdb_latexmk）+ PDF
│   └── edo_paper.pdf            ⭐ 论文 PDF（334 KB，**main body 8 pages COMPLIANT**）
├── anthology.bib.txt            ACL Anthology bibtex（占位）
├── formatting.md                ACL 格式说明
├── README.md                    ACL 模板原 README
└── Association_for_Computational_Linguistics__ACL__conference.zip   原始模板压缩包
```

**编译入口**：`powershell -NoProfile -File scripts/build_paper.ps1`（带 `-Clean` 可清干净中间产物重建）。该脚本会：
1. 跑 `latexmk -pdf -output-directory=article/build article/latex/edo_paper.tex`
2. 解析 .log 提取页数 / overfull / underfull 数量
3. 用 `pdftotext` 自动定位 Limitations 起始页，**判定 main body ≤ 8 页**则报 COMPLIANT，否则告警

**论文 figure 引用**：`\graphicspath{{../../artifacts/figures/}}` 已设，所以 `\includegraphics{fig2_backbone_sensitivity.pdf}` 直接生效。

注：早先 `workspace/autogen/dotnet/website/articles/` 曾被指定为论文资产存放点，但实际工程师选择并验证的是更轻、更标准的 `article/` 目录，不动 autogen submodule。⚠ rebuttal 记录**不放**这里，落点待 U-002-decide 拍板。

---

## 9. 四角色协作文件分布

> 协作规范硬约束：[`.cursor/rules/four-role-todo-workflow.mdc`](./.cursor/rules/four-role-todo-workflow.mdc)（4 个协作角色：用户 / 科学家 / 工程师 / 审稿人；英文版 + Cursor `.mdc` 规范）。
>
> **ID 命名约定**（per cursor rule §12）：用户 `U-x` / 科学家 `S-x` / 工程师 `E-x` / 审稿人 `R-x`。

| 角色 | 入口文件 | 备注 |
|---|---|---|
| **用户**（总协调） | `docs/coordination/USER_TODO.md` | §A 决策池（权威源，`U-XXX`）+ §B 用户专属工作（`U-RES`/`U-FIG`/`U-REF`/`U-DIR`）+ §C 派给用户的 dispatch inbox（`C-XXX`） |
| **科学家** | `docs/coordination/SCIENTIST_TODO.md` | §B–E 写作 TODO（`S-XXX`）+ Reviewer 反馈追踪 + S-104 强制循环（§A 仅 cross-reference 到 USER_TODO §A） |
| **工程师**（统一日志） | `docs/coordination/implementation_log.md` | append-only 工程实现日志（新 phase 用 `E-XXX` 前缀；历史 phase block 用 `[<descriptive-name>]` 不回写） |
| **审稿人** | `docs/coordination/REVIEWER_TODO.md` + `artifacts/idea_reviews/reviewer_<...>/` 每 batch 独立目录 + 聚合 `scoreboard.md` / `fix_themes.md` | §A `R-FULL-XXX` 全文审稿（**仅用户触发**）+ §B `R-PART-XXX` 局部审稿（科学家/工程师可自触发审自己新写的部分内容）；batch 内 stateless；hand-off：scientist 必须按 SCIENTIST_TODO §B.4 S-104 4 步循环处理 |
| **共享决策（权威源）** | `docs/coordination/USER_TODO.md § A` | 用户拍板；科学家/工程师在此挂 `U-XXX`，等用户回复 |
| **派给用户的具体 todo** | `docs/coordination/USER_TODO.md § C` | 任何角色可挂 `C-XXX`（科学家 / 工程师 派给 USER 的 dispatch inbox） |

注 1：原 `agent-1/2/3-task.md` + `agent-1/2/3-summary.md` 六文件协作模式已被用户简化为 `USER_TODO.md` + `SCIENTIST_TODO.md` + `REVIEWER_TODO.md` + `implementation_log.md` 四文件 + 审稿 batch 归档目录。

注 2：**派工方向**：
- 用户的活（决策 / 充 API / 出概念图）：任何角色可在 `USER_TODO.md §A` 或 `§B` 挂 todo 等用户做。
- 科学家的活（写论文 / 改 framing / 处理 reviewer 反馈细节）：在 `SCIENTIST_TODO.md §B` 加 `S-XXX`。
- 工程师的活（跑实验 / 改 core code / 加 runtime guard）：在 `implementation_log.md` 用新 phase 块开。

---

## 9.5 当前 sprint 焦点（Stage-2 + ARR 5/25 deadline）

> 本节是 sprint 期间所有角色的"窄焦点视图"。Sprint 结束（论文 ARR 提交后）请整体删除本节。

| 角色 | 当前可即刻做 | 等待解锁 |
|---|---|---|
| **用户** | 拍板 **U-012**（Stage-2 范围）+ **U-013**（MuSiQue），合计 30 秒；执行 **U-RES-001**（充值 API）；可选 **U-FIG-001/U-EXEC-004**（Figure 1 出图） | — |
| **科学家** | **7 项**不依赖二次决策的 hygiene：S-105 / S-108 / S-110 / S-111 / S-112 / S-113 / S-114（按 four-role rule §2 必须并行做完再问） | S-115/S-116/S-117 等 U-012；S-001 主体 framing rewrite 等 U-012 范围确定 |
| **工程师** | **0 项**（所有 Stage-2 工单 E-001..E-007 阻塞在 U-012/U-013） | E-001..E-005 等 U-012；E-006/E-007 等 U-013 + U-RES-001 |
| **审稿人** | **0 项**（reviewer 不参与 sprint 执行；下次 R-FULL-002 由用户在 Stage-2 实测数据落地后触发） | R-FULL-002 等 E-005 ✅ + S-115/S-116/S-117 ✅ |

**Deadline math**（详见 `implementation_log.md [stage2_sprint_kickoff_20260419]`）：

| 路径 | 主路径完工 | buffer (天) |
|---|---|---:|
| 保守 (R2 单做 + MuSiQue) | **05-04** | 21 |
| 平衡 (R2+R3 + MuSiQue) | **05-07** | 18 |
| 激进 (R1+R2+R3 + MuSiQue) | **05-15** | 10 |

---

## 10. 不要做的事

1. **不要 mv / rm 任何 `artifacts/round*/run_*` 目录** —— 论文 §4 / coordinator note 全部用绝对路径引用，移动会破坏引用链。
2. **不要 mv `workspace/idea04_core/`** —— scripts 全部 `from workspace.idea04_core import …`。
3. **不要 mv 根目录 `idea.md` / `experiment.md`** —— 跨文件引用 15+ 处，需要先做 Phase 2 跨文件改名（U-008-decide）。
4. **不要把 GLM 跑数与 gpt-4.1-mini 跑数合并** —— `experiment.md §1.3` 明确禁止"不混模型社会"。
5. **不要清空 `round2_gpt41mini_fullval/run_20260414_135408/`** —— 这是 corruption forensic evidence，必须保留。
6. **不要把 rebuttal 记录写进 `workspace/autogen/dotnet/website/articles/`** —— 用户指定该目录只存论文交付物。

---

## 11. 整理工作的下一步

待你拍板的"破坏性整理项"全部已挂在 `docs/coordination/USER_TODO.md § A 决策池`（**权威源**）。`SCIENTIST_TODO.md § A` 仅是科学家的 blocked-on cross-reference 视图，内容以 USER_TODO 为准。

---

## 12. 协作简化（2026-04-19）

* 跨角色依赖直接通过 `SCIENTIST_TODO.md` / `implementation_log.md` 各自的 `阻塞` 列传递；不再维护任何独立的依赖追踪文档。
* 每次执行入口先扫自己 TODO 中所有 ⏳ / ❌ 项，检测是否已 done（由上游条件已满足而触发），更新 ✅ 后才开新动作。详见 [`.cursor/rules/four-role-todo-workflow.mdc` §1](./.cursor/rules/four-role-todo-workflow.mdc)。
* 数学统计图（柱 / 箱 / 折 / 散点 / 热图）由科学家用 Python 实绘并落 `artifacts/figures/`；概念示意图 / 逻辑流程图由用户绘制，科学家负责写完整的 prompt 文档落 `docs/paper/figures_prompts/`。
* 论文精细打磨完成后，需做一次本地 commit（依赖 U-010-decide）。
