# Task report — 手写预期结果矩阵 v5

后续完整性复核更正：本报告的“完成交付/逐项对应”只能指已展示表格与数值，
不能指完整覆盖主稿所有子实验。参见 [漏项核查](20261009_expected_vs_main_coverage_audit.md)。
原算术审核和 PDF 历史保留，全部实验对标交付仍未完成。

## 目的和衡量方式

交付唯一的 expected experiment table，与当前主 PDF 的实验矩阵逐项对应；
在机制有利时允许小幅优势，成本、负荷和稀疏条件下保留劣势，数值和分母前后一致。
衡量方式：3 张表行列映射、无结果占位符、U/差值/混合分母验算、独立复核、PDF目视检查。

## 完成

以 v4 为数值底稿，复用 v2 的 contextual 主比较，手工整理 v5 JSON 和 LaTeX。
两页 PDF 对应当前 main.pdf Table 4（9 行）、Table 6（8 行）、Table 7（4 行）。
主 PDF 已由并行写作更新为 zh_authoritative_20261009_v6；核验哈希
3df34bd4c1f0cb36eade424735ef5348477444903cc0854efad5eb6fa2e84910。
本任务没有改主稿或把预期数字写入主稿。

修正了旧稿的未说明覆盖率、FA 分母、机械成本分解、假 CI、零时延与无更新混淆。
H4 在同一输入和同一 gate 下与主基线相等，不制造安全优势。
高负荷 payoff 按含丢弃的 ITT 手工修订为 .542/.558；完成事件均值回推合理。
四格主效用 .430/.448/.455/.474，交互只有 .001；不人为制造协同效应。

公开资料重新存档：Meta-Team、DecisionBench、Contextual Bandit Bake-off、
SelectiveNet、Calibration；复用先前核验的 TeamBench 和 graph-IPD 资料。
数字不是这些论文的同协议结果，具体可比性见 NUMERIC_RATIONALE.md。

## 复核

两位独立 gpt-6-sol 审查员各完成初审和修订后复审，最终均通过预期表内部自洽审核。
数值校验、版面回执和主 PDF 映射回执在对应日志目录。保留所有历史版本。
初次 v5 渲染 PDF 已保存；当时的 TeX 未在第一次修改前单独快照，已在档案如实说明。

## 对照 Goal：完成和未完成

完成本次交付：独立、干净、水印、手写数值、逐表映射、优势/劣势和计算自洽。
未完成：真实 benchmark 结果、真实误差、真实方法优越性、三份科学验收标准的关闭。
原因是本任务仅创建预期参照；不把规划审核变成实证结论，也不降低 Goal。
无新 benchmark/LLM 实验/API 推理或 GPU 作业。

复用产物：实际实验可复用相同 row IDs、单位、成本恒等式、配对比较、共同安全分母、
不利条件和复算脚本；不符合预期的实测结果仍必须保留。

## 交付

- `artifacts/aamas2027/expected_experiment_matrix.pdf`（唯一当前预期表）
- `docs/paper/aamas2027/expected_experiment_matrix_v5_20261009/`
- `scripts/check_expected_v5.py`（只读检查，不生成期望值）
