# Task report — Guide 多角度审核与赢输条件修复

日期：2026-10-08。状态：`CONDITIONAL_GUIDE_GO / EMPIRICAL_FORECAST_NOT_IDENTIFIED`。
Goal、ACTIVE 规范、正文表与论文主版：不改。0 新 API、0 GPU、0 benchmark 实验。

## 目的与衡量

回应用户要求：分别审核 benchmark+baseline 合理性、效果合理性、一致性、方法优势与
不足；合理结果应在适用条件下有优势，在不适用条件下允许持平或逊色。验收指标是
三个正文表的机制映射、匹配强对照、双向条件与可反驳结果、同源费用/误差、公开结果
不混口径、独立审查及版本历史。高置信度真实 forecast 则还需要合格数据拟合和留出验证。

## 审核发现与实际修复

三位只读 Codex `gpt-6-sol` 审查员一致指出：v2 精确条件计算基本自洽，但 S0–S4
没有与真实方法建立可识别的映射，所以不能审核通过现实排名/误差。初次数学 GO
不等于我们的方法已经应该有某个分数、提高某个百分比。

v3 增加条件—对照—收益/代价—反证矩阵：

| 条件 | 合理方向 | 判定要求 |
|---|---|---|
| 多样且有独立增量的合法 judgment | 可能改善预测与后来分工，成本后效用未必提高 | count-only/J-masked、trace-only、terminal-only；独立未来结果 |
| 无信息、恒定判断、冷启动 | 无 J 专属收益；若结果同样而额外成本为正，则净效用更差 | 不制造恒定标签有益的主张；0/1/K、强先验与 pooled |
| 错误/旧判断、peer 变化、任务语义错配 | 可有负迁移，强基线可优于我们 | 版本、时间/root holdout、独立真值、旧/新任务恢复 |
| 责任 gate | 可减少错误 producer credit，同时损失 coverage/更新速度 | 独立 owner 真值；归属正确不保证 judgment 事实正确 |
| 高证据成本、长延迟、高到达率 | 质量可更高，费用/积压/尾延迟可更差 | 全服务及失败成本，不能用单次 core timing 代替 |
| 同信息任务条件 ridge/普通组合 | 我们没有预设优势 | matched gate/trace/feature/cost 与各臂独立历史；普通控制追平则增量未验证 |

增加 ΔU=ΔQ−λΔC 的七个赢/平/输代数边界，而非分配命名方法的均值。修正 v2
费用模型低惩罚的解释，补 UNKNOWN 排序界限；SD、CI、coverage 都不凭空填。

复审又发现并修复：private Qp 混入 live baseline、prediction Qp/Y 时点不清、
constant-J 反证方向、L2-public 的公开身份含混、gate公平性会抹去 abstention 代价、
selected-only 重加权覆盖假设、B2 浮点显示 -0.000。正文 ΔA↑ 和补充强对照/服务指标
的集成缺口明确登记，未在本次导出中静默改写论文。

最新两次真实 judgment 的 datetime 空格/T 误接受，以及 ridge 的离线人工交叉偏好
表达能力均进入审查；它们是问题与对照资格证据，不是总体错误率或未来方法效果。
C1 八次调用明确限定为该冻结快照，不冒充项目最新累计调用量。

## 独立终审

三个审查员最终均判定：**v3 作为未拟合条件研究指南 GO，无剩余 P0；实证 forecast
未通过/不可识别。** 首轮意见、第二轮修复、最终判定记录在
[审查文档](../../paper/aamas2027/guides/v3_20261008/independent_review.md)。
首稿 PDF/源/计算/日志已在 `pre_review/` 保存，v1/v2 原 PDF/计算不变。
最终编译、逐页水印/视觉/源摘要与主版一致性由版本 verification 和 build receipt 记录。

收尾补核并行主线的新 producer screen：两次真实生成均通过三项有限检查，按卡停止，
没有 judgment/action/未来 target/更新。因此它未改变本次 forecast 未识别的结论；
尤其不能把旧固定 bad/good 产物或 Guide 潜在 .7/.3 差异当自然 peer 能力差异。详情
见 [screen 报告](20261008_fresh_producer_support_screen.md)。Guide 的 snapshots 不是
项目全量调用清单；本审核自身不执行这些外部推理。

## 对照 Goal 与三份标准

| 标准 | 完成了什么 | 尚缺与原因 |
|---|---|---|
| ER-G1、故事/创新 | 增量信息、未来分工、代价与反证的对应更清楚 | 无合格未来效能和强对照区分；本次不撤销创新主张或降低 Goal |
| ER-G2、方法 | 归属与事实准确性分开；更新速度/适应/遗忘/coverage 区分 | 训练机制、完整更新路径与真实漂移/稳定性仍缺验证 |
| ER-G3、benchmark/baseline | 查明强对照、合法信息、独立历史与预测人群要求 | 权威独立 roots、live parity、closest adapter 未全部资格化 |
| ER-G4/G5、结果与论文 | 手设边界与真实结果严格隔开；保留审核过程与历史 | 方法均值/误差与留出覆盖未识别；正文结果与投稿 gate 不打开 |

## 下一步与复用

1. 先同步正文/确认卡的 ΔA 诊断方向、Qp/Y 分列定义、任务条件强对照和服务成本
   字段；本任务只提出修复，不假称正式矩阵已更新。
2. 复用现有公开 execution trace、task-conditioned ridge、责任/credit/日志接口，
   资格化 trace-only vs trace+J 和 matched composition。测试事实工具提供的信息
   是否已解释全部收益；避免增加模型/encoder或无意义实验。
3. 独立未来流具备合法多样信号后，拟合可观察联合分布，再用 untouched root/stream
   检验均值、误差、协方差、区间宽度与覆盖。无覆盖时不补造未选结果。

交付：唯一 Guide `artifacts/aamas2027/guide_experiment_matrix.pdf`；固定 v3 包
`artifacts/aamas2027/guide_experiment_matrix_v3_20261008/`；源、输入、审查位于 v3
目录。研发指南已实质修复；高置信度真实效果指南仍是未完成任务，不因本次 GO 降级。
