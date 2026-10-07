# 先验证“值得选谁”，再扩大实验 — 2026-10-07

状态：`PARTIAL / OFFLINE_SCREEN`；Goal、六份生效标准与方法 B 均不改变。

本轮得到一个更明确的筛查条件和一组可复用原生材料，没有得到角色学习效果。
PIPE1 保留为待核验候选；没有替换当前 benchmark，也没有追加 API/GPU 调用。

## 目的与衡量指标

回答两个直接影响论文的问题：历史评价能否改变未来最优协作者；原生任务是否
提供足够可靠的信息交付与终局指标来检验它。通过标准是推导边界明确、原生路径
可追溯、必要简单对照未遗漏、跨机标签风险有逐记录证据；不是新测试数量。

## 本轮做完了什么

1. [选择价值推导](../../research/candidates/benchmark_selection_value_20261007.md)
   说明：固定菜单和执行规则时，增加评价信息的理想选择价值非负；若几乎所有
   评价分支都有同一个最优 peer，价值为零。评价与结果相关并不足以证明分派收益。
   数学算例均不是实测；获取评价的成本另算；同信息强基线同样享有这些信息。
2. [保存四域原生材料](../../../experiments/logs/n03_pipe1_native_material_audit_20261007_v1/summary.json)：
   使用固定 TeamBench commit 的原生 generator，执行4次，保存 seeds 0–3 的
   Planner 规范、Executor brief/工作文件和隔离的 expected。每域10条输入，
   总计40条；四域仍是一个 structural root。没有生成 peer 消息或运行候选代码。
3. [核对完整 native harness](../../../references/aamas/task_signal_materials_20261007/native_harness/manifest.json)：
   Planner 可通过消息转发完整 spec；Executor 读取完整消息；Verifier 也看到
   spec，并可触发最多两轮返修。已捕获两角色视图只是静态投影，不是完整原生复现。
4. [时区逐条审计](../../../experiments/logs/n03_pipe1_timezone_audit_20261007_v1/summary.json)：
   healthcare/financial 各10条时间戳，在 UTC 与 Asia/Shanghai 下20/20日期不同；
   保存的 expected 全部匹配后者。原生 `fromtimestamp` 没有指定 tz；此前捕获
   进程的确切时区未获证明。此结果不是模型失败，也不证明 native grader 的全部
   判定会改变——它对一些日期只验格式，并非逐值 oracle。

本轮总计：4次原生材料生成、20条已存时间戳比较；0次 grader、0次候选程序、
0次模型 API、0次 GPU。配置先于计算保存；原始记录与源码快照均保留。材料捕获
未记录 TZ 是证据缺口，后续独立审计不能替它补写历史环境。

[收尾校验](../../../experiments/logs/n03_selection_value_checks_20261007_v1/summary.json)
确认已存角色视图、harness 与时区输入的哈希及20条记录一致，新增文档链接可达；
六类唯一生效版本检查、任务账与 gate 同步检查通过。它们只校验证据和文档一致性，
机器报告的 `scientific_readiness` 仍为 false。

## 讨论中改变了哪些判断

| 初步判断/疑问 | 独立审查与证据 | 采用的处理 |
|---|---|---|
| Planner 有规则，因此复杂 peer 计划可能有价值 | 原生消息接口允许直接转发；实际效果未跑 | 必须比较无消息、原样规则、真实生成计划；后两者计完整成本 |
| 两角色视图已代表原生任务 | 原 harness 还有全信息 Verifier 与返修 | 两角色切片单独命名；完整复现保留第三角色及成本 |
| expected 可直接跨机器复用 | 20条日期均随 TZ 改变；原捕获 TZ 未记录 | 先固定生成/执行/评分共同环境并让 actor 知道约定，旧日志不改 |
| J 预测更准就能支持方法 | 普通信息价值只在能改善选择时有增量 | 不把相关性、count-only 差异或信息新增解释为 RARE 优势 |

Codex 独立方法审查确认有限菜单、可积效用、信息不改执行行为等假设下的推导，
要求补明“几乎每个 x”和未计评价获取成本，均已修订。未以评审投票替代科学证据。

## 与三个验收标准相比

| 标准 | 本轮实际缩小的缺口 | 尚未达到 |
|---|---|---|
| 故事线与创新 | 明确必须证明“经验帮助后续选人”，不是“预测更准确” | 最近工作差异与实证增量；本轮普通数学性质不是创新声明 |
| 方法论 | 明确 observation、路由收益与 producer 因果功劳不可混用；仍遵守 ADR0049 | 自然持久 peer 经验、合法后续 reward、在线训练/稳定性/实时性证据 |
| Benchmark + baseline | 找到原生规则交付路径，保存可复用材料，补出强简单对照及 TZ 风险 | benchmark freeze、第二独立 root、公平 live 基线、效应与精度、完整成本 |

三份标准均未通过，科学投稿 gate 仍关闭。本轮没有修改标准、删掉必做基线或
把工程验证填进论文效果表。共享论文正在另一图稿任务中更新，本轮不修改正文。

## 下一步，只解决能改变决策的问题

1. 已冻结的 PIPE3 四次判断诊断只检验责任范围，仍待**追加预算**确认；方案 B
   的确认不等于额外预算确认。历史累计仍31 episodes / 68任务请求，不换卡清零。
2. PIPE1 在激活前明确 native/两角色切片边界、原样转发对照、时区约定与原生评分
   覆盖。先复用本轮保存材料；不重复下载或生成，不提前增加模型调用。
3. 最关键的剩余设计是 peer 持久经验如何影响下一次真实生成。没有这个条件，
   做更多静态交付评分仍不会回答角色学习问题。须先冻结同信息、同初始条件下的
   经验和任务划分，再用独立 live histories 判别未来质量/成本；涉及生效方法的
   实质修改仍共同确认。尚无结果支持选定 backbone 或启动 A800 训练。

可复用产出已经落地：固定原生 generator/grader/harness、四域分角色材料、
逐条时区审计以及选择价值的筛查条件。后续实现直接使用这些资产，不从零造任务。

## 2026-10-07 continuation：实际请求与候选 target 的 distinctness audit

为了避免把配置字段误当成新任务，root 只读取已封存的 C1 judging 请求、material
manifest 和 pinned generator 的字面规则，没有导入 generator、运行候选代码、调用
模型或修改历史结果。回执见
[`n03_task_distinctness_audit_20261007_v2/summary.json`](../../../experiments/logs/n03_task_distinctness_audit_20261007_v2/summary.json)。

审计发现 `no_update` 与 `RARE` 的 source/target 请求均为 seed 0，任务合同和 producer
文件相同；`contextual_trust_linear` 只有 source 请求，因为 target 没有启动。历史
runner 的 `generated_target = generated_source` 进一步确认此前的 target seed 字段不能
当作新的 target material。故这些请求不支持未见任务泛化或 peer 选择收益，旧结果保持
原分类。

PIPE1 seed 0 ecommerce 与 seed 3 logistics 的整组 mapping/type/nested/enum/null 规则
没有整组相同项，适合作为同一 structural root 内的先行筛查；它仍不是第二 root。
根据两位独立审查意见，已写入[筛查卡](../../research/candidates/pipe1_source_target_screen_card_v0.1_20261007.md)：
使用 Planner 作为候选 peer，保留原生完整 spec、Executor、Verifier 和成本；必须包括
no-message 与 full-spec relay。后者是合法 Planner 消息的生成绕过对照，不是同信息
selector baseline。相同初态 Planner 可能自然地产生相同消息/历史；若无可重复差异，
记录 `INCONCLUSIVE`，不改 prompt 制造专家。

这个候选卡尚未获预算或执行授权，不能替代 benchmark freeze、真实后续收益、强同信息
baseline 或 A800 门。它的作用是阻止下一次昂贵实验再把“seed 不同”写成任务泛化。
