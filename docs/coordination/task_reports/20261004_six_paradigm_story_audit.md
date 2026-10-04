# 六大叙事范式与当前故事线审查

日期：2026-10-04
状态：`PARTIAL`（叙事审查完成；Introduction 已按审查意见完成一轮小修）
对应 Goal：ER-G1、ER-G4、ER-G5/G0
`goal_change_requested=false`

## 任务目的

用户要求将 `research/2026_AI顶会最佳杰出论文叙事范式_六大范式_阅读整理.md` 作为后续故事线和论文写作的上位参考，并在每次写作后进行独立审查。本任务先不改 active 故事线、方法或 benchmark 文档，完成以下工作：

1. 读取并拆解六种叙事范式及其段落行为逻辑；
2. 将当前生效故事线、方法合同、benchmark/baseline 计划和 LaTeX 主稿映射到该标准；
3. 选出适合本项目的主范式和辅助范式候选；
4. 固化修改前的缺口、衡量指标和审查流程，避免把叙事包装误当成科学证据。

## 来源和证据边界

参考文档的 front matter 明确声明：文章内容来自用户粘贴，微信公众号原文未独立核验，会议、奖项、论文名称和数字只能作为“参考级”叙事材料。本文档因此只吸收其研究顺序和写作行为，不把文章中的奖项、数字或个别论文事实写入本项目证据。

已对照的生效文件：

- `docs/research/versions/storyline/storyline_v1.1_20260928.md`
- `docs/research/versions/method/method_v1.1_20260930.md`
- `docs/research/versions/benchmark-baseline/benchmark_baseline_v1.1_20260930.md`
- `docs/research/versions/evaluation/storyline/storyline_v1.3_20260928_eval.md`
- `article/aamas2027/main.tex`

本任务没有调用 LLM API、没有提交 A800、没有改变实验数据，也没有把现有零调用资格回执升级为科学结果。

## 范式选择（待独立复核后转为写作约束）

### 主范式：①根因手术刀

项目最适合从一个可复现的协作失败切入：recipient 的使用/返工与 producer 的交付缺陷被混在一起，且 later outcome 若直接回写 source producer 会造成责任错配和时间泄漏。这样方法不是“再做一个 selector”，而是针对根因建立 responsibility gate、公开 evidence、执行前 assignment 和 delayed selected-only credit 的闭环。

### 重要辅助范式：④新基准暴露失效

ArtifactRole/PeerRoleBench-TB 的价值应首先是量出 raw acceptance、terminal-only 和不具备 ownership/arrival 边界的现有流程在哪些条件下失效。当前 benchmark 尚未冻结，因此只能把④写成设计目标和诊断方向；没有独立 root、同信息 baseline 和真实 live history 之前，不能声称已经“暴露了系统性失效”。

### 辅助钩子：②反直觉重构

可检验的反直觉句子是：`accept/reject` 或终局成功不是 producer role label；只有绑定具体 delivery、recipient action、ownership 和可见时序的 judgment 才能成为可传播 evidence。该句子必须由最小反例和 mutation controls 支撑，不能只作为标题式修辞。

### 形式支撑：③理论照亮经验

当前事件时序、read-cut、assignment seal、UNKNOWN/no-op 和 replay invariants 已具备形式化对象，但仍是 method contract，不是定理。只有把这些不变量写成可证明的引理或明确的 machine-checkable properties，并与实验指标对应，才可使用“理论照亮经验”的强叙事；否则应称为可审计协议。

### 暂不作为主线的范式

- ⑤社会价值：协作质量和完整成本有实际意义，但目前没有独立社会影响场景，不能硬贴。
- ⑥极简统一美学：两个轨道共享 event/selector/update 接口是工程优点，不足以成为论文主叙事；必须先证明接口统一没有吞掉任务语义。

## 当前叙事链对照

| 六范式要求 | 当前已有内容 | 当前缺口 | 可量化检查 |
|---|---|---|---|
| 现象与后果 | Introduction 开头说明 task-conditioned collaborator 与 fixed/global allocation 的冲突 | 还没有在前两段给出一个具体可复现反例 | 首屏能否写出一条 producer-correct/recipient-wrong 对照 trace |
| 根因 | storyline 已明确责任混淆、future leakage 和 attribution gate | 根因尚未压成一句可反驳的 sharp failure，并未在主稿早段绑定真实 trace | 用一句“由于 X，Y 无法识别 Z”并由 mutation matrix 支撑 |
| 反直觉 | 文中已有“acceptance/terminal score 不能单独完成角色形成” | 仍偏定义性陈述，缺最小反例和 control | raw acceptance 与 responsibility-aware evidence 在同一 trace 上产生不同合法性 |
| 基准暴露失效 | benchmark 计划包含 responsibility mutation、UNKNOWN 和强 baseline | benchmark 未冻结、第二 root/live history 未完成 | 两个结构不同 root、独立 streams、同信息 baseline、主指标预冻结 |
| 理论/形式化 | event-time、read-cut、preview→assignment→commit、replay 合同 | 尚无 theorem/引理；公式后实例化不足 | 至少三条不变量：pre-selection noninterference、recipient-only no producer evidence、idempotent replay |
| 极简统一 | 两轨共享 API | 目前更像工程复用，主稿仍有较多接口和矩阵细节 | 一个主图/一个核心闭环能否解释全部主张；每个模块有必要性消融 |
| 因果闭环 | storyline、method、实验矩阵均按 judgment→evidence→assignment→utility 编排 | 真实 evidence→assignment→unseen utility 尚未完成 | H1/H2/H3 分别有独立 root、成本、UNKNOWN 分母和区间 |

## 现阶段结论

当前故事具备一条有潜力的根因主线，但不能称为“已完成的获奖式叙事”：科学门仍被 benchmark authority、same-information baseline、independent live history 和结果证据卡住。论文主稿更接近“可审计研究设计/内部 pre-results manuscript”，而不是可以直接提交的结果论文。这个判断不降低 Goal；它决定下一步先修正文的根因钩子和 claim–evidence 对齐，同时继续按既定 benchmark gate 推进。

## 后续写作与审查流程

每次修改故事线或 LaTeX 主稿后执行同一顺序：

1. 写作前列出本次修改要证明的一个中心句、对应证据和不主张范围；
2. 修改后先做 topic-sentence/claim–evidence/段落职责检查；
3. 交给独立 Codex 只读审查员，要求其只依据本参考文档、三份 active 文档和主稿给出意见；
4. 将审查报告与版本、diff、测试/编译结果一起写入新的 task report；
5. 只有确认没有改变科学含义，或经过用户/助手双重确认后，才把 substantive storyline/method 版本登记为 `ACTIVE`；
6. 任何审查意见都不得把失败实验改写成成功，不得把参考文档中的未经核验事实当作本项目证据。

## 已执行的两轮小修与复核

在收到独立 Codex 报告后，仅修改 `article/aamas2027/main.tex` 的 Introduction，并在第二轮复核后再次收紧：

- 用两个明确标注的 constructed queue-processing cases 开场：同样的 rejection/failed team outcome 可能来自 producer contract defect 或 recipient integration defect；
- 将单一根因压缩为 producer responsibility、recipient integration 与 downstream outcome 的 evidence ambiguity；
- 修正 sealed assignment 之后 target outcome 的时序语义，避免把“写回后再选择”写成矛盾时间线；
- 将无引文的宽泛断言收窄为一个系统如何解释信号的问题；
- 把 noninterference/idempotent replay 改写为待检验性质，而非已经证明的性质。

独立 Codex 复核结果：`PASS`。问题切口从 6.5 提升为 7.8、根因定位从 5.5 提升为 7.5、反直觉 hook 从 5.0 提升为 7.0、故事设计潜力从 6.2 提升为 7.0；正式投稿就绪度仍为 3.8，因为 benchmark 未冻结且没有正向效能结果。此前共享 build 目录出现并发/陈旧产物，因此不把其中的 3 页 PDF 当作本次验证；`git diff --check` 通过。

第二次独立目录构建 `artifacts/aamas2027/narrative_20261004_isolated_v4/result.json` 收敛为 7 页，0 overfull boxes，0 undefined citations/references；保留模板已知 `ifx` compatibility warning 和 underfull/balance warnings。构建使用 0 API、0 GPU，`scientific_claim_allowed=false`。

三条不变量的合同—证据映射另存于 [`20261004_invariant_mapping.md`](20261004_invariant_mapping.md)：I1 pre-selection noninterference、I2 recipient-only attribution safety、I3 idempotent replay 均有零调用工程回执，但正式 lemma、live stream 和质量/成本结果仍 OPEN。独立审查员对新 Introduction 与该映射再次 `PASS`。

这轮修改没有改变 active storyline/method/benchmark，也没有启动 API/A800。它只改善论文的段落行为逻辑，不能替代 benchmark、baseline 或科学结果门。

## 下一步（不启动 API/A800）

1. 将相同的根因—反例—机制—可测性质结构推广到摘要、Figure 1 caption、Related Work 和 Current Evidence，但每次只改一个段落簇并复审；
2. 先完成已冻结的 canonical PIPE3 same-information parity qualification，确认主比较和公共 `φ` 后再写任何效果性句子；
3. 为 I1–I3 各写最小 lemma 或 machine-checkable property，明确假设、状态字段和反例；
4. 叙事改稿不能替代 benchmark/baseline 科学门，任何结果仍必须遵守 claim–evidence 分级。
