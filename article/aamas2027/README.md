# AAMAS 2027 internal revision

**唯一主版 PDF：[`artifacts/aamas2027/main.pdf`](../../artifacts/aamas2027/main.pdf)。**
迭代稿保存在它下一层的版本目录中。每轮修改先合并到当前 `main.tex`，完成编译与页面检查后，再同步父目录主版及[来源记录](../../artifacts/aamas2027/main_pdf_master.json)；旧版本保留。具体规则见 [ADR 0050](../../docs/user/decisions/0050-canonical-main-pdf-and-versioned-builds.md)。

每轮论文修改的完成条件：

1. 协作者可以在独立版本中起草；由主维护者把选定改动合并到 `article/aamas2027/main.tex` 及其引用的源文件，不能只交付独立 PDF。
2. 使用一个尚不存在的版本目录构建，检查正文恰好 8 页、引用、溢出与实际页面。`--build-dir` 的相对路径以本目录为基准；也可指定仓库内新版本目录的绝对路径。不能重复使用历史轮次目录。
3. 保留版本 PDF、源快照、校验与审阅记录；把通过检查的 PDF 同步为上一层 `artifacts/aamas2027/main.pdf`，同步 `main_pdf_master.json` 的源文件摘要与版本来源。
4. 核对主版和被提升的版本逐字节一致、来源记录与当前源文件一致，并写任务汇报。仅编译成功不表示主版已同步，构建脚本目前不自动执行提升。

`article/aamas2027/build/main.pdf` 是临时构建输出，可能滞后，不能作为当前论文入口；只打开上面的唯一主版。并行协作者不得相互覆盖主版，由主维护者完成合并与同步。

## 当前题目摘要草稿（2026-10-05）

当前确认的工作标题为：**Know Who You Are: Earning Roles from Situated Peer Judgments**（见 [ADR 0046](../../docs/user/decisions/0046-set-know-who-you-are-paper-title.md)）。
“Know Who You Are”提供对外的想象空间；“earning roles”描述待验证的动态角色形成目标，不能替代实时更新、稳定性或角色学习效果证据。

[research_proposal.tex](research_proposal.tex) 是围绕当前主线新写的英文题目与摘要，
使用现有官方 AAMAS 2027 类文件。它明确标记 `INTERNAL PRE-RESULTS PROPOSAL`，
不复用旧稿的经验结果来支持新机制；benchmark、backbone、训练方法均仍待确定。

```bash
python3 scripts/build_aamas2027.py --proposal
```

产物为 `article/aamas2027/build/research_proposal.pdf`；校验记录为
`build/proposal_verification.json`。`--proposal --submission` 会直接拒绝。
以下 `mainline_pre_results.tex` 与 `main_historical_allocation_20261002.tex` 保留历史/过渡稿；当前正式内部初稿为 `main.tex`，其结果表为空并受 submission guard 约束。`supplement.tex` 仍是内部证据补充稿。

当前论文主线落在 [`main.tex`](main.tex)。它围绕唯一问题“situated recipient
judgment 是否能形成可归因的 producer role evidence，并改变未来责任”组织故事、
候选机制 RARE、ArtifactRole/PeerSelect 资格门和同信息 baseline；完整实验矩阵
中的结果列保持为空。`mainline_pre_results.tex` 是此前过渡稿，保留用于审计，不再是
当前主稿。

本地编译：

```bash
python3 scripts/build_aamas2027.py
```

截至 2026-10-08，当前两图主稿已通过本地 AAMAS 模板编译：**正文 8 页，总 9 页，参考文献单独从第 9 页开始**，引用已解析且无 overfull box。AAMAS 2027 主赛道的官方上限是正文 8 页，参考文献可另加页；本轮实验矩阵版式审计记录在 [`EXPERIMENT_MATRIX_AUDIT_20261008.md`](../../docs/paper/aamas2027/EXPERIMENT_MATRIX_AUDIT_20261008.md)，当前 canonical artifact 的 SHA-256 与源快照见 [主版来源记录](../../artifacts/aamas2027/main_pdf_master.json)。主稿当前采用 Figure 1 v51 与 Figure 2 v55；主版是内部 pre-results 审阅稿，不能通过投稿构建。参考文献规模和来源分布审计见 [`REFERENCE_SURVEY_20261007.md`](../../docs/paper/aamas2027/REFERENCE_SURVEY_20261007.md)。

2026-09-26 本地已编译并目视检查：一页、匿名、无溢出和未解析引用；官方文件
哈希一致。仍有官方类/元数据路径的 incomplete-ifx 兼容性警告，校验 JSON 已记录。
2026 官方下载链接返回 404；当前 PDF 使用已核验的 2027 官方模板，不混用届次。
依赖修复和来源详见 [模板复核](../../references/aamas/venue_refresh_20260926/README.md)。

Active specification: [REQUIREMENTS.md](../../docs/paper/aamas2027/REQUIREMENTS.md), v1.5.8. Current gaps/work: [AAMAS_TASKS.md](../../docs/coordination/AAMAS_TASKS.md). **The user resumed bounded real-data / real-API research on 2026-09-22.** [Decisions 0005](../../docs/user/decisions/0005-retain-peer-judged-role-learning.md) and [0006](../../docs/user/decisions/0006-study-peer-judged-role-formation.md) select learning roles from actual collaborators' judgments during agent–workflow co-evolution. [Q1 v6.1](../../docs/scientist/analysis/AAMAS_Q1_worker_differences.md) is a retired conditional-adoption candidate, not the selected main question. The [design contract](../../configs/aamas2027/contract.json) is v5 reference-only: source pins remain preserved, while method, final benchmark roles and comparison matrix are reopened. The older allocation-only scaffold remains historical. The current `main.tex` develops the selected mechanism prospectively; its empirical claims still require matching evidence. The completed acquisition probe failed its promotion gate; the independent dev census stopped incomplete38/57 after transport failures. Their actual records and method assessment are in the task ledger; neither supplies the selected judgment→role→later-duty evidence.

Build from the project root:

```powershell
python scripts/build_aamas2027.py
```

- `main.tex`: current pre-results paper draft with the situated-judgment role-evidence storyline, complete experiment matrix, empty result cells, explicit claim boundaries, and reserved figure/table slots.
- `docs/paper/aamas2027/FORMAL_PAPER_ZH.md`: 当前唯一生效的正式论文中文 Markdown 阅读稿，逐节对应 `main.tex`，用于故事线、方法、benchmark/baseline 和实验设计的中文审阅；不替代英文投稿源文件。`article/aamas2027/main_zh.md` 只是指针。
- `figures/overview.pdf` and `figures/method_state.pdf`: the current internal candidates are v51 and v55. Their original AI rasters use the gallery-derived file/table/feature-strip grammar, 3:1 composition, blue/teal/gray palette and fine rules. Figure 1 has the compact two-row collaboration loop; Figure 2 v55 has visibly stronger existing microtype and preserves the exact P/D, residual, validation and no-op topology. Independent image and actual paper-page reviews pass for internal use; raster-text production and scientific readiness remain open. v53 and v54 are retained as failed/superseded attempts, while v52 remains the rollback figure. Prompts, images, hashes and reviews are under `figures/ai_versions/` and `experiments/logs/figure_microtype_round_20261007_v53_v55/`. The experiment matrix stays in tables; `experiment_map.pdf` is historical. The earlier v30/v32/v34 production claims were narrowed by `docs/coordination/task_reports/20261007_figure_counteraudit_v30_v32_v34.md`. The PDF containers add no drawing or text overlays. `scripts/build_aamas_figures.py` preserves older programmatic candidates and does not generate these AI assets.
- `supplement.tex`: 过渡期内部证据补充稿；与当前主稿的实验结果表尚未合并。
- `build/supplement.pdf`: earlier compiled internal draft. `build/main.pdf` is temporary build output and may be stale; the promoted round is recorded in `artifacts/aamas2027/main_pdf_master.json`. From the repository root, use `python3 scripts/build_aamas2027.py --main-only --require-content-pages 8 --build-dir <new-version-directory>` with a fresh directory. This compiles and checks a candidate; complete the promotion steps above before reporting the paper update finished.
- Canonical current main PDF: [`artifacts/aamas2027/main.pdf`](../../artifacts/aamas2027/main.pdf). The promoted source round is retained under [`artifacts/aamas2027/information_update_20261008_v1/`](../../artifacts/aamas2027/information_update_20261008_v1/); the earlier `experiment_matrix_20261008_v2/`, `reference_supplement_20261007_v3/`, `microtype_20261007_v55/`, and all other child directories are historical or rollback/candidate builds, not alternate main manuscripts. See ADR 0050.
- `aamas.cls`, `ACM-Reference-Format.bst`, `by.pdf`: byte-identical copies from the official AAMAS 2027 template.
- `aamas_metadata.tex`: official conference/copyright settings and an explicit internal submission-ID marker.

The original EMNLP/ACL sources remain in `article/latex/` and have not been overwritten.

This draft separates a revised, not-yet-evaluated protocol from historical measured variants. It is not submission-ready. The external submission guard is:

```powershell
python scripts/build_aamas2027.py --submission
```

It refuses release until `docs/paper/aamas2027/submission_gate.json` and manuscript metadata are finalized. Do not remove internal status text merely to make the guard pass. Replace prospective sections with executed, independently verified evidence or narrow the paper's contribution explicitly.

After reviewed requirements/task-ledger changes, run `python scripts/check_aamas_documents.py --sync-gate --check-gate`. The gate is derived from the fifteen requirement rows and bound to both document hashes; submission builds reject a stale gate. Document checks do not certify scientific validity.

S-518 records the historical first pass. Its separate venue/positioning/reviewer/handoff notes have been consolidated into the two active documents above.
