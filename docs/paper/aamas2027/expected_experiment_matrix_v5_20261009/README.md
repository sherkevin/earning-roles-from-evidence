# 唯一生效的 Expected Experiment Tables — v5

最新主 PDF 在本轮中更新，实验表号已变为 **5、7、8**；下方 4/6/7 是 v5 制作时的旧映射，当前表题与来源哈希已标记过期。

**2026-10-09 完整性复核：结构对应，全部实验覆盖尚未通过。** Table 6/7 显示单元齐全，
Table 4 的 updater、责任情景和消融结果仍有漏项；部分数值只存在 JSON，部分尚未定义。
详见 [逐项核查与修复清单](../../../coordination/task_reports/20261009_expected_vs_main_coverage_audit.md)。
下方“一一对应”仅指表号、行列结构，不表示全部子实验已齐全。

[打开主版 PDF](../../../../artifacts/aamas2027/expected_experiment_matrix.pdf)。
这是两页水印预期数值表，不是实验报告；表内数值手工填写，没有生成模拟样本。

与当前论文主 PDF 一一对应：

| 当前论文表 | 对标 PDF | 数量 |
|---|---|---|
| Table 4：实验矩阵 | 第 2 页 | 9 个实验单元、5 列 |
| Table 6：主要结果 | 第 1 页上方 | 8 行、4 列 |
| Table 7：四格消融 | 第 1 页下方 | 4 行、4 列 |

原稿的 CI 表头在预期表中明确改为 planning range。范围是主观合理区间，
没有伪装成实测 95% CI。无结果占位符；不适用的 no-update 时延只在 JSON
按结构性 null 记录，另有 no-op dispatch 数值，不在 PDF 假写 0 ms 更新。

- [手写数值与定义](expected_results.json)
- [逐组依据、公开参考及历史选择](NUMERIC_RATIONALE.md)
- [两位 Codex 审查记录](INDEPENDENT_REVIEW.md)
- [主 PDF 的逐表映射与哈希](correspondence_receipt.json)
- LaTeX：`article/aamas2027/expected_experiment_matrix_v5_20261009/expected_experiment_matrix.tex`
- 版本 PDF：`artifacts/aamas2027/expected_experiment_matrix_v5_20261009/expected_experiment_matrix.pdf`
- 验算与编译：`experiments/logs/expected_experiment_matrix_v5_20261009/`

v4 提供主要数值底稿和逆转情景，v1–v4 原文件保留；v2 旧 canonical pointer
已由 v5 取代。因排版和指标问题产生的中间 PDF 也保留在版本目录中。
科学验收仍按三份正式标准进行；主观期望不自动赋予数字统计显著性，也不能用于
删改不符合预期的真实结果。新增或修改期望只能另起版本，并保留缘由。
