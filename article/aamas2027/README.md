# AAMAS 2027 internal revision

## 当前题目摘要草稿（2026-10-02）

当前确认的工作标题为：**Know Who You Are: Earning Roles from Situated Peer Judgments**。
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

截至 2026-10-02，当前主稿已通过本地 AAMAS 模板编译：7 页、引用已解析、无
overfull box；主赛道官方上限为 8 页。主稿已预留闭环架构图、事件时序图、实验矩阵图、
headline result 表和 trace 表的位置，结果单元仍为空。`build/main.pdf` 是内部 pre-results 审阅稿，不能通过投稿构建。

2026-09-26 本地已编译并目视检查：一页、匿名、无溢出和未解析引用；官方文件
哈希一致。仍有官方类/元数据路径的 incomplete-ifx 兼容性警告，校验 JSON 已记录。
2026 官方下载链接返回 404；当前 PDF 使用已核验的 2027 官方模板，不混用届次。
依赖修复和来源详见 [模板复核](../../references/aamas/venue_refresh_20260926/README.md)。

Active specification: [REQUIREMENTS.md](../../docs/paper/aamas2027/REQUIREMENTS.md), v1.5.8. Current gaps/work: [AAMAS_TASKS.md](../../docs/coordination/AAMAS_TASKS.md). **The user resumed bounded real-data / real-API research on 2026-09-22.** [Decisions 0005](../../docs/user/decisions/0005-retain-peer-judged-role-learning.md) and [0006](../../docs/user/decisions/0006-study-peer-judged-role-formation.md) select learning roles from actual collaborators' judgments during agent–workflow co-evolution. [Q1 v6.1](../../docs/scientist/analysis/AAMAS_Q1_worker_differences.md) is a retired conditional-adoption candidate, not the selected main question. The [design contract](../../configs/aamas2027/contract.json) is v5 reference-only: source pins remain preserved, while method, final benchmark roles and comparison matrix are reopened. The existing LaTeX source is an older internal allocation-only scaffold, not the selected mechanism or its evidence. Scientific sections must be rewritten once matching evidence exists; the official template remains reusable. The completed acquisition probe failed its promotion gate; the independent dev census stopped incomplete38/57 after transport failures. Their actual records and method assessment are in the task ledger; neither supplies the selected judgment→role→later-duty evidence.

Build from the project root:

```powershell
python scripts/build_aamas2027.py
```

- `main.tex`: current pre-results paper draft with the situated-judgment role-evidence storyline, complete experiment matrix, empty result cells, explicit claim boundaries, and reserved figure/table slots.
- `scripts/build_aamas_figures.py` and `figures/*.pdf`: deterministic external vector figures used by the current draft.
- `supplement.tex`: 过渡期内部证据补充稿；与当前主稿的实验结果表尚未合并。
- `build/main.pdf`, `build/supplement.pdf`: compiled internal drafts.
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
