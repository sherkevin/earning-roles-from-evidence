# 2026-10-04 论文叙事写作小任务：摘要与主线收紧

## 任务目的

只推进论文写作和故事线，不扩展 benchmark、baseline、训练或远程实验。依据：

- `research/2026_AI顶会最佳杰出论文叙事范式_六大范式_阅读整理.md`
- `docs/research/versions/evaluation/storyline/storyline_v1.3_20260928_eval.md`
- `docs/research/versions/storyline/storyline_v1.1_20260928.md`

本轮采用“根因手术刀”为主范式：协作后果 → producer/recipient 责任混淆的最小反例 → situated judgment 的可识别缺口 → earning-roles 闭环 → 可证伪预测与范围边界。

## 本轮修改

文件：`article/aamas2027/main.tex`

1. 重写摘要为五个连续动作：
   - 多 agent 责任分派与下游失败混淆；
   - reputation/acceptance/terminal reward 的具体识别限制；
   - earning roles 的唯一闭环机制；
   - 在匹配信息、候选集和完整成本下的可证伪预测；
   - ArtifactRole/PeerSelect、同信息 baseline、root split、延迟/遗忘/归因/成本范围。
2. 删除摘要中的内部元话语（例如“结果单元预留”“novelty claim”），保留未验证结果的诚实边界，不把协议级设计写成已证实效果。
3. 将方法章节题目从 `Candidate Mechanism` 改为 `Earning Roles: A Responsibility-Aware Protocol`，把 RARE 定义为闭环协议，而不是某个特定 updater/backbone。
4. 将引言中的贡献措辞从“candidate ArtifactRole track”收紧为“ArtifactRole track”，并增加路线图句，明确正文从 gap、事件契约、协议/比较、实验矩阵到证据边界的推进顺序。
5. 将“当前没有效果结果”的表述改为 evidence boundary，避免把论文写成实验日志，同时不越过当前证据等级。

## 验证

- `python3 scripts/build_aamas2027.py`
- 主文档：7 页；保守正文末页 7；无未解析引用；无 overfull box。最终验证记录为 `article/aamas2027/build/verification.json`，本轮 PDF SHA-256 为 `ce2bb76c3ef4f5c7f0934dc2a41a813bdd02e18428e64ec6743262a85f94c4dc`。
- 生成 PDF：`article/aamas2027/build/main.pdf`。
- 本轮未运行实验、未改变 benchmark/baseline、未修改目标标准。

## 验收状态

| 检查项 | 状态 | 说明 |
|---|---|---|
| 主范式唯一 | 待独立审查 | 当前文本明确以根因手术刀为主线 |
| 摘要五句功能 | 初步通过 | 问题、限制、机制、预测、范围均出现 |
| 引言论证链 | 初步通过 | 已含最小反例、机制、贡献、路线图 |
| 结果诚实性 | 通过 | 没有新增实证效果声称 |
| 三份故事线标准 | 待审查 | 由独立 Codex reviewer 复核 |

`goal_change_requested=false`。本轮没有降级或修改 Goal。

## 待独立审查

独立 Codex agent `/root/six_paradigm_story_reviewer` 将按六大范式、故事线评价标准和 AAMAS 写作行为检查题目、摘要、引言、方法命名及内部元话语。若发现硬门问题，只做最小必要文字修改，并在本文件追加结果。

## 独立复核结果

审查文件：`docs/coordination/task_reports/20261004_six_paradigm_story_reviewer_report.md`。

独立 reviewer 判断：

- 主范式为“根因手术刀”，反直觉重构和基准暴露失效为辅助；
- 摘要五句功能完整，没有把未验证效果写成结果；
- 引言已经形成“现象/反例 → 责任混淆 → sharp gap → 机制 → 可证伪预测 → 贡献 → 路线图”；
- 故事设计约 `7.7/10`，正式投稿就绪度约 `4.2/10`。后者受科学证据 hard gate 约束，不是文字质量分数。

按 reviewer 的 P1 建议，随后又做了三处最小文字修正：

1. 将根因统一为 `responsibility confounding`，把 ambiguity 留作现象描述；
2. 摘要把 ArtifactRole/PeerSelect 明确成 candidate evaluation tracks，避免 benchmark 尚未冻结时产生权威性暗示；
3. 将 RARE 明确为 evidence-semantic loop，而不是某个 implementation/updater。

Reviewer 标出的 P0/P2 未在本轮伪装解决：独立 root、live history、later-use、完整成本、strong same-information baseline、novelty table，以及最终稿的 internal/release-gate/空结果标记仍需在证据完成后处理。`goal_change_requested=false`。

## 第二轮：最近邻边界写作

为回应 novelty table 硬门，`main.tex` 的 Related Work and Positioning 已改为“观察信号 → 更新时间 → credit 语义 → 实验对象 → 本文边界”的比较桥接，并加入 `Table~\ref{tab:novelty}`。表格覆盖五个近邻家族：partner selection、LLM-MAS reputation、graph/evolutionary coordination、dynamic role/subtask assignment、contextual trust/bandit。表格明确这些是 comparison families，不把名字本身当作复现结果；faithful adapter 仍需保留可见信息、arrival order、selected-only denominator 和 complete cost。

第二轮排版验证：

- `python3 scripts/build_aamas2027.py`
- 主文档仍为 7 页；保守正文末页为 7；无未解析引用；无 overfull box。
- 当前 PDF SHA-256：`54c92b1929a05758b0e3e91a82ab5715f2eb46543dcd615a4e03b99368357fc9`。
- reviewer 指出 Auer (2002) 只能支撑经典非 contextual MAB。已修正为 `Finite-time multi-armed bandit`，并把 context/propensity/delay 留给同信息 adapter 的实验定义；同时将五个 family 改成具名代表方法，并把绝对措辞改为 cited formulation 的可核验边界。
- 最终 reviewer 复核结论：表格组织通过；Related Work 支持 sharp gap `7.8/10`，novelty 边界表达 `7.4/10`，整体故事 `8.0/10`。最后指出的两处语义问题已修正：Auer 行改为经典 selected-reward control，且明确 contextual/delayed adapter 需单独资格化；时间段改为“到达后可更新后续决策，但不能重构已封存 assignment 或直接把 target outcome 当 source label”。

## 第三轮：六范式全量核查后的收紧

参照 H.3/H.4/H.5 又做了最小修正：

- 在 event 和 score 公式后补 queue 实例；recipient 使用 `k`，避免与 public snapshot `R_t` 冲突；
- 将 protocol properties 改写成可观测指标，并补充 H1/H2/H3/H4 的 primary endpoint lock、方向、control、MCID/precision、95% interval 和 stopping rule 字段要求；
- 将 score 实例拆成独立段落；将 trace 浮动表压缩成 phase-rule 段，避免空结果表占用正文页面；
- 补齐所有 figure/table 的正文引用，静态检查未发现未引用的图或表；
- PDF 重新验证仍为 7 页、无未解析引用、无 overfull box，SHA-256 为 `103d5b803e4465405a30842c6ec71cb3d5b23d210bec441ab6f18c90f74cb553`。

六范式全量核查明细见 `docs/coordination/task_reports/20261004_six_paradigm_full_audit.md`。剩余投稿就绪度限制仍是科学证据门，不通过文字改写掩盖。`goal_change_requested=false`。

独立 reviewer 最终评分：H.3 `8.8/10`、H.4 `8.4/10`、H.5 `8.8/10`、整体故事 `8.6/10`；正式投稿科学就绪度仍 `4.2/10`。根据其最后建议，新增 `docs/research/primary_endpoint_cards_v0.1_20261004.md` 作为 H1--H4 的可追溯设计清单，但保留 `DESIGN_ONLY / NOT_FROZEN`，没有把未确定的数值 MCID/precision 或 stopping rule 伪装成冻结协议。
